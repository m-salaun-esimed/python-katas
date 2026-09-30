# 🐍 pythonNaval — parcours d'exercices Python → Data Engineering

12 niveaux progressifs, **434 tests unitaires** à faire passer.
Tu complètes `exercices.py` de chaque niveau ; les tests te disent si c'est bon.

| # | Niveau | Thèmes | Tests | Infra |
|---|--------|--------|------:|-------|
| 1 | `niveau_01_bases` | boucles, conditions, chaînes, exceptions | 76 | – |
| 2 | `niveau_02_structures` | listes, dicts, sets, compréhensions, `Counter`, récursivité | 26 | – |
| 3 | `niveau_03_fonctions_poo` | classes, `@property`, méthodes spéciales, `@dataclass`, générateurs, décorateurs, context managers, LRU | 35 | – |
| 4 | `niveau_04_algo` | recherche binaire, tris (bulles → quicksort), complexité, piles, hachage, Kadane | 101 | – |
| 5 | `niveau_05_algo_avance` | programmation dynamique, BFS/DFS, Dijkstra, tri topologique, backtracking, tas, deque | 47 | – |
| 6 | `niveau_06_sql` | **PostgreSQL** : jointures, GROUP BY/HAVING, CTE, fonctions de fenêtre, contraintes, transactions, injection SQL | 27 | 🐳 |
| 7 | `niveau_07_sqlalchemy` | **SQLAlchemy 2.0 ORM** : modèles, relations, cascade, N+1, `IntegrityError`, pont vers pandas | 22 | 🐳 |
| 8 | `niveau_08_pandas_bases` | **pandas** : lecture CSV, nettoyage, groupby/agg, merge, pivot_table, `pd.cut`, vectorisation | 30 | – |
| 9 | `niveau_09_pandas_avance` | **pandas** : fenêtres, resample/rolling, melt, explode, `merge_asof`, cohortes, sessionisation, RFM, mémoire | 25 | – |
| 10 | `niveau_10_pandas_volume` | **pandas + gros volumes** : CSV par morceaux, Parquet (partitions, métadonnées), `pyarrow.dataset`, qualité, upsert, **S3** | 14 | 🐳 |
| 11 | `niveau_11_spark_bases` | **PySpark** : schémas, `withColumn`, `Window`, pivot, Spark SQL, explode, écriture Parquet | 16 | – |
| 12 | `niveau_12_spark_bigdata` | **Spark gros volume** : partition pruning, broadcast join, salting (skew), HyperLogLog, petits fichiers, pipeline, **S3A** | 15 | 🐳 |

## Installation

Prérequis : Python 3.10+, Java 17+ (pour Spark), Docker.

```bash
# 1. environnement Python (déjà fait dans .venv si tu utilises celui-ci)
uv venv .venv && uv pip install -p .venv -r requirements.txt
source .venv/bin/activate

# 2. infra : PostgreSQL (localhost:5440) + S3 SeaweedFS (localhost:9010)
docker compose up -d
```

Sans Docker, les tests des niveaux 6, 7, 10 (partie S3) et 12 (partie S3) sont **ignorés** (skip), pas en échec.

## Comment travailler

```bash
pytest niveau_01_bases                       # tout un niveau
pytest niveau_01_bases -k palindrome         # un seul exercice
pytest niveau_04_algo -x                     # s'arrêter au premier échec
python progression.py                        # tableau de bord global
python progression.py 8 9 10                 # seulement quelques niveaux
```

Méthode conseillée pour chaque exercice :
1. lis la docstring (spécification + exemples) ;
2. lis le test correspondant dans `test_niveau_XX.py` : c'est la spec exacte ;
3. code, lance le test, recommence.

**Ne modifie pas les tests.** Certains vérifient aussi *comment* tu codes :
- niveaux 1 et 4 : interdiction de `max()`, `sorted()`, `[::-1]`... quand l'énoncé le dit ;
- niveaux 4-5 : tests de performance (une solution O(n²) ou exponentielle échoue) ;
- niveau 7 : style SQLAlchemy 2.0 obligatoire (`select()`, pas `session.query()`), N+1 détecté ;
- niveaux 8-9 : pas de `iterrows()` ni de `apply(axis=1)`, l'entrée ne doit jamais être modifiée ;
- niveaux 11-12 : pas d'UDF Python ; le **plan d'exécution** Spark est inspecté (broadcast, pruning...).

## Infra et outils

| Service | Accès | Identifiants |
|---------|-------|--------------|
| PostgreSQL 17 | `localhost:5440`, base `exercices` | `exo` / `exo` |
| S3 (SeaweedFS) | `http://localhost:9010` | `exo` / `exo123456` |

```bash
# explorer la base à la main
docker exec -it exos_postgres psql -U exo -d exercices
exercices=# SET search_path TO niveau06;   -- schéma recréé à chaque test du niveau 6
exercices=# \dt

# lister un bucket S3
aws --endpoint-url http://localhost:9010 s3 ls s3://exos-niveau10/   # si awscli installé
```

Variables d'environnement utiles :

| Variable | Défaut | Rôle |
|----------|--------|------|
| `EXOS_PG_URL` | `postgresql://exo:exo@localhost:5440/exercices` | autre PostgreSQL |
| `EXOS_S3_ENDPOINT` | `http://localhost:9010` | autre S3 |
| `EXOS_NB_LIGNES` | `2000000` | volume du niveau 12 (monte à 10-20 M si ta machine suit) |
| `EXOS_SPARK_S3` | `1` | `0` = ne pas charger le connecteur S3A (hors-ligne) |

## Aller plus loin : le vrai gros volume

Le niveau 12 fournit un générateur utilisable seul :

```bash
# 50 millions de transactions (~1 Go de Parquet) en local
python -m niveau_12_spark_bigdata.generateur --lignes 50000000 --sortie data/bigdata

# ou directement sur le S3 local
python -m niveau_12_spark_bigdata.generateur --lignes 20000000 --sortie s3://exos-bigdata/v1
```

Puis rejoue tes fonctions du niveau 12 dessus (dans un notebook ou un script) et compare
les temps avec / sans broadcast, avec / sans salting, `approx_count_distinct` vs `countDistinct`.
Regarde les plans avec `df.explain("formatted")`.

## Conseils par étape

- **Niveaux 1-3** : écris d'abord la version la plus simple qui marche, puis nettoie.
- **Niveaux 4-5** : avant de coder, écris la complexité visée en commentaire.
- **Niveau 6** : teste tes requêtes dans `psql` avant de les coller dans le fichier.
- **Niveau 7** : la doc [ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) couvre 80 % du niveau.
- **Niveaux 8-10 (pandas)** : pense « colonnes entières », jamais « ligne par ligne ».
  `groupby` + `agg`/`transform` règle la moitié des problèmes.
- **Niveaux 11-12 (Spark)** : tout est paresseux (lazy) jusqu'à une action (`count`, `write`, `collect`).
  Le plan physique (`explain`) est ton meilleur ami.
