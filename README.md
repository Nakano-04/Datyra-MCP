# ◈ Datyra MCP — Mediador de Contexto IA

> **Autor: Nakano-04 — Mercenary Company “Mercenario del rojo”** · Software Engineer (Cybersecurity · AI · Systems · ERP) · Building security tools, AI systems, ERP modules & research · ✉️ nakano.04.2025@gmail.com · 🔗 https://github.com/Nakano-04

> Orquestador inteligente + **MCP Server real universal** que entiende lenguaje natural y enruta automáticamente: **Python · R · SQL · Spark · Jupyter · Power BI · Tableau** — compatible con **toda IA que hable MCP**.

![version](https://img.shields.io/badge/version-1.2.0_MCP-00D1FF?style=flat-square) ![python](https://img.shields.io/badge/python-3.10%2B-151a23?style=flat-square) ![mcp](https://img.shields.io/badge/MCP-1.29-FB5607?style=flat-square) ![style](https://img.shields.io/badge/style-MOD%20dark-FF006E?style=flat-square) ![license](https://img.shields.io/badge/license-Apache%202.0-8b949e?style=flat-square)

---

## 1. ¿Qué es?

Mediador CLI + HTML MOD + **MCP Server** que analiza cualquier archivo en `Recursos/` sin código. Tú dices:

```
"analiza las ventas"
"genera dashboard con gráficos"
"predice moroso con machine learning"
"haz analisis estadistico correlacion"
```

Para humanos → CLI. Para IAs → MCP tools (Claude, Devin, Codex, opencode, Cursor, Windsurf, Copilot, Gemini, ChatGPT y cualquier otra con MCP — protocolo abierto).

---

## 2. MCP Server — 10 herramientas (universal)

`mcp_server.py` (FastMCP, stdio + http) expone ciclo 1-6 completo — **universal para toda IA**:

| Herramienta | Descripción | Ejemplo |
|-------------|-------------|---------|
| `analyze_data` | Lenguaje natural → motor correcto | `analiza ciberseguridad` |
| `list_datasets` | Inventario `Recursos/` | — |
| `run_statistics` | Pearson/Spearman/Shapiro/IQR | `correlacion monto vs score` |
| `train_model` | RF regresión/clasificación + KMeans | `predice moroso` |
| `generate_dashboard` | 4 PNGs MOD 180dpi + HTML | `dashboard mineria` |
| `batch_process` | Todos los CSVs batch | `todos batch` |
| `profile_data` | Preview + describe | `finanzas_masivo.csv` |
| `query_sql` | SQL sobre sqlite/duckdb | `SELECT region, SUM(ingreso)...` |
| `get_tool_status` | Motores disponibles | — |
| `author_info` | Info Nakano-04 / Mercenary Company | — |

**Beneficios universales (cualquier IA con MCP):**

- **Devin:** análisis directo, reportes en workflow, logs/métricas auto
- **Claude:** stats complejos, dashboards, Spark masivo
- **Codex/opencode/Cursor/Windsurf/Copilot:** sugerencias por patrones, autocompletado, genera código DS
- **Gemini/ChatGPT/otras:** mismo `mcp.json` — protocolo estándar, no vendor lock-in

### Configuración universal

**Cualquier IA con MCP — Claude Desktop, opencode, Cursor, Windsurf, VS Code, Windsurf, Copilot, Gemini CLI, etc. (`%APPDATA%\Claude\claude_desktop_config.json` / `mcp.json` / `.cursor/mcp.json`):**

```json
{
  "mcpServers": {
    "datyra-mcp": {
      "command": "py",
      "args": ["C:/ruta/a/Mediador-Analisis-de-Datos/mcp_server.py"]
    }
  }
}
```

Ver `mcp.json` y `.opencode.json.example` incluidos.

```bash
py mcp_server.py              # stdio (Claude/opencode)
py -m mcp dev mcp_server.py   # inspector
```

Extra: `profile_data` + `query_sql` + `get_tool_status` como características plus.

---

## 3. Demo visual

**CLI con Rich:** tablas cyan/magenta, panels, spinner `dots12`.
**Informe HTML MOD** `salida/informe_*.html`: header gradiente `#0a0e14→#1a1033`, badges neon, galería base64.
**Gráficos MOD** `visual_motor.py`: histograma KDE, barras horizontales, heatmap anotado, serie temporal — `180dpi`, `seaborn`, fondo `#151a23`, paleta neon.

---

## 4. Arquitectura

```
mediador_ia.py → mediador/nucleo.py → clasificar() → MOTOR_POR_CLAVE → motor.ejecutar() → informe.py → HTML+TXT
mcp_server.py  →  FastMCP 9 tools  →  nucleo/contexto  (mismo core)

motores/: python_motor (1-6), r_motor, sql_motor, spark_motor, jupyter_motor, visual_motor MOD
contexto.py: rglob Recursos/, tipos, filas
herramientas.py: detección binarios
estilos.py: PALETA_MOD, CSS_MOD
```

Clasificación `nucleo.py:22` por keywords + `ORDEN_PRECEDENCIA`: `ml > big_data > sql > jupyter > visual > estadistica > r > python`.

---

## 5. Instalación

```bash
cd Mediador-Analisis-de-Datos
py -m venv .venv; .venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -r requirements-extra.txt  # jupyter/pyspark opcional
py mediador_ia.py -t; py mediador_ia.py -l
```

**requirements.txt:** `pandas, openpyxl, matplotlib, seaborn, scipy, scikit-learn, rich, jinja2, mcp, anyio, httpx, uvicorn, starlette`

---

## 6. Uso CLI

```bash
py mediador_ia.py "analiza las ventas"
py mediador_ia.py "genera dashboard de mineria con graficos"
py mediador_ia.py "predice moroso con machine learning en finanzas"
py mediador_ia.py "analisis estadistico correlacion"
py mediador_ia.py "analiza todos batch"  # batch
py mediador_ia.py                        # REPL: -l, -t, !cmd, salir
```

## 7. Datasets masivos incluidos (test)

| Dataset | Filas | Archivo |
|---------|-------|---------|
| Minería | 15k | `Recursos/mineria_masivo.csv` |
| Ciberseguridad | 20k | `Recursos/ciberseguridad_masivo.csv` |
| Finanzas | 20k | `Recursos/finanzas_masivo.csv` |
| Ventas | 25 | `Recursos/ventas_ejemplo.csv` |

Formatos soportados: `csv/tsv/csv.gz, xlsx/xls, json, parquet, db/sqlite/duckdb, ipynb, pbix, twb/twbx, r/rds, sql, pkl`. Prioridad `csv>excel>parquet>json` o match por nombre.

---

## 8. Motores

**Python (1-6):** duplicados, nulos %, IQR, `skew`, `train_test_split`, `RF 150` `MAE/RMSE/R2/CV`, `KMeans k=3/4/5`, `Pearson/Spearman/Shapiro`.
**Visual MOD:** KDE, barras h, heatmap, serie temporal.
**R:** dplyr, summary, cor, shapiro, kmeans. **SQL/Spark/Jupyter/PBI/Tableau:** detectan binario o fallback.

## 9. Salida `salida/`

`analisis_*.py, graficos_*.py, *.png (180dpi), informe_*.txt, informe_*.html (dark, base64)`

## 10. Ciencia de Datos 1-6 (sin transversal)

| Etapa | Cubierto |
|-------|----------|
| 1 Definición | Clasificación automática |
| 2 Recopilación | Inventario multi-formato |
| 3 Limpieza | duplicados, nulos, IQR, datetime |
| 4 EDA | describe+skew+cor+4 gráficos MOD |
| 5 Modelado | RF+KMeans+Pearson/Spearman/Shapiro |
| 6 Evaluación | métricas, train/test, HTML |

> Sin bloque transversal (gobernanza/ética) a petición.

## 11. Roadmap

- [x] CLI Rich + HTML MOD + 180dpi
- [x] Limpieza IQR + ML evaluado + KMeans + Shapiro
- [x] Batch + MCP Server 9 tools
- [ ] Streamlit drag&drop
- [ ] ARIMA/Prophet

## 12. Autor

**Nakano-04 — Mercenary Company “Mercenario del rojo”**
Software Engineer (Cybersecurity · AI · Systems · ERP)
Building security tools, AI systems, ERP modules & research
📧 nakano.04.2025@gmail.com · 🔗 https://github.com/Nakano-04

## 13. Licencia

Apache 2.0 — ver `LICENSE`.

Hecho con `pandas · seaborn · rich · jinja2 · mcp` estilo MOD dark — Datyra MCP by Nakano-04.
