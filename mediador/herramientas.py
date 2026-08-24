"""Deteccion de herramientas disponibles en el sistema."""

import os
import shutil
import sys
from pathlib import Path


def _primera_existente(candidatos):
    for c in candidatos:
        try:
            if Path(c).exists():
                return c
        except OSError:
            continue
    return None


def _buscar_powerbi():
    return _primera_existente([
        r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
        r"C:\Program Files (x86)\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
        r"C:\Program Files\Microsoft Power BI Desktop RS\bin\PBIDesktop.exe",
    ])


def _buscar_tableau():
    if shutil.which("tabcmd"):
        return shutil.which("tabcmd")
    for base in (Path(os.environ.get("PROGRAMFILES", "")), Path(os.environ.get("PROGRAMFILES(X86)", ""))):
        if not base.exists():
            continue
        for candidato in base.glob("Tableau/Tableau */bin/tableau.exe"):
            if candidato.exists():
                return str(candidato)
    return None


def detectar():
    rscript = shutil.which("Rscript")
    try:
        import httpx
        api_disp = True
        api_ruta = "httpx"
    except ImportError:
        api_disp = False
        api_ruta = None
    return {
        "python": {"disponible": True, "ruta": sys.executable, "detalle": "Analisis de datos, ML y automatizacion (pandas/sklearn)"},
        "api": {"disponible": api_disp, "ruta": api_ruta, "detalle": "Extracción APIs REST/JSON/CSV (httpx)"},
        "streaming": {"disponible": True, "ruta": "anyio", "detalle": "Recolección tiempo real (streaming) bronze/silver/gold"},
        "lake": {"disponible": True, "ruta": str(Path(__file__).resolve().parent.parent / "salida" / "lake"), "detalle": "Data Lake por capas bronze/silver/gold"},
        "r": {"disponible": bool(rscript), "ruta": rscript, "detalle": "Analisis estadistico y visualizacion (Rscript)"},
        "jupyter": {"disponible": bool(shutil.which("jupyter")), "ruta": shutil.which("jupyter"), "detalle": "Notebooks interactivos y documentacion"},
        "spark": {"disponible": bool(shutil.which("spark-submit")), "ruta": shutil.which("spark-submit"), "detalle": "Procesamiento distribuido a gran escala"},
        "powerbi": {"disponible": _buscar_powerbi() is not None, "ruta": _buscar_powerbi(), "detalle": "Dashboards y reportes Power BI Desktop"},
        "tableau": {"disponible": _buscar_tableau() is not None, "ruta": _buscar_tableau(), "detalle": "Dashboards interactivos Tableau"},
        "sql": {"disponible": True, "ruta": "sqlite3 (stdlib)", "detalle": "Consultas sobre bases de datos locales"},
    }


def resumen():
    herramientas = detectar()
    lineas = []
    for nombre, info in herramientas.items():
        estado = "OK" if info["disponible"] else "no disponible"
        ruta = info["ruta"] or "-"
        lineas.append(f"  [{estado:<13}] {nombre:<8} {ruta}")
        lineas.append(f"                 {info['detalle']}")
    return "\n".join(lineas)