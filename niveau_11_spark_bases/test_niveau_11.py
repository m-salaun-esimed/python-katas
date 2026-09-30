import ast
import inspect
import random
from collections import defaultdict
from datetime import date, timedelta

import pytest
from pyspark.sql import types as T

from niveau_11_spark_bases import exercices as ex

REGIONS = ["Bretagne", "Normandie", "Occitanie"]
PRODUITS = {"Clavier": 49.9, "Souris": 19.9, "Écran": 189.0, "Casque": 89.0, "Lampe": 24.5}


def generer_lignes(n=300, seed=1):
    rnd = random.Random(seed)
    lignes = []
    for i in range(1, n + 1):
        p = rnd.choice(list(PRODUITS))
        lignes.append(
            (
                i,
                date(2024, 1, 1) + timedelta(days=rnd.randrange(120)),
                f"C{rnd.randrange(1, 25):02d}",
                rnd.choice(REGIONS),
                p,
                rnd.randint(1, 5),
                PRODUITS[p],
            )
        )
    return lignes


LIGNES = generer_lignes()
COLS = ["id", "date", "client", "region", "produit", "quantite", "prix_unitaire"]


def dicts(lignes=LIGNES):
    return [dict(zip(COLS, l)) for l in lignes]


def montant(r):
    return r["quantite"] * r["prix_unitaire"]


@pytest.fixture(scope="module")
def df(spark):
    return spark.createDataFrame(LIGNES, schema=ex.schema_ventes())


def plan(df) -> str:
    return df._jdf.queryExecution().executedPlan().toString()


# ---------------------------------------------------------------------------
def test_regles_du_niveau():
    arbre = ast.parse(inspect.getsource(ex))
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Attribute):
            assert noeud.attr not in {"collect", "toPandas", "udf", "pandas_udf"}, f"Interdit dans ce niveau : {noeud.attr}"
        if isinstance(noeud, ast.Name):
            assert noeud.id not in {"udf", "pandas_udf"}


def test_schema_ventes():
    s = ex.schema_ventes()
    assert isinstance(s, T.StructType)
    assert [(f.name, type(f.dataType)) for f in s.fields] == [
        ("id", T.IntegerType), ("date", T.DateType), ("client", T.StringType), ("region", T.StringType),
        ("produit", T.StringType), ("quantite", T.IntegerType), ("prix_unitaire", T.DoubleType),
    ]
    assert s["id"].nullable is False


def test_creer_dataframe(spark):
    d = ex.creer_dataframe(spark, LIGNES[:10])
    assert d.count() == 10
    assert d.schema == ex.schema_ventes()


def test_ajouter_colonnes(df):
    res = {r["id"]: r for r in ex.ajouter_colonnes(df).collect()}
    for r in dicts():
        m = round(montant(r), 2)
        sortie = res[r["id"]]
        assert sortie["montant"] == pytest.approx(m)
        assert sortie["mois"] == r["date"].strftime("%Y-%m")
        assert sortie["taille"] == ("gros" if m >= 200 else "moyen" if m >= 50 else "petit")


def test_filtrer(df):
    res = sorted(r["id"] for r in ex.filtrer(df, "Bretagne", 100).collect())
    assert res == sorted(r["id"] for r in dicts() if r["region"] == "Bretagne" and montant(r) >= 100)
    assert res


def test_ca_par_region(df):
    res = ex.ca_par_region(df)
    assert res.columns == ["region", "ca", "nb_ventes"]
    ca, nb = defaultdict(float), defaultdict(int)
    for r in dicts():
        ca[r["region"]] += montant(r)
        nb[r["region"]] += 1
    lignes = res.collect()
    assert [l["region"] for l in lignes] == sorted(ca, key=ca.get, reverse=True)
    for l in lignes:
        assert l["ca"] == pytest.approx(round(ca[l["region"]], 2))
        assert l["nb_ventes"] == nb[l["region"]]


def test_top_n_par_region(df):
    res = ex.top_n_par_region(df, 2)
    assert res.columns == ["region", "produit", "ca", "rang"]
    ca = defaultdict(float)
    for r in dicts():
        ca[(r["region"], r["produit"])] += montant(r)
    attendu = []
    for reg in sorted(REGIONS):
        items = sorted(((p, v) for (rr, p), v in ca.items() if rr == reg), key=lambda t: (-t[1], t[0]))[:2]
        attendu += [(reg, p, i + 1) for i, (p, _) in enumerate(items)]
    assert [(l["region"], l["produit"], l["rang"]) for l in res.collect()] == attendu


def test_pivot_region_mois(df):
    res = ex.pivot_region_mois(df)
    assert res.columns == ["region", "2024-01", "2024-02", "2024-03", "2024-04"]
    ca = defaultdict(float)
    for r in dicts():
        ca[(r["region"], r["date"].strftime("%Y-%m"))] += montant(r)
    lignes = res.collect()
    assert [l["region"] for l in lignes] == sorted(REGIONS)
    for l in lignes:
        for m in res.columns[1:]:
            assert l[m] == pytest.approx(round(ca.get((l["region"], m), 0), 2))


def test_pivot_mois_sans_vente(spark):
    d = spark.createDataFrame(
        [(1, date(2024, 1, 5), "A", "X", "p", 1, 10.0), (2, date(2024, 2, 5), "A", "Y", "p", 2, 10.0)], ex.schema_ventes()
    )
    res = {l["region"]: l for l in ex.pivot_region_mois(d).collect()}
    assert res["X"]["2024-02"] == 0 and res["Y"]["2024-02"] == 20


def test_nettoyer(spark):
    sale = spark.createDataFrame(
        [
            (1, date(2024, 1, 1), "A", "  bretagne ", "p", 1, 1.0),
            (1, date(2024, 1, 1), "A", "  bretagne ", "p", 1, 1.0),
            (2, date(2024, 1, 1), None, "Normandie", "p", 1, 1.0),
            (3, date(2024, 1, 1), "B", "OCCITANIE", "p", None, 1.0),
        ],
        ex.schema_ventes(),
    )
    res = sorted(ex.nettoyer(sale).collect(), key=lambda r: r["id"])
    assert [(r["id"], r["region"], r["quantite"]) for r in res] == [(1, "Bretagne", 1), (3, "Occitanie", 0)]


def test_joindre_clients(spark, df):
    clients = spark.createDataFrame([(f"C{i:02d}", "pro" if i % 2 else "particulier") for i in range(1, 15)], ["client", "segment"])
    res = ex.joindre_clients(df, clients)
    assert res.count() == len(LIGNES)
    for l in res.select("client", "segment").collect():
        n = int(l["client"][1:])
        assert l["segment"] == ("inconnu" if n >= 15 else "pro" if n % 2 else "particulier")


def test_requete_sql(spark, df):
    res = ex.requete_sql(spark, df, 5000)
    assert res.columns == ["produit", "ca"]
    ca = defaultdict(float)
    for r in dicts():
        ca[r["produit"]] += montant(r)
    attendu = sorted(((p, round(v, 2)) for p, v in ca.items() if round(v, 2) > 5000), key=lambda t: -t[1])
    assert [(l["produit"], pytest.approx(l["ca"])) for l in res.collect()] == attendu
    assert spark.catalog.tableExists("ventes")


def test_compter_tags(spark):
    d = spark.createDataFrame([("promo,web",), (" Promo , noel",), ("web, promo,B2B",)], ["tags"])
    assert [(l["tag"], l["nb"]) for l in ex.compter_tags(d).collect()] == [("promo", 3), ("web", 2), ("b2b", 1), ("noel", 1)]


def test_extraire_domaine_sans_udf(spark):
    d = spark.createDataFrame([("  Alice@Gmail.COM ",), ("bob@ENSTA.fr",)], ["email"])
    res = ex.extraire_domaine(d)
    assert [(l["email_propre"], l["domaine"]) for l in res.collect()] == [("alice@gmail.com", "gmail.com"), ("bob@ensta.fr", "ensta.fr")]
    assert "PythonUDF" not in plan(res) and "BatchEvalPython" not in plan(res)


def test_cumul_et_ecart(df):
    res = {l["id"]: l for l in ex.cumul_et_ecart(df).collect()}
    cumul, derniere = defaultdict(float), {}
    for r in sorted(dicts(), key=lambda r: (r["client"], r["date"], r["id"])):
        cumul[r["client"]] += montant(r)
        l = res[r["id"]]
        assert l["ca_cumule"] == pytest.approx(round(cumul[r["client"]], 2))
        precedent = derniere.get(r["client"])
        assert l["jours_depuis"] == (None if precedent is None else (r["date"] - precedent).days)
        derniere[r["client"]] = r["date"]


def test_ecrire_et_relire(spark, df, tmp_path):
    chemin = str(tmp_path / "ventes")
    relu = ex.ecrire_et_relire(spark, df, chemin)
    assert relu.count() == len(LIGNES)
    assert sorted(p.name for p in (tmp_path / "ventes").iterdir() if p.name.startswith("region=")) == [f"region={r}" for r in sorted(REGIONS)]
    ex.ecrire_et_relire(spark, df, chemin)  # overwrite : pas de doublons
    assert spark.read.parquet(chemin).count() == len(LIGNES)
