import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mediador import contexto, herramientas, nucleo
from mediador.motores import python_motor, visual_motor

def test_inventario():
    inv = contexto.inventario()
    assert len(inv) >= 4
    assert any("ventas" in a["ruta"].name for a in inv)
    assert any("finanzas" in a["ruta"].name for a in inv)

def test_tipos_y_formato():
    assert contexto.formatear_bytes(1500) == "1.5 KB"
    assert contexto._tipo_de(Path("a.csv")) == "csv"

def test_clasificar():
    assert nucleo.clasificar("predice ingreso con machine learning")[0]=="machine_learning"
    assert nucleo.clasificar("analisis estadistico correlacion")[0]=="estadistica"
    assert nucleo.clasificar("genera dashboard con graficos")[0]=="visualizacion"
    assert nucleo.clasificar("consulta sql")[0]=="sql"
    assert nucleo.clasificar("analiza las ventas")[0]=="python"

def test_herramientas():
    h = herramientas.detectar()
    assert h["python"]["disponible"] is True
    assert h["sql"]["disponible"] is True

def test_python_motor_analisis(tmp_path):
    inv = contexto.inventario()
    arch = next(a for a in inv if "ventas" in a["ruta"].name)
    res = python_motor.ejecutar("analiza ventas", arch, tmp_path, modo="analisis")
    assert "Dimensiones" in res["salida"]
    assert "LIMPIEZA" in res["salida"]
    assert Path(res["script"]).exists()

def test_python_motor_ml(tmp_path):
    inv = contexto.inventario()
    arch = next(a for a in inv if "finanzas" in a["ruta"].name)
    res = python_motor.ejecutar("predice moroso", arch, tmp_path, modo="ml")
    assert "MODELADO" in res["salida"]
    assert "Accuracy" in res["salida"] or "MAE" in res["salida"]

def test_python_motor_stats(tmp_path):
    inv = contexto.inventario()
    arch = next(a for a in inv if "ventas" in a["ruta"].name)
    res = python_motor.ejecutar("analisis estadistico", arch, tmp_path, modo="stats")
    assert "Pearson" in res["salida"]
    assert "Shapiro" in res["salida"]

def test_visual_motor(tmp_path):
    inv = contexto.inventario()
    arch = next(a for a in inv if "mineria" in a["ruta"].name)
    res = visual_motor.ejecutar("genera dashboard", arch, tmp_path)
    assert "Grafico" in res["salida"]
    pngs = list(tmp_path.glob("*.png")) + list((tmp_path / "cuadros").glob("*.png"))
    assert len(pngs) >= 3

def test_nucleo_ejecutar(tmp_path):
    res = nucleo.ejecutar_peticion("analiza las ventas", salida_dir=str(tmp_path))
    assert res["motor"] in ["python","visualizacion"]
    assert len(list(tmp_path.glob("informe_*.html"))) == 1
    assert len(list(tmp_path.glob("informe_*.txt"))) == 1

def test_mcp_tools():
    import mcp_server
    inv_json = mcp_server.list_datasets()
    inv = json.loads(inv_json)
    assert len(inv) >= 4
    prof = mcp_server.profile_data("finanzas_masivo.csv", 2)
    assert "finanzas_masivo" in prof
    status = mcp_server.get_tool_status()
    assert "python" in status.lower()
    author = json.loads(mcp_server.author_info())
    assert author["github"] == "https://github.com/Nakano-04"

def test_masivos_escala():
    for name, expected_min in [("ciberseguridad_masivo.csv",20000), ("finanzas_masivo.csv",20000), ("mineria_masivo.csv",15000)]:
        inv = contexto.inventario()
        arch = next(a for a in inv if name==a["ruta"].name)
        p = arch["ruta"]
        assert p.exists()
        assert p.stat().st_size > 500_000
        assert arch["filas"] >= expected_min
