"""
NIVEAU 11 — PySpark : les bases de l'API DataFrame
==================================================

Spark tourne en local (local[4]) : la fixture `spark` est dans conftest.py.
Prérequis : Java 17+ installé.

Règles :
  - utilise les fonctions natives de pyspark.sql.functions (F.col, F.when, F.sum...)
  - PAS de UDF Python (@udf) : elles sont lentes (sérialisation Python <-> JVM),
    les tests inspectent le plan d'exécution
  - PAS de .collect() / .toPandas() dans tes fonctions : on reste distribué,
    tu retournes un DataFrame Spark
  - ne crée pas de colonne (F.col(...)) au niveau du module : il faut une
    SparkSession active, mets-la dans une fonction

Doc : https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/index.html
Lance :  pytest niveau_11_spark_bases
"""
from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T


def schema_ventes() -> T.StructType:
    """Schéma EXPLICITE (ne jamais compter sur l'inférence en prod) :
      id            : entier, non nullable
      date          : date
      client        : chaîne
      region        : chaîne
      produit       : chaîne
      quantite      : entier
      prix_unitaire : double
    """
    raise NotImplementedError


def creer_dataframe(spark: SparkSession, lignes: list[tuple]) -> DataFrame:
    """DataFrame à partir de tuples, avec schema_ventes()."""
    raise NotImplementedError


def ajouter_colonnes(df: DataFrame) -> DataFrame:
    """Ajoute :
      montant : quantite * prix_unitaire, arrondi à 2
      mois    : "yyyy-MM" (F.date_format)
      taille  : "gros" si montant >= 200, "moyen" si >= 50, sinon "petit" (F.when)
    """
    raise NotImplementedError


def filtrer(df: DataFrame, region: str, montant_min: float) -> DataFrame:
    """Lignes de la région dont quantite * prix_unitaire >= montant_min."""
    raise NotImplementedError


def ca_par_region(df: DataFrame) -> DataFrame:
    """[region, ca, nb_ventes] : ca arrondi à 2, nb_ventes = nombre de lignes,
    trié par ca décroissant."""
    raise NotImplementedError


def top_n_par_region(df: DataFrame, n: int) -> DataFrame:
    """Les n produits au plus gros CA de chaque région : [region, produit, ca, rang]
    avec rang = F.row_number() sur une Window partitionnée par région (ca décroissant,
    puis produit croissant pour départager). Trié par region, rang.
    """
    raise NotImplementedError


def pivot_region_mois(df: DataFrame) -> DataFrame:
    """Une ligne par région, une colonne par mois "yyyy-MM" (triées), valeur = CA arrondi 2,
    0 si pas de vente. Trié par region.   Indice : groupBy().pivot().agg() puis fillna(0)."""
    raise NotImplementedError


def nettoyer(df: DataFrame) -> DataFrame:
    """- supprime les doublons sur `id` (dropDuplicates)
    - supprime les lignes sans client
    - region : espaces retirés + initiales en majuscule (F.trim, F.initcap)
    - quantite manquante -> 0
    """
    raise NotImplementedError


def joindre_clients(ventes: DataFrame, clients: DataFrame) -> DataFrame:
    """`clients` : [client, segment]. Jointure GAUCHE : toutes les ventes sont gardées ;
    segment = "inconnu" si le client n'est pas dans le référentiel."""
    raise NotImplementedError


def requete_sql(spark: SparkSession, df: DataFrame, seuil: float) -> DataFrame:
    """Enregistre df comme vue temporaire "ventes" puis, EN SQL (spark.sql),
    retourne [produit, ca] pour les produits dont le CA (arrondi 2) est > seuil, trié par ca décroissant.
    """
    raise NotImplementedError


def compter_tags(df: DataFrame) -> DataFrame:
    """`df` a une colonne `tags` "a,b,c". Retourne [tag, nb] (tags en minuscules, sans espaces),
    trié par nb décroissant puis tag.  Indice : F.split + F.explode."""
    raise NotImplementedError


def extraire_domaine(df: DataFrame) -> DataFrame:
    """`df` a une colonne `email` sale ("  Alice@Gmail.COM "). Ajoute :
      email_propre : minuscules, sans espaces autour
      domaine      : la partie après @ (F.regexp_extract ou F.split)
    SANS UDF."""
    raise NotImplementedError


def cumul_et_ecart(df: DataFrame) -> DataFrame:
    """Pour chaque client (ordre chronologique par date puis id) ajoute :
      ca_cumule    : somme cumulée de quantite * prix_unitaire, arrondie à 2
                     (Window.partitionBy(...).orderBy(...).rowsBetween(Window.unboundedPreceding, Window.currentRow))
      jours_depuis : jours depuis l'achat précédent du client (F.lag + F.datediff), null au 1er achat
    """
    raise NotImplementedError


def ecrire_et_relire(spark: SparkSession, df: DataFrame, chemin: str) -> DataFrame:
    """Écrit df en Parquet partitionné par region (mode "overwrite"), puis relit et retourne le résultat."""
    raise NotImplementedError
