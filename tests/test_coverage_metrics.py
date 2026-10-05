"""Pruebas de qualityops.coverage_metrics (T05).

Se crea un proyecto pequeño con una prueba que ejecuta SOLO una de sus dos
funciones, así la cobertura esperada se conoce de antemano:

    app/calc.py tiene 4 líneas ejecutables:
        def suma      -> se ejecuta al importar
        return a + b  -> se ejecuta (la prueba llama a suma)
        def resta     -> se ejecuta al importar
        return a - b  -> NO se ejecuta
    Cobertura esperada = 3 / 4 = 75 %
"""

from qualityops.coverage_metrics import medir_cobertura

CALC = '''def suma(a, b):
    return a + b


def resta(a, b):
    return a - b
'''

PRUEBA = '''from app.calc import suma


def test_suma():
    assert suma(2, 3) == 5
'''


def crear_proyecto(tmp_path, prueba=PRUEBA):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "app" / "calc.py").write_text(CALC, encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_calc.py").write_text(prueba, encoding="utf-8")
    return tmp_path


def test_cobertura_conocida(tmp_path):
    resultado = medir_cobertura(crear_proyecto(tmp_path))
    cobertura = resultado["cobertura"]
    calc = next(a for a in cobertura["por_archivo"] if a["archivo"] == "app/calc.py")
    assert calc["lineas_ejecutables"] == 4
    assert calc["lineas_ejecutadas"] == 3
    assert calc["pct"] == 75.0
    # Las pruebas no cuentan como código de producto.
    assert all(not a["archivo"].startswith("tests/") for a in cobertura["por_archivo"])
    assert cobertura["global_pct"] == 75.0


def test_resultados_de_pruebas(tmp_path):
    resultado = medir_cobertura(crear_proyecto(tmp_path))
    assert resultado["pruebas"]["total"] == 1
    assert resultado["pruebas"]["aprobadas"] == 1
    assert resultado["pruebas"]["codigo_salida"] == 0


def test_detecta_prueba_fallida(tmp_path):
    prueba_mala = PRUEBA.replace("== 5", "== 6")
    resultado = medir_cobertura(crear_proyecto(tmp_path, prueba_mala))
    assert resultado["pruebas"]["fallidas"] == 1
    assert resultado["pruebas"]["aprobadas"] == 0
    assert resultado["pruebas"]["codigo_salida"] == 1
