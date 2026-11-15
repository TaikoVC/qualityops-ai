"""Pruebas de SISTEMA y de ACEPTACIÓN (T33).

Sistema: se ejecuta el producto completo, igual que el pipeline (métricas -> gate -> informe),
sobre un proyecto Python real creado con Git en una carpeta temporal.

Aceptación: cada prueba es un criterio de aceptación del usuario (un líder técnico que
integra QualityOps a su repositorio), escrito como Dado / Cuando / Entonces.
"""

import json

import pytest
from test_cli import crear_proyecto, git

from qualityops import cli, quality_gate, report

COMPLEJA = '''def clasificar(a, b, c, d, e, f):
    puntos = 0
    if a > 1000:
        puntos += 3
    elif a > 500:
        puntos += 2
    if b == "vip":
        puntos += 2
    if c:
        puntos += 1
    if d:
        puntos += 1
    if e and a > 100:
        puntos -= 1
    if f in ("sabado", "domingo"):
        puntos += 1
    if puntos > 5:
        return "alta"
    if puntos > 2:
        return "media"
    return "baja"
'''


PRUEBA_REGLAS = ('from app.reglas import clasificar\n\n\n'
                 'def test_clasificar():\n    assert clasificar(2000, "vip", 1, 1, 1, "sabado") == "alta"\n')


def agregar_funcion_compleja(repo, mensaje):
    """Agrega app/reglas.py (CC 11) con su prueba, para que solo la complejidad decida el gate."""
    (repo / "app" / "reglas.py").write_text(COMPLEJA, encoding="utf-8")
    (repo / "tests" / "test_reglas.py").write_text(PRUEBA_REGLAS, encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", mensaje)


def pipeline(repo, salida, monkeypatch):
    """Ejecuta los tres pasos del pipeline y devuelve (código del gate, informe, análisis)."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert cli.main(["--repo", str(repo), "--salida", str(salida)]) == 0
    codigo = quality_gate.main(["--metricas", str(salida / "metrics.json"), "--config", str(repo / "pyproject.toml")])
    report.main(["--metricas", str(salida / "metrics.json")])
    return (codigo, (salida / "quality_report.md").read_text(encoding="utf-8"),
            json.loads((salida / "ai_analysis.json").read_text(encoding="utf-8")))


@pytest.mark.sistema
def test_cp_sis_01_pipeline_completo_genera_todos_los_artefactos(tmp_path, monkeypatch):
    """CP-SIS-01: métricas -> gate -> informe generan metrics.json, gate.json, ai_analysis.json y el informe."""
    salida = tmp_path / "reports"
    codigo, informe, _ = pipeline(crear_proyecto(tmp_path), salida, monkeypatch)
    assert codigo == 0
    assert {p.name for p in salida.iterdir()} >= {"metrics.json", "gate.json", "ai_analysis.json", "quality_report.md"}
    assert informe.count("\n## ") >= 10          # informe de 12 secciones


@pytest.mark.aceptacion
def test_cp_ace_01_cambio_complejo_se_bloquea(tmp_path, monkeypatch):
    """CP-ACE-01: Dado un proyecto con una función de CC 11, cuando corre el pipeline,
    entonces el gate BLOQUEA (código 1) y el informe dictamina NO LIBERAR."""
    repo = crear_proyecto(tmp_path)
    agregar_funcion_compleja(repo, "feat: reglas complejas")
    codigo, informe, _ = pipeline(repo, tmp_path / "reports", monkeypatch)
    assert codigo == 1 and "NO LIBERAR" in informe


@pytest.mark.aceptacion
def test_cp_ace_02_umbral_propio_del_proyecto(tmp_path, monkeypatch):
    """CP-ACE-02: Dado el mismo proyecto con complejidad_maxima = 16 en su pyproject.toml,
    cuando corre el pipeline, entonces el gate APRUEBA: cada equipo define su política."""
    repo = crear_proyecto(tmp_path)
    (repo / "pyproject.toml").write_text("[tool.qualityops.umbrales]\ncomplejidad_maxima = 16\n", encoding="utf-8")
    agregar_funcion_compleja(repo, "feat: reglas complejas con umbral justificado")
    codigo, _, _ = pipeline(repo, tmp_path / "reports", monkeypatch)
    assert codigo == 0


@pytest.mark.aceptacion
def test_cp_ace_03_sin_llave_de_ia_el_informe_se_genera(tmp_path, monkeypatch):
    """CP-ACE-03: Dado un usuario sin llave de IA, cuando genera el informe,
    entonces lo obtiene completo con la interpretación por reglas (la IA es opcional)."""
    _, informe, analisis = pipeline(crear_proyecto(tmp_path), tmp_path / "reports", monkeypatch)
    assert analisis["fuente"] == "reglas" and "LIBERAR" in informe
