"""Pruebas de qualityops.quality_gate (T10).

Se arma un metrics.json mínimo y se cambia un valor a la vez para comprobar
que cada criterio bloquea por sí solo.
"""

import json

from qualityops.quality_gate import evaluar, leer_umbrales, main, resumen_markdown

UMBRALES = {"cobertura_minima": 75.0, "complejidad_maxima": 10}


def metricas(aprobadas=5, fallidas=0, cobertura=80.0, cc_max=6):
    return {
        "pruebas": {"total": aprobadas + fallidas, "aprobadas": aprobadas, "fallidas": fallidas, "errores": 0},
        "producto": {"cobertura": {"global_pct": cobertura}, "complejidad": {"maximo": cc_max}},
    }


def fallas(resultado):
    return [c["criterio"] for c in resultado["criterios"] if not c["cumple"]]


def test_aprueba_si_todo_cumple():
    assert evaluar(metricas(), UMBRALES)["aprobado"] is True


def test_bloquea_por_prueba_fallida():
    r = evaluar(metricas(fallidas=1), UMBRALES)
    assert r["aprobado"] is False
    assert fallas(r) == ["Pruebas automatizadas sin fallas"]


def test_bloquea_por_cobertura_baja():
    r = evaluar(metricas(cobertura=74.99), UMBRALES)
    assert fallas(r) == ["Cobertura de código"]


def test_bloquea_por_complejidad_alta():
    r = evaluar(metricas(cc_max=11), UMBRALES)
    assert fallas(r) == ["Complejidad ciclomática máxima"]


def test_sin_pruebas_no_aprueba():
    r = evaluar(metricas(aprobadas=0, cobertura=None), UMBRALES)
    assert set(fallas(r)) == {"Pruebas automatizadas sin fallas", "Cobertura de código"}


def test_lee_umbrales_de_pyproject(tmp_path):
    config = tmp_path / "pyproject.toml"
    config.write_text("[tool.qualityops.umbrales]\ncobertura_minima = 90.0\n", encoding="utf-8")
    assert leer_umbrales(config) == {"cobertura_minima": 90.0, "complejidad_maxima": 10}
    assert leer_umbrales(tmp_path / "no_existe.toml") == UMBRALES


def test_codigo_de_salida_y_gate_json(tmp_path):
    ruta = tmp_path / "metrics.json"
    ruta.write_text(json.dumps(metricas(cobertura=50.0)), encoding="utf-8")
    assert main(["--metricas", str(ruta), "--config", str(tmp_path / "x.toml")]) == 1
    gate = json.loads((tmp_path / "gate.json").read_text(encoding="utf-8"))
    assert gate["aprobado"] is False


def test_resumen_markdown_para_github(tmp_path):
    ruta = tmp_path / "metrics.json"
    ruta.write_text(json.dumps(metricas()), encoding="utf-8")
    resumen = tmp_path / "resumen.md"
    assert main(["--metricas", str(ruta), "--config", str(tmp_path / "x.toml"), "--resumen", str(resumen)]) == 0
    texto = resumen.read_text(encoding="utf-8")
    assert "APROBADO" in texto
    assert texto.count("| ✅ |") == 3
    assert "BLOQUEADO" in resumen_markdown(evaluar(metricas(cc_max=20), UMBRALES), {})
