"""Motor Spark: procesamiento distribuido a gran escala (PySpark)."""

import shutil
import subprocess
import sys
from datetime import datetime

from .. import contexto

NOMBRE = "spark"
DESCRIPCION = "Procesamiento distribuido a gran escala (Apache Spark / PySpark)"


def disponible():
    if shutil.which("spark-submit"):
        return True
    try:
        import pyspark  # noqa: F401
        return True
    except ImportError:
        return False


def ejecutar(peticion, archivo, salida_dir, modo="analisis"):
    if archivo is None:
        return {"motor": NOMBRE, "salida": "No hay archivos de datos en Recursos para procesar."}
    nombre = archivo["ruta"].name
    script = salida_dir / f"spark_analisis_{datetime.now():%Y%m%d_%H%M%S}.py"
    codigo = f'''from pyspark.sql import SparkSession

spark = SparkSession.builder \\
    .appName("mediador_spark") \\
    .master("local[*]") \\
    .getOrCreate()

ruta = fr"{archivo["ruta"]}"

if "{nombre}" .lower().endswith(".parquet"):
    df = spark.read.parquet(ruta)
else:
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(ruta)

print("=== RESUMEN DE {nombre} ===")
print("Total de registros:", df.count())
print()
df.printSchema()
print()
print("=== PRIMEROS 10 REGISTROS ===")
df.show(10, truncate=False)
print()
print("=== ESTADISTICAS DESCRIPTIVAS ===")
df.describe().show()
print()
numericas = [f.name for f in df.schema.fields if f.dataType.typeName() in ("int", "long", "double", "float")]
if numericas:
    print("=== AGRUPACION POR PRIMERA COLUMNA CATEGORICA ===")
    categoricas = [c for c in df.columns if c not in numericas]
    if categoricas:
        df.groupBy(categoricas[0]).count().orderBy("count", ascending=False).show(20)
    print("=== MAXIMO Y MINIMO DE COLUMNAS NUMERICAS ===")
    for col in numericas[:3]:
        df.agg({{"max_{{{col}}}": "max", "min_{{{col}}}": "min"}}).show()

spark.stop()
'''
    script.write_text(codigo, encoding="utf-8")
    if shutil.which("spark-submit"):
        comando = ["spark-submit", "--master", "local[*]", str(script)]
        ejecutor = comando
    else:
        ejecutor = [sys.executable, str(script)]
    try:
        resultado = subprocess.run(
            ejecutor, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=1800, cwd=str(salida_dir),
        )
    except subprocess.TimeoutExpired:
        return {"motor": NOMBRE, "script": str(script), "salida": "Tiempo de ejecucion agotado (1800s)."}
    salida = resultado.stdout or ""
    if resultado.returncode != 0:
        salida += "\n[ERROR]\n" + (resultado.stderr or "")
        salida += "\n\nSugerencia: instala PySpark con: uv pip install pyspark, o instala Spark con spark-submit en el PATH."
    return {"motor": NOMBRE, "script": str(script), "salida": salida, "comando": ejecutor}