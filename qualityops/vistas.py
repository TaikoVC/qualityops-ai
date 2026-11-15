"""Vistas nuevas del dashboard (T34): Centro de pruebas, Seguridad e Hipervisor.

Cada botón ejecuta EL MISMO comando de línea de comandos que se documenta en la guía
(así la interfaz no tiene lógica propia que pueda diferir de la CLI) y luego muestra el
JSON que ese comando dejó en la carpeta de reportes.
"""

from __future__ import annotations

import json
import os

# Bandit B404: se ejecutan módulos de QualityOps con argumentos fijos, sin shell
import subprocess  # nosec B404
import sys
from pathlib import Path

import streamlit as st

from qualityops.centro_pruebas import RAIZ, TIPOS, cargar_catalogo, documentar

ICONOS = {"pasa": "✅", "falla": "❌", "omitida": "⏭️", "sin ejecutar": "⬜", "pendiente": "🕒"}


# Defecto 7: en Windows, un proceso hijo cuya salida va a un tubo (pipe) escribe con la
# codificación del sistema (cp1252), no UTF-8. Al leer "↔" o acentos como UTF-8 fallaba la
# lectura y stdout quedaba en None. Se fuerza UTF-8 en el hijo y se reemplaza lo ilegible.
ENTORNO_UTF8 = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


def _correr(modulo: str, *args: str, entorno: dict | None = None) -> subprocess.CompletedProcess:
    """Ejecuta `python -m qualityops.<modulo> ...` desde la raíz del proyecto."""
    return subprocess.run([sys.executable, "-m", f"qualityops.{modulo}", *args], cwd=RAIZ,  # nosec B603
                          capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
                          env={**os.environ, **(entorno or {}), **ENTORNO_UTF8})


def _leer(ruta: Path) -> dict | None:
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def _salida(proceso: subprocess.CompletedProcess) -> None:
    with st.expander("Salida del comando"):
        st.code(((proceso.stdout or "") + (proceso.stderr or ""))[-4000:] or "(sin salida)")


# --------------------------------------------------------------------------
def vista_centro_pruebas(carpeta: Path) -> None:
    st.subheader("Centro de pruebas")
    st.caption("Elige un tipo de prueba y ejecútalo. Los resultados llenan la columna «obtenido» de cada caso.")
    tipo = st.selectbox("Tipo de prueba", ["todas", *TIPOS],
                        format_func=lambda t: "todas — la suite completa" if t == "todas" else f"{t} — {TIPOS[t]}")
    if st.button("▶ Ejecutar pruebas", type="primary", key="btn_pruebas"):
        with st.spinner(f"Ejecutando pruebas '{tipo}'..."):
            _salida(_correr("centro_pruebas", "--tipo", tipo, "--salida", str(carpeta)))

    datos = _leer(carpeta / "casos_prueba.json")
    if datos:
        r = datos["resumen"]
        st.markdown(f"**Última ejecución: `{datos['tipo']}`**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ejecutadas", r["total"])
        c2.metric("Aprobadas", r["aprobada"])
        c3.metric("Fallidas + errores", r["fallida"] + r["error"])
        c4.metric("Omitidas", r["omitida"])
        casos = datos["casos"]
    else:
        st.info("Aún no hay resultados: presiona «Ejecutar pruebas». Abajo está el catálogo de casos.")
        casos = documentar([], cargar_catalogo())

    st.markdown("**Documentación de casos de prueba**")
    st.dataframe([{"estado": ICONOS.get(c["estado"], "") + " " + c["estado"], "id": c["id"], "tipo": c["tipo"],
                   "técnica": c.get("tecnica", ""), "descripción": c["descripcion"], "entrada": c["entrada"],
                   "pasos": c["pasos"], "esperado": c["esperado"], "obtenido": c["obtenido"]} for c in casos],
                 use_container_width=True, hide_index=True)


# --------------------------------------------------------------------------
def vista_seguridad(carpeta: Path) -> None:
    st.subheader("Pruebas de seguridad")
    st.caption("Bandit (código), pip-audit (dependencias) y detect-secrets (secretos). La IA prioriza y propone "
               "correcciones; el dictamen lo da la política, no la IA.")
    usar_ia = st.checkbox("Analizar los hallazgos con IA (requiere GEMINI_API_KEY)",
                          value=bool(os.environ.get("GEMINI_API_KEY")))
    if st.button("🔍 Escanear vulnerabilidades", type="primary", key="btn_seguridad"):
        with st.spinner("Escaneando código, dependencias y secretos..."):
            _salida(_correr("seguridad", "--repo", ".", "--salida", str(carpeta), *([] if usar_ia else ["--sin-ia"])))

    r = _leer(carpeta / "seguridad.json")
    if not r:
        st.info("Aún no hay escaneo: presiona «Escanear vulnerabilidades».")
        return
    st.markdown(f"### Gate de seguridad: {'✅ APROBADO' if r['gate']['aprobado'] else '❌ BLOQUEADO'}")
    st.dataframe(r["gate"]["criterios"], use_container_width=True, hide_index=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Hallazgos en código", len(r["codigo"]))
    c2.metric("Vulnerabilidades en dependencias", len(r["dependencias"]))
    c3.metric("Secretos", len(r["secretos"]))
    if r["codigo"]:
        st.markdown("**Código (Bandit)**")
        st.dataframe(r["codigo"], use_container_width=True, hide_index=True)
    if r["dependencias"]:
        st.markdown("**Dependencias (pip-audit)**")
        st.dataframe(r["dependencias"], use_container_width=True, hide_index=True)
    ia = r.get("ia", {})
    st.markdown(f"**Análisis de IA — fuente: {ia.get('fuente')}**")
    if ia.get("texto"):
        if ia.get("ids_no_verificados"):
            st.warning("La IA mencionó identificadores que los escáneres NO reportan: "
                       + ", ".join(ia["ids_no_verificados"]))
        st.markdown(ia["texto"])
    elif ia.get("error"):
        st.warning(f"La IA no respondió: {ia['error']}")


# --------------------------------------------------------------------------
def vista_hipervisor(carpeta: Path) -> None:
    st.subheader("Hipervisor e hiperconvergencia (Proxmox VE)")
    st.caption("Laptop → API de Proxmox (cómputo, almacenamiento, red) → contenedor 200 → API de QualityOps.")
    c1, c2 = st.columns(2)
    url = c1.text_input("URL de Proxmox", os.environ.get("PVE_URL", "https://192.168.56.10:8006"))
    token_id = c2.text_input("Token ID", os.environ.get("PVE_TOKEN_ID", "qa@pve!qualityops"))
    ca = c1.text_input("Certificado raíz (CA) de Proxmox", os.environ.get("PVE_CA", "infra/pve-root-ca.pem"))
    secreto = c2.text_input("Secreto del token (no se guarda)", os.environ.get("PVE_TOKEN_SECRET", ""), type="password")
    detener = st.checkbox("Probar también detener y arrancar el contenedor (tarda ~30 s)")

    if st.button("🔗 Verificar comunicación", type="primary", key="btn_hipervisor"):
        if not secreto:
            st.error("Falta el secreto del token de Proxmox.")
        else:
            entorno = {"PVE_URL": url, "PVE_TOKEN_ID": token_id, "PVE_CA": ca, "PVE_TOKEN_SECRET": secreto}
            with st.spinner("Consultando la API de Proxmox y el servicio del contenedor..."):
                _salida(_correr("hipervisor", "--salida", str(carpeta), *(["--detener"] if detener else []),
                                entorno=entorno))

    r = _leer(carpeta / "hipervisor.json")
    if not r:
        st.info("Aún no hay verificación: llena el secreto y presiona «Verificar comunicación».")
        return
    st.markdown(f"### {'✅ COMUNICACIÓN VERIFICADA' if r['ok'] else '❌ CON FALLAS'} · Proxmox VE "
                f"{r['proxmox'].get('version')} · nodo {r['nodo']} · CT {r['vmid']} · {r['generado']}")
    filas = r["verificaciones"] + r.get("ciclo_de_vida", {}).get("verificaciones", [])
    st.dataframe([{"": "✅" if c["ok"] else "❌", "verificación": c["verificacion"], "detalle": c["detalle"]}
                  for c in filas], use_container_width=True, hide_index=True)
