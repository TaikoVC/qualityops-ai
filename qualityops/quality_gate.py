"""Quality gate: decide si una versión cumple los criterios mínimos de calidad.

Requisito que cubre: CAL-07 (enfoque preventivo). En el pipeline de CI este
módulo termina con código de salida 1 cuando algún criterio no se cumple, y
eso BLOQUEA la integración del cambio antes de que llegue a la rama principal.

Criterios (los umbrales se leen de [tool.qualityops.umbrales] en pyproject.toml):
  1. Hay pruebas automatizadas y ninguna falla ni da error.
  2. Cobertura global >= cobertura_minima.
  3. Complejidad ciclomática máxima <= complejidad_maxima.
Si un dato falta (por ejemplo, no hay pruebas y la cobertura es None), el
criterio NO se cumple: sin evidencia no se aprueba.

Uso (después de generar metrics.json con `python -m qualityops`):
    python -m qualityops.quality_gate --metricas reports/metrics.json

En GitHub Actions se agrega `--resumen "$GITHUB_STEP_SUMMARY"` para que el
dictamen aparezca como tabla en la página de cada ejecución del pipeline.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

# Valores por defecto si el proyecto analizado no define los suyos.
UMBRALES_POR_DEFECTO = {"cobertura_minima": 75.0, "complejidad_maxima": 10}


def leer_umbrales(ruta_pyproject: Path) -> dict:
    """Lee los umbrales de pyproject.toml; si no existen, usa los por defecto."""
    umbrales = dict(UMBRALES_POR_DEFECTO)
    if ruta_pyproject.exists():
        config = tomllib.loads(ruta_pyproject.read_text(encoding="utf-8"))
        umbrales.update(config.get("tool", {}).get("qualityops", {}).get("umbrales", {}))
    return umbrales


def _criterio(nombre: str, valor, umbral: str, cumple: bool) -> dict:
    return {"criterio": nombre, "valor": valor, "umbral": umbral, "cumple": bool(cumple)}


def evaluar(metricas: dict, umbrales: dict) -> dict:
    """Compara las métricas contra los umbrales y devuelve el dictamen."""
    pruebas = metricas["pruebas"]
    cobertura = metricas["producto"]["cobertura"]["global_pct"]
    complejidad = metricas["producto"]["complejidad"]["maximo"]

    criterios = [
        _criterio("Pruebas automatizadas sin fallas",
                  f"{pruebas['aprobadas']}/{pruebas['total']} aprobadas",
                  "total > 0 y 0 fallidas/errores",
                  pruebas["total"] > 0 and pruebas["fallidas"] == 0 and pruebas["errores"] == 0),
        _criterio("Cobertura de código", cobertura,
                  f">= {umbrales['cobertura_minima']} %",
                  cobertura is not None and cobertura >= umbrales["cobertura_minima"]),
        _criterio("Complejidad ciclomática máxima", complejidad,
                  f"<= {umbrales['complejidad_maxima']}",
                  complejidad is not None and complejidad <= umbrales["complejidad_maxima"]),
    ]
    return {"aprobado": all(c["cumple"] for c in criterios),
            "umbrales": umbrales, "criterios": criterios}


def resumen_markdown(resultado: dict, metricas: dict) -> str:
    """Tabla Markdown con el dictamen (se muestra en el resumen de GitHub Actions)."""
    dictamen = "✅ APROBADO" if resultado["aprobado"] else "❌ BLOQUEADO"
    filas = [f"| {'✅' if c['cumple'] else '❌'} | {c['criterio']} | {c['valor']} | {c['umbral']} |"
             for c in resultado["criterios"]]
    return "\n".join([
        f"## Quality gate — {dictamen}",
        "",
        f"Repositorio `{metricas.get('repo')}` · commit `{metricas.get('commit')}`",
        "",
        "| | Criterio | Valor | Umbral |",
        "|---|---|---|---|",
        *filas,
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    """Imprime el resultado y devuelve 0 (aprobado) o 1 (bloqueado)."""
    parser = argparse.ArgumentParser(description="Quality gate de QualityOps AI.")
    parser.add_argument("--metricas", default="reports/metrics.json", help="Ruta de metrics.json.")
    parser.add_argument("--config", default="pyproject.toml", help="Ruta de pyproject.toml con los umbrales.")
    parser.add_argument("--resumen", help="Archivo Markdown donde AGREGAR la tabla del dictamen (p. ej. $GITHUB_STEP_SUMMARY).")
    args = parser.parse_args(argv)

    ruta_metricas = Path(args.metricas)
    metricas = json.loads(ruta_metricas.read_text(encoding="utf-8"))
    resultado = evaluar(metricas, leer_umbrales(Path(args.config)))

    print("\nQuality gate — QualityOps AI")
    for c in resultado["criterios"]:
        marca = "OK  " if c["cumple"] else "FALLA"
        print(f"  [{marca}] {c['criterio']}: {c['valor']} (umbral {c['umbral']})")
    print(f"\nDictamen: {'APROBADO' if resultado['aprobado'] else 'BLOQUEADO'}\n")

    # Se guarda junto a metrics.json para que el informe de calidad lo use.
    (ruta_metricas.parent / "gate.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.resumen:
        with open(args.resumen, "a", encoding="utf-8") as archivo:
            archivo.write(resumen_markdown(resultado, metricas))
    return 0 if resultado["aprobado"] else 1


if __name__ == "__main__":
    sys.exit(main())
