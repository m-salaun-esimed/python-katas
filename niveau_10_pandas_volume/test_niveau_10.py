import os
import uuid

import boto3
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

from niveau_10_pandas_volume import exercices as ex
from niveau_10_pandas_volume.generateur import REGIONS, generer


# ---------------------------------------------------------------------------
# Données partagées (générées une fois par session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def gros_df():
    return generer(1_000_000, seed=0)


@pytest.fixture(scope="session")
def gros_csv(gros_df, tmp_path_factory):
    chemin = tmp_path_factory.mktemp("csv") / "ventes.csv"
    gros_df.to_csv(chemin, index=False)
    return str(chemin)


@pytest.fixture(scope="session")
def ca_region_attendu(gros_df):
    m = gros_df["quantite"].to_numpy() * gros_df["prix_unitaire"].to_numpy()
    return {r: m[gros_df["region"].to_numpy() == r].sum() for r in REGIONS}


@pytest.fixture(scope="session")
def dossier_partitionne(gros_df, tmp_path_factory):
    dossier = str(tmp_path_factory.mktemp("parquet") / "ventes")
    ex.ecrire_partitionne(gros_df, dossier)
    return dossier


# ---------------------------------------------------------------------------
# 1. Gros CSV
# ---------------------------------------------------------------------------
def test_agreger_csv_par_morceaux(gros_csv, ca_region_attendu, monkeypatch):
    appels = []
    original = pd.read_csv

    def espion(*args, **kwargs):
        appels.append(kwargs)
        return original(*args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", espion)
    res = ex.agreger_csv_par_morceaux(gros_csv, taille_morceau=100_000)
    assert appels, "Utilise pd.read_csv"
    assert all(a.get("chunksize") for a in appels), "Il faut lire par morceaux (chunksize=...)"
    assert all(a.get("usecols") for a in appels), "Ne lis que les colonnes utiles (usecols=...)"
    assert res.name == "ca"
    assert list(res.index) == sorted(REGIONS)
    for r, v in ca_region_attendu.items():
        assert res[r] == pytest.approx(round(v, 2), abs=0.02)


def test_csv_vers_parquet(gros_csv, gros_df, tmp_path):
    cible = str(tmp_path / "ventes.parquet")
    ex.csv_vers_parquet(gros_csv, cible)
    taille_csv, taille_pq = os.path.getsize(gros_csv), os.path.getsize(cible)
    assert taille_pq * 4 <= taille_csv, f"Parquet {taille_pq / 1e6:.1f} Mo vs CSV {taille_csv / 1e6:.1f} Mo"
    meta = pq.ParquetFile(cible).metadata
    assert meta.num_rows == len(gros_df)
    assert meta.row_group(0).column(0).compression == "ZSTD"
    relu = pd.read_parquet(cible)
    assert str(relu["date"].dtype).startswith("datetime64")
    assert isinstance(relu["region"].dtype, pd.CategoricalDtype)
    assert isinstance(relu["produit"].dtype, pd.CategoricalDtype)
    assert relu["quantite"].dtype == "int16"
    assert relu["prix_unitaire"].dtype == "float32"
    assert relu["quantite"].sum() == gros_df["quantite"].sum()


# ---------------------------------------------------------------------------
# 2. Parquet partitionné
# ---------------------------------------------------------------------------
def test_ecrire_partitionne(dossier_partitionne):
    annees = sorted(os.listdir(dossier_partitionne))
    assert annees == ["annee=2024"]
    mois = sorted(os.listdir(os.path.join(dossier_partitionne, "annee=2024")), key=lambda m: int(m.split("=")[1]))
    assert mois == [f"mois={i}" for i in range(1, 13)]
    fichiers = os.listdir(os.path.join(dossier_partitionne, "annee=2024", "mois=3"))
    assert fichiers and all(f.endswith(".parquet") for f in fichiers)


def test_lire_partition(dossier_partitionne, gros_df, monkeypatch):
    res = ex.lire_partition(dossier_partitionne, 2024, 3, ["client", "quantite"])
    attendu = gros_df[gros_df["date"].dt.month == 3]
    assert list(res.columns) == ["client", "quantite"]
    assert len(res) == len(attendu)
    assert res["quantite"].sum() == attendu["quantite"].sum()
    assert list(res.index) == list(range(len(res)))


@pytest.fixture(scope="session")
def fichier_unique(gros_df, tmp_path_factory):
    chemin = str(tmp_path_factory.mktemp("un") / "ventes.parquet")
    gros_df.sort_values("date").to_parquet(chemin, row_group_size=100_000, index=False)
    return chemin


@pytest.fixture
def lecture_interdite(monkeypatch):
    def interdit(*a, **k):
        raise AssertionError("Lecture des données interdite : utilise uniquement les métadonnées !")

    monkeypatch.setattr(pq, "read_table", interdit)
    monkeypatch.setattr(pd, "read_parquet", interdit)
    monkeypatch.setattr(pq.ParquetFile, "read", interdit)
    monkeypatch.setattr(pq.ParquetFile, "read_row_group", interdit)
    monkeypatch.setattr(pq.ParquetFile, "iter_batches", interdit)


def test_compter_lignes_parquet(fichier_unique, lecture_interdite):
    assert ex.compter_lignes_parquet(fichier_unique) == 1_000_000


def test_min_max_colonne(fichier_unique, gros_df, lecture_interdite):
    assert ex.min_max_colonne(fichier_unique, "quantite") == (1, 9)
    mini, maxi = ex.min_max_colonne(fichier_unique, "prix_unitaire")
    assert (mini, maxi) == (gros_df["prix_unitaire"].min(), gros_df["prix_unitaire"].max())


def test_ca_par_produit_arrow(dossier_partitionne, gros_df):
    sous = gros_df[gros_df["region"] == "Bretagne"]
    attendu = (sous["quantite"] * sous["prix_unitaire"]).groupby(sous["produit"]).sum().sort_values(ascending=False)
    res = ex.ca_par_produit_arrow(dossier_partitionne, "Bretagne")
    assert list(res.columns) == ["produit", "ca"]
    assert res["produit"].tolist() == list(attendu.index)
    assert res["ca"].tolist() == pytest.approx(attendu.round(2).tolist(), abs=0.05)
    assert list(res.index) == list(range(len(res)))


# ---------------------------------------------------------------------------
# 3. Qualité & incrémental
# ---------------------------------------------------------------------------
def test_separer_valides_rejets():
    df = pd.DataFrame(
        {
            "client": ["A", None, "C", "D", "E", "F", None],
            "quantite": [1, 2, 0, 3, np.nan, 2, -1],
            "prix_unitaire": [10.0, 5.0, 5.0, -1.0, 3.0, 4.0, 2.0],
            "date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", "2024-05-01", "2025-01-01", "2024-01-01"]),
        },
        index=[10, 11, 12, 13, 14, 15, 16],
    )
    valides, rejets = ex.separer_valides_rejets(df)
    assert list(valides.index) == [10]
    assert list(valides.columns) == list(df.columns)
    assert rejets["raison"].to_dict() == {
        11: "client_manquant",
        12: "quantite_invalide",
        13: "prix_invalide",
        14: "quantite_invalide",
        15: "date_future",
        16: "client_manquant",
    }


def test_fusion_incrementale():
    historique = pd.DataFrame({"id": [1, 2, 3], "valeur": ["a", "b", "c"], "maj_le": pd.to_datetime(["2024-01-01", "2024-01-05", "2024-01-03"])})
    nouveautes = pd.DataFrame({"id": [2, 3, 4], "valeur": ["B", "C", "D"], "maj_le": pd.to_datetime(["2024-01-10", "2024-01-03", "2024-01-02"])})
    res = ex.fusion_incrementale(historique, nouveautes)
    assert res["id"].tolist() == [1, 2, 3, 4]
    assert res["valeur"].tolist() == ["a", "B", "C", "D"]
    assert list(res.index) == [0, 1, 2, 3]


def test_fusion_incrementale_ne_regresse_pas():
    historique = pd.DataFrame({"id": [1], "valeur": ["recent"], "maj_le": pd.to_datetime(["2024-06-01"])})
    nouveautes = pd.DataFrame({"id": [1], "valeur": ["vieux"], "maj_le": pd.to_datetime(["2024-01-01"])})
    assert ex.fusion_incrementale(historique, nouveautes)["valeur"].tolist() == ["recent"]


# ---------------------------------------------------------------------------
# 4. S3 (docker compose up -d)
# ---------------------------------------------------------------------------
BUCKET = "exos-niveau10"


@pytest.fixture(scope="session")
def s3(s3_endpoint):
    client = boto3.client("s3", endpoint_url=s3_endpoint, aws_access_key_id=ex.CLE_S3, aws_secret_access_key=ex.SECRET_S3, region_name="us-east-1")
    try:
        client.create_bucket(Bucket=BUCKET)
    except client.exceptions.ClientError:
        pass
    return client


@pytest.fixture
def prefixe():
    return f"tests/{uuid.uuid4().hex}"


@pytest.mark.s3
def test_options_stockage():
    opts = ex.options_stockage("http://localhost:9010")
    assert opts["client_kwargs"]["endpoint_url"] == "http://localhost:9010"
    assert opts["key"] == ex.CLE_S3 and opts["secret"] == ex.SECRET_S3


@pytest.mark.s3
def test_ecrire_lire_s3(s3, s3_endpoint, prefixe, gros_df):
    petit = gros_df.head(1000)
    uri = f"s3://{BUCKET}/{prefixe}/petit.parquet"
    ex.ecrire_s3(petit, uri, s3_endpoint)
    assert s3.head_object(Bucket=BUCKET, Key=f"{prefixe}/petit.parquet")["ContentLength"] > 0
    pd.testing.assert_frame_equal(ex.lire_s3(uri, s3_endpoint), petit.reset_index(drop=True))


@pytest.mark.s3
def test_lister_s3_pagination(s3, s3_endpoint, prefixe):
    cles = [f"{prefixe}/fichier_{i:05d}.txt" for i in range(1050)]
    for c in cles:
        s3.put_object(Bucket=BUCKET, Key=c, Body=b"x")
    assert ex.lister_s3(BUCKET, prefixe, s3_endpoint) == cles


@pytest.mark.s3
def test_s3_partitionne(s3, s3_endpoint, prefixe, gros_df, ca_region_attendu, monkeypatch):
    uri = f"s3://{BUCKET}/{prefixe}/ventes"
    ex.ecrire_s3_partitionne(gros_df.head(200_000), uri, s3_endpoint)
    cles = [o["Key"] for page in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=prefixe) for o in page.get("Contents", [])]
    assert any("region=Bretagne/" in c for c in cles)
    sous = gros_df.head(200_000)
    sous = sous[sous["region"] == "Normandie"]
    assert ex.ca_region_s3(uri, s3_endpoint, "Normandie") == pytest.approx(round((sous["quantite"] * sous["prix_unitaire"]).sum(), 2), abs=0.02)
