"""Générateur du jeu de données de ventes (niveaux 8 et 9). Ne pas modifier.

Pour explorer dans un terminal / notebook :
    from niveau_08_pandas_bases.jeu_de_donnees import generer_ventes
    df = generer_ventes()
    df.head()
"""
import numpy as np
import pandas as pd

VILLES = {
    "Brest": "Bretagne",
    "Rennes": "Bretagne",
    "Quimper": "Bretagne",
    "Nantes": "Pays de la Loire",
    "Angers": "Pays de la Loire",
    "Paris": "Île-de-France",
    "Lyon": "Auvergne-Rhône-Alpes",
}

CATALOGUE = {
    "Clavier": ("informatique", 49.9),
    "Souris": ("informatique", 19.9),
    "Écran": ("informatique", 189.0),
    "Casque": ("audio", 89.0),
    "Enceinte": ("audio", 59.0),
    "Cafetière": ("maison", 39.0),
    "Lampe": ("maison", 24.5),
    "Aspirateur": ("maison", 149.0),
}


def generer_ventes(n: int = 500, seed: int = 42) -> pd.DataFrame:
    """Ventes : date, client, ville, region, categorie, produit, quantite, prix_unitaire."""
    rng = np.random.default_rng(seed)
    produits = rng.choice(list(CATALOGUE), n)
    villes = rng.choice(list(VILLES), n, p=[0.2, 0.15, 0.1, 0.15, 0.1, 0.2, 0.1])
    remise = rng.choice([1.0, 1.0, 1.0, 0.9, 0.8], n)
    df = pd.DataFrame(
        {
            "date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 182, n), unit="D"),
            "client": [f"C{i:03d}" for i in rng.integers(1, 60, n)],
            "ville": villes,
            "region": [VILLES[v] for v in villes],
            "categorie": [CATALOGUE[p][0] for p in produits],
            "produit": produits,
            "quantite": rng.integers(1, 6, n),
            "prix_unitaire": np.round([CATALOGUE[p][1] for p in produits] * remise, 2),
        }
    )
    return df.sort_values(["date", "client"], kind="stable").reset_index(drop=True)


def version_sale(df: pd.DataFrame, seed: int = 0) -> pd.DataFrame:
    """Ajoute des défauts réalistes : doublons, NaN, espaces et casse incohérente."""
    rng = np.random.default_rng(seed)
    sale = df.copy()
    sale["quantite"] = sale["quantite"].astype("float")
    idx = rng.choice(len(sale), 60, replace=False)
    sale.loc[idx[:15], "quantite"] = np.nan
    sale.loc[idx[15:30], "prix_unitaire"] = np.nan
    sale.loc[idx[30:40], "client"] = None
    sale.loc[idx[40:], "ville"] = sale.loc[idx[40:], "ville"].map(lambda v: f"  {v.upper()} ")
    doublons = sale.sample(12, random_state=seed)
    return pd.concat([sale, doublons]).reset_index(drop=True)


def ecrire_csv_francais(df: pd.DataFrame, chemin) -> None:
    """CSV "à la française" : séparateur ;  décimale ,  dates JJ/MM/AAAA."""
    df.to_csv(chemin, sep=";", decimal=",", index=False, date_format="%d/%m/%Y")
