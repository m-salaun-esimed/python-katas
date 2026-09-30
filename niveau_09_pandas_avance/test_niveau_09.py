import statistics
from collections import defaultdict
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from niveau_08_pandas_bases.jeu_de_donnees import generer_ventes
from niveau_09_pandas_avance import exercices as ex


@pytest.fixture
def df():
    return generer_ventes()


def lignes(df):
    """Itère en Python pur pour les calculs de référence."""
    return df.to_dict("records")


def montant(r):
    return r["quantite"] * r["prix_unitaire"]


@pytest.mark.parametrize(
    "nom, args",
    [("ca_cumule_par_client", ()), ("rang_produits_par_region", ()), ("ca_quotidien", ()), ("evolution_mensuelle", ()),
     ("matrice_cohortes", ()), ("detecter_anomalies", ()), ("rfm", ("2024-07-01",)), ("optimiser_memoire", ()),
     ("meilleur_client_par_mois", ())],
)
def test_ne_modifie_pas_l_entree(df, nom, args):
    copie = df.copy()
    getattr(ex, nom)(df, *args)
    pd.testing.assert_frame_equal(df, copie)


# ---------------------------------------------------------------------------
def test_ca_cumule_par_client(df):
    res = ex.ca_cumule_par_client(df)
    assert list(res.index) == list(range(len(df)))
    cumul, num = defaultdict(float), defaultdict(int)
    attendu = []
    for r in sorted(lignes(df), key=lambda r: (r["client"], r["date"])):
        cumul[r["client"]] += montant(r)
        num[r["client"]] += 1
        attendu.append((r["client"], cumul[r["client"]], num[r["client"]]))
    assert res["client"].tolist() == [a[0] for a in attendu]
    assert res["ca_cumule"].tolist() == pytest.approx([a[1] for a in attendu])
    assert res["num_achat"].tolist() == [a[2] for a in attendu]


def test_rang_produits_par_region(df):
    res = ex.rang_produits_par_region(df)
    assert list(res.columns) == ["region", "produit", "ca", "rang"]
    ca = defaultdict(float)
    for r in lignes(df):
        ca[(r["region"], r["produit"])] += montant(r)
    assert len(res) == len(ca)
    for region, groupe in res.groupby("region"):
        assert groupe["rang"].tolist() == sorted(groupe["rang"])
        meilleur = max((v, p) for (reg, p), v in ca.items() if reg == region)[1]
        assert groupe.iloc[0]["produit"] == meilleur and groupe.iloc[0]["rang"] == 1
    assert res["region"].is_monotonic_increasing


def test_ca_quotidien(df):
    res = ex.ca_quotidien(df)
    assert isinstance(res.index, pd.DatetimeIndex)
    debut, fin = df["date"].min(), df["date"].max()
    assert len(res) == (fin - debut).days + 1
    ca = defaultdict(float)
    for r in lignes(df):
        ca[r["date"]] += montant(r)
    for jour, v in res.items():
        assert v == pytest.approx(ca.get(jour, 0))


def test_ca_quotidien_jours_manquants():
    petit = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-04"]), "quantite": [1, 2], "prix_unitaire": [5.0, 1.0]})
    assert ex.ca_quotidien(petit).tolist() == [5.0, 0, 0, 2.0]


def test_moyenne_mobile():
    petit = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=5), "quantite": [1] * 5, "prix_unitaire": [10.0, 20, 30, 40, 50]})
    assert ex.moyenne_mobile(petit, 3).tolist() == [10.0, 15.0, 20.0, 30.0, 40.0]


def test_ca_hebdomadaire(df):
    res = ex.ca_hebdomadaire(df)
    assert all(d.dayofweek == 0 for d in res.index), "L'index doit contenir des lundis"
    ca = defaultdict(float)
    for r in lignes(df):
        ca[r["date"] - timedelta(days=r["date"].dayofweek)] += montant(r)
    for lundi, v in ca.items():
        assert res[lundi] == pytest.approx(v)
    assert res.sum() == pytest.approx(sum(ca.values()))


def test_evolution_mensuelle(df):
    res = ex.evolution_mensuelle(df)
    assert list(res.columns) == ["ca", "variation_pct", "ca_cumule"]
    ca = defaultdict(float)
    for r in lignes(df):
        ca[r["date"].strftime("%Y-%m")] += montant(r)
    mois = sorted(ca)
    assert list(res.index) == mois
    assert np.isnan(res["variation_pct"].iloc[0])
    for m_prec, m in zip(mois, mois[1:]):
        assert res.loc[m, "variation_pct"] == pytest.approx(round((ca[m] - ca[m_prec]) / ca[m_prec] * 100, 1))
    assert res["ca_cumule"].iloc[-1] == pytest.approx(sum(ca.values()))


def test_format_long_et_large():
    large = pd.DataFrame({"produit": ["B", "A"], "T1": [10, 1], "T2": [20, np.nan], "T3": [30, 3], "T4": [40, 4]})
    long = ex.format_long(large)
    assert list(long.columns) == ["produit", "trimestre", "ventes"]
    assert long["produit"].tolist() == ["A"] * 3 + ["B"] * 4
    assert long["trimestre"].tolist() == ["T1", "T3", "T4", "T1", "T2", "T3", "T4"]
    assert long["ventes"].tolist() == [1, 3, 4, 10, 20, 30, 40]
    retour = ex.format_large(long)
    assert retour.loc["B", "T2"] == 20
    assert np.isnan(retour.loc["A", "T2"])
    assert list(retour.columns) == ["T1", "T2", "T3", "T4"]


def test_compter_tags():
    df_tags = pd.DataFrame({"tags": ["promo|web", " Promo | noel ", np.nan, "web|promo|B2B", "noel"]})
    res = ex.compter_tags(df_tags)
    assert res.to_dict() == {"promo": 3, "noel": 2, "web": 2, "b2b": 1}
    assert list(res.index) == ["promo", "noel", "web", "b2b"]


def test_prix_au_moment_de_la_vente():
    ventes = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-03-01", "2024-01-15", "2024-02-01", "2024-02-20", "2024-01-01"]),
            "produit": ["A", "A", "B", "A", "B"],
            "quantite": [1, 2, 3, 1, 1],
        }
    )
    historique = pd.DataFrame(
        {
            "date_effet": pd.to_datetime(["2024-01-01", "2024-02-15", "2023-12-01", "2024-02-01"]),
            "produit": ["A", "A", "B", "B"],
            "prix": [10.0, 12.0, 5.0, 6.0],
        }
    )
    res = ex.prix_au_moment_de_la_vente(ventes, historique)
    assert res["produit"].tolist() == ["A", "A", "B", "A", "B"], "l'ordre d'origine doit être conservé"
    assert res["prix"].tolist() == [12.0, 10.0, 6.0, 12.0, 5.0]
    assert res["montant"].tolist() == [12.0, 20.0, 18.0, 12.0, 5.0]


def test_matrice_cohortes(df):
    res = ex.matrice_cohortes(df)
    premier = {}
    for r in sorted(lignes(df), key=lambda r: r["date"]):
        premier.setdefault(r["client"], r["date"])
    actifs = defaultdict(set)
    for r in lignes(df):
        p = premier[r["client"]]
        age = (r["date"].year - p.year) * 12 + r["date"].month - p.month
        actifs[(p.strftime("%Y-%m"), age)].add(r["client"])
    assert list(res.index) == sorted({c for c, _ in actifs})
    assert list(res.columns) == list(range(max(a for _, a in actifs) + 1))
    for (cohorte, age), clients in actifs.items():
        assert res.loc[cohorte, age] == len(clients)
    for cohorte in res.index:
        assert res.loc[cohorte, 0] == sum(1 for p in premier.values() if p.strftime("%Y-%m") == cohorte)


def test_detecter_anomalies(df):
    sale = df.copy()
    sale.loc[[10, 200, 350], "prix_unitaire"] = [999.0, 0.01, 2500.0]
    res = ex.detecter_anomalies(sale)
    stats = {}
    for p, g in sale.groupby("produit"):
        stats[p] = (statistics.mean(g["prix_unitaire"]), statistics.stdev(g["prix_unitaire"]))
    attendu = []
    for i, r in sale.iterrows():
        m, s = stats[r["produit"]]
        z = (r["prix_unitaire"] - m) / s
        if abs(z) > 2.5:
            attendu.append((abs(z), i))
    attendu.sort(reverse=True)
    assert len(res) == len(attendu) >= 2
    assert list(res.index) == [i for _, i in attendu], "garde l'index d'origine, trie par |z| décroissant"
    assert "zscore" in res.columns
    assert abs(res["zscore"].iloc[0]) == round(attendu[0][0], 2)


def test_sessionniser():
    ev = pd.DataFrame(
        {
            "utilisateur": ["bob", "alice", "alice", "alice", "bob", "alice", "bob"],
            "horodatage": pd.to_datetime(
                ["2024-01-01 10:00", "2024-01-01 09:00", "2024-01-01 09:20", "2024-01-01 09:50",
                 "2024-01-01 10:31", "2024-01-01 10:21", "2024-01-01 11:00"]
            ),
            "page": list("abcdefg"),
        }
    )
    res = ex.sessionniser(ev)
    assert res["utilisateur"].tolist() == ["alice"] * 4 + ["bob"] * 3
    assert res["session"].tolist() == ["alice-1", "alice-1", "alice-1", "alice-2", "bob-1", "bob-2", "bob-2"]
    assert list(res.index) == list(range(7))


def test_rfm(df):
    res = ex.rfm(df, "2024-07-01")
    ref = pd.Timestamp("2024-07-01")
    par_client = defaultdict(list)
    for r in lignes(df):
        par_client[r["client"]].append(r)
    assert list(res.index) == sorted(par_client)
    assert list(res.columns) == ["recence", "frequence", "montant", "segment"]
    segments = set()
    for c, rs in par_client.items():
        recence = (ref - max(r["date"] for r in rs)).days
        frequence = len({r["date"] for r in rs})
        seg = "champion" if recence <= 30 and frequence >= 10 else "a_risque" if recence > 60 else "regulier"
        segments.add(seg)
        assert res.loc[c, "recence"] == recence
        assert res.loc[c, "frequence"] == frequence
        assert res.loc[c, "montant"] == pytest.approx(round(sum(map(montant, rs)), 2))
        assert res.loc[c, "segment"] == seg, c
    assert segments == {"champion", "regulier", "a_risque"}


def test_optimiser_memoire():
    gros = generer_ventes(50_000, seed=1)
    opti = ex.optimiser_memoire(gros)
    avant = gros.memory_usage(deep=True).sum()
    apres = opti.memory_usage(deep=True).sum()
    assert apres <= 0.4 * avant, f"gain insuffisant : {apres / avant:.0%} de la taille initiale"
    assert isinstance(opti["produit"].dtype, pd.CategoricalDtype)
    assert opti["quantite"].dtype == "int8"
    assert opti["prix_unitaire"].dtype == "float32"
    pd.testing.assert_frame_equal(opti.astype(gros.dtypes.to_dict()), gros, check_exact=False, rtol=1e-6)


def test_meilleur_client_par_mois(df):
    res = ex.meilleur_client_par_mois(df)
    assert list(res.columns) == ["mois", "client", "ca"]
    ca = defaultdict(float)
    for r in lignes(df):
        ca[(r["date"].strftime("%Y-%m"), r["client"])] += montant(r)
    mois = sorted({m for m, _ in ca})
    assert res["mois"].tolist() == mois
    for m, client, v in res.itertuples(index=False):
        meilleur = min(((-val, c) for (mm, c), val in ca.items() if mm == m))
        assert (client, v) == (meilleur[1], pytest.approx(-meilleur[0]))
