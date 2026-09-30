"""
NIVEAU 7 — SQLAlchemy 2.0 (ORM) sur PostgreSQL
==============================================

Prérequis :  docker compose up -d
Doc : https://docs.sqlalchemy.org/en/20/orm/quickstart.html

Style SQLAlchemy 2.0 OBLIGATOIRE :
  - modèles avec `Mapped[...]` et `mapped_column(...)`
  - requêtes avec `select(...)` + `session.scalars(...)` / `session.execute(...)`
  - PAS de `session.query(...)` (ancien style 1.x, les tests le vérifient)

Domaine : une bibliothèque.

PARTIE A — Modèles (complète les classes)
-----------------------------------------
Auteur   (table "auteurs")
    id       : int, clé primaire
    nom      : str (100), obligatoire, UNIQUE
    pays     : str (50), optionnel
    livres   : relation vers Livre (back_populates="auteur"),
               supprimer un auteur supprime ses livres (cascade="all, delete-orphan")

Livre    (table "livres")
    id        : int, clé primaire
    titre     : str (200), obligatoire
    annee     : int, obligatoire
    genre     : str (50), obligatoire
    auteur_id : int, clé étrangère -> auteurs.id, obligatoire
    auteur    : relation vers Auteur (back_populates="livres")
    emprunts  : relation vers Emprunt (back_populates="livre")

Membre   (table "membres")
    id       : int, clé primaire
    nom      : str (100), obligatoire
    email    : str (200), obligatoire, UNIQUE
    emprunts : relation vers Emprunt (back_populates="membre")

Emprunt  (table "emprunts")
    id           : int, clé primaire
    livre_id     : FK -> livres.id, obligatoire
    membre_id    : FK -> membres.id, obligatoire
    date_emprunt : date, obligatoire
    date_retour  : date, optionnelle (None = pas encore rendu)
    livre, membre : relations (back_populates="emprunts")

Lance :  pytest niveau_07_sqlalchemy
"""
from datetime import date

import pandas as pd
from sqlalchemy import Engine, ForeignKey, String, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload


class Base(DeclarativeBase):
    pass


class Auteur(Base):
    __tablename__ = "auteurs"
    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO


class Livre(Base):
    __tablename__ = "livres"
    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO


class Membre(Base):
    __tablename__ = "membres"
    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO


class Emprunt(Base):
    __tablename__ = "emprunts"
    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO


class LivreIndisponibleError(Exception):
    """Le livre est déjà emprunté (emprunt sans date_retour)."""


class QuotaDepasseError(Exception):
    """Le membre a déjà 3 emprunts en cours."""


# =============================================================================
# PARTIE B — Fonctions
# =============================================================================
def creer_tables(engine: Engine) -> None:
    """Crée toutes les tables des modèles (metadata.create_all)."""
    raise NotImplementedError


def ajouter_auteur_avec_livres(session: Session, nom: str, pays: str | None, livres: list[tuple[str, int, str]]) -> Auteur:
    """Crée un auteur et ses livres [(titre, annee, genre), ...] en passant par la
    RELATION (auteur.livres), commit, et retourne l'auteur.
    """
    raise NotImplementedError


def titres_par_auteur(session: Session, nom_auteur: str) -> list[str]:
    """Titres des livres d'un auteur, triés par année puis titre. [] si auteur inconnu."""
    raise NotImplementedError


def livres_publies_entre(session: Session, debut: int, fin: int) -> list[Livre]:
    """Objets Livre dont l'année est dans [debut, fin], triés par année puis titre."""
    raise NotImplementedError


def nombre_livres_par_genre(session: Session) -> dict[str, int]:
    """{genre: nombre de livres} avec un GROUP BY (func.count)."""
    raise NotImplementedError


def inscrire_membre(session: Session, nom: str, email: str) -> Membre | None:
    """Crée un membre et commit. Si l'email existe déjà, la base lève une
    IntegrityError : il faut faire un rollback et retourner None.
    La session doit rester utilisable après.
    """
    raise NotImplementedError


def emprunter(session: Session, livre_id: int, membre_id: int, jour: date) -> Emprunt:
    """Enregistre un emprunt et commit.
    - LivreIndisponibleError si le livre a un emprunt en cours (date_retour IS NULL)
    - QuotaDepasseError si le membre a déjà 3 emprunts en cours
    - ValueError si le livre ou le membre n'existe pas (session.get)
    """
    raise NotImplementedError


def rendre(session: Session, livre_id: int, jour: date) -> Emprunt:
    """Clôture l'emprunt en cours du livre (date_retour = jour), commit, le retourne.
    ValueError si le livre n'est pas emprunté.
    """
    raise NotImplementedError


def emprunts_en_retard(session: Session, aujourdhui: date, duree_max_jours: int = 14) -> list[tuple[str, str, int]]:
    """Emprunts EN COURS dont la durée dépasse duree_max_jours.
    Retourne [(nom_membre, titre, jours_de_retard)] où
    jours_de_retard = (aujourdhui - date_emprunt).days - duree_max_jours,
    triés par jours_de_retard décroissant puis nom.
    """
    raise NotImplementedError


def auteurs_populaires(session: Session, n: int) -> list[tuple[str, int]]:
    """Les n auteurs les plus empruntés (tous emprunts, rendus ou non) :
    [(nom_auteur, nb_emprunts)] triés par nb décroissant puis nom.
    Les auteurs jamais empruntés n'apparaissent pas.
    """
    raise NotImplementedError


def membres_sans_emprunt(session: Session) -> list[str]:
    """Noms (triés) des membres n'ayant jamais emprunté (indice : ~Membre.emprunts.any())."""
    raise NotImplementedError


def auteurs_avec_livres(session: Session) -> list[Auteur]:
    """Tous les auteurs triés par nom, avec leurs livres PRÉCHARGÉS.
    Le test compte les requêtes SQL : accéder à `a.livres` pour chaque auteur
    ne doit PAS déclencher une requête par auteur (problème N+1).
    Indice : .options(selectinload(...))
    """
    raise NotImplementedError


def supprimer_auteur(session: Session, auteur_id: int) -> bool:
    """Supprime l'auteur (et ses livres grâce à la cascade), commit.
    Retourne False si l'auteur n'existe pas.
    """
    raise NotImplementedError


def statistiques_par_genre(engine: Engine) -> pd.DataFrame:
    """Pont SQLAlchemy -> pandas : DataFrame avec les colonnes
    ["genre", "nb_livres", "nb_emprunts"], une ligne par genre, triée par genre.
    nb_emprunts compte tous les emprunts des livres du genre (0 si aucun).
    Construis la requête avec select() puis pd.read_sql(requete, engine).
    Attention au piège du double comptage avec les jointures : count(distinct ...).
    """
    raise NotImplementedError
