"""Pruebas de la API REST (T30): componente, interfaz (contrato), funcionales y de seguridad.

Se usan con TestClient de FastAPI: la API se ejecuta en memoria, sin abrir un puerto.
Las mismas peticiones se repiten contra el contenedor real de Proxmox en
test_hipervisor_vivo.py (pruebas de servicios).
"""

import pytest
from fastapi.testclient import TestClient

from qualityops.api import ENCABEZADOS_SEGUROS, app

cliente = TestClient(app)

APROBABLE = {"pruebas": {"total": 58, "aprobadas": 58, "fallidas": 0, "errores": 0},
             "cobertura": 88.79, "complejidad_maxima": 9}


@pytest.mark.componente
@pytest.mark.humo
def test_cp_api_01_salud_responde_ok():
    """CP-API-01: GET /salud devuelve 200, estado ok y el nombre del equipo."""
    r = cliente.get("/salud")
    assert r.status_code == 200
    datos = r.json()
    assert datos["estado"] == "ok" and datos["servicio"] == "qualityops-api" and datos["host"]


@pytest.mark.interfaz
def test_cp_api_02_contrato_de_gate():
    """CP-API-02: POST /gate respeta el contrato: dictamen, aprobado, criterios y umbrales."""
    r = cliente.post("/gate", json=APROBABLE)
    assert r.status_code == 200
    datos = r.json()
    assert set(datos) >= {"dictamen", "aprobado", "criterios", "umbrales"}
    assert [c["criterio"] for c in datos["criterios"]] == [
        "Pruebas automatizadas sin fallas", "Cobertura de código", "Complejidad ciclomática máxima"]
    assert r.headers["content-type"].startswith("application/json")


@pytest.mark.funcional
def test_cp_api_03_gate_aprueba_las_metricas_de_v101():
    """CP-API-03: con las métricas documentadas de v1.0.1 el servicio dictamina APROBADO."""
    assert cliente.post("/gate", json=APROBABLE).json()["dictamen"] == "APROBADO"


@pytest.mark.funcional
def test_cp_api_04_gate_bloquea_complejidad_11():
    """CP-API-04: el mismo caso de la demo en vivo (CC 11) se BLOQUEA también vía API."""
    datos = cliente.post("/gate", json={**APROBABLE, "complejidad_maxima": 11}).json()
    assert datos["dictamen"] == "BLOQUEADO"
    assert [c["cumple"] for c in datos["criterios"]] == [True, True, False]


@pytest.mark.funcional
def test_cp_api_05_umbrales_personalizados():
    """CP-API-05: un proyecto con umbral CC 16 (justificado) aprueba CC 11."""
    datos = cliente.post("/gate", json={**APROBABLE, "complejidad_maxima": 11,
                                         "umbrales": {"complejidad_maxima": 16}}).json()
    assert datos["dictamen"] == "APROBADO"


@pytest.mark.interfaz
def test_cp_api_06_metricas_sin_reportes_da_404(tmp_path, monkeypatch):
    """CP-API-06: GET /metricas sin metrics.json responde 404 con un mensaje que orienta."""
    monkeypatch.setenv("QUALITYOPS_REPORTS", str(tmp_path))
    r = cliente.get("/metricas")
    assert r.status_code == 404 and "python -m qualityops" in r.json()["detail"]


@pytest.mark.seguridad
@pytest.mark.parametrize("cuerpo", [
    {**APROBABLE, "cobertura": 150},                     # fuera de rango
    {**APROBABLE, "cobertura": "noventa"},               # tipo incorrecto
    {"cobertura": 80},                                    # falta un campo obligatorio
    {**APROBABLE, "pruebas": {**APROBABLE["pruebas"], "total": -1}},
])
def test_cp_seg_01_entradas_invalidas_se_rechazan_sin_trazas(cuerpo):
    """CP-SEG-01: datos inválidos -> 422, sin 'Traceback' ni rutas internas en la respuesta."""
    r = cliente.post("/gate", json=cuerpo)
    assert r.status_code == 422
    assert "Traceback" not in r.text and "site-packages" not in r.text


@pytest.mark.seguridad
def test_cp_seg_02_token_obligatorio_si_esta_configurado(monkeypatch):
    """CP-SEG-02: con QUALITYOPS_API_TOKEN, POST /gate sin X-API-Key o con uno falso -> 401."""
    monkeypatch.setenv("QUALITYOPS_API_TOKEN", "token-de-prueba")
    assert cliente.post("/gate", json=APROBABLE).status_code == 401
    assert cliente.post("/gate", json=APROBABLE, headers={"X-API-Key": "falso"}).status_code == 401
    assert cliente.post("/gate", json=APROBABLE, headers={"X-API-Key": "token-de-prueba"}).status_code == 200


@pytest.mark.seguridad
def test_cp_seg_03_encabezados_de_seguridad_en_todas_las_respuestas():
    """CP-SEG-03: cada respuesta (también los errores) trae los encabezados de seguridad."""
    for r in (cliente.get("/salud"), cliente.get("/no-existe"), cliente.post("/gate", json={})):
        for nombre, valor in ENCABEZADOS_SEGUROS.items():
            assert r.headers.get(nombre) == valor


@pytest.mark.seguridad
def test_cp_seg_04_metodos_no_permitidos():
    """CP-SEG-04: los endpoints solo aceptan su método (DELETE /gate -> 405)."""
    assert cliente.delete("/gate").status_code == 405
    assert cliente.post("/salud").status_code == 405
