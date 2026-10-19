"""Nucleo del mediador: clasifica la peticion y la enruta al motor adecuado."""

import sys
from datetime import datetime
from pathlib import Path

from . import contexto, herramientas
from .motores import api_motor, jupyter_motor, python_motor, r_motor, spark_motor, sql_motor, streaming_motor, visual_motor

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

PATRONES = {
    "api": [
        "api", "rest", "endpoint", "extrae", "extraer", "httpx", "json api", "fetch", "url http",
        "extraccion", "fuente externa", "open api", "identifica", "fuentes relevantes", "catalogo",
    ],
    "streaming": [
        "streaming", "tiempo real", "real-time", "realtime", "kafka", "kinesis", "stream", "evento", "sensor",
        "cola", "broker", "colecta",
    ],
    "lake": [
        "lake", "data lake", "datalake", "bronze", "silver", "gold", "warehouse", "consolida", "consolidar", "delta", "metadatos", "linaje",
    ],
    "machine_learning": [
        "machine learning", "ml ", " modelo", "entrenar", "clasificacion", "prediccion",
        "scikit", "sklearn", "cluster", "kmeans", "prediga", "predice", "predecir",
    ],
    "estadistica": [
        "estadistic", "desviacion", "media ", "mediana", "correlacion", "histograma",
        "normalidad", "prueba t", "anova", "test", "analisis estadistico",
    ],
    "big_data": [
        "big data", "spark", "distribuido", "gran escala", "millones de",
        "masivo", "parquet",
    ],
    "sql": [
        "sql", "consulta", "base de datos", "tabla", "select", "join", "database",
        "sqlite", "query", "duckdb",
    ],
    "jupyter": ["jupyter", "notebook", "cuaderno", "ipynb"],
    "visualizacion": [
        "dashboard", "visualiz", "reporte", "powerbi", "power bi", "tableau",
        "grafico", "gráfico", "chart", "pbi", "grafica", "gráfica",
    ],
    "r": ["lenguaje r", "script r", "rstudio", "motor r"],
    "python": [
        "analiza", "analizar", "analisis", "análisis", "limpia", "limpiar",
        "transforma", "transformar", "resume", "resumir", "ventas", "ingresos",
        "gastos", "finanzas", "excel", "csv", "xlsx", "explora", "explorar",
        "agrupa", "agrupar", "automatiza", "automatizar",
    ],
}

MOTOR_POR_CLAVE = {
    "api": api_motor,
    "streaming": streaming_motor,
    "lake": api_motor,  # lake usa api_motor para consolidación
    "machine_learning": python_motor,
    "estadistica": r_motor,
    "big_data": spark_motor,
    "sql": sql_motor,
    "jupyter": jupyter_motor,
    "visualizacion": visual_motor,
    "r": r_motor,
    "python": python_motor,
}

ORDEN_PRECEDENCIA = [
    "api",
    "streaming",
    "lake",
    "machine_learning",
    "big_data",
    "sql",
    "jupyter",
    "visualizacion",
    "estadistica",
    "r",
    "python",
]


def clasificar(peticion):
    texto = " " + peticion.lower() + " "
    puntajes = {clave: sum(1 for k in claves if k in texto) for clave, claves in PATRONES.items()}
    for clave in ORDEN_PRECEDENCIA:
        if puntajes[clave] > 0:
            razones = [k.strip() for k in PATRONES[clave] if k.strip() in texto]
            return clave, razones[:3]
    return "python", ["peticion generica: analisis exploratorio por defecto"]


def _elegir_archivo(peticion, inventario):
    terminos = []
    for palabra in peticion.lower().replace("-", " ").replace("_", " ").split():
        if len(palabra) > 3 and palabra not in ("analiza", "analizar", "analisis", "genera", "crear", "dame", "quiero", "reporte", "graficos", "visualiza"):
            terminos.append(palabra)
    return contexto.elegir_dataset(inventario, terminos)


def _elegir_todos(peticion, inventario):
    if "todos" in peticion.lower() or "batch" in peticion.lower() or "todo" in peticion.lower():
        return inventario
    return None


def listar_contexto():
    inventario = contexto.inventario()
    if HAS_RICH and sys.stdout.isatty():
        t = Table(title="◈ CONTEXTO DE DATOS - Recursos/", box=box.ROUNDED, border_style="cyan", header_style="bold cyan", title_style="bold white")
        t.add_column("Tipo", style="bold magenta", justify="center")
        t.add_column("Tamaño", style="dim", justify="right")
        t.add_column("Filas", justify="right")
        t.add_column("Archivo", style="white")
        if not inventario:
            t.add_row("-", "-", "-", "[dim]Coloca archivos en Recursos/[/dim]")
        for a in inventario:
            filas = str(a['filas']) if a["filas"] else "-"
            t.add_row(a['tipo'], contexto.formatear_bytes(a['tamano']), filas, a['ruta'].name)
        with console.capture() as cap:
            console.print(t)
        return cap.get()
    lineas = ["CONTEXTO DE DATOS (Recursos):"]
    if not inventario:
        lineas.append("  No se encontraron archivos de datos. Colocalos en Recursos/")
    for a in inventario:
        filas = f"  filas~{a['filas']}" if a["filas"] else "  filas: -"
        lineas.append(f"  {a['tipo']:<9} {contexto.formatear_bytes(a['tamano']):>7}  {filas:<14} {a['ruta'].name}")
    return "\n".join(lineas)


def listar_herramientas():
    if HAS_RICH and sys.stdout.isatty():
        info = herramientas.detectar()
        t = Table(title="◆ HERRAMIENTAS DETECTADAS", box=box.ROUNDED, border_style="magenta", header_style="bold magenta")
        t.add_column("Motor", style="bold white")
        t.add_column("Estado", justify="center")
        t.add_column("Ruta", style="dim", overflow="fold")
        t.add_column("Detalle", style="cyan")
        for n, d in info.items():
            estado = "[green]● OK[/green]" if d["disponible"] else "[red]○ no[/red]"
            t.add_row(n, estado, d["ruta"] or "-", d["detalle"])
        with console.capture() as cap:
            console.print(t)
        return cap.get()
    return "HERRAMIENTAS DISPONIBLES EN EL SISTEMA:\n" + herramientas.resumen()


def ejecutar_peticion(peticion, salida_dir=None, silent=False):
    carpeta = Path(salida_dir) if salida_dir else contexto.carpeta_salida()
    carpeta.mkdir(parents=True, exist_ok=True)
    inventario = contexto.inventario()
    linea_contexto = listar_contexto()
    clave, razones = clasificar(peticion)
    motor = MOTOR_POR_CLAVE[clave]
    if not motor.disponible() and motor.NOMBRE != "python":
        razones.append(f"motor {motor.NOMBRE} no disponible; fallback a python")
        clave = "estadistica" if clave == "estadistica" else "python"
        motor = python_motor
    lote = _elegir_todos(peticion, inventario)
    if lote:
        for arch in lote:
            if not silent:
                print(f"\n>>> BATCH: {arch['ruta'].name}")
            ejecutar_peticion(f"{peticion} {arch['ruta'].stem}", salida_dir=str(carpeta), silent=silent)
        return {"motor": "batch", "salida": f"Batch completado: {len(lote)} archivos"}
    archivo = _elegir_archivo(peticion, inventario)
    modo = "ml" if clave == "machine_learning" else ("stats" if clave == "estadistica" else "analisis")
    lineas = [linea_contexto, "", "=" * 60]
    lineas.append(f"PETICION: {peticion}")
    lineas.append(f"INTENCION DETECTADA: {clave}")
    lineas.append(f"MOTOR SELECCIONADO: {motor.NOMBRE} - {motor.DESCRIPCION}")
    lineas.append(f"RAZONES: {', '.join(razones)}")
    if archivo:
        lineas.append(f"ARCHIVO DE TRABAJO: {archivo['ruta'].name}")
    else:
        lineas.append("ARCHIVO DE TRABAJO: ninguno (solo contexto)")
    lineas.append("=" * 60)
    if not silent:
        if HAS_RICH and sys.stdout.isatty():
            console.print(Panel(linea_contexto, title="◈ MEDIADOR_IA", border_style="cyan", box=box.ROUNDED))
            grid = Table.grid(padding=(0,2))
            grid.add_column(style="bold cyan")
            grid.add_column(style="white")
            grid.add_row("Petición:", f"[white]{peticion}[/white]")
            grid.add_row("Intención:", f"[magenta]{clave}[/magenta]  [dim]{', '.join(razones)}[/dim]")
            grid.add_row("Motor:", f"[green]{motor.NOMBRE}[/green] - {motor.DESCRIPCION}")
            grid.add_row("Archivo:", f"[yellow]{archivo['ruta'].name if archivo else '—'}[/yellow]")
            console.print(Panel(grid, title="⚡ Ejecución", border_style="magenta", box=box.ROUNDED))
            console.print(f"[dim]Ejecutando motor '{motor.NOMBRE}'...[/dim]")
        else:
            print("\n".join(lineas))
            print()
            print(f"Ejecutando motor '{motor.NOMBRE}'...")
            print()
    if HAS_RICH and sys.stdout.isatty() and not silent:
        with console.status(f"[cyan]Procesando con {motor.NOMBRE}...", spinner="dots12"):
            resultado = motor.ejecutar(peticion, archivo, carpeta, modo=modo)
    else:
        resultado = motor.ejecutar(peticion, archivo, carpeta, modo=modo)
    informe = "\n".join(lineas) + "\n\n=== RESULTADO ===\n\n" + resultado["salida"]
    if resultado.get("script"):
        informe += f"\n\nScript generado: {resultado['script']}"
    if resultado.get("comando"):
        informe += f"\nComando: {' '.join(map(str, resultado['comando']))}"
    # por tipo: txt en txt/, html en html/, central para archivo único
    is_real = False
    try:
        is_real = carpeta.resolve() == contexto.carpeta_salida().resolve()
    except Exception:
        pass
    txt_dir = (contexto.carpeta_txt() if is_real else carpeta)
    txt_dir.mkdir(parents=True, exist_ok=True)
    archivo_informe = txt_dir / f"informe_{datetime.now():%Y%m%d_%H%M%S}.txt"
    archivo_informe.write_text(informe, encoding="utf-8")
    try:
        from .informe import generar_informe_html
        stats = []
        for a in inventario[:4]:
            stats.append({"k": a['ruta'].name[:14], "v": f"{a['filas'] or '-'} filas"})
        html_path = generar_informe_html(carpeta, peticion, clave, f"{motor.NOMBRE} - {motor.DESCRIPCION}", razones, archivo, resultado["salida"], "\n".join(lineas), script=resultado.get("script"), stats=stats)
    except Exception as e:
        html_path = None
    # Data Lake por capas (bronze/silver/gold) y catálogo metadatos/linaje
    try:
        if is_real and archivo:
            bronze = contexto.carpeta_lake("bronze")
            # bronze: copia raw si no existe
            import shutil
            bronze_dest = bronze / archivo["ruta"].name
            if not bronze_dest.exists():
                try:
                    shutil.copy2(str(archivo["ruta"]), str(bronze_dest))
                except: pass
        if is_real:
            try:
                import json
                catalogo = contexto.catalogo_metadatos()
                central = contexto.carpeta_central()
                (central / "catalogo_metadatos.json").write_text(json.dumps(catalogo, ensure_ascii=False, indent=2), encoding="utf-8")
                # también en raíz salida para compatibilidad
                (contexto.carpeta_salida() / "catalogo_metadatos.json").write_text(json.dumps(catalogo, ensure_ascii=False, indent=2), encoding="utf-8")
                linaje_path = central / "linaje.json"
                linaje = {
                    "ultima_peticion": peticion,
                    "motor": motor.NOMBRE,
                    "archivo": str(archivo["ruta"]) if archivo else None,
                    "timestamp": datetime.now().isoformat(),
                    "salida": str(archivo_informe),
                    "html": str(html_path) if html_path else None,
                    "lake": {
                        "bronze": str(contexto.carpeta_lake("bronze")),
                        "silver": str(contexto.carpeta_lake("silver")),
                        "gold": str(contexto.carpeta_lake("gold"))
                    }
                }
                linaje_path.write_text(json.dumps(linaje, ensure_ascii=False, indent=2), encoding="utf-8")
                (contexto.carpeta_salida() / "linaje.json").write_text(json.dumps(linaje, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass
    except Exception:
        pass
    if not silent:
        if HAS_RICH and sys.stdout.isatty():
            console.print(Panel(resultado["salida"][:4000], title="✔ Resultado", border_style="green", box=box.ROUNDED))
            console.print(f"[dim]TXT:[/dim] {archivo_informe}")
            if html_path:
                console.print(f"[bold cyan]HTML MOD:[/bold cyan] {html_path}  [dim](abre en navegador)[/dim]")
        else:
            print(resultado["salida"])
            print()
            print(f"Informe guardado en: {archivo_informe}")
            if html_path:
                print(f"Informe HTML MOD: {html_path}")
    return resultado


def repl():
    try:
        import readline
    except ImportError:
        pass
    if HAS_RICH and sys.stdout.isatty():
        console.print(Panel("[bold cyan]◈ MEDIADOR_IA[/bold cyan]  [dim]v1.0 - escribe tu petición en lenguaje natural[/dim]\n[dim]Comandos:[/dim] [cyan]-l[/cyan] contexto  [cyan]-t[/cyan] herramientas  [cyan]salir[/cyan]  [cyan]!comando[/cyan]", border_style="cyan", box=box.ROUNDED, title="⚡ Mediador de Contexto"))
    else:
        print("Mediador de Contexto IA (enter 'salir' o Ctrl+C para terminar)")
    while True:
        try:
            peticion = input("mediador-ia> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not peticion:
            continue
        if peticion.lower() in ("salir", "exit", "quit"):
            break
        if peticion.startswith("!"):
            import subprocess
            subprocess.run(peticion[1:], shell=True)
            continue
        if peticion in ("--listar", "-l"):
            print(listar_contexto())
            continue
        if peticion in ("--herramientas", "-t"):
            print(listar_herramientas())
            continue
        try:
            ejecutar_peticion(peticion)
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()