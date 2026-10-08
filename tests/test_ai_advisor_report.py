"""Pruebas de qualityops.ai_advisor (T17) y qualityops.report (T12).

Se usa un metrics.json mínimo y completo construido a mano, con valores
coherentes entre sí (cobertura 80 = 8/10, KLOC 0.5, densidad 2.0 = 1/0.5).
"""

import json

from qualityops.ai_advisor import analizar, verificar_coherencia
from qualityops.report import dictamen, generar_informe, main


def metricas(n_defectos=1):
    defectos = [{"severidad": "critica", "fase": "pruebas", "mttd_horas": 3.0, "mttr_horas": 1.5}][:n_defectos]
    return {
        "herramienta": {"nombre": "QualityOps AI", "version": "0.1.0"},
        "generado": "2026-10-08T01:00:00-06:00", "repo": "demo", "commit": "abc1234",
        "pruebas": {"total": 4, "aprobadas": 4, "fallidas": 0, "errores": 0, "omitidas": 0},
        "producto": {
            "complejidad": {"promedio": 3.0, "maximo": 6, "n_funciones": 5, "en_bajo_riesgo": 5},
            "cobertura": {"global_pct": 80.0, "lineas_ejecutadas": 8, "lineas_ejecutables": 10,
                          "por_archivo": [{"archivo": "a.py", "pct": 50.0}]},
            "lineas": {"sloc": 500, "kloc": 0.5, "n_archivos": 2},
            "densidad": {"n_defectos": n_defectos, "densidad_global": round(n_defectos / 0.5, 2)},
        },
        "proceso": {"n_defectos": n_defectos,
                    "mttd": {"n": n_defectos, "mediana_h": 3.0 if n_defectos else None},
                    "mttr": {"n": n_defectos, "mediana_h": 1.5 if n_defectos else None},
                    "eficacia_pruebas": {"criticos": {"pct": 100.0 if n_defectos else None,
                                                      "con_fase_conocida": n_defectos}}},
        "proyecto": {"eficacia_revision": {"pct": 0.0},
                     "desviacion": {"desviacion_pct": -40.0, "real_h": 3.0, "estimado_h": 5.0, "tareas_terminadas": 4},
                     "plazos": {"pct_a_tiempo": 50.0, "tarde": ["T2", "T3"]}},
        "estimacion": {"juicio_expertos": {"horas": 5.0}, "analoga": {"horas": 4.0},
                       "tres_puntos": {"horas": 5.5, "sigma_h": 0.5},
                       "puntos_de_funcion": {"horas": 4.2, "pf_sin_ajustar": 97}},
        "defectos": {"n_defectos": n_defectos, "defectos": defectos},
    }


GATE_OK = {"aprobado": True, "criterios": [{"cumple": True, "criterio": "Cobertura", "valor": 80.0, "umbral": ">= 75"}]}


def test_verificaciones_de_coherencia():
    assert all(v["ok"] for v in verificar_coherencia(metricas()))
    malo = metricas()
    malo["producto"]["cobertura"]["global_pct"] = 95.0        # no coincide con 8/10
    assert not all(v["ok"] for v in verificar_coherencia(malo))


def test_ruta_por_reglas_sin_llm():
    r = analizar(metricas(), GATE_OK)
    assert r["fuente"] == "reglas"
    nombres = [i["metrica"] for i in r["interpretaciones"]]
    assert "Cobertura de código" in nombres and "Cumplimiento de plazos" in nombres
    assert any("a.py" in i["texto"] for i in r["interpretaciones"])   # archivo con < 60 %


def test_ruta_llm_y_respaldo_si_falla():
    r = analizar(metricas(), GATE_OK, cliente=lambda prompt: "Interpretación de prueba")
    assert r["fuente"] == "llm" and "NO las recalcules" in r["prompt"]

    def falla(prompt):
        raise RuntimeError("sin conexión")

    r = analizar(metricas(), GATE_OK, cliente=falla)
    assert r["fuente"] == "reglas" and "RuntimeError" in r["error_llm"]


def test_dictamen():
    assert dictamen(None, analizar(metricas())) == "NO LIBERAR"
    assert dictamen({"aprobado": False}, analizar(metricas())) == "NO LIBERAR"
    assert dictamen(GATE_OK, analizar(metricas(n_defectos=1))) == "LIBERAR"
    assert dictamen(GATE_OK, analizar(metricas(n_defectos=0))) == "LIBERAR CON CONDICIONES"


def test_informe_tiene_todas_las_secciones():
    texto = generar_informe(metricas(), GATE_OK, analizar(metricas(), GATE_OK))
    for seccion in ("1. Identificación", "2. Resumen y dictamen", "3. Resultados de las pruebas",
                    "4. Criterios de salida", "5. Métricas de producto", "6. Métricas de proceso",
                    "7. Métricas de proyecto", "8. Estimación", "9. Defectos por severidad",
                    "10. Interpretación", "11. Verificaciones", "12. Aprobación"):
        assert seccion in texto


def test_main_escribe_archivos(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    (tmp_path / "metrics.json").write_text(json.dumps(metricas()), encoding="utf-8")
    (tmp_path / "gate.json").write_text(json.dumps(GATE_OK), encoding="utf-8")
    assert main(["--metricas", str(tmp_path / "metrics.json")]) == 0
    assert "Dictamen: LIBERAR" in (tmp_path / "quality_report.md").read_text(encoding="utf-8")
    assert json.loads((tmp_path / "ai_analysis.json").read_text(encoding="utf-8"))["fuente"] == "reglas"


def test_nombres_de_archivo_no_se_rompen_en_markdown():
    # Defecto real encontrado al revisar el PR #38: "__main__.py" se mostraba como **main.py**.
    m = metricas()
    m["producto"]["cobertura"]["por_archivo"] = [{"archivo": "qualityops/__main__.py", "pct": 0.0}]
    texto = generar_informe(m, GATE_OK, analizar(m, GATE_OK))
    assert "`qualityops/__main__.py`" in texto
