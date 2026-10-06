"""Pruebas de qualityops.defects (T06).

Se construye un repositorio Git pequeño con fechas controladas, para que
el MTTD, el MTTR y la fase de cada defecto se conozcan de antemano:

  10:00  feat  dividir() con un error (* en vez de /)              [main]
  13:00  fix   corrige dividir (Severidad: critica, Detectado-en: pruebas)  [rama PR #1]
  14:30  merge PR #1                                  -> MTTD 3 h, MTTR 1.5 h
  14:45  fix(docs) solo toca README                   -> fix EXCLUIDO
  15:00  feat  restar() con error                     [rama PR #2]
  15:30  fix   corrige restar (sin trailers)          [misma rama PR #2]
  16:00  merge PR #2                                  -> fase "revision" automática
  17:00  feat  doble() con error                      [directo a main]
  18:00  tag v0.1.0 (salida a producción)
  19:00  fix   corrige doble (sin trailers, directo a main) -> "produccion", sin MTTR
"""

import os
import subprocess

import pytest

from qualityops.defects import es_codigo_de_producto, minar_defectos


def git(repo, *args, fecha=None):
    """Ejecuta git en `repo`; si se da `fecha`, la usa como fecha del commit."""
    entorno = dict(os.environ)
    if fecha:
        entorno.update(GIT_AUTHOR_DATE=fecha, GIT_COMMITTER_DATE=fecha)
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, env=entorno)


def escribir(repo, ruta, texto):
    archivo = repo / ruta
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(texto, encoding="utf-8")


def commit(repo, mensaje, fecha):
    git(repo, "add", ".")
    git(repo, "commit", "-m", mensaje, fecha=fecha)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path
    git(r, "init", "-b", "main")
    git(r, "config", "user.name", "Prueba")
    git(r, "config", "user.email", "prueba@example.com")
    git(r, "config", "commit.gpgsign", "false")
    git(r, "config", "tag.gpgsign", "false")
    d = "2026-01-01T{}:00+00:00"

    escribir(r, "app/calc.py", "def dividir(a, b):\n    return a * b\n")
    escribir(r, "README.md", "Proyeto\n")
    commit(r, "feat: agrega dividir", d.format("10:00"))

    git(r, "switch", "-c", "pr1")
    escribir(r, "app/calc.py", "def dividir(a, b):\n    return a / b\n")
    commit(r, "fix(calc): dividir usaba multiplicación\n\nSeveridad: Crítica\nDetectado-en: pruebas",
           d.format("13:00"))
    git(r, "switch", "main")
    git(r, "merge", "--no-ff", "pr1", "-m", "Merge pull request #1", fecha=d.format("14:30"))

    escribir(r, "README.md", "Proyecto\n")
    commit(r, "fix(docs): corrige typo del README", d.format("14:45"))

    git(r, "switch", "-c", "pr2")
    escribir(r, "app/calc.py", "def dividir(a, b):\n    return a / b\n\n\ndef restar(a, b):\n    return a + b\n")
    commit(r, "feat: agrega restar", d.format("15:00"))
    escribir(r, "app/calc.py", "def dividir(a, b):\n    return a / b\n\n\ndef restar(a, b):\n    return a - b\n")
    commit(r, "fix(calc): restar sumaba", d.format("15:30"))
    git(r, "switch", "main")
    git(r, "merge", "--no-ff", "pr2", "-m", "Merge pull request #2", fecha=d.format("16:00"))

    escribir(r, "app/doble.py", "def doble(x):\n    return x + x + 1\n")
    commit(r, "feat: agrega doble", d.format("17:00"))
    git(r, "tag", "-a", "v0.1.0", "-m", "v0.1.0", fecha=d.format("18:00"))
    escribir(r, "app/doble.py", "def doble(x):\n    return x + x\n")
    commit(r, "fix: doble sumaba 1 de más", d.format("19:00"))
    return r


def por_asunto(resultado, texto):
    return next(d for d in resultado["defectos"] if texto in d["asunto"])


def test_conteos_generales(repo):
    r = minar_defectos(repo)
    assert r["n_defectos"] == 3
    assert r["n_merges"] == 2
    assert r["tags_release"] == ["v0.1.0"]
    assert [e["asunto"] for e in r["fixes_excluidos"]] == ["fix(docs): corrige typo del README"]


def test_defecto_con_trailers(repo):
    d = por_asunto(minar_defectos(repo), "dividir")
    assert d["mttd_horas"] == 3.0          # 10:00 -> 13:00
    assert d["mttr_horas"] == 1.5          # 13:00 -> merge 14:30
    assert d["severidad"] == "critica"     # "Crítica" normalizado
    assert (d["fase"], d["fuente_fase"]) == ("pruebas", "trailer")


def test_defecto_atrapado_en_revision(repo):
    d = por_asunto(minar_defectos(repo), "restar")
    assert d["mttd_horas"] == 0.5
    assert d["mttr_horas"] == 0.5
    assert (d["fase"], d["fuente_fase"]) == ("revision", "automatica")
    assert d["severidad"] == "sin_clasificar"


def test_defecto_escapado_a_produccion(repo):
    d = por_asunto(minar_defectos(repo), "doble")
    assert d["mttd_horas"] == 2.0
    assert d["mttr_horas"] is None         # directo a main: sin PR, sin MTTR
    assert (d["fase"], d["fuente_fase"]) == ("produccion", "automatica")


def test_regla_de_codigo_de_producto():
    assert es_codigo_de_producto("qualityops/defects.py")
    assert not es_codigo_de_producto("tests/test_defects.py")
    assert not es_codigo_de_producto("README.md")
    assert not es_codigo_de_producto(".venv/lib/x.py")
