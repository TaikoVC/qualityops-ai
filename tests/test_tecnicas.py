"""Técnicas de prueba aplicadas al quality gate y a la CLI (T33).

- Funcionales: particiones de equivalencia y análisis de valores límite sobre los umbrales.
- No funcionales: tiempos de respuesta (rendimiento) del gate y de la API.
- Humo: lo esencial arranca (módulos importan, la CLI responde a --help, la API contesta).
- Exploratorias automatizadas: Hypothesis genera cientos de entradas al azar buscando
  combinaciones que rompan las reglas del gate (pruebas basadas en propiedades).
"""

import importlib
import statistics
import time

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st

from qualityops.api import app
from qualityops.quality_gate import UMBRALES_POR_DEFECTO, evaluar

UMBRALES = dict(UMBRALES_POR_DEFECTO)   # cobertura >= 75.0 y CC <= 10


def metricas(cobertura=88.79, cc=9, total=58, fallidas=0, errores=0):
    return {"pruebas": {"total": total, "aprobadas": total - fallidas - errores,
                        "fallidas": fallidas, "errores": errores},
            "producto": {"cobertura": {"global_pct": cobertura}, "complejidad": {"maximo": cc}}}


# --------------------------------------------------------------------------
# Funcionales: valores límite y particiones de equivalencia
# --------------------------------------------------------------------------
@pytest.mark.funcional
@pytest.mark.parametrize(("cobertura", "esperado"), [
    (74.99, False),   # justo debajo del límite
    (75.0, True),     # en el límite (>= 75)
    (75.01, True),    # justo arriba
    (0.0, False), (100.0, True),
    (None, False),    # sin dato -> no se aprueba (sin evidencia no se aprueba)
])
def test_cp_fun_01_valores_limite_de_cobertura(cobertura, esperado):
    """CP-FUN-01: límite de cobertura en 75 %."""
    assert evaluar(metricas(cobertura=cobertura), UMBRALES)["aprobado"] is esperado


@pytest.mark.funcional
@pytest.mark.parametrize(("cc", "esperado"), [(9, True), (10, True), (11, False), (1, True), (None, False)])
def test_cp_fun_02_valores_limite_de_complejidad(cc, esperado):
    """CP-FUN-02: límite de complejidad ciclomática en 10 (McCabe)."""
    assert evaluar(metricas(cc=cc), UMBRALES)["aprobado"] is esperado


@pytest.mark.funcional
@pytest.mark.parametrize(("total", "fallidas", "errores", "esperado"), [
    (58, 0, 0, True),    # partición válida: hay pruebas y ninguna falla
    (0, 0, 0, False),    # sin pruebas
    (58, 1, 0, False),   # con una fallida
    (58, 0, 1, False),   # con un error
])
def test_cp_fun_03_particiones_de_pruebas(total, fallidas, errores, esperado):
    """CP-FUN-03: particiones de equivalencia del criterio de pruebas."""
    assert evaluar(metricas(total=total, fallidas=fallidas, errores=errores), UMBRALES)["aprobado"] is esperado


# --------------------------------------------------------------------------
# No funcionales: rendimiento
# --------------------------------------------------------------------------
@pytest.mark.no_funcional
def test_cp_nf_01_gate_evalua_en_menos_de_1_ms():
    """CP-NF-01: la evaluación del gate tarda < 1 ms en promedio (1 000 ejecuciones)."""
    inicio = time.perf_counter()
    for _ in range(1000):
        evaluar(metricas(), UMBRALES)
    assert (time.perf_counter() - inicio) / 1000 < 0.001


@pytest.mark.no_funcional
def test_cp_nf_02_api_responde_en_menos_de_100_ms():
    """CP-NF-02: la mediana de 50 peticiones POST /gate es < 100 ms (en memoria)."""
    cliente = TestClient(app)
    tiempos = []
    for _ in range(50):
        inicio = time.perf_counter()
        assert cliente.post("/gate", json={"pruebas": metricas()["pruebas"], "cobertura": 80,
                                           "complejidad_maxima": 5}).status_code == 200
        tiempos.append(time.perf_counter() - inicio)
    assert statistics.median(tiempos) < 0.1


# --------------------------------------------------------------------------
# Humo
# --------------------------------------------------------------------------
@pytest.mark.humo
@pytest.mark.parametrize("modulo", ["cli", "quality_gate", "report", "ai_advisor", "api", "hipervisor", "seguridad"])
def test_cp_humo_01_los_modulos_importan(modulo):
    """CP-HUMO-01: cada módulo principal se importa sin errores."""
    importlib.import_module(f"qualityops.{modulo}")


@pytest.mark.humo
@pytest.mark.interfaz
def test_cp_humo_02_cli_del_gate_muestra_ayuda(capsys):
    """CP-HUMO-02: la interfaz de línea de comandos responde a --help."""
    from qualityops.quality_gate import main
    with pytest.raises(SystemExit) as salida:
        main(["--help"])
    assert salida.value.code == 0 and "--metricas" in capsys.readouterr().out


# --------------------------------------------------------------------------
# Exploratorias automatizadas (Hypothesis)
# --------------------------------------------------------------------------
coberturas = st.one_of(st.none(), st.floats(min_value=0, max_value=100, allow_nan=False))
complejidades = st.one_of(st.none(), st.integers(min_value=1, max_value=60))


@pytest.mark.exploratoria
@settings(max_examples=300, deadline=None)
@given(cobertura=coberturas, cc=complejidades, fallidas=st.integers(0, 5))
def test_cp_exp_01_el_dictamen_es_exactamente_la_regla(cobertura, cc, fallidas):
    """CP-EXP-01: para CUALQUIER combinación, el gate aprueba si y solo si se cumplen los 3 criterios."""
    esperado = (fallidas == 0 and cobertura is not None and cobertura >= 75
                and cc is not None and cc <= 10)
    assert evaluar(metricas(cobertura=cobertura, cc=cc, fallidas=fallidas), UMBRALES)["aprobado"] is esperado


@pytest.mark.exploratoria
@settings(max_examples=200, deadline=None)
@given(cobertura=st.floats(min_value=0, max_value=100, allow_nan=False), extra=st.floats(min_value=0, max_value=100))
def test_cp_exp_02_mas_cobertura_nunca_empeora_el_dictamen(cobertura, extra):
    """CP-EXP-02: propiedad de monotonía: subir la cobertura nunca cambia APROBADO a BLOQUEADO."""
    antes = evaluar(metricas(cobertura=cobertura), UMBRALES)["aprobado"]
    despues = evaluar(metricas(cobertura=min(100.0, cobertura + extra)), UMBRALES)["aprobado"]
    assert not (antes and not despues)
