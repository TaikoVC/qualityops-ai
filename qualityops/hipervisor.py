"""Hipervisor e hiperconvergencia (T31): verificación por API de Proxmox VE.

Conceptos (ver capítulo de hiperconvergencia del reporte):
  - Hipervisor: software que crea y ejecuta máquinas virtuales o contenedores.
    Proxmox VE usa KVM (tipo 1) para VMs y LXC para contenedores.
  - Hiperconvergencia (HCI): CÓMPUTO, ALMACENAMIENTO y RED virtualizados en los mismos
    nodos y administrados desde un solo plano de control. En Proxmox ese plano de
    control es su API REST (https://<nodo>:8006/api2/json).

Qué verifica este módulo, todo desde la laptop y a través de la API de Proxmox:
  1. Cómputo         -> el nodo está en línea; CPU y memoria en uso.
  2. Almacenamiento  -> los almacenamientos del nodo están activos; espacio usado.
  3. Contenedor      -> el contenedor del servicio existe y está "running".
  4. Red             -> la IP que Proxmox tiene configurada para el contenedor.
  5. Servicio        -> la API de QualityOps responde en ESA IP (GET /salud).
  6. Comunicación    -> el hostname que reporta el servicio es el mismo que Proxmox
                        tiene registrado para el contenedor: el hipervisor y el servicio
                        hablan de la misma máquina.

Configuración (variables de entorno; el secreto NUNCA va en archivos del repositorio):
  PVE_URL           https://192.168.56.10:8006
  PVE_TOKEN_ID      qa@pve!qualityops
  PVE_TOKEN_SECRET  (se pega con Read-Host, no se guarda)
  PVE_CA            ruta al certificado raíz de Proxmox (pve-root-ca.pem) para validar TLS
  PVE_NODO          pve          (opcional)
  PVE_VMID          200          (opcional)
  QUALITYOPS_API_PUERTO 8000     (opcional)

Uso:
    python -m qualityops.hipervisor               # verificación completa -> reports/hipervisor.json
    python -m qualityops.hipervisor --detener     # además prueba detener/arrancar el contenedor
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx


class ConfiguracionInsegura(ValueError):
    """La conexión pedida no cumple la política de seguridad (p. ej. http:// o sin validar TLS)."""


class ClienteProxmox:
    """Cliente mínimo de la API REST de Proxmox VE autenticado con token de API."""

    def __init__(self, url: str, token_id: str, token_secreto: str, ca: str | None,
                 transporte: httpx.BaseTransport | None = None, timeout: float = 10.0):
        # Política de seguridad: solo HTTPS y con validación del certificado.
        if not url.startswith("https://"):
            raise ConfiguracionInsegura("La API de Proxmox solo se usa por https://")
        if transporte is None and not ca:
            raise ConfiguracionInsegura(
                "Falta PVE_CA: el certificado de Proxmox es autofirmado y debe validarse con su CA "
                "(no se desactiva la verificación TLS)")
        self.base = url.rstrip("/") + "/api2/json"
        self._http = httpx.Client(
            headers={"Authorization": f"PVEAPIToken={token_id}={token_secreto}"},
            verify=ssl.create_default_context(cafile=ca) if ca else True, timeout=timeout, transport=transporte)

    @classmethod
    def desde_entorno(cls) -> ClienteProxmox:
        faltan = [v for v in ("PVE_URL", "PVE_TOKEN_ID", "PVE_TOKEN_SECRET", "PVE_CA") if not os.environ.get(v)]
        if faltan:
            raise RuntimeError("Faltan variables de entorno: " + ", ".join(faltan))
        return cls(os.environ["PVE_URL"], os.environ["PVE_TOKEN_ID"],
                   os.environ["PVE_TOKEN_SECRET"], os.environ["PVE_CA"])

    def _get(self, ruta: str):
        respuesta = self._http.get(self.base + ruta)
        respuesta.raise_for_status()
        return respuesta.json()["data"]

    def _post(self, ruta: str):
        respuesta = self._http.post(self.base + ruta)
        respuesta.raise_for_status()
        return respuesta.json()["data"]

    # Consultas de solo lectura -------------------------------------------------
    def version(self) -> dict:
        return self._get("/version")

    def nodos(self) -> list[dict]:
        return self._get("/nodes")

    def almacenamiento(self, nodo: str) -> list[dict]:
        return self._get(f"/nodes/{nodo}/storage")

    def contenedores(self, nodo: str) -> list[dict]:
        return self._get(f"/nodes/{nodo}/lxc")

    def estado_contenedor(self, nodo: str, vmid: int) -> dict:
        return self._get(f"/nodes/{nodo}/lxc/{vmid}/status/current")

    def config_contenedor(self, nodo: str, vmid: int) -> dict:
        return self._get(f"/nodes/{nodo}/lxc/{vmid}/config")

    # Acciones (requieren el permiso VM.PowerMgmt sobre el contenedor) --------
    def detener_contenedor(self, nodo: str, vmid: int) -> str:
        return self._post(f"/nodes/{nodo}/lxc/{vmid}/status/stop")

    def iniciar_contenedor(self, nodo: str, vmid: int) -> str:
        return self._post(f"/nodes/{nodo}/lxc/{vmid}/status/start")


def ip_de_config(config: dict) -> str | None:
    """Extrae la IP de net0 (formato de Proxmox: 'name=eth0,bridge=vmbr0,ip=192.168.56.20/24,...')."""
    for parte in config.get("net0", "").split(","):
        if parte.startswith("ip=") and "/" in parte:
            return parte[3:].split("/")[0]
    return None


def _pct(usado, total) -> float | None:
    return round(100 * usado / total, 1) if total else None


def _check(nombre: str, ok: bool, detalle: str) -> dict:
    return {"verificacion": nombre, "ok": bool(ok), "detalle": detalle}


def consultar_servicio(ip: str, puerto: int, cliente_http: httpx.Client | None = None) -> dict:
    """GET /salud del servicio de QualityOps; devuelve la respuesta y el tiempo en ms."""
    http = cliente_http or httpx.Client(timeout=5.0)
    inicio = time.perf_counter()
    respuesta = http.get(f"http://{ip}:{puerto}/salud")
    respuesta.raise_for_status()
    return {"respuesta": respuesta.json(), "ms": round((time.perf_counter() - inicio) * 1000, 1)}


def _check_computo(nodos: list[dict], nodo: str) -> dict:
    info = next((n for n in nodos if n.get("node") == nodo), None)
    if not info:
        return _check("Cómputo: nodo en línea", False, f"nodo '{nodo}' no encontrado")
    return _check("Cómputo: nodo en línea", info.get("status") == "online",
                  f"{nodo}: CPU {round(100 * info.get('cpu', 0), 1)} %, memoria "
                  f"{_pct(info.get('mem'), info.get('maxmem'))} %")


def _check_almacenamiento(almacenes: list[dict]) -> dict:
    activos = [a for a in almacenes if a.get("active")]
    detalle = ", ".join(f"{a['storage']} ({a.get('type')}) {_pct(a.get('used'), a.get('total'))} % usado"
                        for a in activos)
    return _check("Almacenamiento: pools activos", bool(activos), detalle or "ninguno activo")


def _checks_servicio(ip: str, puerto: int, hostname: str | None, cliente_http: httpx.Client | None) -> list[dict]:
    """Servicio responde en la IP del contenedor y lo hace DESDE el contenedor que registra Proxmox."""
    try:
        servicio = consultar_servicio(ip, puerto, cliente_http)
    except httpx.HTTPError as error:
        return [_check("Servicio: API de QualityOps responde", False, f"{type(error).__name__}: {error}")]
    respuesta = servicio["respuesta"]
    return [
        _check("Servicio: API de QualityOps responde", respuesta.get("estado") == "ok",
               f"GET http://{ip}:{puerto}/salud en {servicio['ms']} ms"),
        _check("Comunicación hipervisor ↔ servicio", respuesta.get("host") == hostname,
               f"Proxmox registra '{hostname}'; el servicio responde desde '{respuesta.get('host')}'"),
    ]


def verificar_hiperconvergencia(pve: ClienteProxmox, nodo: str = "pve", vmid: int = 200,
                                puerto: int = 8000, cliente_http: httpx.Client | None = None) -> dict:
    """Recorre los tres pilares de la HCI y el servicio; devuelve cada verificación."""
    version = pve.version()
    estado = pve.estado_contenedor(nodo, vmid)
    config = pve.config_contenedor(nodo, vmid)
    ip = ip_de_config(config)
    checks = [
        _check("API de Proxmox accesible (TLS validado)", True,
               f"Proxmox VE {version.get('version')} (release {version.get('release')})"),
        _check_computo(pve.nodos(), nodo),
        _check_almacenamiento(pve.almacenamiento(nodo)),
        _check("Contenedor en ejecución", estado.get("status") == "running",
               f"CT {vmid} '{config.get('hostname')}': {estado.get('status')}"),
        _check("Red: IP asignada por el hipervisor", ip is not None, f"net0 = {config.get('net0')}"),
    ]
    if ip:
        checks += _checks_servicio(ip, puerto, config.get("hostname"), cliente_http)
    return {"generado": datetime.now().astimezone().isoformat(timespec="seconds"),
            "nodo": nodo, "vmid": vmid, "ip_servicio": ip, "proxmox": version,
            "ok": all(c["ok"] for c in checks), "verificaciones": checks}


def prueba_ciclo_de_vida(pve: ClienteProxmox, nodo: str, vmid: int, puerto: int,
                         espera_max_s: float = 90.0, cliente_http: httpx.Client | None = None) -> dict:
    """Detiene el contenedor por API, comprueba que el servicio cae, lo arranca y comprueba que vuelve."""
    ip = ip_de_config(pve.config_contenedor(nodo, vmid))
    http = cliente_http or httpx.Client(timeout=3.0)
    pasos = []

    pve.detener_contenedor(nodo, vmid)
    caido = _esperar(lambda: pve.estado_contenedor(nodo, vmid).get("status") == "stopped", espera_max_s)
    try:
        http.get(f"http://{ip}:{puerto}/salud")
        servicio_caido = False
    except httpx.HTTPError:
        servicio_caido = True
    pasos.append(_check("Detener por API -> contenedor 'stopped' y servicio sin respuesta",
                        caido and servicio_caido, f"stopped={caido}, servicio_caido={servicio_caido}"))

    inicio = time.monotonic()
    corriendo = _arrancar(pve, nodo, vmid, espera_max_s)
    volvio = corriendo and _esperar(lambda: _responde(http, ip, puerto), espera_max_s)
    pasos.append(_check("Iniciar por API -> el servicio vuelve a responder", volvio,
                        f"running={corriendo}, responde={volvio}, "
                        f"recuperado en {round(time.monotonic() - inicio, 1)} s"))
    return {"ok": all(p["ok"] for p in pasos), "verificaciones": pasos}


def _arrancar(pve: ClienteProxmox, nodo: str, vmid: int, espera_max_s: float) -> bool:
    """Pide el arranque y espera 'running'. Defecto 8: si la orden llega mientras Proxmox aún
    libera el bloqueo del 'stop', la tarea de arranque falla en segundo plano y el contenedor
    se queda detenido; por eso se reintenta una vez."""
    for _ in range(2):
        pve.iniciar_contenedor(nodo, vmid)
        if _esperar(lambda: pve.estado_contenedor(nodo, vmid).get("status") == "running", espera_max_s / 2):
            return True
    return False


def _responde(http: httpx.Client, ip: str, puerto: int) -> bool:
    try:
        return http.get(f"http://{ip}:{puerto}/salud").status_code == 200
    except httpx.HTTPError:
        return False


def _esperar(condicion, espera_max_s: float, intervalo_s: float = 2.0) -> bool:
    limite = time.monotonic() + espera_max_s
    while time.monotonic() < limite:
        if condicion():
            return True
        time.sleep(intervalo_s)
    return condicion()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verifica la hiperconvergencia (Proxmox VE) y el servicio.")
    parser.add_argument("--salida", default="reports", help="Carpeta donde se guarda hipervisor.json.")
    parser.add_argument("--detener", action="store_true", help="Prueba también detener y arrancar el contenedor.")
    args = parser.parse_args(argv)

    nodo = os.environ.get("PVE_NODO", "pve")
    vmid = int(os.environ.get("PVE_VMID", "200"))
    puerto = int(os.environ.get("QUALITYOPS_API_PUERTO", "8000"))
    pve = ClienteProxmox.desde_entorno()

    resultado = verificar_hiperconvergencia(pve, nodo, vmid, puerto)
    if args.detener:
        resultado["ciclo_de_vida"] = prueba_ciclo_de_vida(pve, nodo, vmid, puerto)
        resultado["ok"] = resultado["ok"] and resultado["ciclo_de_vida"]["ok"]

    print(f"\nHiperconvergencia — Proxmox VE {resultado['proxmox'].get('version')} · nodo {nodo} · CT {vmid}")
    for c in resultado["verificaciones"] + resultado.get("ciclo_de_vida", {}).get("verificaciones", []):
        print(f"  [{'OK  ' if c['ok'] else 'FALLA'}] {c['verificacion']}: {c['detalle']}")
    print(f"\nResultado: {'COMUNICACIÓN VERIFICADA' if resultado['ok'] else 'CON FALLAS'}\n")

    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "hipervisor.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if resultado["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
