"""CLI principal de QualityOps AI: ejecuta todas las métricas y genera metrics.json.

Requisito que cubre: PRG-06 (ejecución del código y salida visible).
El archivo metrics.json es el "contrato" que leen el quality gate, el informe
de calidad, el AI Advisor y el dashboard: ninguno vuelve a calcular nada.

Uso:
    python -m qualityops --repo . --salida reports
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

from qualityops import __version__
from qualityops.coverage_metrics import medir_cobertura
from qualityops.defects import minar_defectos
from qualityops.density import calcular_densidad
from qualityops.process_metrics import calcular_proceso
from qualityops.product_metrics import analizar_complejidad, contar_lineas
from qualityops.project_metrics import calcular_proyecto


def _commit_actual(repo: Path) -> str | None:
    """Hash corto del commit analizado (None si la carpeta no es un repositorio)."""
    proceso = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=False)
    return proceso.stdout.strip() or None


def recolectar_metricas(repo: Path) -> dict:
    """Ejecuta cada módulo una sola vez y arma el diccionario de resultados."""
    repo = Path(repo).resolve()
    lineas = contar_lineas(repo)
    defectos = minar_defectos(repo)          # se mina una vez y se reutiliza
    pruebas_y_cobertura = medir_cobertura(repo)
    return {
        "herramienta": {"nombre": "QualityOps AI", "version": __version__},
        "generado": datetime.now().astimezone().isoformat(timespec="seconds"),
        "repo": repo.name,
        "commit": _commit_actual(repo),
        "producto": {
            "complejidad": analizar_complejidad(repo),
            "lineas": lineas,
            "cobertura": pruebas_y_cobertura["cobertura"],
            "densidad": calcular_densidad(defectos, lineas),
        },
        "pruebas": pruebas_y_cobertura["pruebas"],
        "proceso": calcular_proceso(defectos),
        "proyecto": calcular_proyecto(defectos, repo),
        "defectos": defectos,
    }


def guardar(metricas: dict, carpeta: Path) -> Path:
    """Escribe metrics.json (UTF-8, legible) en `carpeta` y devuelve su ruta."""
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / "metrics.json"
    ruta.write_text(json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta


def _resumen(m: dict) -> str:
    """Texto corto para la terminal con los valores principales."""
    p, prod = m["pruebas"], m["producto"]
    return "\n".join([
        f"QualityOps AI {m['herramienta']['version']} — {m['repo']} @ {m['commit']}",
        f"  Pruebas:       {p['aprobadas']}/{p['total']} aprobadas · {p['fallidas']} fallidas · {p['errores']} errores",
        f"  Cobertura:     {prod['cobertura']['global_pct']} %",
        f"  Complejidad:   promedio {prod['complejidad']['promedio']} · máximo {prod['complejidad']['maximo']}",
        f"  Tamaño:        {prod['lineas']['kloc']} KLOC en {prod['lineas']['n_archivos']} archivos",
        f"  Defectos:      {m['defectos']['n_defectos']} · densidad {prod['densidad']['densidad_global']} def/KLOC",
        (f"  MTTD / MTTR:   {m['proceso']['mttd']['promedio_h']} h / {m['proceso']['mttr']['promedio_h']} h "
         f"(n = {m['proceso']['mttd']['n']} / {m['proceso']['mttr']['n']})"),
        (f"  Desviación:    {m['proyecto']['desviacion']['desviacion_pct']} % "
         f"({m['proyecto']['desviacion']['tareas_terminadas']} tareas terminadas)"),
        f"  Plazos:        {m['proyecto']['plazos']['pct_a_tiempo']} % a tiempo",
    ])


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada. Devuelve 0 si pudo generar las métricas."""
    parser = argparse.ArgumentParser(prog="qualityops", description="Métricas de calidad de un proyecto Python con Git.")
    parser.add_argument("--repo", default=".", help="Proyecto a analizar (por defecto, la carpeta actual).")
    parser.add_argument("--salida", default="reports", help="Carpeta donde se guarda metrics.json.")
    args = parser.parse_args(argv)

    metricas = recolectar_metricas(Path(args.repo))
    ruta = guardar(metricas, Path(args.salida))
    print(_resumen(metricas))
    print(f"\nResultados guardados en {ruta}")
    return 0
