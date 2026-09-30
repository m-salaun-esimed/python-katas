import ast
import inspect
from collections import defaultdict

import numpy as np
import pandas as pd
import pytest

from niveau_08_pandas_bases import exercices as ex
from niveau_08_pandas_bases.jeu_de_donnees import VILLES, ecrire_csv_francais, generer_ventes, version_sale


@pytest.fixture
def df():
    return generer_ventes()


@pytest.fixture
def df_sale():
    return version_sale(generer_ventes())


def montant_python(df) -> list[float]:
    return [q * p for q, p in zip(df["quantite"], df["prix_unitaire"])]


def ca_python(df, cle) -> dict:
    """Calcul de référence en Python pur (sans pandas)."""
    res = defaultdict(float)
    for k, m in zip(df[cle], montant_python(df)):
        res[k] += m
    return dict(res)


# ---------------------------------------------------------------------------
# Règles générales
# ---------------------------------------------------------------------------
def test_pas_de_boucles_sur_les_lignes():
    arbre = ast.parse(inspect.getsource(ex))
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Attribute):
            assert noeud.attr not in {"iterrows", "itertuples"}, f"Interdit : .{noeud.attr}()"
        if isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Attribute) and noeud.func.attr == "apply":
            for kw in noeud.keywords:
                assert not (kw.arg == "axis" and getattr(kw.value, "value", None) in (1, "columns")), "Interdit : apply(axis=1)"


FONCTIONS_DF = [
    ("ajouter_montant", ()),
    ("filtrer", ("Bretagne", 100)),
    ("valeurs_manquantes", ()),
    ("ca_par_region", ()),
    ("top_n_produits", (3,)),
    ("part_par_region", ()),
    ("tableau_croise", ()),
    ("ajouter_tranche", ()),
    ("ca_par_jour_semaine", ()),
    ("clients_fideles", (3,)),
    ("remise_fidelite", ()),
]


@pytest.mark.parametrize("nom, args", FONCTIONS_DF)
def test_ne_modifie_pas_l_entree(df, nom, args):
    copie = df.copy()
    getattr(ex, nom)(df, *args)
    pd.testing.assert_frame_equal(df, copie, obj=f"{nom} a modifié le DataFrame d'entrée !")


def test_nettoyer_ne_modifie_pas_l_entree(df_sale):
    copie = df_sale.copy()
    ex.nettoyer(df_sale)
    pd.testing.assert_frame_equal(df_sale, copie)


# ---------------------------------------------------------------------------
# Lecture / aperçu
# ---------------------------------------------------------------------------
def test_charger_ventes(df, tmp_path):
    chemin = tmp_path / "ventes.csv"
    ecrire_csv_francais(df, chemin)
    assert "," in chemin.read_text().splitlines()[1], "le CSV contient bien des virgules décimales"
    lu = ex.charger_ventes(str(chemin))
    assert lu["date"].dtype == "datetime64[ns]"
    assert lu["quantite"].dtype == "int64"
    assert lu["prix_unitaire"].dtype == "float64"
    pd.testing.assert_frame_equal(lu, df, check_dtype=False)
    assert lu["date"].iloc[0] == pd.Timestamp("2024-01-01")


def test_apercu(df):
    assert ex.apercu(df) == {"lignes": 500, "colonnes": 8, "colonnes_numeriques": ["quantite", "prix_unitaire"]}


# ---------------------------------------------------------------------------
# Transformations
# ---------------------------------------------------------------------------
def test_ajouter_montant(df):
    res = ex.ajouter_montant(df)
    assert list(res.columns) == list(df.columns) + ["montant"]
    assert res["montant"].tolist() == [round(m, 2) for m in montant_python(df)]


def test_filtrer(df):
    res = ex.filtrer(df, "Bretagne", 100)
    attendu = [i for i, (r, m) in enumerate(zip(df["region"], montant_python(df))) if r == "Bretagne" and m >= 100]
    assert len(res) == len(attendu) > 0
    assert list(res.columns) == list(df.columns)
    assert list(res.index) == list(range(len(res)))
    pd.testing.assert_frame_equal(res, df.iloc[attendu].reset_index(drop=True))


def test_valeurs_manquantes(df_sale, df):
    res = ex.valeurs_manquantes(df_sale)
    assert list(res.index) == sorted(res.index, key=lambda c: (-res[c], c))
    for col in res.index:
        assert res[col] == sum(1 for v in df_sale[col] if pd.isna(v))
    assert set(res.index) == {"quantite", "prix_unitaire", "client"}
    assert ex.valeurs_manquantes(df).empty


def test_nettoyer(df_sale):
    res = ex.nettoyer(df_sale)
    assert not res.duplicated().any()
    assert res.isna().sum().sum() == 0
    assert set(res["ville"]) <= set(VILLES)
    assert res["quantite"].dtype == "int64"
    assert list(res.index) == list(range(len(res)))
    # nombre de lignes : doublons retirés puis lignes sans client
    sans_doublons = df_sale.drop_duplicates()
    assert len(res) == sans_doublons["client"].notna().sum()
    # les prix manquants sont remplacés par la médiane du produit
    base = sans_doublons[sans_doublons["client"].notna()].reset_index(drop=True)
    for i in np.flatnonzero(base["prix_unitaire"].isna()):
        produit = base.loc[i, "produit"]
        assert res.loc[i, "prix_unitaire"] == base.loc[base["produit"] == produit, "prix_unitaire"].median()
    # les quantités manquantes valent 0
    assert (res.loc[base["quantite"].isna(), "quantite"] == 0).all()


# ---------------------------------------------------------------------------
# Agrégations
# ---------------------------------------------------------------------------
def test_ca_par_region(df):
    res = ex.ca_par_region(df)
    assert isinstance(res, pd.Series)
    assert res.name == "ca"
    assert res.index.name == "region"
    attendu = ca_python(df, "region")
    assert list(res.index) == sorted(attendu, key=attendu.get, reverse=True)
    for r, v in attendu.items():
        assert res[r] == pytest.approx(v)


def test_stats_par_categorie(df):
    res = ex.stats_par_categorie(df)
    assert list(res.columns) == ["ca_total", "panier_moyen", "nb_ventes", "vente_max"]
    assert res.index.name == "categorie"
    assert res["ca_total"].is_monotonic_decreasing
    montants = defaultdict(list)
    for c, m in zip(df["categorie"], montant_python(df)):
        montants[c].append(m)
    for c, ms in montants.items():
        assert res.loc[c, "ca_total"] == pytest.approx(sum(ms))
        assert res.loc[c, "panier_moyen"] == round(sum(ms) / len(ms), 2)
        assert res.loc[c, "nb_ventes"] == len(ms)
        assert res.loc[c, "vente_max"] == pytest.approx(max(ms))


def test_top_n_produits(df):
    res = ex.top_n_produits(df, 3)
    attendu = sorted(ca_python(df, "produit").items(), key=lambda t: -t[1])[:3]
    assert list(res.columns) == ["produit", "ca"]
    assert list(res.index) == [0, 1, 2]
    assert res["produit"].tolist() == [p for p, _ in attendu]
    assert res["ca"].tolist() == pytest.approx([v for _, v in attendu])


def test_part_par_region(df):
    res = ex.part_par_region(df)
    ca = ca_python(df, "region")
    total = sum(ca.values())
    for r, v in ca.items():
        assert res[r] == round(v / total * 100, 1)
    assert res.is_monotonic_decreasing
    assert res.sum() == pytest.approx(100, abs=0.5)


def test_comparer_objectifs(df):
    objectifs = pd.DataFrame(
        {"region": ["Bretagne", "Occitanie", "Île-de-France"], "objectif": [15_000, 5_000, 10_000]}
    )
    res = ex.comparer_objectifs(df, objectifs)
    assert list(res.columns) == ["region", "ca", "objectif", "ecart", "atteint"]
    assert res["region"].tolist() == ["Bretagne", "Occitanie", "Île-de-France"]
    ca = ca_python(df, "region")
    ligne = res.set_index("region")
    assert ligne.loc["Occitanie", "ca"] == 0
    assert bool(ligne.loc["Occitanie", "atteint"]) is False
    assert ligne.loc["Bretagne", "ca"] == pytest.approx(ca["Bretagne"])
    assert ligne.loc["Bretagne", "ecart"] == round(ca["Bretagne"] - 15_000, 2)
    assert bool(ligne.loc["Bretagne", "atteint"]) is (ca["Bretagne"] >= 15_000)
    assert bool(ligne.loc["Île-de-France", "atteint"]) is (ca["Île-de-France"] >= 10_000)


def test_tableau_croise(df):
    res = ex.tableau_croise(df)
    assert sorted(res.index) == sorted(set(df["region"]))
    assert sorted(res.columns) == ["audio", "informatique", "maison"]
    ca = defaultdict(float)
    for r, c, m in zip(df["region"], df["categorie"], montant_python(df)):
        ca[(r, c)] += m
    for r in res.index:
        for c in res.columns:
            assert res.loc[r, c] == round(ca.get((r, c), 0), 2)


def test_tableau_croise_avec_trous():
    petit = pd.DataFrame(
        {"region": ["A", "B"], "categorie": ["x", "y"], "quantite": [1, 2], "prix_unitaire": [10.0, 5.0]}
    )
    res = ex.tableau_croise(petit)
    assert res.loc["A", "y"] == 0 and res.loc["B", "y"] == 10


def test_ajouter_tranche():
    petit = pd.DataFrame({"quantite": [1, 1, 2, 4, 1], "prix_unitaire": [49.99, 50, 99.99, 50, 0]})
    res = ex.ajouter_tranche(petit)
    assert res["tranche"].tolist() == ["petit", "moyen", "moyen", "gros", "petit"]
    assert isinstance(res["tranche"].dtype, pd.CategoricalDtype)


def test_ca_par_jour_semaine():
    petit = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-06-03", "2024-06-03", "2024-06-09", "2024-06-05"]),  # lun, lun, dim, mer
            "quantite": [1, 2, 1, 1],
            "prix_unitaire": [10.0, 10.0, 7.0, 1.0],
        }
    )
    res = ex.ca_par_jour_semaine(petit)
    assert list(res.index) == ex.JOURS
    assert res.tolist() == [30.0, 0, 1.0, 0, 0, 0, 7.0]


def test_clients_fideles(df):
    dates = defaultdict(set)
    for c, d in zip(df["client"], df["date"]):
        dates[c].add(d)
    for k in (3, 12, 15):
        assert ex.clients_fideles(df, k) == sorted(c for c, ds in dates.items() if len(ds) >= k)


def test_remise_fidelite():
    petit = pd.DataFrame({"quantite": [1, 2, 3, 4, 5], "prix_unitaire": [10.0] * 5})
    res = ex.remise_fidelite(petit)
    assert res["montant_final"].tolist() == [10.0, 19.0, 28.5, 36.0, 45.0]
