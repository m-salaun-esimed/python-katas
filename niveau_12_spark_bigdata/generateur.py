"""Générateur de gros volumes pour le niveau 12 (ne pas modifier).

Données d'une chaîne de magasins sur l'année 2024 :

  transactions/  (Parquet partitionné par jour=YYYY-MM-DD)
      transaction_id : int64    identifiant métier
      version        : int8     1 = original ; 2 = correction (même transaction_id !) -> il faut dédoublonner
      horodatage     : timestamp
      client_id      : int32
      magasin_id     : int32    ⚠️ très déséquilibré : le magasin 1 (l'entrepôt web) = ~30 % des lignes
      produit_id     : int32
      quantite       : int16    ⚠️ ~0.5 % de lignes invalides (<= 0)
      prix_unitaire  : float64
  magasins.parquet  : magasin_id, ville, region, surface_m2       (200 lignes)
  produits.parquet  : produit_id, nom, categorie, prix_catalogue  (500 lignes)

Utilisation en ligne de commande (pour t'entraîner sur BEAUCOUP de données) :
    python -m niveau_12_spark_bigdata.generateur --lignes 50000000 --sortie data/bigdata
    python -m niveau_12_spark_bigdata.generateur --lignes 20000000 --sortie s3://exos-bigdata/v1
(50 M de lignes ≈ 1 Go de Parquet, quelques minutes.)
"""
import argparse
import os

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.fs as pafs
import pyarrow.parquet as pq

REGIONS = {
    "Bretagne": ["Brest", "Rennes", "Quimper", "Lorient", "Vannes"],
    "Pays de la Loire": ["Nantes", "Angers", "Le Mans"],
    "Île-de-France": ["Paris", "Versailles", "Créteil"],
    "Occitanie": ["Toulouse", "Montpellier"],
    "Grand Est": ["Strasbourg", "Metz", "Reims"],
    "Normandie": ["Rouen", "Caen", "Le Havre"],
}
CATEGORIES = ["informatique", "audio", "maison", "jardin", "sport", "jouets", "livres", "beaute"]
NB_MAGASINS = 200
NB_PRODUITS = 500
NB_CLIENTS = 2_000_000

SCHEMA = pa.schema(
    [
        ("transaction_id", pa.int64()),
        ("version", pa.int8()),
        ("horodatage", pa.timestamp("us")),
        ("client_id", pa.int32()),
        ("magasin_id", pa.int32()),
        ("produit_id", pa.int32()),
        ("quantite", pa.int16()),
        ("prix_unitaire", pa.float64()),
    ]
)


def magasins() -> pd.DataFrame:
    rng = np.random.default_rng(1)
    villes = [(v, r) for r, vs in REGIONS.items() for v in vs]
    choix = [villes[i] for i in rng.integers(0, len(villes), NB_MAGASINS)]
    choix[0] = ("Paris", "Île-de-France")  # magasin 1 = entrepôt web
    return pd.DataFrame(
        {
            "magasin_id": np.arange(1, NB_MAGASINS + 1, dtype="int32"),
            "ville": [v for v, _ in choix],
            "region": [r for _, r in choix],
            "surface_m2": rng.integers(200, 5000, NB_MAGASINS).astype("int32"),
        }
    )


def produits() -> pd.DataFrame:
    rng = np.random.default_rng(2)
    return pd.DataFrame(
        {
            "produit_id": np.arange(1, NB_PRODUITS + 1, dtype="int32"),
            "nom": [f"Produit {i:03d}" for i in range(1, NB_PRODUITS + 1)],
            "categorie": np.array(CATEGORIES)[rng.integers(0, len(CATEGORIES), NB_PRODUITS)],
            "prix_catalogue": np.round(rng.gamma(2.0, 30.0, NB_PRODUITS) + 2, 2),
        }
    )


def _jour(rng, jour: pd.Timestamp, n: int, premier_id: int, prix_catalogue: np.ndarray) -> pa.Table:
    magasin = rng.integers(2, NB_MAGASINS + 1, n)
    magasin[rng.random(n) < 0.30] = 1  # skew
    produit = rng.integers(1, NB_PRODUITS + 1, n)
    quantite = rng.integers(1, 6, n)
    quantite[rng.random(n) < 0.005] = rng.choice([0, -1], 1)[0]
    prix = np.round(prix_catalogue[produit - 1] * rng.choice([1.0, 1.0, 1.0, 0.9, 0.7], n), 2)
    base = pd.DataFrame(
        {
            "transaction_id": np.arange(premier_id, premier_id + n, dtype="int64"),
            "version": np.ones(n, dtype="int8"),
            "horodatage": jour + pd.to_timedelta(np.sort(rng.integers(7 * 3600, 22 * 3600, n)), unit="s"),
            "client_id": rng.integers(1, NB_CLIENTS + 1, n).astype("int32"),
            "magasin_id": magasin.astype("int32"),
            "produit_id": produit.astype("int32"),
            "quantite": quantite.astype("int16"),
            "prix_unitaire": prix,
        }
    )
    corrections = base.sample(frac=0.01, random_state=int(rng.integers(1 << 31))).copy()
    corrections["version"] = np.int8(2)
    corrections["quantite"] = (corrections["quantite"].clip(lower=1) + 1).astype("int16")
    return pa.Table.from_pandas(pd.concat([base, corrections]).sample(frac=1, random_state=0), schema=SCHEMA, preserve_index=False)


def _fs_et_chemin(sortie: str, endpoint: str | None):
    if sortie.startswith("s3://"):
        fs = pafs.S3FileSystem(
            access_key=os.environ.get("EXOS_S3_KEY", "exo"),
            secret_key=os.environ.get("EXOS_S3_SECRET", "exo123456"),
            endpoint_override=endpoint or os.environ.get("EXOS_S3_ENDPOINT", "http://localhost:9010"),
            scheme="http",
            region="us-east-1",
        )
        return fs, sortie[len("s3://"):]
    os.makedirs(sortie, exist_ok=True)
    return pafs.LocalFileSystem(), os.path.abspath(sortie)


def generer(sortie: str, nb_lignes: int = 2_000_000, seed: int = 0, endpoint: str | None = None) -> None:
    """Écrit transactions/ (partitionné par jour), magasins.parquet et produits.parquet sous `sortie`."""
    fs, racine = _fs_et_chemin(sortie, endpoint)
    rng = np.random.default_rng(seed)
    jours = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    par_jour = nb_lignes // len(jours)
    prix = produits()["prix_catalogue"].to_numpy()
    prochain_id = 1
    for jour in jours:
        table = _jour(rng, jour, par_jour, prochain_id, prix)
        prochain_id += par_jour
        dossier = f"{racine}/transactions/jour={jour:%Y-%m-%d}"
        fs.create_dir(dossier, recursive=True)
        pq.write_table(table, f"{dossier}/part-0.parquet", filesystem=fs, compression="snappy")
    pq.write_table(pa.Table.from_pandas(magasins(), preserve_index=False), f"{racine}/magasins.parquet", filesystem=fs)
    pq.write_table(pa.Table.from_pandas(produits(), preserve_index=False), f"{racine}/produits.parquet", filesystem=fs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lignes", type=int, default=10_000_000)
    parser.add_argument("--sortie", default="data/bigdata")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--endpoint", default=None, help="endpoint S3 (défaut http://localhost:9010)")
    args = parser.parse_args()
    generer(args.sortie, args.lignes, args.seed, args.endpoint)
    print(f"OK : ~{args.lignes:,} transactions écrites dans {args.sortie}")
