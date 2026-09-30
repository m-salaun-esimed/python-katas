"""Les résultats attendus sont recalculés en Python à partir de donnees.py :
tu ne peux pas "tricher" en recopiant des valeurs."""
from collections import defaultdict
from decimal import Decimal
from statistics import mean

import psycopg
import pytest

from niveau_06_sql import donnees as D
from niveau_06_sql import exercices as ex


# ---------------------------------------------------------------------------
# Fixtures & outils
# ---------------------------------------------------------------------------
@pytest.fixture
def conn(pg_url):
    connexion = psycopg.connect(pg_url, autocommit=True)
    D.charger(connexion)
    yield connexion
    connexion.close()


def normaliser(valeur):
    if isinstance(valeur, (Decimal, float)):
        return round(float(valeur), 2)
    return valeur


def executer(conn, requete: str) -> list[tuple]:
    if "TODO" in requete and "select" not in requete.lower():
        pytest.fail("Requête pas encore écrite")
    lignes = conn.execute(requete).fetchall()
    return [tuple(normaliser(v) for v in ligne) for ligne in lignes]


def colonnes(conn, requete: str) -> list[str]:
    cur = conn.execute(requete)
    return [c.name for c in cur.description]


CLIENT = {c[0]: c for c in D.CLIENTS}
PRODUIT = {p[0]: p for p in D.PRODUITS}
COMMANDE = {c[0]: c for c in D.COMMANDES}
VALIDES = {c[0] for c in D.COMMANDES if c[3] != "annulee"}


def montant_commandes(ids) -> dict[int, float]:
    m = defaultdict(float)
    for cmd, _, q, pu in D.LIGNES:
        if cmd in ids:
            m[cmd] += q * pu
    return m


def ca_par(cle) -> dict:
    res = defaultdict(float)
    for cmd, prod, q, pu in D.LIGNES:
        if cmd in VALIDES:
            res[cle(cmd, prod)] += q * pu
    return res


def mois(cmd_id) -> str:
    return COMMANDE[cmd_id][2].strftime("%Y-%m")


def r2(x):
    return round(x + 1e-9, 2)


# ---------------------------------------------------------------------------
# Partie A
# ---------------------------------------------------------------------------
def test_requete_01(conn):
    attendu = sorted([(c[0], c[1]) for c in D.CLIENTS if c[2] == "Brest"], key=lambda t: t[1])
    assert executer(conn, ex.REQUETE_01) == attendu
    assert colonnes(conn, ex.REQUETE_01) == ["id", "nom"]


def test_requete_02(conn):
    attendu = [(p[1], p[3]) for p in sorted(D.PRODUITS, key=lambda p: -p[3]) if p[3] > 50]
    assert executer(conn, ex.REQUETE_02) == attendu


def test_requete_03(conn):
    compte = defaultdict(int)
    for c in D.COMMANDES:
        compte[c[3]] += 1
    assert executer(conn, ex.REQUETE_03) == sorted(compte.items())
    assert colonnes(conn, ex.REQUETE_03) == ["statut", "nb"]


def test_requete_04(conn):
    compte = {c[1]: 0 for c in D.CLIENTS}
    for c in D.COMMANDES:
        compte[CLIENT[c[1]][1]] += 1
    attendu = sorted(compte.items(), key=lambda t: (-t[1], t[0]))
    assert executer(conn, ex.REQUETE_04) == attendu
    assert colonnes(conn, ex.REQUETE_04) == ["nom", "nb_commandes"]


def test_requete_05(conn):
    ca = ca_par(lambda cmd, prod: PRODUIT[prod][1])
    attendu = [(nom, r2(v)) for nom, v in sorted(ca.items(), key=lambda t: (-t[1], t[0]))]
    assert executer(conn, ex.REQUETE_05) == attendu


def test_requete_06(conn):
    ca = ca_par(lambda cmd, prod: CLIENT[COMMANDE[cmd][1]][1])
    attendu = [(nom, r2(v)) for nom, v in sorted(ca.items(), key=lambda t: -t[1])[:3]]
    assert executer(conn, ex.REQUETE_06) == attendu


def test_requete_07(conn):
    commandes = {l[1] for l in D.LIGNES}
    attendu = sorted((p[1],) for p in D.PRODUITS if p[0] not in commandes)
    assert executer(conn, ex.REQUETE_07) == attendu


def test_requete_08(conn):
    ca = ca_par(lambda cmd, prod: mois(cmd))
    assert executer(conn, ex.REQUETE_08) == [(m, r2(v)) for m, v in sorted(ca.items())]
    assert colonnes(conn, ex.REQUETE_08) == ["mois", "ca"]


def test_requete_09(conn):
    compte = defaultdict(int)
    for c in D.COMMANDES:
        if c[3] == "livree":
            compte[CLIENT[c[1]][1]] += 1
    attendu = sorted((n, k) for n, k in compte.items() if k >= 2)
    assert executer(conn, ex.REQUETE_09) == attendu


def test_requete_10(conn):
    montants = montant_commandes(VALIDES)
    par_ville = defaultdict(list)
    for cmd, m in montants.items():
        par_ville[CLIENT[COMMANDE[cmd][1]][2]].append(m)
    attendu = sorted((v, r2(mean(ms))) for v, ms in par_ville.items())
    assert executer(conn, ex.REQUETE_10) == attendu
    assert colonnes(conn, ex.REQUETE_10) == ["ville", "panier_moyen"]


def test_requete_11(conn):
    ca = ca_par(lambda cmd, prod: prod)
    par_cat = defaultdict(list)
    for prod, v in ca.items():
        par_cat[PRODUIT[prod][2]].append((PRODUIT[prod][1], r2(v)))
    attendu = []
    for cat, items in par_cat.items():
        for nom, v in items:
            rang = 1 + sum(1 for _, autre in items if autre > v)
            attendu.append((cat, nom, v, rang))
    attendu.sort(key=lambda t: (t[0], t[3], t[1]))
    assert executer(conn, ex.REQUETE_11) == attendu
    assert colonnes(conn, ex.REQUETE_11) == ["categorie", "nom", "ca", "rang"]


def test_requete_12(conn):
    ca = sorted(ca_par(lambda cmd, prod: mois(cmd)).items())
    cumul, attendu = 0.0, []
    for m, v in ca:
        cumul += v
        attendu.append((m, r2(v), r2(cumul)))
    assert executer(conn, ex.REQUETE_12) == attendu


def test_requete_13(conn):
    dates = defaultdict(list)
    for c in D.COMMANDES:
        dates[CLIENT[c[1]][1]].append(c[2])
    attendu = sorted((n, min(d), max(d), (max(d) - min(d)).days) for n, d in dates.items())
    assert executer(conn, ex.REQUETE_13) == attendu
    assert colonnes(conn, ex.REQUETE_13) == ["nom", "premiere", "derniere", "jours"]


def test_requete_14(conn):
    montants = montant_commandes(VALIDES)
    moyenne = mean(montants.values())
    attendu = sorted((c, r2(m)) for c, m in montants.items() if m > moyenne)
    assert executer(conn, ex.REQUETE_14) == attendu
    assert "with" in ex.REQUETE_14.lower(), "Utilise une CTE (WITH)"


def test_requete_15(conn):
    ca = sorted(ca_par(lambda cmd, prod: mois(cmd)).items())
    attendu, precedent = [], None
    for m, v in ca:
        var = None if precedent is None else round((r2(v) - r2(precedent)) / r2(precedent) * 100 + 1e-9, 1)
        attendu.append((m, r2(v), var))
        precedent = v
    assert executer(conn, ex.REQUETE_15) == attendu
    assert "lag" in ex.REQUETE_15.lower()


# ---------------------------------------------------------------------------
# Partie B
# ---------------------------------------------------------------------------
def test_ajouter_client(conn):
    nouvel_id = ex.ajouter_client(conn, "Iris Le Bihan", "Lorient")
    assert nouvel_id == 9
    ligne = conn.execute("SELECT nom, ville, date_inscription = CURRENT_DATE FROM clients WHERE id = %s", (nouvel_id,)).fetchone()
    assert ligne == ("Iris Le Bihan", "Lorient", True)


def test_ajouter_client_avec_apostrophe(conn):
    nouvel_id = ex.ajouter_client(conn, "Jean d'Ormesson", "Paris")
    assert conn.execute("SELECT nom FROM clients WHERE id = %s", (nouvel_id,)).fetchone()[0] == "Jean d'Ormesson"


def test_clients_par_ville(conn):
    assert ex.clients_par_ville(conn, "Brest") == ["Alice Martin", "Chloé Durand", "Gaëlle Tanguy"]
    assert ex.clients_par_ville(conn, "Tokyo") == []


def test_clients_par_ville_injection_sql(conn):
    assert ex.clients_par_ville(conn, "' OR '1'='1") == [], "Injection SQL réussie : utilise des paramètres !"
    ex.clients_par_ville(conn, "x'; DROP TABLE clients; --")
    assert conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0] == 8


def test_ca_client(conn):
    ca = ca_par(lambda cmd, prod: COMMANDE[cmd][1])
    assert isinstance(ex.ca_client(conn, 1), float)
    assert round(ex.ca_client(conn, 1), 2) == r2(ca[1])
    assert round(ex.ca_client(conn, 3), 2) == r2(ca[3])
    assert ex.ca_client(conn, 7) == 0.0


def test_creer_table_avis(conn):
    ex.creer_table_avis(conn)
    conn.execute("INSERT INTO avis (client_id, produit_id, note) VALUES (1, 1, 5)")
    ligne = conn.execute("SELECT id, commentaire, cree_le IS NOT NULL FROM avis").fetchone()
    assert ligne[1] is None and ligne[2] is True

    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute("INSERT INTO avis (client_id, produit_id, note) VALUES (2, 1, 6)")
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute("INSERT INTO avis (client_id, produit_id, note) VALUES (2, 1, 0)")
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute("INSERT INTO avis (client_id, produit_id, note) VALUES (1, 1, 3)")
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        conn.execute("INSERT INTO avis (client_id, produit_id, note) VALUES (999, 1, 3)")
    with pytest.raises(psycopg.errors.NotNullViolation):
        conn.execute("INSERT INTO avis (client_id, produit_id) VALUES (2, 2)")


def test_avis_suppression_en_cascade(conn):
    ex.creer_table_avis(conn)
    conn.execute("INSERT INTO avis (client_id, produit_id, note) VALUES (8, 2, 4)")
    conn.execute("DELETE FROM clients WHERE id = 8")
    assert conn.execute("SELECT COUNT(*) FROM avis").fetchone()[0] == 0


def test_creer_index(conn):
    ex.creer_index(conn)
    ex.creer_index(conn)  # idempotent
    index = {
        r[0]: r[1]
        for r in conn.execute("SELECT indexname, indexdef FROM pg_indexes WHERE schemaname = 'niveau06'").fetchall()
    }
    assert "idx_commandes_client" in index and "(client_id)" in index["idx_commandes_client"]
    assert "idx_lignes_produit" in index and "(produit_id)" in index["idx_lignes_produit"]


def etat(conn):
    return (
        conn.execute("SELECT COUNT(*) FROM commandes").fetchone()[0],
        conn.execute("SELECT COUNT(*) FROM lignes_commande").fetchone()[0],
        conn.execute("SELECT array_agg(stock ORDER BY id) FROM produits").fetchone()[0],
    )


def test_passer_commande(conn):
    cmd_id = ex.passer_commande(conn, 7, [(2, 3), (9, 10)])
    assert cmd_id == 15
    statut, client = conn.execute("SELECT statut, client_id FROM commandes WHERE id = %s", (cmd_id,)).fetchone()
    assert (statut, client) == ("en_cours", 7)
    lignes = conn.execute(
        "SELECT produit_id, quantite, prix_unitaire FROM lignes_commande WHERE commande_id = %s ORDER BY produit_id",
        (cmd_id,),
    ).fetchall()
    assert [(p, q, float(pu)) for p, q, pu in lignes] == [(2, 3, 29.9), (9, 10, 12.0)]
    stocks = dict(conn.execute("SELECT id, stock FROM produits WHERE id IN (2, 9)").fetchall())
    assert stocks == {2: 97, 9: 190}


def test_passer_commande_stock_insuffisant_rollback(conn):
    avant = etat(conn)
    with pytest.raises(ex.StockInsuffisantError):
        ex.passer_commande(conn, 1, [(2, 1), (8, 1)])  # la webcam (id 8) a un stock de 0
    assert etat(conn) == avant, "Tout ou rien : rien ne doit avoir changé"


def test_passer_commande_produit_inexistant_rollback(conn):
    avant = etat(conn)
    with pytest.raises(ValueError):
        ex.passer_commande(conn, 1, [(1, 1), (999, 1)])
    assert etat(conn) == avant


def test_top_produits(conn):
    ca = ca_par(lambda cmd, prod: prod)
    tous = sorted(((PRODUIT[p][1], r2(v)) for p, v in ca.items()), key=lambda t: -t[1])
    assert [(n, round(v, 2)) for n, v in ex.top_produits(conn)] == tous[:3]
    audio = [t for t in tous if PRODUIT[[p for p in PRODUIT if PRODUIT[p][1] == t[0]][0]][2] == "audio"]
    assert [(n, round(v, 2)) for n, v in ex.top_produits(conn, "audio", 10)] == audio
    assert ex.top_produits(conn, "'; DROP TABLE produits; --") == []
