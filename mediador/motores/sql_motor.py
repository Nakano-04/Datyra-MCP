"""Motor SQL: consultas e inspeccion de bases de datos locales (sqlite/duckdb)."""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path

from .. import contexto

NOMBRE = "sql"
DESCRIPCION = "Consultas y gestion de bases de datos (SQLite / DuckDB)"


def disponible():
    return True


def _crear_base_desde(archivo, destino):
    if archivo["tipo"] != "csv":
        if contexto.hay_pandas():
            import pandas as pd
            ruta = str(archivo["ruta"])
            if archivo["tipo"] == "excel":
                df = pd.read_excel(ruta)
            elif archivo["tipo"] == "json":
                df = pd.read_json(ruta)
            else:
                df = pd.read_csv(ruta, encoding="utf-8-sig")
            conexion = sqlite3.connect(str(destino))
            df.to_sql("datos", conexion, if_exists="replace", index=False)
            conexion.close()
            return
    nombre = archivo["ruta"].stem
    conexion = sqlite3.connect(str(destino))
    cursor = conexion.cursor()
    primeras = []
    with archivo["ruta"].open("r", encoding="utf-8-sig", errors="ignore", newline="") as f:
        lector = csv.reader(f)
        encabezados = next(lector, None)
        if not encabezados:
            conexion.close()
            return
        columnas = [f"col_{i}" if not e else e.replace('"', "").replace("'", "") for i, e in enumerate(encabezados)]
        definiciones = ", ".join(f'"{c}" TEXT' for c in columnas)
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{nombre}" ({definiciones})')
        marcadores = ", ".join("?" for _ in columnas)
        for fila in lector:
            primeras.append(fila[: len(columnas)])
            if len(primeras) >= 500:
                break
        cursor.executemany(f'INSERT INTO "{nombre}" VALUES ({marcadores})', primeras)
    conexion.commit()
    conexion.close()


def ejecutar(peticion, archivo, salida_dir, modo="analisis"):
    base = contexto.buscar_base_datos()
    creada = False
    if base is None:
        if archivo is None:
            return {"motor": NOMBRE, "salida": "No hay archivos de datos ni bases de datos en Recursos."}
        base = salida_dir / f"datos_mediador_{datetime.now():%Y%m%d_%H%M%S}.db"
        _crear_base_desde(archivo, base)
        creada = True
    conexion = sqlite3.connect(str(base))
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    lineas = []
    if creada:
        lineas.append(f"Base de datos creada a partir de {archivo['ruta'].name}: {base.name}")
        lineas.append("")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [fila[0] for fila in cursor.fetchall()]
        if not tablas:
            lineas.append("La base de datos no tiene tablas.")
        for tabla in tablas:
            cursor.execute(f'SELECT COUNT(*) FROM "{tabla}"')
            total = cursor.fetchone()[0]
            lineas.append(f"Tabla: {tabla}  |  registros: {total}")
            cursor.execute(f'PRAGMA table_info("{tabla}")')
            columnas = [fila[1] for fila in cursor.fetchall()]
            lineas.append(f"  columnas: {', '.join(columnas)}")
            cursor.execute(f'SELECT * FROM "{tabla}" LIMIT 10')
            filas = cursor.fetchall()
            if filas:
                lineas.append(f"  muestra ({len(filas)} de {total}):")
                for fila in filas:
                    lineas.append("    " + " | ".join(str(fila[c]) for c in fila.keys()))
            lineas.append("")
    except sqlite3.Error as e:
        lineas.append(f"Error SQL: {e}")
    conexion.close()
    return {"motor": NOMBRE, "salida": "\n".join(lineas), "base": str(base)}