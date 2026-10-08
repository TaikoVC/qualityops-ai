"""Pruebas de qualityops.product_metrics (T04).

Cada prueba crea un proyecto pequeño en una carpeta temporal (tmp_path)
con complejidad y número de líneas CONOCIDOS, y comprueba que el cálculo
dé exactamente esos valores.
"""

from qualityops.product_metrics import (
    analizar_complejidad,
    contar_lineas,
    encontrar_archivos_python,
)

# Código de ejemplo con valores conocidos:
#   simple()   -> CC 1 (sin decisiones)
#   decide()   -> CC 4 (if + and + elif)
#   Caja.mide  -> CC 3 (for + if)
CODIGO = '''# comentario
def simple():
    return 1


def decide(x):
    if x > 0 and x < 10:
        return 1
    elif x == 0:
        return 0
    return -1


class Caja:
    def mide(self, y):
        for i in range(y):
            if i:
                pass
        return y
'''


def crear_proyecto(tmp_path):
    """Arma un proyecto falso: 1 archivo de producto + archivos que deben ignorarse."""
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "logica.py").write_text(CODIGO, encoding="utf-8")
    # Estos NO son código de producto y no deben contarse:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_logica.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "lib.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    # Herramientas de documentación (p. ej. docs/reporte/graficas.py) tampoco son producto (D20).
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "graficas.py").write_text("def dibujar():\n    return 1\n", encoding="utf-8")
    return tmp_path


def test_solo_encuentra_codigo_de_producto(tmp_path):
    repo = crear_proyecto(tmp_path)
    archivos = [a.relative_to(repo).as_posix() for a in encontrar_archivos_python(repo)]
    assert archivos == ["app/logica.py"]


def test_complejidad_por_funcion(tmp_path):
    repo = crear_proyecto(tmp_path)
    resultado = analizar_complejidad(repo)
    cc = {f["nombre"]: f["cc"] for f in resultado["funciones"]}
    # La clase no aparece como bloque propio; su método sí, con prefijo de clase.
    assert cc == {"simple": 1, "decide": 4, "Caja.mide": 3}


def test_estadisticas_de_complejidad(tmp_path):
    repo = crear_proyecto(tmp_path)
    resultado = analizar_complejidad(repo)
    assert resultado["n_funciones"] == 3
    assert resultado["promedio"] == round((1 + 4 + 3) / 3, 2)
    assert resultado["mediana"] == 3
    assert resultado["maximo"] == 4
    assert resultado["en_bajo_riesgo"] == 3


def test_proyecto_sin_codigo_no_inventa_valores(tmp_path):
    resultado = analizar_complejidad(tmp_path)
    assert resultado["n_funciones"] == 0
    assert resultado["promedio"] is None
    assert resultado["maximo"] is None


def test_conteo_de_lineas(tmp_path):
    repo = crear_proyecto(tmp_path)
    resultado = contar_lineas(repo)
    assert resultado["n_archivos"] == 1
    assert resultado["loc"] == 19
    assert resultado["sloc"] == 14
    assert resultado["comentarios"] == 1
    assert resultado["blancos"] == 4
    assert resultado["kloc"] == 0.014
