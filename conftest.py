import os
import sys

import pytest


def version_hadoop() -> str:
    """Version de Hadoop embarquée par pyspark (le jar hadoop-aws doit être identique)."""
    import glob

    import pyspark

    jar = glob.glob(os.path.join(os.path.dirname(pyspark.__file__), "jars", "hadoop-client-api-*.jar"))[0]
    return os.path.basename(jar)[len("hadoop-client-api-"):-len(".jar")]


@pytest.fixture(scope="session")
def spark():
    """SparkSession locale partagée par tous les tests Spark (niveaux 11 et 12)."""
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
    from pyspark.sql import SparkSession

    builder = (
        SparkSession.builder.master("local[4]")
        .appName("pythonNaval-tests")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.driver.memory", "4g")
        # listing des dossiers de partitions côté driver (évite un job Spark de 366 tâches à chaque lecture)
        .config("spark.sql.sources.parallelPartitionDiscovery.threshold", "1000")
    )
    if os.environ.get("EXOS_SPARK_S3", "1") == "1":
        # connecteur S3A (téléchargé une seule fois depuis Maven, puis en cache dans ~/.ivy2)
        builder = builder.config("spark.jars.packages", f"org.apache.hadoop:hadoop-aws:{version_hadoop()}")
    session = builder.getOrCreate()
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()


PG_URL = os.environ.get("EXOS_PG_URL", "postgresql://exo:exo@localhost:5440/exercices")
S3_ENDPOINT = os.environ.get("EXOS_S3_ENDPOINT", "http://localhost:9010")


@pytest.fixture(scope="session")
def pg_url():
    """URL PostgreSQL (docker compose up -d). Les tests sont SKIP si la base est éteinte."""
    import psycopg

    try:
        psycopg.connect(PG_URL, connect_timeout=3).close()
    except psycopg.OperationalError:
        pytest.skip(f"PostgreSQL injoignable ({PG_URL}) -> lance `docker compose up -d`")
    return PG_URL


@pytest.fixture(scope="session")
def s3_endpoint():
    """Endpoint S3 local (SeaweedFS). Les tests sont SKIP s'il est éteint."""
    import urllib.request

    try:
        urllib.request.urlopen(S3_ENDPOINT, timeout=3)
    except Exception as e:  # une 403/404 HTTP veut dire que le serveur répond
        if not hasattr(e, "code"):
            pytest.skip(f"S3 injoignable ({S3_ENDPOINT}) -> lance `docker compose up -d`")
    return S3_ENDPOINT
