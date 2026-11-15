"""Pruebas de API y de servicios contra el Proxmox VE REAL (T31).

Solo se ejecutan si existen las variables PVE_URL, PVE_TOKEN_ID, PVE_TOKEN_SECRET y PVE_CA
(en la laptop con la VM encendida). En GitHub Actions no existen y se OMITEN: el pipeline
no tiene acceso a la red privada 192.168.56.0/24.

    python -m pytest -m hipervisor -v
"""

import os

import httpx
import pytest

from qualityops.hipervisor import (
    ClienteProxmox,
    ip_de_config,
    verificar_hiperconvergencia,
)

VARIABLES = ("PVE_URL", "PVE_TOKEN_ID", "PVE_TOKEN_SECRET", "PVE_CA")
pytestmark = [
    pytest.mark.hipervisor,
    pytest.mark.skipif(not all(os.environ.get(v) for v in VARIABLES),
                       reason="sin Proxmox VE: faltan las variables PVE_*"),
]
NODO, VMID = os.environ.get("PVE_NODO", "pve"), int(os.environ.get("PVE_VMID", "200"))
PUERTO = int(os.environ.get("QUALITYOPS_API_PUERTO", "8000"))


@pytest.fixture(scope="module")
def pve():
    return ClienteProxmox.desde_entorno()


@pytest.fixture(scope="module")
def url_servicio(pve):
    return f"http://{ip_de_config(pve.config_contenedor(NODO, VMID))}:{PUERTO}"


@pytest.mark.integracion
def test_cp_hv_10_api_de_proxmox_con_tls_validado(pve):
    """CP-HV-10: la API de Proxmox responde por HTTPS validando su certificado con la CA del nodo."""
    assert pve.version()["version"].startswith("9.")


@pytest.mark.integracion
def test_cp_hv_11_pilares_de_la_hiperconvergencia(pve):
    """CP-HV-11: nodo en línea (cómputo), almacenamientos activos y contenedor corriendo."""
    assert any(n["node"] == NODO and n["status"] == "online" for n in pve.nodos())
    assert any(a.get("active") for a in pve.almacenamiento(NODO))
    assert pve.estado_contenedor(NODO, VMID)["status"] == "running"


@pytest.mark.sistema
def test_cp_hv_12_servicio_en_el_contenedor_responde(url_servicio):
    """CP-HV-12: la API de QualityOps responde dentro del contenedor (prueba de servicio)."""
    r = httpx.get(url_servicio + "/salud", timeout=5)
    assert r.status_code == 200 and r.json()["estado"] == "ok"


@pytest.mark.sistema
def test_cp_hv_13_gate_remoto_igual_que_local(url_servicio):
    """CP-HV-13: el gate en el contenedor da el mismo dictamen que la herramienta local."""
    cuerpo = {"pruebas": {"total": 58, "aprobadas": 58, "fallidas": 0, "errores": 0},
              "cobertura": 88.79, "complejidad_maxima": 11}
    headers = {"X-API-Key": os.environ["QUALITYOPS_API_TOKEN"]} if os.environ.get("QUALITYOPS_API_TOKEN") else {}
    r = httpx.post(url_servicio + "/gate", json=cuerpo, headers=headers, timeout=5)
    assert r.status_code == 200 and r.json()["dictamen"] == "BLOQUEADO"


@pytest.mark.aceptacion
def test_cp_hv_14_comunicacion_hipervisor_servicio(pve):
    """CP-HV-14: Dado Proxmox y el contenedor, cuando se verifica la HCI, entonces todo está en OK
    y el hostname que responde es el que Proxmox tiene registrado."""
    r = verificar_hiperconvergencia(pve, NODO, VMID, PUERTO)
    assert r["ok"], [c for c in r["verificaciones"] if not c["ok"]]
