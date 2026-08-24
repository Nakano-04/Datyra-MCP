"""Motor de visualizacion: Power BI, Tableau y graficos generados por Python."""

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .. import contexto, herramientas

NOMBRE = "visualizacion"
DESCRIPCION = "Dashboards y reportes (Power BI / Tableau / matplotlib MOD)"


def disponible():
    return True


def _abrir_powerbi(archivo, info):
    peticion_pbix = contexto.filtro_tipo(contexto.escanear(), ["powerbi"])
    destino = peticion_pbix[0]["ruta"] if peticion_pbix else (archivo["ruta"] if archivo else None)
    if destino is None:
        return "No hay reportes .pbix en Recursos para abrir con Power BI."
    ruta_pbi = info["powerbi"]["ruta"]
    subprocess.Popen([ruta_pbi, str(destino)])
    return f"Abriendo Power BI Desktop con: {destino.name}"


def _abrir_tableau(info):
    peticion_tab = contexto.filtro_tipo(contexto.escanear(), ["tableau"])
    if not peticion_tab:
        return "No hay libros .twb/.twbx en Recursos para abrir con Tableau."
    ruta_tab = info["tableau"]["ruta"]
    args = [ruta_tab, str(peticion_tab[0]["ruta"])]
    if "tabcmd" in ruta_tab.lower():
        return "tabcmd detectado. Uso sugerido: tabcmd login -s <server> -u <user>"
    subprocess.Popen(args)
    return f"Abriendo Tableau con: {peticion_tab[0]['ruta'].name}"


def _graficos_matplotlib(archivo, salida_dir):
    if not contexto.hay_pandas():
        return "matplotlib/pandas no estan instalados: instala con: uv pip install pandas matplotlib seaborn"
    nombre = archivo["ruta"].name
    # por tipo: scripts en scripts/, cuadros en cuadros/
    try:
        is_real = Path(salida_dir).resolve() == contexto.carpeta_salida().resolve()
    except Exception:
        is_real = False
    script_dir = (contexto.carpeta_scripts() if is_real else Path(salida_dir))
    script_dir.mkdir(parents=True, exist_ok=True)
    script = script_dir / f"graficos_{datetime.now():%Y%m%d_%H%M%S}.py"
    codigo = '''import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

PALETA = ["#00D1FF", "#FF006E", "#8338EC", "#00F5A0", "#FFBE0B", "#FB5607"]
BG = "#0a0e14"
CARD = "#151a23"
GRID = "#21262d"
TEXT = "#e6e8eb"
MUTED = "#8b949e"

mpl.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": CARD,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": TEXT,
    "grid.color": GRID,
    "grid.alpha": 0.35,
    "axes.grid": True,
    "font.family": "sans-serif",
})
sns.set_palette(PALETA)

ruta = @RUTA@
if ruta.endswith((".csv", ".csv.gz")):
    df = pd.read_csv(ruta, encoding="utf-8-sig", low_memory=False)
elif ruta.endswith((".xlsx", ".xls")):
    df = pd.read_excel(ruta)
elif ruta.endswith(".json"):
    df = pd.read_json(ruta)
elif ruta.endswith(".parquet"):
    df = pd.read_parquet(ruta)
else:
    raise SystemExit("Formato no soportado")

numericas = df.select_dtypes(include="number").columns
categoricas = df.select_dtypes(include="object").columns
ruta_salida = r"@SALIDA@"
marca = "@TS@"

def estilo(fig, ax, title, subtitle=""):
    ax.set_title(title, fontsize=13, fontweight="800", color=TEXT, loc="left", pad=14)
    if subtitle:
        fig.text(0.125, 0.92, subtitle, fontsize=8, color=MUTED)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.yaxis.label.set_color(MUTED)
    ax.xaxis.label.set_color(MUTED)

if len(numericas) > 0:
    col = numericas[0]
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=180)
    sns.histplot(df[col].dropna(), bins=24, ax=ax, color=PALETA[0], edgecolor=BG, linewidth=1, alpha=0.95, kde=True, line_kws={"color": PALETA[1], "lw":1.5})
    estilo(fig, ax, f"Distribucion — {col}", f"n={df[col].dropna().shape[0]} · Mediador IA MOD")
    ax.set_xlabel(col, fontsize=9)
    ax.set_ylabel("Frecuencia", fontsize=9)
    plt.tight_layout()
    archivo1 = os.path.join(ruta_salida, f"histograma_{col}_{marca}.png")
    plt.savefig(archivo1, dpi=180, bbox_inches="tight")
    plt.close()
    print("Grafico 1:", archivo1)

if len(categoricas) > 0:
    col = categoricas[0]
    conteos = df[col].value_counts().head(12)
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=180)
    bars = ax.barh(conteos.index[::-1], conteos.values[::-1], color=PALETA, edgecolor=BG, height=0.62)
    ax.bar_label(bars, padding=6, fontsize=8, color=TEXT)
    estilo(fig, ax, f"Top categorias — {col}", "Barras horizontales · MOD dark")
    ax.set_xlabel("Conteo")
    plt.tight_layout()
    archivo2 = os.path.join(ruta_salida, f"barras_{col}_{marca}.png")
    plt.savefig(archivo2, dpi=180, bbox_inches="tight")
    plt.close()
    print("Grafico 2:", archivo2)

if len(numericas) >= 2:
    import warnings
    warnings.filterwarnings("ignore")
    cols = list(numericas[:6])
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(7.2, 6.2), dpi=180)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1, cbar_kws={"shrink":0.82}, linewidths=0.6, linecolor=BG, annot_kws={"fontsize":8}, ax=ax)
    estilo(fig, ax, "Matriz de correlacion", "Pearson · MOD")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=32, ha="right", fontsize=8)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
    plt.tight_layout()
    archivo3 = os.path.join(ruta_salida, f"correlacion_{marca}.png")
    plt.savefig(archivo3, dpi=180, bbox_inches="tight")
    plt.close()
    print("Grafico 3:", archivo3)

# Boxplot — distribución
try:
    if len(numericas) > 0:
        fig, ax = plt.subplots(figsize=(10, 4.5), dpi=180)
        if len(categoricas) > 0 and df[categoricas[0]].nunique() <= 12:
            cat = categoricas[0]
            top_cats = df[cat].value_counts().head(4).index
            df_box = df[df[cat].isin(top_cats)]
            sns.boxplot(data=df_box, x=cat, y=numericas[0], ax=ax, palette=PALETA, linewidth=1.2, fliersize=3)
            estilo(fig, ax, f"Boxplot — {numericas[0]} por {cat}", "Distribución y outliers · MOD")
        else:
            sns.boxplot(data=df[numericas[:4]], ax=ax, palette=PALETA, linewidth=1.2, fliersize=3)
            estilo(fig, ax, "Boxplots — variables numéricas", "Distribución · MOD")
        ax.tick_params(axis='x', rotation=18)
        plt.tight_layout()
        archivo_box = os.path.join(ruta_salida, f"boxplot_{marca}.png")
        plt.savefig(archivo_box, dpi=180, bbox_inches="tight")
        plt.close()
        print("Grafico boxplot:", archivo_box)
except Exception as e:
    pass

# Scatter matrix (pairplot)
try:
    if len(numericas) >= 2:
        import warnings
        warnings.filterwarnings("ignore")
        cols = list(numericas[:4])
        # limitar a 500 filas para rendimiento
        df_pair = df[cols].dropna().head(500)
        if len(df_pair) >= 10:
            g = sns.pairplot(df_pair, diag_kind="kde", plot_kws={"alpha":0.6, "s":18, "edgecolor": BG}, diag_kws={"color": PALETA[0]})
            g.fig.suptitle(f"Scatter Matrix — {', '.join(cols)}", fontsize=13, fontweight="800", color=TEXT, y=1.02)
            for ax in g.axes.flatten():
                if ax is not None:
                    ax.set_facecolor(CARD)
                    for spine in ax.spines.values():
                        spine.set_color(GRID)
            plt.tight_layout()
            archivo_scatter = os.path.join(ruta_salida, f"scatter_{marca}.png")
            g.savefig(archivo_scatter, dpi=180, bbox_inches="tight")
            plt.close('all')
            print("Grafico scatter:", archivo_scatter)
except Exception as e:
    pass

# Extra: serie temporal si hay fecha
try:
    fecha_col = next((c for c in df.columns if "fecha" in c.lower() or "date" in c.lower()), None)
    if fecha_col and len(numericas) > 0:
        df[fecha_col] = pd.to_datetime(df[fecha_col], errors="coerce")
        if df[fecha_col].notna().sum() > 2:
            ycol = [c for c in numericas if c != fecha_col][0] if len([c for c in numericas if c != fecha_col]) else numericas[0]
            tmp = df.dropna(subset=[fecha_col]).sort_values(fecha_col)
            fig, ax = plt.subplots(figsize=(10, 3.8), dpi=180)
            ax.plot(tmp[fecha_col], tmp[ycol], color=PALETA[0], lw=2.2, marker="o", markersize=4, markerfacecolor=PALETA[1], markeredgecolor=BG)
            ax.fill_between(tmp[fecha_col], tmp[ycol], alpha=0.12, color=PALETA[0])
            estilo(fig, ax, f"Evolucion — {ycol} en el tiempo", f"{fecha_col} vs {ycol}")
            ax.set_xlabel(fecha_col); ax.set_ylabel(ycol)
            fig.autofmt_xdate(rotation=28)
            plt.tight_layout()
            archivo4 = os.path.join(ruta_salida, f"serie_{ycol}_{marca}.png")
            plt.savefig(archivo4, dpi=180, bbox_inches="tight")
            plt.close()
            print("Grafico 4:", archivo4)
except Exception as e:
    pass

print("Analisis de @NOMBRE@ completado · MOD dark.")
'''
    # cuadros en hija, central para archivo único
    cuadros_dir = salida_dir / "cuadros"
    cuadros_dir.mkdir(parents=True, exist_ok=True)
    codigo = (
        codigo
        .replace("@RUTA@", repr(str(archivo["ruta"])))
        .replace("@SALIDA@", str(cuadros_dir))
        .replace("@TS@", datetime.now().strftime("%Y%m%d_%H%M%S"))
        .replace("@NOMBRE@", nombre)
    )
    script.write_text(codigo, encoding="utf-8")
    resultado = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=600, cwd=str(salida_dir),
        stdin=subprocess.DEVNULL,
    )
    salida = resultado.stdout or ""
    if resultado.returncode != 0:
        salida += "\n[ERROR]\n" + (resultado.stderr or "")
    return salida


def ejecutar(peticion, archivo, salida_dir, modo="analisis"):
    info = herramientas.detectar()
    p = peticion.lower()
    if "power" in p or "pbi" in p or "pbix" in p:
        if info["powerbi"]["disponible"]:
            return {"motor": NOMBRE, "salida": _abrir_powerbi(archivo, info)}
        return {"motor": NOMBRE, "salida": "Power BI Desktop no encontrado. Genero graficos MOD con matplotlib."}
    if "tableau" in p:
        if info["tableau"]["disponible"]:
            return {"motor": NOMBRE, "salida": _abrir_tableau(info)}
        return {"motor": NOMBRE, "salida": "Tableau no encontrado. Genero graficos MOD con matplotlib."}
    if archivo is None:
        return {"motor": NOMBRE, "salida": "No hay archivos de datos en Recursos para visualizar."}
    return {"motor": NOMBRE, "salida": _graficos_matplotlib(archivo, salida_dir)}
