"""Pruebas de qualityops.estimation (T15). Valores calculados a mano."""

import math

from qualityops.estimation import (
    estimar,
    puntos_de_funcion,
    tareas_linea_base,
    tres_puntos,
)

TAREAS = [
    {"optimista_h": "1", "mas_probable_h": "2", "pesimista_h": "4", "nota": ""},
    {"optimista_h": "0.5", "mas_probable_h": "1", "pesimista_h": "3", "nota": ""},
    {"optimista_h": "1", "mas_probable_h": "1", "pesimista_h": "1", "nota": "Agregada después de la línea base (D13)"},
]


def test_linea_base_excluye_tareas_agregadas_despues():
    assert len(tareas_linea_base(TAREAS)) == 2


def test_tres_puntos_pert():
    r = tres_puntos(tareas_linea_base(TAREAS))
    # E1 = (1 + 8 + 4)/6 = 2.1667 ; E2 = (0.5 + 4 + 3)/6 = 1.25 -> 3.4167
    assert r["horas"] == 3.42
    # σ1 = 3/6 = 0.5 ; σ2 = 2.5/6 = 0.4167 -> sqrt(0.25 + 0.1736) = 0.6509
    assert r["sigma_h"] == round(math.sqrt(0.5**2 + (2.5 / 6) ** 2), 2)


def test_puntos_de_funcion_ifpug():
    conteo = [{"tipo": "EI", "complejidad": "baja", "cantidad": 2},   # 2 × 3 = 6
              {"tipo": "EO", "complejidad": "media", "cantidad": 3},  # 3 × 5 = 15
              {"tipo": "ILF", "complejidad": "baja", "cantidad": 1}]  # 1 × 7 = 7
    assert puntos_de_funcion(conteo) == 28


def test_cuatro_tecnicas_comparables():
    datos = {
        "puntos_de_funcion": {"conteo": [{"tipo": "EO", "complejidad": "media", "cantidad": 4}],  # 20 PF
                              "horas_por_pf": 0.5},
        "analoga": {"nombre": "ref", "horas_reales": 10, "pf": 40, "factor_ajuste": 1.2},
    }
    r = estimar(TAREAS, datos)
    assert r["juicio_expertos"]["horas"] == 3.0
    assert r["puntos_de_funcion"]["horas"] == 10.0          # 20 PF × 0.5 h/PF
    assert r["analoga"]["horas"] == 6.0      # 10 × (20/40) × 1.2


def test_sin_datos_no_inventa():
    r = estimar(TAREAS, {})
    assert r["analoga"]["horas"] is None
    assert r["puntos_de_funcion"]["horas"] is None


def test_tasa_derivada_de_la_referencia():
    datos = {
        "puntos_de_funcion": {"conteo": [{"tipo": "EO", "complejidad": "media", "cantidad": 4}],  # 20 PF
                              "horas_por_pf": None},
        "analoga": {"horas_reales": 10, "pf": 40, "factor_ajuste": 1.0},
    }
    r = estimar(TAREAS, datos)["puntos_de_funcion"]
    assert (r["horas_por_pf"], r["horas"]) == (0.25, 5.0)     # 10 h / 40 PF
    assert r["fuente_tasa"] == "derivada del proyecto de referencia"
