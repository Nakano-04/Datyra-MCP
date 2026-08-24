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
    # hijas por tipo — central queda para archivo único completo
    for sub in ["cuadros", "html", "txt", "scripts", "central"]:
        (carpeta / sub).mkdir(exist_ok=True)
    return carpeta

def carpeta_cuadros():
    c = carpeta_salida() / "cuadros"
    c.mkdir(exist_ok=True)
    return c

def carpeta_html():
    c = carpeta_salida() / "html"
    c.mkdir(exist_ok=True)
    return c

def carpeta_txt():
    c = carpeta_salida() / "txt"
    c.mkdir(exist_ok=True)
    return c

def carpeta_scripts():
    c = carpeta_salida() / "scripts"
    c.mkdir(exist_ok=True)
    return c

def carpeta_central():
    c = carpeta_salida() / "central"
    c.mkdir(exist_ok=True)
    return c


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


def identificar_fuentes_relevantes(peticion: str = "", top_n: int = 5):
    """Identifica fuentes relevantes con scoring por tipo, frescura, tamaño y match semántico"""
    import time
    inv = inventario()
    if not inv:
        return []
    terminos = [t for t in peticion.lower().split() if len(t) > 3] if peticion else []
    scored = []
    for a in inv:
        score = 0
        # tipo prioridad (csv > excel > parquet > json)
        tipo_score = max(0, 10 - TIPO_PRIORIDAD.index(a["tipo"])) if a["tipo"] in TIPO_PRIORIDAD else 0
        score += tipo_score * 2
        # tamaño (normalizado, más filas = más relevante hasta 20k)
        if a["filas"]:
            score += min(a["filas"] / 5000, 4)
        # frescura (mtime)
        try:
            mtime = a["ruta"].stat().st_mtime
            age_days = (time.time() - mtime) / 86400
            score += max(0, 3 - age_days / 30)  # más reciente = más score
        except: pass
        # match semántico con petición
        nombre = a["ruta"].name.lower()
        matches = sum(1 for t in terminos if t in nombre)
        score += matches * 5
        # bonus por estar en subcarpeta organizada (masivo/internet/ejemplo)
        if "masivo" in str(a["ruta"]).lower():
            score += 1
        scored.append({**a, "score": round(score, 2), "relevancia": "alta" if score > 8 else "media" if score > 5 else "baja"})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]

def catalogo_metadatos():
    """Genera catálogo de metadatos y linaje para Data Lake"""
    import datetime, json, hashlib
    inv = inventario()
    catalogo = []
    for a in inv:
        try:
            stat = a["ruta"].stat()
            # linaje: origen -> bronze -> silver -> gold
            linaje = {
                "origen": str(a["ruta"]),
                "bronze": f"lake/bronze/{a['ruta'].name}",
                "silver": f"lake/silver/{a['ruta'].stem}_clean.parquet",
                "gold": f"lake/gold/{a['ruta'].stem}_features.parquet",
                "central": f"salida/central/informe_completo.html"
            }
            # hash para control de versiones
            h = hashlib.md5(str(a["ruta"]).encode()).hexdigest()[:8]
            catalogo.append({
                "dataset": a["ruta"].name,
                "tipo": a["tipo"],
                "tamano": formatear_bytes(a["tamano"]),
                "tamano_bytes": a["tamano"],
                "filas": a["filas"],
                "ruta": str(a["ruta"]),
                "modificado": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "linaje": linaje,
                "version": h,
                "esquema": _inferir_esquema(a["ruta"], a["tipo"])
            })
        except Exception as e:
            catalogo.append({"dataset": a["ruta"].name, "error": str(e)})
    return catalogo

def _inferir_esquema(ruta, tipo):
    if tipo != "csv":
        return []
    try:
        with ruta.open("r", encoding="utf-8-sig", errors="ignore", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            sample = next(reader, [])
            return [{"col": h, "ejemplo": s, "tipo_inferido": "numeric" if s.replace(".","",1).replace("-","",1).isdigit() else "text"} for h,s in zip(header, sample)]
    except:
        return []

def carpeta_lake(capa: str = "bronze"):
    """Data Lake por capas: bronze (raw), silver (clean), gold (features)"""
    base = carpeta_base() / "salida" / "lake" / capa
    base.mkdir(parents=True, exist_ok=True)
    return base

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