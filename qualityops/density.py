"""Métrica de PRODUCTO: densidad de defectos.

Requisito que cubre: MET-P3 (densidad de defectos).

Fórmula: densidad = defectos / KLOC   (defectos por cada mil líneas de código)
  - Defectos: los de producto que encuentra la minería SZZ (qualityops.defects).
  - KLOC: líneas de código fuente de producto / 1000 (qualityops.product_metrics).

Por archivo: un defecto cuenta en CADA archivo de producto que su fix modificó
(un fix que toca dos archivos suma 1 en cada uno). El total global usa los
defectos únicos, así que no se duplica.

Uso rápido desde la terminal:
    python -m qualityops.density --repo .
"""

from __future__ import annotations

import argparse
from pathlib import Path

from qualityops.defects import minar_defectos
from qualityops.product_metrics import contar_lineas


def _densidad(defectos: int, sloc: int) -> float | None:
    """defectos / (sloc / 1000) con 2 decimales; None si no hay código que medir."""
    return round(defectos / (sloc / 1000), 2) if sloc else None


def calcular_densidad(defectos: dict, lineas: dict) -> dict:
    """Combina el resultado de la minería y el conteo de líneas.

    `defectos` es la salida de minar_defectos(); `lineas`, la de contar_lineas().
    Con 0 defectos y código existente la densidad es 0.0 (es un dato real,
    no un valor inventado); sin código, es None.
    """
    por_archivo = []
    for archivo in lineas["por_archivo"]:
        n = sum(1 for d in defectos["defectos"] if archivo["archivo"] in d["archivos"])
        por_archivo.append({
            "archivo": archivo["archivo"],
            "defectos": n,
            "sloc": archivo["sloc"],
            "densidad": _densidad(n, archivo["sloc"]),
        })
    return {
        "n_defectos": defectos["n_defectos"],
        "sloc": lineas["sloc"],
        "kloc": lineas["kloc"],
        "densidad_global": _densidad(defectos["n_defectos"], lineas["sloc"]),
        "por_archivo": por_archivo,
    }


def medir_densidad(repo) -> dict:
    """Mina los defectos y cuenta las líneas del proyecto en `repo`."""
    return calcular_densidad(minar_defectos(repo), contar_lineas(Path(repo)))


def _imprimir(repo) -> None:
    """Muestra la densidad en la terminal (evidencia de MET-P3)."""
    r = medir_densidad(repo)
    print(f"\nDensidad de defectos — {Path(repo).resolve()}")
    print(f"{'Defectos':>8} {'SLOC':>6} {'Def/KLOC':>9}  Archivo")
    for a in r["por_archivo"]:
        print(f"{a['defectos']:>8} {a['sloc']:>6} {a['densidad']!s:>9}  {a['archivo']}")
    print(f"\nGlobal: {r['n_defectos']} defectos / {r['kloc']} KLOC = {r['densidad_global']} defectos/KLOC\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Densidad de defectos de un proyecto Python con Git.")
    parser.add_argument("--repo", default=".", help="Ruta del repositorio a analizar.")
    _imprimir(parser.parse_args().repo)
