"""Motor API: extracción mediante APIs REST, bases de datos y archivos."""

import json
import re
from datetime import datetime
from pathlib import Path

from .. import contexto

NOMBRE = "api"
DESCRIPCION = "Extracción via APIs REST, BD y archivos (httpx/json/csv)"


def disponible():
    try:
        import httpx
        return True
    except ImportError:
        return False


def _extraer_url(peticion: str):
    # busca URL en la petición
    urls = re.findall(r'https?://[^\s"\'<>]+', peticion)
    return urls[0] if urls else None


def ejecutar(peticion, archivo, salida_dir, modo="analisis"):
    import httpx
    from ..contexto import carpeta_lake

    salida_dir = Path(salida_dir)
    bronze = carpeta_lake("bronze")
    lower = peticion.lower()
    # 0. Manejo especial para catálogo, linaje y lake (cumplimiento completo)
    if "catalogo" in lower or "metadatos" in lower:
        cat = contexto.catalogo_metadatos()
        import json as js
        central = contexto.carpeta_central()
        out = central / "catalogo_metadatos.json"
        out.write_text(js.dumps(cat, ensure_ascii=False, indent=2), encoding="utf-8")
        (contexto.carpeta_salida() / "catalogo_metadatos.json").write_text(js.dumps(cat, ensure_ascii=False, indent=2), encoding="utf-8")
        resumen = "\n".join([f"  {c['dataset']} → {c['linaje']['bronze']} ({c['tamano']})" for c in cat[:5]])
        return {"motor": NOMBRE, "salida": f"Catálogo metadatos ({len(cat)} datasets):\n{resumen}\n→ {out}\nLinaje: bronze→silver→gold en lake/"}
    if "linaje" in lower:
        p = contexto.carpeta_central() / "linaje.json"
        if p.exists():
            return {"motor": NOMBRE, "salida": f"Linaje:\n{p.read_text(encoding='utf-8')[:3000]}"}
        return {"motor": NOMBRE, "salida": "No hay linaje aún. Ejecuta 'analiza las ventas' primero."}
    if "consolida" in lower and "lake" in lower:
        lake_base = Path("salida/lake")
        out_lines = []
        for capa in ["bronze","silver","gold"]:
            pp = lake_base / capa
            if pp.exists():
                files = list(pp.glob("*"))
                out_lines.append(f"{capa}: {len(files)} archivos → {pp}")
                for f in files[:2]:
                    out_lines.append(f"  - {f.name}")
            else:
                out_lines.append(f"{capa}: vacío")
        return {"motor": NOMBRE, "salida": "Data Lake por capas:\n" + "\n".join(out_lines)}
    if "identifica" in lower and "fuente" in lower:
        rel = contexto.identificar_fuentes_relevantes(peticion, top_n=5)
        import json as js
        return {"motor": NOMBRE, "salida": f"Fuentes relevantes (scoring):\n{js.dumps(rel, ensure_ascii=False, indent=2, default=str)}"}
    # 1. Si hay URL explícita, extraer de API
    url = _extraer_url(peticion)
    if url:
        try:
            # Detectar tipo por URL o petición
            is_json = "json" in peticion.lower() or url.endswith(".json") or "api" in url.lower()
            with httpx.Client(timeout=15, follow_redirects=True) as client:
                r = client.get(url)
                r.raise_for_status()
                # Guardar en bronze
                fname = url.split("/")[-1].split("?")[0] or "api_data.json"
                if not fname.endswith((".json", ".csv", ".txt")):
                    fname += ".json" if is_json else ".csv"
                dest = bronze / f"api_{datetime.now():%Y%m%d_%H%M%S}_{fname}"
                # Intentar guardar como binario/texto según contenido
                ctype = r.headers.get("content-type", "")
                if "json" in ctype or is_json:
                    try:
                        data = r.json()
                        dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                        # también convertir a CSV si es lista de dicts
                        if isinstance(data, list) and data and isinstance(data[0], dict):
                            import pandas as pd
                            df = pd.DataFrame(data)
                            csv_dest = dest.with_suffix(".csv")
                            df.to_csv(csv_dest, index=False, encoding="utf-8-sig")
                            return {"motor": NOMBRE, "salida": f"API extraída: {url}\n→ {dest} ({len(data)} registros)\n→ {csv_dest} (CSV)\nContent-Type: {ctype}\nBronze: {bronze}", "api_file": str(dest)}
                    except:
                        dest.write_bytes(r.content)
                else:
                    dest.write_bytes(r.content)
                return {"motor": NOMBRE, "salida": f"API extraída: {url}\n→ {dest} ({len(r.content)} bytes)\nContent-Type: {ctype}\nBronze: {bronze}", "api_file": str(dest)}
        except Exception as e:
            return {"motor": NOMBRE, "salida": f"Error extrayendo API {url}: {e}\nTip: usa una URL pública CSV/JSON. Ej: https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv"}

    # 2. Si no hay URL, intentar extraer de BD/archivos existentes
    inv = contexto.inventario()
    if archivo:
        # Consolidar archivo existente a bronze
        try:
            dest = bronze / archivo["ruta"].name
            # copiar a bronze como parquet si posible
            import pandas as pd
            ruta = str(archivo["ruta"])
            if ruta.endswith(".csv"):
                df = pd.read_csv(ruta, encoding="utf-8-sig", nrows=10000)
            elif ruta.endswith((".xlsx",".xls")):
                df = pd.read_excel(ruta, nrows=10000)
            elif ruta.endswith(".json"):
                df = pd.read_json(ruta)
            else:
                return {"motor": NOMBRE, "salida": f"Archivo {archivo['ruta'].name} no requiere conversión API, ya en {archivo['ruta']}"}
            # Guardar a bronze como parquet y csv
            parquet_dest = bronze / f"{archivo['ruta'].stem}.parquet"
            try:
                df.to_parquet(parquet_dest, index=False)
                parquet_msg = f"→ {parquet_dest} (parquet)"
            except:
                parquet_msg = "(parquet no disponible, falta pyarrow)"
            return {"motor": NOMBRE, "salida": f"Extracción BD/archivos: {archivo['ruta'].name} ({len(df)} filas)\n→ Bronze: {bronze}\n{parquet_msg}\nInventario: {len(inv)} fuentes"}
        except Exception as e:
            return {"motor": NOMBRE, "salida": f"Error consolidando {archivo['ruta'].name}: {e}"}

    # 3. Listar fuentes disponibles para extracción
    inv_det = contexto.catalogo_metadatos()
    resumen = "\n".join([f"  {a['dataset']} ({a['tipo']}, {a['tamano']})" for a in inv_det[:5]])
    return {"motor": NOMBRE, "salida": f"Fuentes disponibles para extracción ({len(inv)}):\n{resumen}\n\nUsa: 'extrae datos de https://api.example.com/data.json' o 'extrae {inv[0]['ruta'].name} a bronze'"}
