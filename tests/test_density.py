"""Pruebas de qualityops.density (T07).

Se usan datos de entrada fijos (sin git), así el resultado esperado
se calcula a mano:
  a.py: 300 SLOC, tocado por 2 defectos -> 2 / 0.3 = 6.67 def/KLOC
  b.py: 200 SLOC, tocado por 1 defecto  -> 1 / 0.2 = 5.0  def/KLOC
  Global: 2 defectos únicos / 0.5 KLOC = 4.0 def/KLOC
"""

from qualityops.density import calcular_densidad

LINEAS = {
    "sloc": 500,
    "kloc": 0.5,
    "por_archivo": [
        {"archivo": "a.py", "sloc": 300},
        {"archivo": "b.py", "sloc": 200},
    ],
}


def test_densidad_global_y_por_archivo():
    defectos = {"n_defectos": 2, "defectos": [{"archivos": ["a.py"]}, {"archivos": ["a.py", "b.py"]}]}
    r = calcular_densidad(defectos, LINEAS)
    assert r["densidad_global"] == 4.0
    por = {a["archivo"]: a for a in r["por_archivo"]}
    assert (por["a.py"]["defectos"], por["a.py"]["densidad"]) == (2, 6.67)
    assert (por["b.py"]["defectos"], por["b.py"]["densidad"]) == (1, 5.0)


def test_cero_defectos_es_dato_real():
    r = calcular_densidad({"n_defectos": 0, "defectos": []}, LINEAS)
    assert r["densidad_global"] == 0.0


def test_sin_codigo_no_inventa_valores():
    vacio = {"sloc": 0, "kloc": 0.0, "por_archivo": []}
    r = calcular_densidad({"n_defectos": 0, "defectos": []}, vacio)
    assert r["densidad_global"] is None
