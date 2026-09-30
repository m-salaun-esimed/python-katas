"""
NIVEAU 6 — SQL avec PostgreSQL
==============================

Prérequis :  docker compose up -d     (PostgreSQL sur localhost:5440, user/mdp : exo/exo)

Le schéma et les données sont dans `niveau_06_sql/donnees.py` (lis-le d'abord !).
Pour explorer à la main :
    docker exec -it exos_postgres psql -U exo -d exercices
    exercices=# SET search_path TO niveau06;      -- après un premier lancement des tests
    exercices=# \\dt

PARTIE A : écris les requêtes dans les constantes REQUETE_XX.
           Respecte EXACTEMENT les colonnes et l'ordre demandés (ORDER BY !).
PARTIE B : fonctions Python avec psycopg (requêtes paramétrées, transactions, DDL).

Définitions utilisées partout :
  - montant d'une ligne     = quantite * prix_unitaire
  - montant d'une commande  = somme de ses lignes
  - CA (chiffre d'affaires) = somme des montants, EN EXCLUANT les commandes 'annulee'
  - mois                    = texte 'YYYY-MM'  (indice : to_char(date, 'YYYY-MM'))

Lance :  pytest niveau_06_sql
"""

# =============================================================================
# PARTIE A — Requêtes
# =============================================================================

# 1. Les clients habitant à Brest.  Colonnes : id, nom.  Tri : nom.
REQUETE_01 = """
-- TODO
"""

# 2. Produits dont le prix est > 50.  Colonnes : nom, prix.  Tri : prix décroissant.
REQUETE_02 = """
-- TODO
"""

# 3. Nombre de commandes par statut.  Colonnes : statut, nb.  Tri : statut.
REQUETE_03 = """
-- TODO
"""

# 4. Nombre de commandes (tous statuts) par client, clients SANS commande inclus (0).
#    Colonnes : nom, nb_commandes.  Tri : nb_commandes décroissant, puis nom.
REQUETE_04 = """
-- TODO
"""

# 5. CA par produit (seulement les produits vendus).
#    Colonnes : nom, ca.  Tri : ca décroissant, puis nom.
REQUETE_05 = """
-- TODO
"""

# 6. Top 3 des clients par CA.  Colonnes : nom, ca.  Tri : ca décroissant.
REQUETE_06 = """
-- TODO
"""

# 7. Produits qui n'ont JAMAIS été commandés (tous statuts confondus).
#    Colonnes : nom.  Tri : nom.
REQUETE_07 = """
-- TODO
"""

# 8. CA par mois.  Colonnes : mois, ca.  Tri : mois.
REQUETE_08 = """
-- TODO
"""

# 9. Clients ayant au moins 2 commandes 'livree'.  Colonnes : nom, nb.  Tri : nom.
REQUETE_09 = """
-- TODO
"""

# 10. Panier moyen par ville du client : moyenne des montants de commande
#     (commandes non annulées), arrondi à 2 décimales.
#     Colonnes : ville, panier_moyen.  Tri : ville.
#     Piège : il faut d'abord calculer le montant PAR COMMANDE, puis faire la moyenne.
REQUETE_10 = """
-- TODO
"""

# 11. Classement des produits vendus au sein de leur catégorie selon leur CA
#     (fonction de fenêtre RANK()).
#     Colonnes : categorie, nom, ca, rang.  Tri : categorie, rang, nom.
REQUETE_11 = """
-- TODO
"""

# 12. CA par mois et CA cumulé depuis le début (SUM(...) OVER (ORDER BY ...)).
#     Colonnes : mois, ca, ca_cumule.  Tri : mois.
REQUETE_12 = """
-- TODO
"""

# 13. Pour chaque client ayant commandé (tous statuts) : date de la première
#     et de la dernière commande, et le nombre de jours entre les deux.
#     Colonnes : nom, premiere, derniere, jours.  Tri : nom.
REQUETE_13 = """
-- TODO
"""

# 14. Commandes (non annulées) dont le montant est STRICTEMENT supérieur au montant moyen
#     des commandes non annulées. Utilise une CTE (WITH ...).
#     Colonnes : commande_id, montant.  Tri : commande_id.
REQUETE_14 = """
-- TODO
"""

# 15. Variation du CA d'un mois sur l'autre en %, arrondie à 1 décimale (LAG()).
#     variation_pct = (ca - ca_mois_precedent) / ca_mois_precedent * 100 ; NULL pour le 1er mois.
#     Colonnes : mois, ca, variation_pct.  Tri : mois.
REQUETE_15 = """
-- TODO
"""


# =============================================================================
# PARTIE B — Python + psycopg
# `conn` est une connexion psycopg 3 (autocommit activé, search_path déjà positionné).
# Pour une transaction :  with conn.transaction(): ...
# =============================================================================


def ajouter_client(conn, nom: str, ville: str) -> int:
    """Insère un client (date_inscription = aujourd'hui, CURRENT_DATE) et retourne son id.
    Utilise une requête PARAMÉTRÉE (%s) et RETURNING id.
    """
    raise NotImplementedError


def clients_par_ville(conn, ville: str) -> list[str]:
    """Noms des clients d'une ville, triés.
    ⚠️ Le test essaie une injection SQL : jamais de f-string dans une requête !
    """
    raise NotImplementedError


def ca_client(conn, client_id: int) -> float:
    """CA d'un client (float). 0.0 s'il n'a rien acheté (indice : COALESCE)."""
    raise NotImplementedError


def creer_table_avis(conn) -> None:
    """Crée la table `avis` :
      - id           : clé primaire auto-incrémentée
      - client_id    : obligatoire, clé étrangère vers clients, ON DELETE CASCADE
      - produit_id   : obligatoire, clé étrangère vers produits
      - note         : entier obligatoire entre 1 et 5 (CHECK)
      - commentaire  : texte optionnel
      - cree_le      : TIMESTAMPTZ, par défaut now()
      - un client ne peut donner qu'UN avis par produit (UNIQUE)
    """
    raise NotImplementedError


def creer_index(conn) -> None:
    """Crée deux index :
      - idx_commandes_client sur commandes(client_id)
      - idx_lignes_produit   sur lignes_commande(produit_id)
    Doit pouvoir être appelée deux fois sans erreur (IF NOT EXISTS).
    """
    raise NotImplementedError


class StockInsuffisantError(Exception):
    pass


def passer_commande(conn, client_id: int, lignes: list[tuple[int, int]]) -> int:
    """Crée une commande 'en_cours' datée d'aujourd'hui pour `client_id`
    avec les `lignes` [(produit_id, quantite), ...] et retourne l'id de la commande.

    - prix_unitaire = prix catalogue actuel du produit
    - le stock de chaque produit est décrémenté
    - produit inexistant -> ValueError
    - stock insuffisant  -> StockInsuffisantError
    - TOUT OU RIEN : en cas d'erreur, aucune commande, aucune ligne et aucun
      stock ne doit avoir été modifié (transaction).
    Bonus : verrouille les lignes produits lues (SELECT ... FOR UPDATE).
    """
    raise NotImplementedError


def top_produits(conn, categorie: str | None = None, limite: int = 3) -> list[tuple[str, float]]:
    """Les `limite` produits au plus gros CA [(nom, ca), ...] (ca en float, tri ca décroissant),
    éventuellement filtrés sur une catégorie. Requête paramétrée (même pour LIMIT).
    """
    raise NotImplementedError
