"""Motor Streaming: recolección de datos en tiempo real."""

import json
import time
from datetime import datetime
from pathlib import Path

from .. import contexto

NOMBRE = "streaming"
DESCRIPCION = "Recolección tiempo real (streaming) - buffer + Data Lake"


def disponible():
    return True


def _simular_stream(n=20, delay=0.01):
    """Genera datos streaming simulados (ej. sensores)"""
    import random
    for i in range(n):
        yield {
            "timestamp": datetime.now().isoformat(),
            "sensor_id": f"s{i%3 + 1}",
            "valor": round(random.uniform(20, 100), 2),
            "evento": random.choice(["normal", "alerta", "normal", "normal"])
        }
        time.sleep(delay)


def ejecutar(peticion, archivo, salida_dir, modo="analisis"):
    from ..contexto import carpeta_lake
    salida_dir = Path(salida_dir)
    bronze = carpeta_lake("bronze")
    silver = carpeta_lake("silver")

    # Detectar si es streaming real (watch) o simulado
    lower = peticion.lower()
    n_mensajes = 20
    # extraer número si se pide "20 eventos" etc.
    import re
    m = re.search(r'(\d+)\s*(evento|mensaje|fila|registro)', lower)
    if m:
        n_mensajes = min(int(m.group(1)), 100)

    # Si hay archivo existente, simular tail streaming sobre él
    if archivo and "stream" in lower:
        try:
            # Leer últimas líneas como stream
            import pandas as pd
            ruta = str(archivo["ruta"])
            df = pd.read_csv(ruta, encoding="utf-8-sig", nrows=100)
            # Guardar como stream en bronze
            stream_file = bronze / f"stream_{archivo['ruta'].stem}_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
            with stream_file.open("w", encoding="utf-8") as f:
                for _, row in df.head(n_mensajes).iterrows():
                    f.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")
            # Consolidar a silver como parquet/csv
            silver_file = silver / f"{archivo['ruta'].stem}_stream_{datetime.now():%Y%m%d_%H%M%S}.csv"
            df.head(n_mensajes).to_csv(silver_file, index=False, encoding="utf-8-sig")
            return {"motor": NOMBRE, "salida": f"Streaming (tail) de {archivo['ruta'].name}: {n_mensajes} eventos\n→ Bronze (jsonl): {stream_file}\n→ Silver: {silver_file}\nLatencia ~{0.01*n_mensajes:.2f}s"}
        except Exception as e:
            return {"motor": NOMBRE, "salida": f"Error streaming tail: {e}"}

    # Streaming simulado (sensores)
    stream_file = bronze / f"stream_sim_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
    silver_file = silver / f"stream_sim_{datetime.now():%Y%m%d_%H%M%S}.csv"
    registros = []
    with stream_file.open("w", encoding="utf-8") as f:
        for rec in _simular_stream(n=n_mensajes, delay=0.005):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            registros.append(rec)

    # Consolidar a silver
    try:
        import pandas as pd
        df = pd.DataFrame(registros)
        df.to_csv(silver_file, index=False, encoding="utf-8-sig")
        silver_msg = f"→ Silver: {silver_file} ({len(df)} filas)"
    except Exception as e:
        silver_msg = f"Silver error: {e}"

    # También a gold (agregado)
    try:
        gold = carpeta_lake("gold")
        gold_file = gold / f"stream_agg_{datetime.now():%Y%m%d_%H%M%S}.json"
        agg = {"total": len(registros), "por_sensor": {}, "eventos": {}}
        for r in registros:
            agg["por_sensor"][r["sensor_id"]] = agg["por_sensor"].get(r["sensor_id"], 0) + 1
            agg["eventos"][r["evento"]] = agg["eventos"].get(r["evento"], 0) + 1
        gold_file.write_text(json.dumps(agg, indent=2, ensure_ascii=False), encoding="utf-8")
        gold_msg = f"→ Gold (agregado): {gold_file}"
    except Exception as e:
        gold_msg = f"Gold error: {e}"

    return {"motor": NOMBRE, "salida": f"Streaming tiempo real: {n_mensajes} eventos generados\n→ Bronze (raw jsonl): {stream_file}\n{silver_msg}\n{gold_msg}\nLake: {bronze.parent}"}
