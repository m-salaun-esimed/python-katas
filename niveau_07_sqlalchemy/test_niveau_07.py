import ast
import inspect
from datetime import date

import pandas as pd
import pytest
from sqlalchemy import create_engine, event, inspect as sa_inspect, text
from sqlalchemy.orm import Session

from niveau_07_sqlalchemy import exercices as ex

LIVRES = {
    ("Victor Hugo", "France"): [
        ("Les Misérables", 1862, "roman"),
        ("Notre-Dame de Paris", 1831, "roman"),
        ("Les Contemplations", 1856, "poesie"),
    ],
    ("Albert Camus", "France"): [
        ("L'Étranger", 1942, "roman"),
        ("La Peste", 1947, "roman"),
        ("L'Homme révolté", 1951, "essai"),
    ],
    ("Agatha Christie", "Royaume-Uni"): [
        ("Le Crime de l'Orient-Express", 1934, "policier"),
        ("Mort sur le Nil", 1937, "policier"),
    ],
    ("Isaac Asimov", "États-Unis"): [
        ("Fondation", 1951, "science-fiction"),
        ("Les Robots", 1950, "science-fiction"),
    ],
    ("Anne Hébert", None): [("Kamouraska", 1970, "roman")],
}

MEMBRES = [("Léa", "lea@biblio.fr"), ("Marc", "marc@biblio.fr"), ("Nora", "nora@biblio.fr"), ("Omar", "omar@biblio.fr")]

EMPRUNTS = [  # (membre, titre, emprunt, retour)
    ("Léa", "Les Misérables", date(2024, 1, 2), date(2024, 1, 20)),
    ("Léa", "Fondation", date(2024, 3, 1), None),
    ("Marc", "La Peste", date(2024, 2, 10), None),
    ("Marc", "Les Misérables", date(2024, 2, 1), date(2024, 2, 5)),
    ("Nora", "Mort sur le Nil", date(2024, 3, 10), None),
    ("Nora", "L'Étranger", date(2024, 1, 5), date(2024, 1, 10)),
    ("Léa", "Notre-Dame de Paris", date(2024, 3, 5), None),
]


@pytest.fixture
def engine(pg_url):
    url = pg_url.replace("postgresql://", "postgresql+psycopg://")
    with create_engine(url).begin() as c:
        c.execute(text("DROP SCHEMA IF EXISTS niveau07 CASCADE"))
        c.execute(text("CREATE SCHEMA niveau07"))
    moteur = create_engine(url, connect_args={"options": "-c search_path=niveau07"})
    ex.creer_tables(moteur)
    yield moteur
    moteur.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        auteurs = {}
        for (nom, pays), livres in LIVRES.items():
            a = ex.Auteur(nom=nom, pays=pays)
            a.livres = [ex.Livre(titre=t, annee=an, genre=g) for t, an, g in livres]
            s.add(a)
            auteurs[nom] = a
        membres = {n: ex.Membre(nom=n, email=e) for n, e in MEMBRES}
        s.add_all(membres.values())
        livres = {l.titre: l for a in auteurs.values() for l in a.livres}
        for m, t, d1, d2 in EMPRUNTS:
            s.add(ex.Emprunt(membre=membres[m], livre=livres[t], date_emprunt=d1, date_retour=d2))
        s.commit()
        yield s


def id_livre(session, titre):
    return session.execute(text("SELECT id FROM livres WHERE titre = :t"), {"t": titre}).scalar_one()


def id_membre(session, nom):
    return session.execute(text("SELECT id FROM membres WHERE nom = :n"), {"n": nom}).scalar_one()


# ---------------------------------------------------------------------------
# Partie A — modèles
# ---------------------------------------------------------------------------
def test_style_sqlalchemy_2():
    arbre = ast.parse(inspect.getsource(ex))
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Attribute):
            assert noeud.func.attr != "query", "session.query() est l'ancien style : utilise select()"


def test_tables_et_colonnes(engine):
    insp = sa_inspect(engine)
    assert set(insp.get_table_names()) >= {"auteurs", "livres", "membres", "emprunts"}
    attendu = {
        "auteurs": {"id": False, "nom": False, "pays": True},
        "livres": {"id": False, "titre": False, "annee": False, "genre": False, "auteur_id": False},
        "membres": {"id": False, "nom": False, "email": False},
        "emprunts": {"id": False, "livre_id": False, "membre_id": False, "date_emprunt": False, "date_retour": True},
    }
    for table, cols in attendu.items():
        reelles = {c["name"]: c["nullable"] for c in insp.get_columns(table)}
        assert reelles == cols, f"Table {table} : colonnes/nullable incorrectes"


def test_cles_etrangeres(engine):
    insp = sa_inspect(engine)
    fk = lambda t: {(f["constrained_columns"][0], f["referred_table"]) for f in insp.get_foreign_keys(t)}
    assert fk("livres") == {("auteur_id", "auteurs")}
    assert fk("emprunts") == {("livre_id", "livres"), ("membre_id", "membres")}


def test_contraintes_unique(engine):
    insp = sa_inspect(engine)

    def uniques(t):
        cols = {tuple(u["column_names"]) for u in insp.get_unique_constraints(t)}
        cols |= {tuple(i["column_names"]) for i in insp.get_indexes(t) if i["unique"]}
        return cols

    assert ("nom",) in uniques("auteurs")
    assert ("email",) in uniques("membres")


def test_relations(session):
    hugo = session.scalars(ex.select(ex.Auteur).where(ex.Auteur.nom == "Victor Hugo")).one()
    assert len(hugo.livres) == 3
    assert hugo.livres[0].auteur is hugo
    lea = session.scalars(ex.select(ex.Membre).where(ex.Membre.nom == "Léa")).one()
    assert {e.livre.titre for e in lea.emprunts} == {"Les Misérables", "Fondation", "Notre-Dame de Paris"}


# ---------------------------------------------------------------------------
# Partie B
# ---------------------------------------------------------------------------
def test_ajouter_auteur_avec_livres(session):
    a = ex.ajouter_auteur_avec_livres(session, "Jules Verne", "France", [("Vingt mille lieues sous les mers", 1870, "aventure"), ("Le Tour du monde en 80 jours", 1872, "aventure")])
    assert a.id is not None
    assert session.execute(text("SELECT COUNT(*) FROM livres WHERE auteur_id = :i"), {"i": a.id}).scalar() == 2


def test_titres_par_auteur(session):
    assert ex.titres_par_auteur(session, "Victor Hugo") == ["Notre-Dame de Paris", "Les Contemplations", "Les Misérables"]
    assert ex.titres_par_auteur(session, "Albert Camus") == ["L'Étranger", "La Peste", "L'Homme révolté"]
    assert ex.titres_par_auteur(session, "Inconnu") == []


def test_livres_publies_entre(session):
    livres = ex.livres_publies_entre(session, 1934, 1947)
    assert all(isinstance(l, ex.Livre) for l in livres)
    assert [l.titre for l in livres] == ["Le Crime de l'Orient-Express", "Mort sur le Nil", "L'Étranger", "La Peste"]


def test_nombre_livres_par_genre(session):
    assert ex.nombre_livres_par_genre(session) == {"roman": 5, "poesie": 1, "essai": 1, "policier": 2, "science-fiction": 2}


def test_inscrire_membre(session):
    m = ex.inscrire_membre(session, "Paul", "paul@biblio.fr")
    assert m is not None and m.id is not None
    assert ex.inscrire_membre(session, "Faux Léa", "lea@biblio.fr") is None
    # la session doit rester utilisable
    assert ex.inscrire_membre(session, "Quentin", "quentin@biblio.fr") is not None
    assert session.execute(text("SELECT COUNT(*) FROM membres")).scalar() == 6


def test_emprunter(session):
    e = ex.emprunter(session, id_livre(session, "Kamouraska"), id_membre(session, "Omar"), date(2024, 4, 1))
    assert e.id is not None and e.date_retour is None
    assert e.livre.titre == "Kamouraska"


def test_emprunter_livre_indisponible(session):
    with pytest.raises(ex.LivreIndisponibleError):
        ex.emprunter(session, id_livre(session, "La Peste"), id_membre(session, "Omar"), date(2024, 4, 1))


def test_emprunter_livre_rendu_est_disponible(session):
    ex.emprunter(session, id_livre(session, "Les Misérables"), id_membre(session, "Omar"), date(2024, 4, 1))


def test_emprunter_quota(session):
    lea = id_membre(session, "Léa")
    ex.emprunter(session, id_livre(session, "Kamouraska"), lea, date(2024, 4, 1))  # 3e emprunt : ok
    with pytest.raises(ex.QuotaDepasseError):
        ex.emprunter(session, id_livre(session, "Les Robots"), lea, date(2024, 4, 1))


def test_emprunter_inexistant(session):
    with pytest.raises(ValueError):
        ex.emprunter(session, 9999, id_membre(session, "Omar"), date(2024, 4, 1))
    with pytest.raises(ValueError):
        ex.emprunter(session, id_livre(session, "Kamouraska"), 9999, date(2024, 4, 1))


def test_rendre(session):
    e = ex.rendre(session, id_livre(session, "La Peste"), date(2024, 3, 15))
    assert e.date_retour == date(2024, 3, 15)
    ex.emprunter(session, id_livre(session, "La Peste"), id_membre(session, "Omar"), date(2024, 3, 16))
    with pytest.raises(ValueError):
        ex.rendre(session, id_livre(session, "Kamouraska"), date(2024, 3, 15))


def test_emprunts_en_retard(session):
    assert ex.emprunts_en_retard(session, date(2024, 3, 20)) == [
        ("Marc", "La Peste", 25),
        ("Léa", "Fondation", 5),
        ("Léa", "Notre-Dame de Paris", 1),
    ]
    assert ex.emprunts_en_retard(session, date(2024, 3, 20), duree_max_jours=60) == []


def test_auteurs_populaires(session):
    assert ex.auteurs_populaires(session, 3) == [("Victor Hugo", 3), ("Albert Camus", 2), ("Agatha Christie", 1)]
    assert len(ex.auteurs_populaires(session, 10)) == 4


def test_membres_sans_emprunt(session):
    assert ex.membres_sans_emprunt(session) == ["Omar"]


def test_auteurs_avec_livres_pas_de_n_plus_1(engine, session):
    session.expunge_all()
    requetes = []
    ecouteur = lambda *args: requetes.append(args[2])
    event.listen(engine, "before_cursor_execute", ecouteur)
    try:
        auteurs = ex.auteurs_avec_livres(session)
        titres = {a.nom: sorted(l.titre for l in a.livres) for a in auteurs}
    finally:
        event.remove(engine, "before_cursor_execute", ecouteur)
    assert [a.nom for a in auteurs] == sorted(n for n, _ in LIVRES)
    assert titres["Isaac Asimov"] == ["Fondation", "Les Robots"]
    assert len(requetes) <= 2, f"{len(requetes)} requêtes SQL : problème N+1 !"


def test_supprimer_auteur_cascade(session):
    hebert = session.execute(text("SELECT id FROM auteurs WHERE nom = 'Anne Hébert'")).scalar_one()
    assert ex.supprimer_auteur(session, hebert) is True
    assert session.execute(text("SELECT COUNT(*) FROM livres WHERE titre = 'Kamouraska'")).scalar() == 0
    assert ex.supprimer_auteur(session, 9999) is False


def test_statistiques_par_genre(engine, session):
    df = ex.statistiques_par_genre(engine)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["genre", "nb_livres", "nb_emprunts"]
    attendu = pd.DataFrame(
        {
            "genre": ["essai", "poesie", "policier", "roman", "science-fiction"],
            "nb_livres": [1, 1, 2, 5, 2],
            "nb_emprunts": [0, 0, 1, 5, 1],
        }
    )
    pd.testing.assert_frame_equal(df.reset_index(drop=True).astype({"nb_livres": int, "nb_emprunts": int}), attendu)
