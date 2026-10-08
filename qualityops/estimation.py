"""Técnicas de ESTIMACIÓN aplicadas al alcance del proyecto.

Requisitos que cubre: EST-1 (juicio de expertos), EST-2 (estimación análoga),
EST-3 (tres puntos / PERT) y EST-4 (puntos de función).

Las cuatro técnicas estiman el MISMO alcance (la línea base de tareas registrada
en data/time_log.csv antes de programar) para que se puedan comparar entre sí y
contra las horas reales.

  EST-1 Juicio de expertos: suma de la columna "mas_probable_h" (estimación del autor).
  EST-3 Tres puntos (PERT): por tarea E = (O + 4M + P) / 6 y σ = (P − O) / 6;
        el total suma las E y combina las σ como raíz de la suma de cuadrados.
  EST-4 Puntos de función (IFPUG / ISO/IEC 20926): PF sin ajustar =
        Σ (cantidad × peso) de EI, EO, EQ, ILF y EIF; horas = PF × tasa (h/PF).
        Si no se da una tasa, se usa la del proyecto de referencia
        (horas reales / PF de la referencia).
  EST-2 Análoga: horas = horas reales del proyecto de referencia
        × (PF del proyecto nuevo / PF de la referencia) × factor de ajuste.

Los datos de entrada de EST-2 y EST-4 están en data/estimacion.json; si falta un
dato, esa técnica queda en None (no se inventa un número).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

# Pesos IFPUG por tipo de función y complejidad (baja, media, alta).
PESOS_PF = {
    "EI": {"baja": 3, "media": 4, "alta": 6},
    "EO": {"baja": 4, "media": 5, "alta": 7},
    "EQ": {"baja": 3, "media": 4, "alta": 6},
    "ILF": {"baja": 7, "media": 10, "alta": 15},
    "EIF": {"baja": 5, "media": 7, "alta": 10},
}


def tareas_linea_base(tareas: list[dict]) -> list[dict]:
    """Solo las tareas de la estimación inicial (las agregadas después se excluyen)."""
    return [t for t in tareas if "después de la línea base" not in t.get("nota", "")]


def juicio_expertos(tareas: list[dict]) -> dict:
    """EST-1: suma de la estimación más probable del autor."""
    return {"horas": round(sum(float(t["mas_probable_h"]) for t in tareas), 2), "tareas": len(tareas)}


def tres_puntos(tareas: list[dict]) -> dict:
    """EST-3: PERT por tarea y total, con su desviación estándar."""
    esperado, varianza = 0.0, 0.0
    for t in tareas:
        o, m, p = float(t["optimista_h"]), float(t["mas_probable_h"]), float(t["pesimista_h"])
        esperado += (o + 4 * m + p) / 6
        varianza += ((p - o) / 6) ** 2
    sigma = math.sqrt(varianza)
    return {"horas": round(esperado, 2), "sigma_h": round(sigma, 2),
            "rango_95_h": [round(esperado - 2 * sigma, 2), round(esperado + 2 * sigma, 2)]}


def puntos_de_funcion(conteo: list[dict]) -> int:
    """PF sin ajustar: Σ cantidad × peso IFPUG de cada función contada."""
    return sum(f["cantidad"] * PESOS_PF[f["tipo"]][f["complejidad"]] for f in conteo)


def _hay_datos(*valores):
    """True si todos los valores existen (para no calcular con datos faltantes)."""
    return all(v is not None for v in valores)


def estimar(tareas: list[dict], datos: dict) -> dict:
    """Aplica las cuatro técnicas y devuelve un cuadro comparable (en horas)."""
    base = tareas_linea_base(tareas)
    pf = puntos_de_funcion(datos.get("puntos_de_funcion", {}).get("conteo", []))
    ref = datos.get("analoga", {})
    tasa = datos.get("puntos_de_funcion", {}).get("horas_por_pf")
    fuente_tasa = "dada en estimacion.json"
    if tasa is None and _hay_datos(ref.get("horas_reales"), ref.get("pf")) and ref.get("pf"):
        tasa = round(ref["horas_reales"] / ref["pf"], 4)
        fuente_tasa = "derivada del proyecto de referencia"

    est4 = round(pf * tasa, 2) if _hay_datos(tasa) and pf else None
    est2 = None
    if _hay_datos(ref.get("horas_reales"), ref.get("pf"), ref.get("factor_ajuste")) and ref.get("pf"):
        est2 = round(ref["horas_reales"] * (pf / ref["pf"]) * ref["factor_ajuste"], 2)

    return {
        "juicio_expertos": juicio_expertos(base),
        "analoga": {"horas": est2, "referencia": ref.get("nombre")},
        "tres_puntos": tres_puntos(base),
        "puntos_de_funcion": {"pf_sin_ajustar": pf, "horas_por_pf": tasa,
                              "fuente_tasa": fuente_tasa if tasa is not None else None, "horas": est4},
    }


def leer_datos(repo: Path) -> dict:
    """Lee data/estimacion.json del proyecto (vacío si no existe)."""
    ruta = Path(repo) / "data" / "estimacion.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
