"""Pruebas de qualityops.cli (T08).

Se crea un proyecto mínimo con Git, una función y una prueba, y se verifica
que la CLI genere metrics.json con todas las secciones esperadas.
"""

import json
import subprocess

from qualityops.cli import main


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def crear_proyecto(tmp_path):
    repo = tmp_path / "proyecto"
    (repo / "app").mkdir(parents=True)
    (repo / "app" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "app" / "calc.py").write_text("def suma(a, b):\n    return a + b\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_calc.py").write_text(
        "from app.calc import suma\n\n\ndef test_suma():\n    assert suma(1, 2) == 3\n", encoding="utf-8")
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Prueba")
    git(repo, "config", "user.email", "prueba@example.com")
    git(repo, "config", "commit.gpgsign", "false")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "feat: proyecto inicial")
    return repo


def test_genera_metrics_json(tmp_path):
    repo = crear_proyecto(tmp_path)
    salida = tmp_path / "reports"
    assert main(["--repo", str(repo), "--salida", str(salida)]) == 0

    m = json.loads((salida / "metrics.json").read_text(encoding="utf-8"))
    assert m["repo"] == "proyecto"
    assert m["commit"]
    assert set(m["producto"]) == {"complejidad", "lineas", "cobertura", "densidad"}
    assert m["pruebas"]["aprobadas"] == 1
    assert m["producto"]["cobertura"]["global_pct"] == 100.0
    assert m["producto"]["complejidad"]["maximo"] == 1
    assert m["defectos"]["n_defectos"] == 0
    assert m["proceso"]["mttd"]["n"] == 0
    assert m["proyecto"]["desviacion"]["tareas_terminadas"] == 0
    assert m["estimacion"]["juicio_expertos"]["horas"] == 0
