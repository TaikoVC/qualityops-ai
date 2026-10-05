"""Métrica de PRODUCTO: cobertura de código + resultado de las pruebas.

Requisito que cubre: MET-P2 (cobertura de código). Además deja listos los
datos de pruebas (aprobadas, fallidas...) que usará el informe de calidad.

Cómo funciona:
  1. Ejecuta pytest con pytest-cov sobre el proyecto indicado (--repo),
     en un proceso aparte, como lo haría el pipeline de CI.
  2. Lee dos archivos que generan esas herramientas:
       - coverage.json  -> líneas ejecutables y líneas ejecutadas por archivo
       - junit.xml      -> cuántas pruebas pasaron, fallaron o se omitieron
  3. Solo cuenta los archivos de PRODUCTO (los mismos que mide la
     complejidad), para que ambas métricas hablen del mismo código.

Fórmula: cobertura = líneas ejecutadas / líneas ejecutables × 100

Uso rápido desde la terminal:
    python -m qualityops.coverage_metrics --repo .
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from qualityops.product_metrics import encontrar_archivos_python

# Tiempo máximo para la ejecución de las pruebas (segundos).
TIEMPO_MAXIMO = 600


def _ejecutar_pytest(repo: Path, carpeta_temporal: Path) -> int:
    """Corre pytest con cobertura en `repo` y devuelve su código de salida.

    Los archivos de resultados se escriben en una carpeta temporal para no
    ensuciar el proyecto analizado.
    """
    comando = [
        sys.executable, "-m", "pytest", "-q",
        "-p", "no:cacheprovider",                      # no crear .pytest_cache en el proyecto
        "--cov=.",                                      # medir todo; luego se filtra
        f"--cov-report=json:{carpeta_temporal / 'coverage.json'}",
        f"--junitxml={carpeta_temporal / 'junit.xml'}",
    ]
    entorno = dict(os.environ, COVERAGE_FILE=str(carpeta_temporal / ".coverage"))
    # check=False: una prueba fallida NO es un error de la herramienta; se reporta.
    proceso = subprocess.run(comando, cwd=repo, env=entorno, capture_output=True,
                             text=True, timeout=TIEMPO_MAXIMO, check=False)
    return proceso.returncode


def leer_resultados_pruebas(ruta_junit: Path, codigo_salida: int) -> dict:
    """Extrae del reporte JUnit cuántas pruebas pasaron, fallaron, etc."""
    resumen = {"total": 0, "aprobadas": 0, "fallidas": 0, "errores": 0,
               "omitidas": 0, "codigo_salida": codigo_salida}
    if not ruta_junit.exists():
        return resumen
    raiz = ET.parse(ruta_junit).getroot()
    # El archivo puede tener <testsuites> con varios <testsuite> o uno solo.
    suites = raiz.findall("testsuite") if raiz.tag == "testsuites" else [raiz]
    for suite in suites:
        resumen["total"] += int(suite.get("tests", 0))
        resumen["fallidas"] += int(suite.get("failures", 0))
        resumen["errores"] += int(suite.get("errors", 0))
        resumen["omitidas"] += int(suite.get("skipped", 0))
    resumen["aprobadas"] = (resumen["total"] - resumen["fallidas"]
                            - resumen["errores"] - resumen["omitidas"])
    return resumen


def leer_cobertura(ruta_json: Path, repo: Path) -> dict:
    """Calcula la cobertura global y por archivo SOLO del código de producto."""
    repo = Path(repo).resolve()
    if not ruta_json.exists():
        return {"global_pct": None, "lineas_ejecutables": 0, "lineas_ejecutadas": 0, "por_archivo": []}

    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    producto = {a.resolve() for a in encontrar_archivos_python(repo)}

    por_archivo = []
    for nombre, info in datos.get("files", {}).items():
        # coverage.json guarda rutas relativas a la carpeta del proyecto
        # (en Windows con "\"); se normalizan para compararlas.
        ruta = (repo / nombre).resolve()
        if ruta not in producto:
            continue
        resumen = info["summary"]
        por_archivo.append({
            "archivo": ruta.relative_to(repo).as_posix(),
            "lineas_ejecutables": resumen["num_statements"],
            "lineas_ejecutadas": resumen["covered_lines"],
            "pct": _porcentaje(resumen["covered_lines"], resumen["num_statements"]),
        })
    por_archivo.sort(key=lambda a: a["archivo"])

    ejecutables = sum(a["lineas_ejecutables"] for a in por_archivo)
    ejecutadas = sum(a["lineas_ejecutadas"] for a in por_archivo)
    return {
        "global_pct": _porcentaje(ejecutadas, ejecutables),
        "lineas_ejecutables": ejecutables,
        "lineas_ejecutadas": ejecutadas,
        "por_archivo": por_archivo,
    }


def _porcentaje(parte: int, total: int) -> float | None:
    """parte / total × 100 con 2 decimales; None si no hay nada que medir."""
    return round(100 * parte / total, 2) if total else None


def medir_cobertura(repo: Path) -> dict:
    """Ejecuta las pruebas del proyecto y devuelve pruebas + cobertura."""
    repo = Path(repo).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        codigo = _ejecutar_pytest(repo, tmp)
        return {
            "pruebas": leer_resultados_pruebas(tmp / "junit.xml", codigo),
            "cobertura": leer_cobertura(tmp / "coverage.json", repo),
        }


def _imprimir(repo: Path) -> None:
    """Muestra los resultados en la terminal (evidencia E06)."""
    r = medir_cobertura(repo)
    p, c = r["pruebas"], r["cobertura"]
    print(f"\nPruebas — {Path(repo).resolve()}")
    print(f"Total {p['total']} · aprobadas {p['aprobadas']} · fallidas {p['fallidas']} · "
          f"errores {p['errores']} · omitidas {p['omitidas']} · código de salida {p['codigo_salida']}")
    print(f"\n{'Ejecutables':>11} {'Ejecutadas':>10} {'%':>7}  Archivo")
    for a in c["por_archivo"]:
        print(f"{a['lineas_ejecutables']:>11} {a['lineas_ejecutadas']:>10} {a['pct']!s:>7}  {a['archivo']}")
    print(f"\nCobertura global del código de producto: {c['global_pct']} % "
          f"({c['lineas_ejecutadas']} de {c['lineas_ejecutables']} líneas)\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pruebas y cobertura de un proyecto Python.")
    parser.add_argument("--repo", default=".", help="Ruta del proyecto a analizar (por defecto, la carpeta actual).")
    _imprimir(Path(parser.parse_args().repo))
