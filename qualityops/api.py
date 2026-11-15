"""API REST de QualityOps AI (T30): el quality gate como SERVICIO.

Para qué existe: en la demostración de hiperconvergencia, este servicio corre dentro
de un contenedor LXC administrado por Proxmox VE (hipervisor). Las pruebas de API y de
servicios lo llaman por la red y comprueban que responde lo mismo que la herramienta
de línea de comandos.

Endpoints:
  GET  /salud      -> el servicio está vivo; devuelve el nombre del equipo (hostname)
                      para comprobar QUÉ máquina respondió (el contenedor de Proxmox).
  GET  /version    -> versión de QualityOps y de Python.
  POST /gate       -> evalúa un conjunto de métricas contra los umbrales y devuelve el
                      dictamen APROBADO / BLOQUEADO (misma lógica que quality_gate.py).
  GET  /metricas   -> el último reports/metrics.json generado en el equipo del servicio.

Seguridad (pruebas de seguridad, sección 21 del reporte):
  - Si existe la variable QUALITYOPS_API_TOKEN, POST /gate exige el encabezado
    X-API-Key con ese valor (comparación en tiempo constante).
  - Toda entrada se valida con Pydantic (tipos y rangos); los datos inválidos
    se rechazan con 422 sin mostrar trazas internas.
  - Cada respuesta lleva encabezados de seguridad (nosniff, no-store, DENY).

Ejecutar:
    uvicorn qualityops.api:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import json
import os
import platform
import secrets
import socket
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from qualityops import __version__
from qualityops.quality_gate import UMBRALES_POR_DEFECTO, evaluar

app = FastAPI(
    title="QualityOps AI — API",
    version=__version__,
    description="Quality gate como servicio. Pensado para correr en un contenedor de Proxmox VE.",
)

# Encabezados que se agregan a TODAS las respuestas (pruebas de seguridad).
ENCABEZADOS_SEGUROS = {
    "X-Content-Type-Options": "nosniff",      # el navegador no "adivina" el tipo de contenido
    "X-Frame-Options": "DENY",                # la API no se puede incrustar en otra página
    "Cache-Control": "no-store",              # los resultados no se guardan en cachés
    "Referrer-Policy": "no-referrer",
}


@app.middleware("http")
async def agregar_encabezados_seguros(request: Request, call_next):
    """Agrega los encabezados de seguridad a cada respuesta."""
    respuesta = await call_next(request)
    for nombre, valor in ENCABEZADOS_SEGUROS.items():
        respuesta.headers[nombre] = valor
    return respuesta


# --------------------------------------------------------------------------
# Modelos de entrada (validación de datos)
# --------------------------------------------------------------------------
class Pruebas(BaseModel):
    total: int = Field(ge=0)
    aprobadas: int = Field(ge=0)
    fallidas: int = Field(ge=0)
    errores: int = Field(ge=0)


class Umbrales(BaseModel):
    cobertura_minima: float = Field(default=UMBRALES_POR_DEFECTO["cobertura_minima"], ge=0, le=100)
    complejidad_maxima: int = Field(default=UMBRALES_POR_DEFECTO["complejidad_maxima"], ge=1, le=100)


class SolicitudGate(BaseModel):
    pruebas: Pruebas
    cobertura: float | None = Field(default=None, ge=0, le=100)
    complejidad_maxima: int | None = Field(default=None, ge=0)
    umbrales: Umbrales = Umbrales()


def _verificar_token(x_api_key: str | None) -> None:
    """Si el servicio tiene token configurado, exige que la petición lo traiga."""
    esperado = os.environ.get("QUALITYOPS_API_TOKEN")
    if not esperado:
        return
    if x_api_key is None or not secrets.compare_digest(x_api_key, esperado):
        raise HTTPException(status_code=401, detail="Falta o es incorrecto el encabezado X-API-Key")


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------
@app.get("/salud")
def salud() -> dict:
    """El servicio responde; incluye el nombre del equipo que atendió la petición."""
    return {"estado": "ok", "servicio": "qualityops-api", "version": __version__,
            "host": socket.gethostname(), "hora": datetime.now().astimezone().isoformat(timespec="seconds")}


@app.get("/version")
def version() -> dict:
    return {"qualityops": __version__, "python": platform.python_version()}


@app.post("/gate")
def gate(solicitud: SolicitudGate, x_api_key: str | None = Header(default=None)) -> dict:
    """Evalúa las métricas recibidas con la MISMA función que usa el pipeline."""
    _verificar_token(x_api_key)
    metricas = {
        "pruebas": solicitud.pruebas.model_dump(),
        "producto": {"cobertura": {"global_pct": solicitud.cobertura},
                     "complejidad": {"maximo": solicitud.complejidad_maxima}},
    }
    resultado = evaluar(metricas, solicitud.umbrales.model_dump())
    resultado["dictamen"] = "APROBADO" if resultado["aprobado"] else "BLOQUEADO"
    return resultado


@app.get("/metricas")
def metricas() -> dict:
    """Último metrics.json generado en el equipo del servicio (404 si no existe)."""
    ruta = Path(os.environ.get("QUALITYOPS_REPORTS", "reports")) / "metrics.json"
    if not ruta.exists():
        raise HTTPException(status_code=404, detail="Aún no hay métricas: ejecuta python -m qualityops")
    return json.loads(ruta.read_text(encoding="utf-8"))
