"""Datos para el dashboard (T18). Funciones puras y probadas; app.py solo las muestra.

El dashboard NO calcula métricas: lee los archivos que generó el pipeline
(reports/metrics.json, gate.json, ai_analysis.json) y la matriz de cumplimiento.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ESTADOS = {"✅": "Cumple", "🟨": "En progreso", "🟧": "Parcial", "⬜": "Pendiente", "❌": "No cumple"}


def cargar_reportes(carpeta: Path) -> dict:
    """Lee los JSON de reports/; los que no existan quedan en None."""
    carpeta = Path(carpeta)
    datos = {}
    for nombre in ("metrics", "gate", "ai_analysis"):
        ruta = carpeta / f"{nombre}.json"
        datos[nombre] = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None
    return datos


def _fila_de_requisito(linea: str) -> dict | None:
    """Convierte una fila de la tabla de la matriz en {id, requisito, estado}."""
    if not re.match(r"^\| [A-Z]{2,4}-[A-Z0-9]+ \|", linea):
        return None
    celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
    estado = next((v for k, v in ESTADOS.items() if k in celdas[-1]), "Pendiente")
    return {"id": celdas[0], "requisito": celdas[1], "estado": estado}


def resumen_matriz(ruta_matriz: Path) -> dict:
    """Cuenta los requisitos de docs/MATRIZ_CUMPLIMIENTO.md por estado (CAL-01)."""
    ruta = Path(ruta_matriz)
    if not ruta.exists():
        return {"total": 0, "por_estado": {}, "pct_cumple": None, "filas": []}
    filas = [f for f in map(_fila_de_requisito, ruta.read_text(encoding="utf-8").splitlines()) if f]
    por_estado = {e: sum(1 for f in filas if f["estado"] == e) for e in ESTADOS.values()}
    pct = round(100 * por_estado["Cumple"] / len(filas), 2) if filas else None
    return {"total": len(filas), "por_estado": por_estado, "pct_cumple": pct, "filas": filas}


def tabla_estimacion(m: dict) -> list[dict]:
    """Las cuatro técnicas y el real en una sola tabla comparable."""
    est, real = m["estimacion"], m["proyecto"]["desviacion"]["real_h"]
    return [
        {"técnica": "Juicio de expertos", "horas": est["juicio_expertos"]["horas"]},
        {"técnica": "Análoga", "horas": est["analoga"]["horas"]},
        {"técnica": "Tres puntos (PERT)", "horas": est["tres_puntos"]["horas"]},
        {"técnica": "Puntos de función", "horas": est["puntos_de_funcion"]["horas"]},
        {"técnica": "Real (tareas terminadas)", "horas": real},
    ]


def tabla_desviacion(m: dict) -> list[dict]:
    """Estimado vs real por módulo (MET-J2)."""
    return [{"módulo": nombre, **valores} for nombre, valores in m["proyecto"]["desviacion"]["por_modulo"].items()]
