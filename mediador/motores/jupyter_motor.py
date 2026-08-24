"""Motor Jupyter: generacion y ejecucion de notebooks interactivos."""

import json
import shutil
import subprocess
from datetime import datetime

from .. import contexto

NOMBRE = "jupyter"
DESCRIPCION = "Analisis interactivo y documentacion con Jupyter Notebook"


def disponible():
    return bool(shutil.which("jupyter"))


def ejecutar(peticion, archivo, salida_dir, modo="analisis"):
    if not disponible():
        return {"motor": NOMBRE, "salida": "jupyter no esta instalado. Ejecuta: pip install jupyter nbconvert"}
    ruta_notebook = salida_dir / f"notebook_{datetime.now():%Y%m%d_%H%M%S}.ipynb"
    celdas = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Mediador de Contexto IA - Notebook generado\n",
                f"\nPeticion: **{peticion}**\n",
                f"\nArchivo de trabajo: `{archivo['ruta'].name if archivo else 'ninguno'}`\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "from IPython.display import display\n",
                f"ruta = {str(archivo['ruta']) if archivo else 'None'!r}\n",
                "if ruta and ruta.endswith(('.csv', '.csv.gz')):\n",
                "    df = pd.read_csv(ruta, encoding='utf-8-sig', low_memory=False)\n",
                "elif ruta and ruta.endswith(('.xlsx', '.xls')):\n",
                "    df = pd.read_excel(ruta)\n",
                "elif ruta and ruta.endswith('.parquet'):\n",
                "    df = pd.read_parquet(ruta)\n",
                "elif ruta and ruta.endswith('.json'):\n",
                "    df = pd.read_json(ruta)\n",
                "else:\n",
                "    raise SystemExit('Sin datos disponibles en Recursos')\n",
                "\n",
                "print('Dimensiones:', df.shape)\n",
                "display(df.head(10))\n",
                "display(df.describe(include='all'))\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "if hasattr(df, 'select_dtypes'):\n",
                "    numericas = df.select_dtypes(include='number')\n",
                "    if len(numericas.columns) > 1:\n",
                "        display(numericas.corr().style.background_gradient(cmap='coolwarm'))\n",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## Conclusiones\n", "\nInline los resultados del analisis en esta celda."],
        },
    ]
    notebook = {
        "cells": celdas,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    ruta_notebook.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    comando = ["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", str(ruta_notebook)]
    try:
        resultado = subprocess.run(
            comando, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=900, cwd=str(salida_dir),
        )
    except subprocess.TimeoutExpired:
        return {"motor": NOMBRE, "script": str(ruta_notebook), "salida": "Tiempo de ejecucion agotado (900s)."}
    if resultado.returncode != 0:
        return {
            "motor": NOMBRE,
            "script": str(ruta_notebook),
            "salida": "Notebook generado pero no ejecutado (instala nbconvert):\n" + (resultado.stderr or ""),
        }
    con_lineas = []
    for celda in json.loads(ruta_notebook.read_text(encoding="utf-8")).get("cells", []):
        for salida in celda.get("outputs", []):
            if salida.get("output_type") == "stream":
                con_lineas.append(salida.get("text", ""))
    return {"motor": NOMBRE, "script": str(ruta_notebook), "salida": "Notebook ejecutado: " + str(ruta_notebook) + "\n" + "".join(con_lineas), "comando": comando}