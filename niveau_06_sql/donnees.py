"""Jeu de données e-commerce du niveau 6 (ne pas modifier).

Tables :
  clients(id, nom, ville, date_inscription)
  produits(id, nom, categorie, prix, stock)
  commandes(id, client_id, date_commande, statut)   statut ∈ {'livree', 'en_cours', 'annulee'}
  lignes_commande(commande_id, produit_id, quantite, prix_unitaire)

Montant d'une ligne = quantite * prix_unitaire (le prix payé peut différer du prix catalogue : promos).
"""
from datetime import date

CLIENTS = [
    (1, "Alice Martin", "Brest", date(2024, 1, 10)),
    (2, "Bruno Le Gall", "Rennes", date(2024, 2, 1)),
    (3, "Chloé Durand", "Brest", date(2024, 2, 15)),
    (4, "David Morel", "Paris", date(2024, 3, 1)),
    (5, "Emma Kerouac", "Quimper", date(2024, 3, 20)),
    (6, "Farid Benali", "Paris", date(2024, 4, 5)),
    (7, "Gaëlle Tanguy", "Brest", date(2024, 5, 12)),
    (8, "Hugo Petit", "Rennes", date(2024, 6, 1)),
]

PRODUITS = [
    (1, "Clavier mécanique", "informatique", 89.90, 50),
    (2, "Souris sans fil", "informatique", 29.90, 100),
    (3, "Écran 27 pouces", "informatique", 249.00, 20),
    (4, "Casque audio", "audio", 119.00, 30),
    (5, "Enceinte bluetooth", "audio", 59.90, 40),
    (6, "Cafetière", "maison", 45.00, 25),
    (7, "Lampe de bureau", "maison", 34.50, 60),
    (8, "Webcam HD", "informatique", 69.00, 0),
    (9, "Tapis de souris", "informatique", 12.00, 200),
    (10, "Bouilloire", "maison", 39.90, 15),
]

COMMANDES = [
    (1, 1, date(2024, 1, 15), "livree"),
    (2, 1, date(2024, 2, 20), "livree"),
    (3, 2, date(2024, 2, 22), "livree"),
    (4, 3, date(2024, 3, 5), "annulee"),
    (5, 3, date(2024, 3, 18), "livree"),
    (6, 4, date(2024, 3, 25), "livree"),
    (7, 1, date(2024, 4, 2), "livree"),
    (8, 5, date(2024, 4, 10), "en_cours"),
    (9, 6, date(2024, 4, 28), "livree"),
    (10, 2, date(2024, 5, 3), "annulee"),
    (11, 4, date(2024, 5, 15), "livree"),
    (12, 6, date(2024, 5, 30), "en_cours"),
    (13, 3, date(2024, 6, 2), "livree"),
    (14, 1, date(2024, 6, 18), "en_cours"),
]

LIGNES = [
    (1, 1, 1, 89.90), (1, 2, 1, 29.90), (1, 9, 2, 12.00),
    (2, 3, 1, 249.00),
    (3, 4, 1, 119.00), (3, 2, 2, 29.90),
    (4, 3, 2, 249.00),
    (5, 5, 1, 59.90), (5, 7, 2, 34.50),
    (6, 1, 1, 79.90), (6, 3, 1, 249.00),
    (7, 6, 1, 45.00),
    (8, 4, 1, 119.00), (8, 5, 1, 59.90),
    (9, 2, 3, 29.90), (9, 9, 3, 12.00),
    (10, 1, 1, 89.90),
    (11, 7, 1, 34.50), (11, 6, 1, 45.00), (11, 2, 1, 29.90),
    (12, 3, 1, 239.00),
    (13, 4, 2, 109.00),
    (14, 5, 2, 59.90),
]

SCHEMA_SQL = """
CREATE TABLE clients (
    id               SERIAL PRIMARY KEY,
    nom              TEXT NOT NULL,
    ville            TEXT NOT NULL,
    date_inscription DATE NOT NULL
);
CREATE TABLE produits (
    id        SERIAL PRIMARY KEY,
    nom       TEXT NOT NULL,
    categorie TEXT NOT NULL,
    prix      NUMERIC(10, 2) NOT NULL,
    stock     INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE commandes (
    id            SERIAL PRIMARY KEY,
    client_id     INTEGER NOT NULL REFERENCES clients(id),
    date_commande DATE NOT NULL,
    statut        TEXT NOT NULL CHECK (statut IN ('livree', 'en_cours', 'annulee'))
);
CREATE TABLE lignes_commande (
    commande_id   INTEGER NOT NULL REFERENCES commandes(id),
    produit_id    INTEGER NOT NULL REFERENCES produits(id),
    quantite      INTEGER NOT NULL CHECK (quantite > 0),
    prix_unitaire NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (commande_id, produit_id)
);
"""


def charger(conn, schema: str = "niveau06") -> None:
    """(Re)crée le schéma et insère les données. `conn` : connexion psycopg."""
    with conn.transaction():
        conn.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
        conn.execute(f"CREATE SCHEMA {schema}")
        conn.execute(f"SET search_path TO {schema}")
        conn.execute(SCHEMA_SQL)
        with conn.cursor() as cur:
            cur.executemany("INSERT INTO clients VALUES (%s, %s, %s, %s)", CLIENTS)
            cur.executemany("INSERT INTO produits VALUES (%s, %s, %s, %s, %s)", PRODUITS)
            cur.executemany("INSERT INTO commandes VALUES (%s, %s, %s, %s)", COMMANDES)
            cur.executemany("INSERT INTO lignes_commande VALUES (%s, %s, %s, %s)", LIGNES)
        # remet les séquences SERIAL après les id insérés à la main
        for table in ("clients", "produits", "commandes"):
            conn.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), (SELECT MAX(id) FROM {table}))")
