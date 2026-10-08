"""Métricas de PROCESO: MTTD, MTTR y eficacia de las pruebas.

Requisitos que cubre: MET-R1 (tiempo medio de detección), MET-R2 (tiempo
medio de reparación) y MET-R3 (eficacia de las pruebas).

Todas se calculan a partir de la minería de defectos (qualityops.defects),
es decir, del historial real de Git. Si todavía no hay defectos, los valores
quedan en None con n = 0: no se inventan cifras.

  - MTTD (h) = promedio(fecha del fix − fecha del commit que introdujo el defecto)
  - MTTR (h) = promedio(fecha del merge del PR − fecha del fix)
  - Eficacia de las pruebas (%) = defectos CRÍTICOS detectados antes de producción
        / defectos críticos con fase conocida × 100
    (también se reporta la misma razón con todas las severidades, como referencia)
"""

from __future__ import annotations

import statistics

FASES_ANTES_DE_PRODUCCION = {"revision", "pruebas"}
FASES_CONOCIDAS = FASES_ANTES_DE_PRODUCCION | {"produccion"}


def resumen_tiempos(valores: list[float]) -> dict:
    """n, promedio y mediana (en horas) de una lista de tiempos; None si está vacía."""
    if not valores:
        return {"n": 0, "promedio_h": None, "mediana_h": None}
    return {"n": len(valores),
            "promedio_h": round(statistics.mean(valores), 2),
            "mediana_h": round(statistics.median(valores), 2)}


def eficacia(defectos: list[dict]) -> dict:
    """Porcentaje de defectos (con fase conocida) atrapados antes de producción."""
    conocidos = [d for d in defectos if d["fase"] in FASES_CONOCIDAS]
    antes = [d for d in conocidos if d["fase"] in FASES_ANTES_DE_PRODUCCION]
    pct = round(100 * len(antes) / len(conocidos), 2) if conocidos else None
    return {"antes_de_produccion": len(antes), "con_fase_conocida": len(conocidos), "pct": pct}


def calcular_proceso(mineria: dict) -> dict:
    """Recibe la salida de minar_defectos() y devuelve las métricas de proceso."""
    defectos = mineria["defectos"]
    criticos = [d for d in defectos if d["severidad"] == "critica"]
    return {
        "mttd": resumen_tiempos([d["mttd_horas"] for d in defectos if d["mttd_horas"] is not None]),
        "mttr": resumen_tiempos([d["mttr_horas"] for d in defectos if d["mttr_horas"] is not None]),
        "eficacia_pruebas": {
            "criticos": eficacia(criticos),            # lo que pide el requisito MET-R3
            "todas_las_severidades": eficacia(defectos),
        },
        "n_defectos": len(defectos),
    }
