"""Prueba de humo del cluster (informe, seccion 4): 4 comprobaciones antes del notebook.

Se ejecuta dentro del contenedor del driver:
    docker compose exec jupyter python3 verificar_cluster.py

Cada comprobacion descarta un fallo concreto:
    1. sesion       -> el driver alcanza al master
    2. executors    -> hay recursos asignados de verdad (0 = executor pide mas memoria que el worker)
    3. visibilidad  -> todos los executors ven /opt/workspace/data/raw (si no, FileNotFoundException)
    4. lectura real -> el camino completo funciona sobre los 10 M de eventos
"""
import glob
import os
import socket
import sys
import time

from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, LongType, StringType, StructField, StructType

RUTA_DATOS = "/opt/workspace/data/raw"

spark = (
    SparkSession.builder
    .appName("verificar-cluster")
    .master("spark://spark-master:7077")
    .config("spark.driver.host", "jupyter")
    .config("spark.driver.bindAddress", "0.0.0.0")
    .config("spark.executor.memory", os.environ.get("SPARK_EXECUTOR_MEMORY", "1g"))
    .getOrCreate()
)
sc = spark.sparkContext
sc.setLogLevel("ERROR")

print("[1/4] Sesion creada")
print(f"      Spark   : {spark.version}")
print(f"      Python  : {sys.version.split()[0]}")
print(f"      Master  : {sc.master}")

# los executors tardan unos segundos en registrarse con el driver
esperados = int(os.environ.get("SPARK_WORKERS", "1"))
ejecutores = 0
for _ in range(30):
    ejecutores = sc._jsc.sc().getExecutorMemoryStatus().size() - 1  # -1 = el propio driver
    if ejecutores >= esperados:
        break
    time.sleep(1)
print(f"[2/4] Executors vivos : {ejecutores}")
print(f"      Paralelismo     : {sc.defaultParallelism} tareas en paralelo")
if ejecutores == 0:
    sys.exit("      ERROR: no hay executors. Revisa SPARK_EXECUTOR_MEMORY <= SPARK_WORKER_MEMORY")


def mirar(_):
    # esto corre DENTRO de cada executor, no en el driver
    return socket.gethostname(), len(glob.glob(RUTA_DATOS + "/*.jsonl"))


vistas = sorted(set(sc.parallelize(range(40), 40).map(mirar).collect()))
print(f"[3/4] Visibilidad de {RUTA_DATOS} desde los executors:")
for host, n in vistas:
    estado = f"ve los datos ({n} archivos)" if n else "NO VE LOS DATOS"
    print(f"      {host:<30} {estado}")

esquema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("sensor_id", StringType(), True),
    StructField("metric",    StringType(), True),
    StructField("value",     DoubleType(), True),
    StructField("unit",      StringType(), True),
    StructField("worker_id", LongType(),   True),
])
print("[4/4] Leyendo los datos crudos de la Fase 1...")
df = spark.read.schema(esquema).json(RUTA_DATOS + "/*.jsonl")
print(f"      Registros leidos : {df.count():,}")
print(f"      Particiones      : {df.rdd.getNumPartitions()}")

spark.stop()
