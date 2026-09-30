"""
NIVEAU 8 — pandas : les fondamentaux
====================================

Jeu de données : voir `jeu_de_donnees.py` (generer_ventes()).
Colonnes : date, client, ville, region, categorie, produit, quantite, prix_unitaire

Règles d'or (vérifiées par les tests) :
  - NE MODIFIE JAMAIS le DataFrame reçu en entrée : travaille sur une copie
    (df = df.copy()  ou  df.assign(...)).
  - PAS de boucle `for` sur les lignes, PAS de `iterrows()` / `itertuples()`,
    PAS de `.apply(..., axis=1)` : on vectorise !

Doc : https://pandas.pydata.org/docs/user_guide/10min.html
Lance :  pytest niveau_08_pandas_bases
"""
import numpy as np
import pandas as pd


def charger_ventes(chemin: str) -> pd.DataFrame:
    """Lit un CSV "à la française" : séparateur `;`, décimale `,`,
    dates au format JJ/MM/AAAA dans la colonne `date`.
    Résultat attendu : `date` en datetime64, `quantite` en int64, `prix_unitaire` en float64.
    """
    raise NotImplementedError


def apercu(df: pd.DataFrame) -> dict:
    """Retourne {"lignes": int, "colonnes": int, "colonnes_numeriques": [noms dans l'ordre du df]}.
    Indice : df.shape, df.select_dtypes.
    """
    raise NotImplementedError


def ajouter_montant(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne une copie avec une colonne `montant` = quantite * prix_unitaire (arrondi à 2)."""
    raise NotImplementedError


def filtrer(df: pd.DataFrame, region: str, montant_min: float) -> pd.DataFrame:
    """Lignes de la `region` dont le montant (quantite * prix_unitaire) est >= montant_min.
    Retourne les colonnes d'origine uniquement, index réinitialisé (reset_index(drop=True)).
    """
    raise NotImplementedError


def valeurs_manquantes(df: pd.DataFrame) -> pd.Series:
    """Nombre de valeurs manquantes par colonne, UNIQUEMENT pour les colonnes
    qui en ont, trié par nombre décroissant (puis nom de colonne)."""
    raise NotImplementedError


def nettoyer(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage, dans cet ordre :
    1. supprime les lignes dupliquées (strictement identiques)
    2. supprime les lignes sans client
    3. `ville` : espaces retirés + Casse Titre ("  BREST " -> "Brest")
    4. `quantite` manquante -> 0, puis type int64
    5. `prix_unitaire` manquant -> médiane du prix_unitaire du MÊME produit
       (calculée sur les données après l'étape 2)   indice : groupby().transform("median")
    6. index réinitialisé
    """
    raise NotImplementedError


def ca_par_region(df: pd.DataFrame) -> pd.Series:
    """CA (somme de quantite * prix_unitaire) par région, trié décroissant.
    Series indexée par `region`, nommée "ca".
    """
    raise NotImplementedError


def stats_par_categorie(df: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par catégorie (index = categorie), trié par ca_total décroissant, colonnes :
      ca_total      : somme des montants
      panier_moyen  : moyenne des montants, arrondie à 2
      nb_ventes     : nombre de lignes
      vente_max     : montant max
    Indice : agrégation nommée  .agg(ca_total=("montant", "sum"), ...)
    """
    raise NotImplementedError


def top_n_produits(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Les n produits au plus gros CA : DataFrame colonnes ["produit", "ca"],
    trié par ca décroissant, index 0..n-1."""
    raise NotImplementedError


def part_par_region(df: pd.DataFrame) -> pd.Series:
    """Part (en %) de chaque région dans le CA total, arrondie à 1 décimale,
    triée décroissante, indexée par region."""
    raise NotImplementedError


def comparer_objectifs(df: pd.DataFrame, objectifs: pd.DataFrame) -> pd.DataFrame:
    """`objectifs` : colonnes [region, objectif].
    Retourne une ligne PAR RÉGION DES OBJECTIFS (même si elle n'a aucune vente -> ca = 0),
    colonnes [region, ca, objectif, ecart, atteint] où ecart = ca - objectif (arrondi 2)
    et atteint = ca >= objectif. Trié par region.   Indice : merge(how="left") + fillna.
    """
    raise NotImplementedError


def tableau_croise(df: pd.DataFrame) -> pd.DataFrame:
    """Tableau croisé du CA : index = region, colonnes = categorie, 0 si pas de vente,
    valeurs arrondies à 2. Indice : pivot_table(..., aggfunc="sum", fill_value=0)."""
    raise NotImplementedError


def ajouter_tranche(df: pd.DataFrame) -> pd.DataFrame:
    """Copie avec une colonne `tranche` selon le montant (quantite * prix_unitaire) :
      [0, 50[ -> "petit" ; [50, 200[ -> "moyen" ; >= 200 -> "gros"
    Indice : pd.cut(..., right=False, labels=[...]).  La colonne doit être de type category.
    """
    raise NotImplementedError


JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def ca_par_jour_semaine(df: pd.DataFrame) -> pd.Series:
    """CA par jour de la semaine, index = JOURS (dans cet ordre, TOUS présents, 0 si aucun).
    Indice : .dt.dayofweek (0 = lundi) puis reindex."""
    raise NotImplementedError


def clients_fideles(df: pd.DataFrame, min_jours: int) -> list[str]:
    """Clients ayant acheté sur au moins `min_jours` dates DIFFÉRENTES, triés."""
    raise NotImplementedError


def remise_fidelite(df: pd.DataFrame) -> pd.DataFrame:
    """Copie avec une colonne `montant_final` : montant avec 10 % de remise si la
    quantité est >= 4, 5 % si >= 2, sinon aucune remise. Arrondi à 2.
    Vectorisé : np.select ou np.where (pas de apply !).
    """
    raise NotImplementedError
