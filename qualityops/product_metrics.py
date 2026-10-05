"""Métricas de PRODUCTO: complejidad ciclomática y tamaño (LOC / KLOC).

Requisitos que cubre: MET-P1 (complejidad ciclomática) y la base de MET-P3
(KLOC para la densidad de defectos).

Fuente de los datos: la biblioteca Radon, que analiza el código fuente real.
  - Complejidad ciclomática (McCabe, 1976): número de caminos independientes
    de una función = 1 + puntos de decisión (if, for, while, and, or, except...).
  - LOC: Radon "raw" separa líneas de código (SLOC), comentarios y líneas en blanco.

Uso rápido desde la terminal (muestra una tabla con los resultados):
    python -m qualityops.product_metrics --repo .
"""

from __future__ import annotations

import argparse
import statistics
from pathlib import Path

from radon.complexity import cc_rank, cc_visit
from radon.raw import analyze

# --------------------------------------------------------------------------
# Configuración: qué carpetas y archivos NO son código de producto.
# Se excluyen entornos virtuales, cachés, compilados y las pruebas
# (las pruebas se miden aparte con la cobertura, no con la complejidad).
# --------------------------------------------------------------------------
CARPETAS_EXCLUIDAS = {
    ".git", ".venv", "venv", "env", "__pycache__", "build", "dist",
    "node_modules", "site-packages", ".pytest_cache", ".ruff_cache",
    "tests", "test",
}

# Umbral de referencia de McCabe (1976): CC <= 10 se considera bajo riesgo.
UMBRAL_MCCABE = 10


def es_archivo_de_prueba(ruta: Path) -> bool:
    """True si el archivo es de pruebas (test_*.py, *_test.py o conftest.py)."""
    nombre = ruta.name
    return nombre.startswith("test_") or nombre.endswith("_test.py") or nombre == "conftest.py"


def encontrar_archivos_python(repo: Path) -> list[Path]:
    """Devuelve, ordenados, los archivos .py de producto dentro de `repo`.

    Recorre todas las subcarpetas, saltando las de CARPETAS_EXCLUIDAS y los
    archivos de prueba. El orden fijo hace que los resultados sean reproducibles.
    """
    repo = Path(repo)
    archivos = []
    for ruta in repo.rglob("*.py"):
        partes_relativas = ruta.relative_to(repo).parts
        if any(parte in CARPETAS_EXCLUIDAS for parte in partes_relativas[:-1]):
            continue
        if es_archivo_de_prueba(ruta):
            continue
        archivos.append(ruta)
    return sorted(archivos)


def _leer(ruta: Path) -> str:
    """Lee un archivo como UTF-8 (formato estándar del código Python)."""
    return ruta.read_text(encoding="utf-8")


def analizar_complejidad(repo: Path) -> dict:
    """Calcula la complejidad ciclomática de cada función y método del proyecto.

    Solo se cuentan funciones y métodos: Radon también reporta un bloque por
    clase (la suma de sus métodos), pero contarlo duplicaría esos métodos.

    Devuelve un diccionario con:
      - funciones: lista con archivo, nombre, línea, cc y rango de Radon (A-F)
      - n_funciones, promedio, mediana, maximo
      - en_bajo_riesgo: cuántas funciones tienen CC <= UMBRAL_MCCABE
    """
    repo = Path(repo)
    funciones = []
    for archivo in encontrar_archivos_python(repo):
        for bloque in cc_visit(_leer(archivo)):
            # Los bloques de clase tienen el atributo "methods"; se omiten.
            if hasattr(bloque, "methods"):
                continue
            nombre = f"{bloque.classname}.{bloque.name}" if bloque.classname else bloque.name
            funciones.append({
                "archivo": archivo.relative_to(repo).as_posix(),
                "nombre": nombre,
                "linea": bloque.lineno,
                "cc": bloque.complexity,
                "rango": cc_rank(bloque.complexity),
            })

    resultado = {"funciones": funciones, "umbral_mccabe": UMBRAL_MCCABE}
    resultado.update(_estadisticas([f["cc"] for f in funciones]))
    return resultado


def _estadisticas(valores: list[int]) -> dict:
    """Resumen estadístico de una lista de complejidades.

    Si no hay funciones, las estadísticas quedan en None: no se inventa un cero.
    """
    if not valores:
        return {"n_funciones": 0, "promedio": None, "mediana": None,
                "maximo": None, "en_bajo_riesgo": 0}
    return {
        "n_funciones": len(valores),
        "promedio": round(statistics.mean(valores), 2),
        "mediana": statistics.median(valores),
        "maximo": max(valores),
        "en_bajo_riesgo": sum(1 for v in valores if v <= UMBRAL_MCCABE),
    }


def contar_lineas(repo: Path) -> dict:
    """Cuenta las líneas del código de producto, por archivo y en total.

    - loc: líneas físicas totales
    - sloc: líneas de código fuente (sin comentarios ni blancos) -> base del KLOC
    - comentarios y blancos
    - kloc: sloc / 1000 (miles de líneas de código, para la densidad de defectos)
    """
    repo = Path(repo)
    por_archivo = []
    for archivo in encontrar_archivos_python(repo):
        r = analyze(_leer(archivo))
        por_archivo.append({
            "archivo": archivo.relative_to(repo).as_posix(),
            "loc": r.loc,
            "sloc": r.sloc,
            "comentarios": r.comments,
            "blancos": r.blank,
        })

    total_sloc = sum(a["sloc"] for a in por_archivo)
    return {
        "por_archivo": por_archivo,
        "n_archivos": len(por_archivo),
        "loc": sum(a["loc"] for a in por_archivo),
        "sloc": total_sloc,
        "comentarios": sum(a["comentarios"] for a in por_archivo),
        "blancos": sum(a["blancos"] for a in por_archivo),
        "kloc": round(total_sloc / 1000, 3),
    }


def _imprimir(repo: Path) -> None:
    """Muestra los resultados en la terminal (usado como evidencia E07)."""
    cc = analizar_complejidad(repo)
    loc = contar_lineas(repo)

    print(f"\nComplejidad ciclomática — {Path(repo).resolve()}")
    print(f"{'CC':>4} {'Rango':>5}  Función (archivo:línea)")
    for f in sorted(cc["funciones"], key=lambda f: -f["cc"]):
        print(f"{f['cc']:>4} {f['rango']:>5}  {f['nombre']} ({f['archivo']}:{f['linea']})")
    print(f"\nFunciones: {cc['n_funciones']} · promedio: {cc['promedio']} · "
          f"mediana: {cc['mediana']} · máximo: {cc['maximo']} · "
          f"CC <= {cc['umbral_mccabe']}: {cc['en_bajo_riesgo']}")
    print(f"Tamaño: {loc['n_archivos']} archivos · LOC {loc['loc']} · SLOC {loc['sloc']} · "
          f"KLOC {loc['kloc']} · comentarios {loc['comentarios']} · blancos {loc['blancos']}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Complejidad y LOC de un proyecto Python.")
    parser.add_argument("--repo", default=".", help="Ruta del proyecto a analizar (por defecto, la carpeta actual).")
    _imprimir(Path(parser.parse_args().repo))
