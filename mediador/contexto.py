"""Descubrimiento y gestion del contexto de datos del mediador."""

import csv
import importlib.util
from pathlib import Path

EXT_TIPOS = {
    ".xlsx": "excel",
    ".xls": "excel",
    ".csv": "csv",
    ".tsv": "csv",
    ".json": "json",
    ".parquet": "parquet",
    ".db": "sqlite",
    ".sqlite": "sqlite",
    ".sqlite3": "sqlite",
    ".duckdb": "sqlite",
    ".ipynb": "jupyter",
    ".pbix": "powerbi",
    ".twb": "tableau",
    ".twbx": "tableau",
    ".rds": "r",
    ".rdata": "r",
    ".r": "r",
    ".sql": "sql",
    ".pkl": "python",
    ".pickle": "python",
}

TIPO_PRIORIDAD = ["csv", "excel", "json", "parquet", "sqlite", "jupyter", "powerbi", "tableau", "r", "sql", "python"]


def carpeta_base():
    return Path(__file__).resolve().parent.parent


def carpeta_recursos():
    carpeta = carpeta_base() / "Recursos"
    carpeta.mkdir(exist_ok=True)
    return carpeta


def carpeta_salida():
    carpeta = carpeta_base() / "salida"
    carpeta.mkdir(exist_ok=True)
    return carpeta


def _tipo_de(archivo):
    nombre = archivo.name.lower()
    if nombre.endswith(".csv.gz") or nombre.endswith(".tsv.gz"):
        return "csv"
    return EXT_TIPOS.get(archivo.suffix.lower(), "otro")


def escanear(carpeta=None):
    raiz = Path(carpeta) if carpeta else carpeta_recursos()
    if not raiz.exists():
        return []
    hallazgos = []
    for p in raiz.rglob("*"):
        if not p.is_file() or p.name.startswith("~$"):
            continue
        tipo = _tipo_de(p)
        if tipo == "otro":
            continue
        try:
            tamano = p.stat().st_size
        except OSError:
            tamano = 0
        hallazgos.append({"ruta": p, "tipo": tipo, "tamano": tamano})
    hallazgos.sort(key=lambda a: (TIPO_PRIORIDAD.index(a["tipo"]) if a["tipo"] in TIPO_PRIORIDAD else 99, -a["tamano"]))
    return hallazgos


def _filas_excel(p):
    if importlib.util.find_spec("openpyxl") is None:
        return 0
    try:
        import openpyxl
        libro = openpyxl.load_workbook(p, read_only=True)
        hoja = libro.active
        filas = hoja.max_row or 0
        libro.close()
        return filas
    except Exception:
        return 0


def _filas_csv(p):
    try:
        with p.open("r", encoding="utf-8-sig", errors="ignore", newline="") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def inventario():
    return [
        {
            "ruta": a["ruta"],
            "tipo": a["tipo"],
            "tamano": a["tamano"],
            "filas": _filas(a["ruta"], a["tipo"]),
        }
        for a in escanear()
    ]


def _filas(p, tipo):
    if tipo == "csv":
        return _filas_csv(p)
    if tipo == "excel":
        return _filas_excel(p)
    return 0


def elegir_dataset(archivos, terminos=None):
    if not archivos:
        return None
    if terminos:
        for a in archivos:
            nombre = a["ruta"].name.lower()
            if any(t in nombre for t in terminos):
                return a
    for tipo in ("csv", "excel", "parquet", "json"):
        for a in archivos:
            if a["tipo"] == tipo:
                return a
    return archivos[0]


def filtro_tipo(archivos, tipos):
    return [a for a in archivos if a["tipo"] in tipos]


def buscar_base_datos(archivos=None):
    for a in (archivos or escanear()):
        if a["tipo"] == "sqlite":
            return a["ruta"]
    return None


def hay_pandas():
    return importlib.util.find_spec("pandas") is not None


def csv_a_texto(p, limite_filas=50):
    filas = []
    try:
        with p.open("r", encoding="utf-8-sig", errors="ignore", newline="") as f:
            lector = csv.reader(f)
            for n, fila in enumerate(lector):
                if n == 0:
                    filas.append(";".join(fila))
                else:
                    filas.append(";".join(fila))
                if n >= limite_filas:
                    filas.append("...")
                    break
    except Exception as e:
        return f"Error al leer {p.name}: {e}"
    return "\n".join(filas)


def formatear_bytes(n):
    for unidad in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unidad}"
        n /= 1024
    return f"{n:.1f} TB"