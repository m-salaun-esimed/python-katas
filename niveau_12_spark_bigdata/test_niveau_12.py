import ast
import inspect
import os
import uuid

import boto3
import pandas as pd
import pytest
from pyspark.sql import functions as F
from pyspark.sql import types as T

from niveau_12_spark_bigdata import exercices as ex
from niveau_12_spark_bigdata.generateur import generer

NB_LIGNES = int(os.environ.get("EXOS_NB_LIGNES", 2_000_000))


# ---------------------------------------------------------------------------
# Données : générées une fois, références calculées avec pandas
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def racine(tmp_path_factory):
    chemin = str(tmp_path_factory.mktemp("bigdata"))
    generer(chemin, NB_LIGNES, seed=0)
    return chemin


@pytest.fixture(scope="session")
def ref(racine):
    """Toutes les transactions en pandas + dimensions (référence de calcul)."""
    tx = pd.read_parquet(os.path.join(racine, "transactions"))
    tx["jour"] = pd.to_datetime(tx["jour"].astype(str))
    return {
        "tx": tx,
        "magasins": pd.read_parquet(os.path.join(racine, "magasins.parquet")),
        "produits": pd.read_parquet(os.path.join(racine, "produits.parquet")),
    }


@pytest.fixture(scope="session")
def ref_propre(ref):
    tx = ref["tx"].sort_values("version").drop_duplicates("transaction_id", keep="last")
    tx = tx[(tx["quantite"] > 0) & (tx["prix_unitaire"] > 0)]
    tx = tx.merge(ref["magasins"][["magasin_id", "ville", "region"]], on="magasin_id").merge(
        ref["produits"][["produit_id", "nom", "categorie"]], on="produit_id"
    )
    tx["montant"] = tx["quantite"] * tx["prix_unitaire"]
    return tx


@pytest.fixture(scope="session")
def tx(spark, racine):
    return spark.read.parquet(os.path.join(racine, "transactions"))


@pytest.fixture(scope="session")
def magasins(spark, racine):
    return spark.read.parquet(os.path.join(racine, "magasins.parquet"))


@pytest.fixture(scope="session")
def produits(spark, racine):
    return spark.read.parquet(os.path.join(racine, "produits.parquet"))


@pytest.fixture
def sans_broadcast_auto(spark):
    """Désactive le broadcast automatique : seuls les broadcasts explicites restent."""
    ancien = spark.conf.get("spark.sql.autoBroadcastJoinThreshold")
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    yield
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", ancien)


def plan(df) -> str:
    return df._jdf.queryExecution().executedPlan().toString()


def plan_final(df) -> str:
    """Plan après exécution (inclut les décisions de l'AQE)."""
    df.write.format("noop").mode("overwrite").save()
    return df._jdf.queryExecution().executedPlan().toString()


# ---------------------------------------------------------------------------
def test_regles_du_niveau():
    arbre = ast.parse(inspect.getsource(ex))
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Attribute):
            assert noeud.attr not in {"toPandas", "udf", "pandas_udf"}, f"Interdit : {noeud.attr}"


# --- 1. Lecture ------------------------------------------------------------
def test_lire_transactions(spark, racine, ref):
    df = ex.lire_transactions(spark, os.path.join(racine, "transactions"))
    assert df.count() == len(ref["tx"])
    assert isinstance(df.schema["jour"].dataType, T.DateType)


def test_filtrer_periode_partition_pruning(spark, racine, ref):
    df = ex.filtrer_periode(spark, os.path.join(racine, "transactions"), "2024-03-01", "2024-03-10")
    p = plan(df)
    filtres_partition = p.split("PartitionFilters: [", 1)[1].split("]", 1)[0] if "PartitionFilters: [" in p else ""
    assert "jour" in filtres_partition, "Le filtre doit porter sur la colonne de partition `jour` (PartitionFilters vide)"
    t = ref["tx"]
    assert df.count() == ((t["jour"] >= "2024-03-01") & (t["jour"] <= "2024-03-10")).sum()


# --- 2. Nettoyage ----------------------------------------------------------
def test_dedoublonner(tx, ref):
    d = ex.dedoublonner(tx)
    assert d.columns == tx.columns
    attendu = ref["tx"].sort_values("version").drop_duplicates("transaction_id", keep="last")
    stats = d.agg(F.count("*").alias("n"), F.countDistinct("transaction_id").alias("ids"), F.sum("quantite").alias("q")).first()
    assert stats["n"] == stats["ids"] == len(attendu)
    assert stats["q"] == attendu["quantite"].sum(), "Il faut garder la version la plus HAUTE"


def test_nettoyer(tx, ref_propre):
    d = ex.nettoyer(tx)
    stats = d.agg(F.count("*").alias("n"), F.min("quantite").alias("qmin"), F.sum("quantite").alias("q")).first()
    assert stats["n"] == len(ref_propre)
    assert stats["qmin"] > 0
    assert stats["q"] == ref_propre["quantite"].sum()


# --- 3. Jointures ----------------------------------------------------------
def test_enrichir_broadcast(tx, magasins, produits, ref_propre, sans_broadcast_auto):
    d = ex.enrichir(ex.nettoyer(tx), magasins, produits)
    assert {"ville", "region", "nom", "categorie", "montant"} <= set(d.columns)
    p = plan_final(d)
    assert "BroadcastHashJoin" in p, "Utilise F.broadcast() sur les petites tables"
    assert "SortMergeJoin" not in p, "La grosse table ne doit pas être shufflée pour la jointure"
    total = d.agg(F.sum("montant")).first()[0]
    assert total == pytest.approx(ref_propre["montant"].sum(), rel=1e-9)


def test_part_magasin_dominant(tx, ref):
    part = ex.part_magasin_dominant(tx)
    assert part == round(ref["tx"]["magasin_id"].value_counts(normalize=True).iloc[0], 2)
    assert part >= 0.25, "Le magasin 1 est sur-représenté : c'est le skew à traiter"


def test_jointure_salee(tx, magasins, ref, sans_broadcast_auto):
    d = ex.jointure_salee(tx, magasins, nb_sels=8)
    assert set(d.columns) == set(tx.columns) | {"ville", "region", "surface_m2"}
    p = plan_final(d)
    assert "BroadcastHashJoin" not in p, "Ici on veut un vrai shuffle join salé, pas un broadcast"
    assert "Generate" in p or "explode" in p.lower(), "La table magasins doit être répliquée (explode)"
    stats = d.agg(F.count("*").alias("n"), F.sum("quantite").alias("q")).first()
    assert stats["n"] == len(ref["tx"])
    assert stats["q"] == ref["tx"]["quantite"].sum()


# --- 4. Agrégations --------------------------------------------------------
@pytest.fixture(scope="module")
def enrichi(tx, magasins, produits):
    d = ex.enrichir(ex.nettoyer(tx), magasins, produits).cache()
    d.count()
    yield d
    d.unpersist()


def test_ca_par_jour_region(enrichi, ref_propre):
    res = ex.ca_par_jour_region(enrichi)
    assert res.columns == ["jour", "region", "ca", "nb_transactions"]
    lignes = res.collect()
    attendu = ref_propre.groupby(["jour", "region"]).agg(ca=("montant", "sum"), n=("montant", "size")).reset_index()
    assert len(lignes) == len(attendu)
    assert [(l["jour"], l["region"]) for l in lignes[:3]] == [(r.jour.date(), r.region) for r in attendu.head(3).itertuples()]
    for l, r in zip(lignes, attendu.itertuples()):
        assert l["ca"] == pytest.approx(round(r.ca, 2), abs=0.011)
        assert l["nb_transactions"] == r.n


def test_top_produits_par_categorie(enrichi, ref_propre):
    res = ex.top_produits_par_categorie(enrichi, 3)
    assert res.columns == ["categorie", "nom", "ca", "rang"]
    ca = ref_propre.groupby(["categorie", "nom"])["montant"].sum().round(2).reset_index()
    attendu = ca.sort_values(["categorie", "montant", "nom"], ascending=[True, False, True]).groupby("categorie").head(3)
    assert [(l["categorie"], l["nom"], l["rang"]) for l in res.collect()] == [
        (r.categorie, r.nom, i % 3 + 1) for i, r in enumerate(attendu.itertuples())
    ]


def test_ca_par_heure(enrichi, ref_propre):
    res = ex.ca_par_heure(enrichi).collect()
    attendu = ref_propre.groupby(ref_propre["horodatage"].dt.hour)["montant"].sum()
    assert [l["heure"] for l in res] == list(attendu.index)
    assert [l["ca"] for l in res] == pytest.approx(attendu.round(2).tolist(), abs=0.011)


def test_nb_clients_approx(tx, ref):
    exact = ref["tx"]["client_id"].nunique()
    approx = ex.nb_clients_approx(tx)
    assert isinstance(approx, int)
    assert abs(approx - exact) / exact < 0.05
    assert "approx_count_distinct" in inspect.getsource(ex.nb_clients_approx)


# --- 5. Écriture -----------------------------------------------------------
def test_ecrire_optimise(tx, tmp_path, spark):
    janvier = tx.filter(F.col("jour") < "2024-02-01")
    chemin = str(tmp_path / "sortie")
    ex.ecrire_optimise(janvier, chemin)
    partitions = sorted(p for p in os.listdir(chemin) if p.startswith("jour="))
    assert len(partitions) == 31
    for p in partitions:
        fichiers = [f for f in os.listdir(os.path.join(chemin, p)) if f.endswith(".parquet")]
        assert len(fichiers) == 1, f"{p} contient {len(fichiers)} fichiers (1 attendu)"
    assert spark.read.parquet(chemin).count() == janvier.count()


def test_pipeline(spark, racine, ref_propre, tmp_path):
    sortie = str(tmp_path / "agregats")
    n = ex.pipeline(spark, racine, sortie)
    t = ref_propre.assign(mois=ref_propre["jour"].dt.strftime("%Y-%m"))
    attendu = t.groupby(["region", "mois"]).agg(ca=("montant", "sum"), nb_transactions=("montant", "size"), nb_clients=("client_id", "nunique"))
    assert n == len(attendu)
    assert sorted(p for p in os.listdir(sortie) if p.startswith("region=")) == sorted(f"region={r}" for r in t["region"].unique())
    res = spark.read.parquet(sortie).toPandas().set_index(["region", "mois"]).sort_index()
    assert len(res) == len(attendu)
    for cle, r in attendu.iterrows():
        assert res.loc[cle, "ca"] == pytest.approx(round(r.ca, 2), abs=0.011)
        assert res.loc[cle, "nb_transactions"] == r.nb_transactions
        assert res.loc[cle, "nb_clients"] == r.nb_clients


# --- 6. S3 -----------------------------------------------------------------
BUCKET = "exos-niveau12"


@pytest.mark.s3
def test_s3_aller_retour(spark, s3_endpoint, enrichi, ref_propre):
    client = boto3.client("s3", endpoint_url=s3_endpoint, aws_access_key_id="exo", aws_secret_access_key="exo123456", region_name="us-east-1")
    try:
        client.create_bucket(Bucket=BUCKET)
    except client.exceptions.ClientError:
        pass
    ex.configurer_s3a(spark, s3_endpoint, "exo", "exo123456")
    conf = spark.sparkContext._jsc.hadoopConfiguration()
    assert conf.get("fs.s3a.path.style.access") == "true"

    uri = f"s3a://{BUCKET}/tests/{uuid.uuid4().hex}/ca"
    agregats = ex.ca_par_jour_region(enrichi)
    ex.exporter_vers_s3(agregats, uri)
    cles = [o["Key"] for o in client.list_objects_v2(Bucket=BUCKET, Prefix=uri.split(f"{BUCKET}/")[1]).get("Contents", [])]
    assert any("region=Bretagne/" in c for c in cles)
    attendu = ref_propre[ref_propre["region"] == "Bretagne"].groupby("jour")["montant"].sum().round(2).sum()
    assert ex.ca_region_depuis_s3(spark, uri, "Bretagne") == pytest.approx(attendu, abs=0.05)
