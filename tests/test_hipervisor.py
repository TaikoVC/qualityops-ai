"""Pruebas del cliente de Proxmox VE (T31) con un Proxmox SIMULADO.

httpx.MockTransport responde como lo hace la API real de Proxmox (mismas rutas y
mismo formato {"data": ...}). Así estas pruebas corren en cualquier equipo y en
GitHub Actions; las pruebas contra el Proxmox real están en test_hipervisor_vivo.py.
"""

import httpx
import pytest

from qualityops.hipervisor import (
    ClienteProxmox,
    ConfiguracionInsegura,
    ip_de_config,
    prueba_ciclo_de_vida,
    verificar_hiperconvergencia,
)

CONFIG_CT = {"hostname": "qualityops-api", "net0": "name=eth0,bridge=vmbr0,ip=192.168.56.20/24,gw=192.168.56.10"}


def proxmox_simulado(estado_ct: dict, peticiones: list):
    """Devuelve un transporte que imita la API de Proxmox y guarda cada petición recibida."""
    def responder(request: httpx.Request) -> httpx.Response:
        peticiones.append(request)
        ruta = request.url.path.removeprefix("/api2/json")
        datos = {
            "/version": {"version": "9.2.2", "release": "9.2"},
            "/nodes": [{"node": "pve", "status": "online", "cpu": 0.08, "mem": 1.5e9, "maxmem": 4e9}],
            "/nodes/pve/storage": [
                {"storage": "local", "type": "dir", "active": 1, "used": 3e9, "total": 1e10},
                {"storage": "local-lvm", "type": "lvmthin", "active": 1, "used": 1e9, "total": 1.4e10}],
            "/nodes/pve/lxc/200/status/current": {"status": estado_ct["status"]},
            "/nodes/pve/lxc/200/config": CONFIG_CT,
        }
        if request.method == "POST" and ruta.endswith("/status/stop"):
            estado_ct["status"] = "stopped"
            return httpx.Response(200, json={"data": "UPID:pve:stop"})
        if request.method == "POST" and ruta.endswith("/status/start"):
            estado_ct["status"] = "running"
            return httpx.Response(200, json={"data": "UPID:pve:start"})
        if ruta not in datos:
            return httpx.Response(404, json={"data": None})
        return httpx.Response(200, json={"data": datos[ruta]})
    return httpx.MockTransport(responder)


def servicio_simulado(estado_ct: dict, host: str = "qualityops-api"):
    """Imita la API de QualityOps dentro del contenedor: no responde si el contenedor está detenido."""
    def responder(request: httpx.Request) -> httpx.Response:
        if estado_ct["status"] != "running":
            raise httpx.ConnectError("sin ruta al contenedor", request=request)
        return httpx.Response(200, json={"estado": "ok", "host": host})
    return httpx.Client(transport=httpx.MockTransport(responder))


def cliente(estado_ct, peticiones):
    return ClienteProxmox("https://192.168.56.10:8006", "qa@pve!qualityops", "secreto", None,
                          transporte=proxmox_simulado(estado_ct, peticiones))


@pytest.mark.unitaria
def test_cp_hv_01_ip_de_config():
    """CP-HV-01: se extrae la IP del formato net0 de Proxmox."""
    assert ip_de_config(CONFIG_CT) == "192.168.56.20"
    assert ip_de_config({"net0": "name=eth0,bridge=vmbr0,ip=dhcp"}) is None
    assert ip_de_config({}) is None


@pytest.mark.componente
def test_cp_hv_02_verificacion_completa_con_proxmox_simulado():
    """CP-HV-02: los tres pilares (cómputo, almacenamiento, red) + servicio + comunicación en OK."""
    estado, peticiones = {"status": "running"}, []
    r = verificar_hiperconvergencia(cliente(estado, peticiones), cliente_http=servicio_simulado(estado))
    assert r["ok"] is True and r["ip_servicio"] == "192.168.56.20"
    assert [c["ok"] for c in r["verificaciones"]] == [True] * 7


@pytest.mark.seguridad
def test_cp_hv_03_autenticacion_con_token_de_api():
    """CP-HV-03: cada petición viaja con el encabezado PVEAPIToken (no usuario/contraseña)."""
    estado, peticiones = {"status": "running"}, []
    cliente(estado, peticiones).version()
    assert peticiones[0].headers["Authorization"] == "PVEAPIToken=qa@pve!qualityops=secreto"


@pytest.mark.componente
def test_cp_hv_04_detecta_hostname_distinto():
    """CP-HV-04: si responde OTRA máquina en esa IP, la comunicación se marca como FALLA."""
    estado = {"status": "running"}
    r = verificar_hiperconvergencia(cliente(estado, []), cliente_http=servicio_simulado(estado, host="otra-maquina"))
    assert r["ok"] is False
    assert r["verificaciones"][-1]["verificacion"].startswith("Comunicación") and not r["verificaciones"][-1]["ok"]


@pytest.mark.componente
def test_cp_hv_05_contenedor_detenido_se_reporta():
    """CP-HV-05: con el contenedor detenido, el estado y el servicio fallan (sin excepción)."""
    estado = {"status": "stopped"}
    r = verificar_hiperconvergencia(cliente(estado, []), cliente_http=servicio_simulado(estado))
    estados = {c["verificacion"]: c["ok"] for c in r["verificaciones"]}
    assert estados["Contenedor en ejecución"] is False
    assert estados["Servicio: API de QualityOps responde"] is False and r["ok"] is False


@pytest.mark.integracion
def test_cp_hv_06_ciclo_de_vida_detener_e_iniciar():
    """CP-HV-06: detener por API tumba el servicio; iniciar por API lo recupera."""
    estado, peticiones = {"status": "running"}, []
    r = prueba_ciclo_de_vida(cliente(estado, peticiones), "pve", 200, 8000, espera_max_s=1,
                             cliente_http=servicio_simulado(estado))
    assert r["ok"] is True
    assert [p.url.path for p in peticiones if p.method == "POST"] == [
        "/api2/json/nodes/pve/lxc/200/status/stop", "/api2/json/nodes/pve/lxc/200/status/start"]


@pytest.mark.seguridad
def test_cp_seg_05_cliente_rechaza_conexiones_inseguras():
    """CP-SEG-05: no se permite http:// ni desactivar la validación del certificado."""
    with pytest.raises(ConfiguracionInsegura):
        ClienteProxmox("http://192.168.56.10:8006", "id", "secreto", "ca.pem")
    with pytest.raises(ConfiguracionInsegura):
        ClienteProxmox("https://192.168.56.10:8006", "id", "secreto", None)


@pytest.mark.componente
def test_reintenta_el_arranque_si_proxmox_no_lo_inicia():
    """Defecto 8: si el primer 'start' no deja el contenedor en running, se reintenta una vez."""
    estado, peticiones = {"status": "running"}, []
    pve = cliente(estado, peticiones)
    original = pve.iniciar_contenedor
    llamadas = []

    def inicio_que_falla_la_primera_vez(nodo, vmid):
        llamadas.append(vmid)
        if len(llamadas) > 1:
            return original(nodo, vmid)
        return "UPID:pve:start-fallido"
    pve.iniciar_contenedor = inicio_que_falla_la_primera_vez
    r = prueba_ciclo_de_vida(pve, "pve", 200, 8000, espera_max_s=2, cliente_http=servicio_simulado(estado))
    assert r["ok"] is True and len(llamadas) == 2
