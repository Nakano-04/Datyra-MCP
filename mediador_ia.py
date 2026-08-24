"""Punto de entrada del Mediador de Contexto IA.

Uso:
  python mediador_ia.py "analiza las ventas"
  python mediador_ia.py -l
  python mediador_ia.py -t
  python mediador_ia.py
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mediador import nucleo, __version__


def _configurar_consola():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main():
    _configurar_consola()
    parser = argparse.ArgumentParser(
        prog="mediador-ia",
        description="Mediador de contexto IA: analiza datos con Python, R, SQL, Jupyter, Spark, Power BI y Tableau.",
    )
    parser.add_argument("peticion", nargs="?", help="Peticion en lenguaje natural, p. ej. 'analiza las ventas del mes'")
    parser.add_argument("-l", "--listar", action="store_true", help="Listar el contexto de datos de Recursos/")
    parser.add_argument("-t", "--herramientas", action="store_true", help="Mostrar herramientas disponibles en el sistema")
    parser.add_argument("-o", "--salida", default=None, help="Carpeta de salida para scripts e informes (default: salida/)")
    parser.add_argument("-v", "--version", action="version", version=f"mediador-ia {__version__}")
    args = parser.parse_args()

    if args.listar:
        print(nucleo.listar_contexto())
        return
    if args.herramientas:
        print(nucleo.listar_herramientas())
        return
    if args.peticion:
        nucleo.ejecutar_peticion(args.peticion, salida_dir=args.salida)
        return
    nucleo.repl()


if __name__ == "__main__":
    main()