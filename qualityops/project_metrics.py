"""Métricas de PROYECTO: eficacia de la revisión, desviación de tiempo y esfuerzo
por módulo y cumplimiento de plazos.

Requisitos que cubre: MET-J1, MET-J2 y MET-J3.

Fuentes reales:
  - Minería de defectos (qualityops.defects) -> eficacia de la revisión.
  - data/time_log.csv (estimación registrada ANTES de programar y tiempo real
    de cada tarea) -> desviación por módulo y plazos.
  - [tool.qualityops.calendario] en pyproject.toml -> fecha planeada de cada sprint.

Fórmulas:
  - Eficacia de la revisión (%) = defectos detectados en revisión
        / defectos con fase conocida × 100
  - Desviación (%) = (horas reales − horas estimadas) / horas estimadas × 100
        (solo tareas terminadas; estimado = columna "mas_probable_h")
  - Plazos (%) = tareas terminadas en o antes de la fecha de su sprint / tareas terminadas × 100
"""

from __future__ import annotations

import csv
import tomllib
from pathlib import Path

FASES_CONOCIDAS = {"revision", "pruebas", "produccion"}


def eficacia_revision(mineria: dict) -> dict:
    """Porcentaje de defectos que se atraparon en la revisión del PR."""
    conocidos = [d for d in mineria["defectos"] if d["fase"] in FASES_CONOCIDAS]
    en_revision = sum(1 for d in conocidos if d["fase"] == "revision")
    pct = round(100 * en_revision / len(conocidos), 2) if conocidos else None
    return {"en_revision": en_revision, "con_fase_conocida": len(conocidos), "pct": pct}


def leer_time_log(repo: Path) -> list[dict]:
    """Lee data/time_log.csv del proyecto; lista vacía si no existe."""
    ruta = Path(repo) / "data" / "time_log.csv"
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def leer_calendario(repo: Path) -> dict:
    """Fecha planeada (AAAA-MM-DD) de cada sprint, desde pyproject.toml."""
    ruta = Path(repo) / "pyproject.toml"
    if not ruta.exists():
        return {}
    config = tomllib.loads(ruta.read_text(encoding="utf-8"))
    return config.get("tool", {}).get("qualityops", {}).get("calendario", {})


def _pct_desviacion(estimado: float, real: float) -> float | None:
    return round(100 * (real - estimado) / estimado, 2) if estimado else None


def desviacion_por_modulo(tareas: list[dict]) -> dict:
    """Suma horas estimadas y reales de las tareas TERMINADAS, por módulo y total."""
    terminadas = [t for t in tareas if t.get("real_h")]
    modulos: dict[str, dict] = {}
    for t in terminadas:
        m = modulos.setdefault(t["modulo"], {"tareas": 0, "estimado_h": 0.0, "real_h": 0.0})
        m["tareas"] += 1
        m["estimado_h"] += float(t["mas_probable_h"])
        m["real_h"] += float(t["real_h"])
    for m in modulos.values():
        m["estimado_h"], m["real_h"] = round(m["estimado_h"], 2), round(m["real_h"], 2)
        m["desviacion_pct"] = _pct_desviacion(m["estimado_h"], m["real_h"])
    est = round(sum(m["estimado_h"] for m in modulos.values()), 2)
    real = round(sum(m["real_h"] for m in modulos.values()), 2)
    return {"por_modulo": modulos, "tareas_terminadas": len(terminadas),
            "estimado_h": est, "real_h": real, "desviacion_pct": _pct_desviacion(est, real)}


def _fecha_planeada(sprint: str, calendario: dict) -> str | None:
    """'S1D-S3B' -> se toma el último sprint del rango."""
    return calendario.get(sprint.split("-")[-1]) if sprint else None


def cumplimiento_plazos(tareas: list[dict], calendario: dict) -> dict:
    """Compara la FECHA real de cierre con la fecha planeada de su sprint."""
    evaluadas, a_tiempo, tarde = 0, 0, []
    for t in tareas:
        planeada = _fecha_planeada(t.get("sprint_planeado", ""), calendario)
        if not t.get("fin") or not planeada:
            continue
        evaluadas += 1
        if t["fin"][:10] <= planeada:
            a_tiempo += 1
        else:
            tarde.append(t["tarea"])
    pct = round(100 * a_tiempo / evaluadas, 2) if evaluadas else None
    return {"evaluadas": evaluadas, "a_tiempo": a_tiempo, "tarde": tarde, "pct_a_tiempo": pct}


def calcular_proyecto(mineria: dict, repo: Path) -> dict:
    """Arma las métricas de proyecto del repositorio `repo`."""
    tareas = leer_time_log(repo)
    return {
        "eficacia_revision": eficacia_revision(mineria),
        "desviacion": desviacion_por_modulo(tareas),
        "plazos": cumplimiento_plazos(tareas, leer_calendario(repo)),
    }
