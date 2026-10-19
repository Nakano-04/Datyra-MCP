"""MCP Server real para Datyra MCP - FastMCP stdio + streamable-http.
Autor: Nakano-04 - Mercenary Company “Mercenario del rojo”
  Software Engineer (Cybersecurity · AI · Systems · ERP)
  Building security tools, AI systems, ERP modules & research
  Contact: nakano.04.2025@gmail.com
Compatible con TODA IA que soporte MCP: Claude, Devin, Codex, opencode, Windsurf, Cursor, Copilot, Gemini, ChatGPT, etc.
"""

import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP
from mediador import contexto, herramientas, nucleo
from mediador.motores import python_motor, visual_motor

# Pre-import pesados para evitar deadlock en Windows stdio (anyio)
try:
    import pandas  # noqa: F401
    import numpy  # noqa: F401
    import scipy  # noqa: F401
    import sklearn  # noqa: F401
except Exception:
    pass

AUTHOR = "Nakano-04 - Mercenary Company 'Mercenario del rojo' | Software Engineer (Cybersecurity · AI · Systems · ERP) | nakano.04.2025@gmail.com | https://github.com/Nakano-04"

mcp = FastMCP(
    name="datyra-mcp",
    instructions="Datyra MCP por Nakano-04 (Mercenary Company). Mediador de Contexto IA: analiza datos con Python/R/SQL/Spark/Jupyter/PowerBI/Tableau en lenguaje natural. Recursos en ./Recursos, salida en ./salida. Compatible con cualquier IA via MCP (Claude, Devin, Codex, opencode, Cursor, Windsurf, Copilot, Gemini, etc.).",
)

@mcp.tool()
def author_info() -> str:
    """Devuelve info del autor del proyecto."""
    return json.dumps({"autor": "Nakano-04", "alias": "Mercenario del rojo", "company": "Mercenary Company", "rol": "Software Engineer (Cybersecurity · AI · Systems · ERP)", "focus": "Building security tools, AI systems, ERP modules & research", "email": "nakano.04.2025@gmail.com", "github": "https://github.com/Nakano-04", "mcp": "datyra-mcp", "compatible": "Toda IA con MCP - Claude, Devin, Codex, opencode, Cursor, Windsurf, Copilot, Gemini, ChatGPT"}, ensure_ascii=False, indent=2)

@mcp.tool()
def list_datasets() -> str:
    """Lista datasets disponibles en Recursos/ con tipo, tamaño y filas."""
    inv = contexto.inventario()
    if not inv:
        return "No hay datasets en Recursos/. Coloca csv/xlsx/json/parquet/db allí."
    out = []
    for a in inv:
        out.append({"archivo": a["ruta"].name, "tipo": a["tipo"], "tamano": contexto.formatear_bytes(a["tamano"]), "filas": a["filas"], "ruta": str(a["ruta"])})
    return json.dumps(out, ensure_ascii=False, indent=2)

@mcp.tool()
def get_tool_status() -> str:
    """Estado de motores disponibles en el sistema."""
    return herramientas.resumen()

@mcp.tool()
def analyze_data(peticion: str, dataset: Optional[str] = None, salida_dir: Optional[str] = None) -> str:
    """Analiza datos con lenguaje natural. Ej: 'analiza las ventas', 'limpia y resume ciberseguridad'. Si dataset se da, fuerza ese archivo."""
    carpeta = Path(salida_dir) if salida_dir else contexto.carpeta_salida()
    carpeta.mkdir(parents=True, exist_ok=True)
    if dataset:
        inv = contexto.inventario()
        forced = next((a for a in inv if dataset.lower() in a["ruta"].name.lower()), None)
        if forced:
            peticion = f"{peticion} {forced['ruta'].stem}"
    res = nucleo.ejecutar_peticion(peticion, salida_dir=str(carpeta), silent=True)
    # por tipo: html en html/ , compatibilidad con tmp_path
    html_candidates = list(carpeta.glob("informe_*.html")) + list((carpeta / "html").glob("informe_*.html"))
    htmls = sorted(html_candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    html = str(htmls[0]) if htmls else ""
    return json.dumps({"motor": res.get("motor"), "salida": res.get("salida","")[:6000], "script": res.get("script"), "html": html}, ensure_ascii=False, indent=2)

@mcp.tool()
def run_statistics(peticion: str = "analisis estadistico correlacion", dataset: Optional[str] = None) -> str:
    """Ejecuta análisis estadístico (Pearson/Spearman/Shapiro/IQR). Ej: 'correlacion entre monto y score'."""
    if "estadistic" not in peticion.lower() and "correlacion" not in peticion.lower():
        peticion = f"analisis estadistico {peticion}"
    return analyze_data(peticion, dataset=dataset)

@mcp.tool()
def train_model(peticion: str, target: Optional[str] = None, dataset: Optional[str] = None) -> str:
    """Entrena modelo ML. Ej: peticion='predice moroso', target='moroso', dataset='finanzas_masivo.csv'. Soporta regresion, clasificacion y clustering kmeans."""
    if target:
        peticion = f"{peticion} {target}"
    if "machine learning" not in peticion.lower() and "ml" not in peticion.lower() and "cluster" not in peticion.lower():
        peticion = f"{peticion} con machine learning"
    return analyze_data(peticion, dataset=dataset)

@mcp.tool()
def generate_dashboard(peticion: str = "genera dashboard con graficos", dataset: Optional[str] = None) -> str:
    """Genera dashboard MOD dark: histograma KDE, barras, heatmap correlacion y serie temporal. Devuelve rutas PNG y HTML."""
    if dataset:
        peticion = f"{peticion} {dataset}"
    carpeta = contexto.carpeta_salida()
    res = nucleo.ejecutar_peticion(peticion, salida_dir=str(carpeta), silent=True)
    pngs = sorted(list((carpeta / "cuadros").glob("*.png")) + list(carpeta.glob("*.png")), key=lambda p: p.stat().st_mtime, reverse=True)[:6]
    html_candidates = list(carpeta.glob("informe_*.html")) + list((carpeta / "html").glob("informe_*.html"))
    htmls = sorted(html_candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    return json.dumps({"salida": res.get("salida","")[:4000], "imagenes": [str(p) for p in pngs], "html": str(htmls[0]) if htmls else ""}, ensure_ascii=False, indent=2)

@mcp.tool()
def batch_process(peticion: str = "analiza todos batch") -> str:
    """Procesa todos los datasets en Recursos/ en batch."""
    if "todos" not in peticion.lower() and "batch" not in peticion.lower():
        peticion = f"{peticion} todos batch"
    return analyze_data(peticion)

@mcp.tool()
def profile_data(dataset: str, n_rows: int = 50) -> str:
    """Devuelve preview + stats rápidos de un dataset (primeras n_rows)."""
    inv = contexto.inventario()
    arch = next((a for a in inv if dataset.lower() in a["ruta"].name.lower()), None)
    if not arch:
        return json.dumps({"error": f"Dataset '{dataset}' no encontrado", "disponibles": [a["ruta"].name for a in inv]}, ensure_ascii=False)
    p = arch["ruta"]
    try:
        import pandas as pd
        if p.suffix.lower() in [".csv"]:
            df = pd.read_csv(p, nrows=5000, encoding="utf-8-sig")
        elif p.suffix.lower() in [".xlsx",".xls"]:
            df = pd.read_excel(p, nrows=5000)
        elif p.suffix.lower()==".parquet":
            df = pd.read_parquet(p).head(5000)
        else:
            return contexto.csv_a_texto(p, limite_filas=n_rows)
        preview = df.head(n_rows).to_json(orient="records", force_ascii=False, indent=2)
        desc = df.describe(include="all").to_json(force_ascii=False, indent=2)
        return json.dumps({"archivo": p.name, "shape_preview": list(df.head(5000).shape), "dtypes": {k:str(v) for k,v in df.dtypes.items()}, "preview": json.loads(preview), "describe": json.loads(desc)}, ensure_ascii=False, indent=2)
    except Exception as e:
        return contexto.csv_a_texto(p, limite_filas=n_rows) + f"\n[preview error: {e}]"

@mcp.tool()
def query_sql(sql: str, db: Optional[str] = None) -> str:
    """Ejecuta SQL sobre sqlite/duckdb en Recursos/. Ej: 'SELECT region, SUM(ingreso) FROM ventas GROUP BY region'."""
    import sqlite3
    target = None
    if db:
        inv = contexto.inventario()
        target = next((a["ruta"] for a in inv if db.lower() in a["ruta"].name.lower()), None)
        if not target:
            target = Path(db)
    else:
        target = contexto.buscar_base_datos()
        if not target:
            # crear db temporal desde csv si no hay sqlite
            from mediador.motores import sql_motor
            return sql_motor.ejecutar(sql, None, contexto.carpeta_salida(), modo="analisis")["salida"]
    try:
        con = sqlite3.connect(str(target))
        cur = con.cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(100)
        con.close()
        return json.dumps({"db": str(target), "columns": cols, "rows": rows, "total": len(rows)}, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"SQL error: {e}"

@mcp.tool()
def identificar_fuentes(peticion: str = "", top_n: int = 5) -> str:
    """Identifica fuentes relevantes con scoring (tipo, frescura, tamaño, match semántico)."""
    res = contexto.identificar_fuentes_relevantes(peticion, top_n=top_n)
    return json.dumps(res, ensure_ascii=False, indent=2, default=str)

@mcp.tool()
def extraer_api(url: str, formato: Optional[str] = None) -> str:
    """Extrae datos de API REST/JSON/CSV y consolida en Data Lake bronze."""
    from mediador.motores import api_motor
    res = api_motor.ejecutar(f"extrae datos de {url} {formato or ''}", None, contexto.carpeta_salida(), modo="analisis")
    return res["salida"]

@mcp.tool()
def colectar_streaming(peticion: str = "streaming 20 eventos", dataset: Optional[str] = None) -> str:
    """Recolecta datos en tiempo real (streaming) a lake/bronze/silver/gold."""
    from mediador.motores import streaming_motor
    inv = contexto.inventario()
    arch = next((a for a in inv if dataset and dataset.lower() in a["ruta"].name.lower()), None) if dataset else None
    res = streaming_motor.ejecutar(peticion, arch, contexto.carpeta_salida(), modo="analisis")
    return res["salida"]

@mcp.tool()
def consolidar_lake(capa: str = "all") -> str:
    """Consolida Data Lake por capas bronze/silver/gold."""
    lake_base = Path("salida/lake")
    if capa == "all":
        capas = ["bronze", "silver", "gold"]
    else:
        capas = [capa]
    out = []
    for c in capas:
        p = lake_base / c
        if p.exists():
            files = list(p.glob("*"))
            out.append(f"{c}: {len(files)} archivos → {p}")
            for f in files[:3]:
                out.append(f"  - {f.name} ({contexto.formatear_bytes(f.stat().st_size)})")
        else:
            out.append(f"{c}: vacío (no existe)")
    # central catalog
    central = contexto.carpeta_central()
    cat = central / "catalogo_metadatos.json"
    if cat.exists():
        out.append(f"Catálogo: {cat} ({cat.stat().st_size} bytes)")
    lin = central / "linaje.json"
    if lin.exists():
        out.append(f"Linaje: {lin}")
    return "\n".join(out)

@mcp.tool()
def catalogo_metadatos() -> str:
    """Documentación de metadatos y linaje de datos."""
    cat = contexto.catalogo_metadatos()
    # guardar
    import json as js
    central = contexto.carpeta_central()
    out = central / "catalogo_metadatos.json"
    out.write_text(js.dumps(cat, ensure_ascii=False, indent=2), encoding="utf-8")
    (contexto.carpeta_salida() / "catalogo_metadatos.json").write_text(js.dumps(cat, ensure_ascii=False, indent=2), encoding="utf-8")
    return js.dumps(cat, ensure_ascii=False, indent=2)

@mcp.tool()
def documentar_linaje() -> str:
    """Muestra linaje del último análisis."""
    import json as js
    p = contexto.carpeta_central() / "linaje.json"
    if p.exists():
        return p.read_text(encoding="utf-8")
    p2 = contexto.carpeta_salida() / "linaje.json"
    if p2.exists():
        return p2.read_text(encoding="utf-8")
    return "No hay linaje aún. Ejecuta 'analiza las ventas' primero."

if __name__ == "__main__":
    mcp.run()
