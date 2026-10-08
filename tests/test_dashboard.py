"""Pruebas del dashboard (T18): funciones de datos + ejecución real de app.py
con el banco de pruebas de Streamlit (AppTest), sin abrir el navegador."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from qualityops.dashboard import (
    cargar_reportes,
    resumen_matriz,
    tabla_desviacion,
    tabla_estimacion,
)

APP = Path(__file__).resolve().parent.parent / "app.py"

METRICAS = {
    "repo": "demo", "commit": "abc1234", "generado": "2026-10-08T02:00:00-06:00",
    "pruebas": {"total": 2, "aprobadas": 2, "fallidas": 0, "errores": 0, "omitidas": 0},
    "producto": {
        "complejidad": {"promedio": 2.0, "maximo": 3, "funciones": [
            {"archivo": "a.py", "nombre": "f", "linea": 1, "cc": 3, "rango": "A"}]},
        "cobertura": {"global_pct": 90.0, "por_archivo": [{"archivo": "a.py", "pct": 90.0}]},
        "lineas": {"kloc": 0.1},
        "densidad": {"densidad_global": 10.0},
    },
    "proceso": {"mttd": {"mediana_h": 1.0, "n": 1}, "mttr": {"mediana_h": 0.5, "n": 1},
                "eficacia_pruebas": {"criticos": {"pct": None}}},
    "proyecto": {"eficacia_revision": {"pct": 100.0},
                 "desviacion": {"desviacion_pct": -50.0, "real_h": 1.0,
                                "por_modulo": {"cli": {"tareas": 1, "estimado_h": 2.0, "real_h": 1.0,
                                                       "desviacion_pct": -50.0}}},
                 "plazos": {"pct_a_tiempo": 100.0}},
    "estimacion": {"juicio_expertos": {"horas": 2.0}, "analoga": {"horas": 1.2},
                   "tres_puntos": {"horas": 2.2}, "puntos_de_funcion": {"horas": None}},
    "defectos": {"defectos": [{"fix": "a1b2c3d", "severidad": "menor", "fase": "revision"}]},
}

MATRIZ = """| ID | Requisito | Implementación | Evidencia | Criterio | Estado |
|---|---|---|---|---|---|
| DOC-01 | Portada | x | — | y | ✅ |
| MET-P1 | Complejidad | x | E07 | y | ✅ |
| MET-R1 | MTTD | x | E11 | y | 🟨 (calculado, n = 0) |
| EST-1 | Juicio | x | — | y | ⬜ |
"""


def test_resumen_de_la_matriz(tmp_path):
    ruta = tmp_path / "matriz.md"
    ruta.write_text(MATRIZ, encoding="utf-8")
    r = resumen_matriz(ruta)
    assert r["total"] == 4
    assert r["por_estado"]["Cumple"] == 2 and r["por_estado"]["En progreso"] == 1
    assert r["pct_cumple"] == 50.0
    assert resumen_matriz(tmp_path / "no_existe.md")["pct_cumple"] is None


def test_tablas_de_estimacion_y_desviacion():
    assert [f["horas"] for f in tabla_estimacion(METRICAS)] == [2.0, 1.2, 2.2, None, 1.0]
    assert tabla_desviacion(METRICAS)[0]["módulo"] == "cli"


def test_cargar_reportes_faltantes(tmp_path):
    assert cargar_reportes(tmp_path) == {"metrics": None, "gate": None, "ai_analysis": None}


def test_app_se_ejecuta_sin_errores(tmp_path, monkeypatch):
    (tmp_path / "metrics.json").write_text(json.dumps(METRICAS), encoding="utf-8")
    (tmp_path / "matriz.md").write_text(MATRIZ, encoding="utf-8")
    monkeypatch.setenv("QUALITYOPS_REPORTS", str(tmp_path))
    monkeypatch.setenv("QUALITYOPS_MATRIZ", str(tmp_path / "matriz.md"))
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception
    assert app.title[0].value == "QualityOps AI — Dashboard de calidad"


def test_app_sin_metricas_muestra_aviso(tmp_path, monkeypatch):
    monkeypatch.setenv("QUALITYOPS_REPORTS", str(tmp_path))
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception
    assert "python -m qualityops" in app.warning[0].value
