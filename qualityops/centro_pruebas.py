"""Centro de pruebas (T34): ejecuta las pruebas por TIPO y arma la documentación de casos.

Cada caso de prueba documentado en docs/pruebas/casos.toml tiene los componentes
principales de la documentación de pruebas: identificador, descripción, datos de entrada,
pasos de ejecución, resultado esperado y resultado OBTENIDO.

- Casos automatizados: el resultado obtenido se llena solo, leyendo el reporte JUnit de
  pytest. La prueba se encuentra por su nombre: el caso CP-API-01 es la prueba
  test_cp_api_01_... (también sus variantes parametrizadas).
- Casos manuales: el resultado obtenido lo escribe la persona que ejecutó la prueba
  (campo `obtenido` y la captura de evidencia).

Uso (también lo usan los botones del dashboard):
    python -m qualityops.centro_pruebas --tipo humo
    python -m qualityops.centro_pruebas --tipo todas      # -> reports/casos_prueba.json
"""

from __future__ import annotations

import argparse
import json
import os

# Bandit B404: se ejecuta pytest con argumentos fijos, sin shell
import subprocess  # nosec B404
import sys
import tomllib
from pathlib import Path

from defusedxml import ElementTree

# Tipo de prueba (marcador de pytest) -> descripción breve para la interfaz y el reporte.
TIPOS = {
    "humo": "Lo esencial arranca: módulos, CLI y API responden",
    "unitaria": "Funciones aisladas con entradas conocidas",
    "componente": "Un módulo completo por su interfaz pública (API, cliente de Proxmox, AI Advisor)",
    "integracion": "Varios módulos juntos (CLI, ciclo de vida del contenedor)",
    "sistema": "El producto completo de punta a punta (métricas -> gate -> informe)",
    "aceptacion": "Criterios de aceptación del usuario (Dado / Cuando / Entonces)",
    "interfaz": "Contrato de la API, de la CLI y del dashboard",
    "funcional": "Particiones de equivalencia y valores límite de los umbrales",
    "no_funcional": "Rendimiento: tiempos de respuesta del gate y de la API",
    "exploratoria": "Hypothesis genera cientos de entradas al azar buscando fallas",
    "usabilidad": "El dashboard guía al usuario, no muestra errores y responde rápido",
    "seguridad": "Validación de entradas, token, encabezados, TLS y escáner de vulnerabilidades",
    "hipervisor": "API de Proxmox VE y servicio en el contenedor (requiere la VM encendida)",
}

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / "docs" / "pruebas" / "casos.toml"


def ejecutar_tipo(tipo: str, salida: Path, raiz: Path = RAIZ) -> dict:
    """Corre pytest solo con las pruebas de un tipo (o todas) y devuelve los resultados por prueba."""
    salida.mkdir(parents=True, exist_ok=True)
    junit = salida / f"pruebas_{tipo}.xml"
    comando = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={junit}"]
    if tipo != "todas":
        comando += ["-m", tipo]
    # Bandit B603: argumentos fijos
    proceso = subprocess.run(comando, cwd=raiz, capture_output=True, text=True,  # nosec B603
                             encoding="utf-8", errors="replace", check=False,
                             env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    resultados = leer_junit(junit)
    return {"tipo": tipo, "codigo_salida": proceso.returncode, "pruebas": resultados,
            "resumen": resumir(resultados), "salida": proceso.stdout[-3000:]}


def leer_junit(ruta: Path) -> list[dict]:
    """Lista de pruebas con su resultado (aprobada, fallida, error u omitida) y su tiempo."""
    if not ruta.exists():
        return []
    pruebas = []
    for caso in ElementTree.parse(ruta).getroot().iter("testcase"):
        resultado = "aprobada"
        for etiqueta, nombre in (("failure", "fallida"), ("error", "error"), ("skipped", "omitida")):
            if caso.find(etiqueta) is not None:
                resultado = nombre
        pruebas.append({"prueba": caso.get("name"), "archivo": caso.get("classname"),
                        "resultado": resultado, "segundos": float(caso.get("time", 0))})
    return pruebas


def resumir(pruebas: list[dict]) -> dict:
    resumen = {"total": len(pruebas)}
    for estado in ("aprobada", "fallida", "error", "omitida"):
        resumen[estado] = sum(p["resultado"] == estado for p in pruebas)
    return resumen


def cargar_catalogo(ruta: Path = CATALOGO) -> list[dict]:
    if not ruta.exists():
        return []
    return tomllib.loads(ruta.read_text(encoding="utf-8")).get("caso", [])


def prefijo_de_prueba(id_caso: str) -> str:
    """CP-API-01 -> test_cp_api_01 (inicio del nombre de la función de pytest)."""
    return "test_" + id_caso.lower().replace("-", "_")


def resultado_de_caso(caso: dict, pruebas: list[dict]) -> dict:
    """Resultado obtenido de un caso: manual (lo que se registró) o automático (JUnit)."""
    if caso.get("modo") == "manual":
        return {"obtenido": caso.get("obtenido", "Pendiente de ejecutar"),
                "estado": caso.get("estado", "pendiente")}
    prefijo = caso.get("prueba") or prefijo_de_prueba(caso["id"])
    propias = [p for p in pruebas if p["prueba"].split("[")[0] == prefijo or p["prueba"].startswith(prefijo + "_")]
    if not propias:
        return {"obtenido": "No ejecutada en esta corrida", "estado": "sin ejecutar"}
    return _resultado_automatico(resumir(propias))


def _resultado_automatico(resumen: dict) -> dict:
    """Estado del caso según sus ejecuciones: falla si alguna falla; omitida si todas se omitieron."""
    if resumen["fallida"] or resumen["error"]:
        estado = "falla"
    elif resumen["omitida"] == resumen["total"]:
        estado = "omitida"
    else:
        estado = "pasa"
    detalle = f"{resumen['aprobada']}/{resumen['total']} ejecuciones aprobadas"
    if resumen["omitida"]:
        detalle += f", {resumen['omitida']} omitidas"
    return {"obtenido": detalle, "estado": estado}


def documentar(pruebas: list[dict], catalogo: list[dict] | None = None) -> list[dict]:
    """Catálogo de casos con el resultado obtenido de cada uno."""
    catalogo = cargar_catalogo() if catalogo is None else catalogo
    return [{**caso, **resultado_de_caso(caso, pruebas)} for caso in catalogo]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ejecuta las pruebas por tipo y documenta los casos.")
    parser.add_argument("--tipo", default="todas", choices=["todas", *TIPOS])
    parser.add_argument("--salida", default="reports")
    args = parser.parse_args(argv)

    r = ejecutar_tipo(args.tipo, Path(args.salida))
    casos = documentar(r["pruebas"])
    Path(args.salida, "casos_prueba.json").write_text(
        json.dumps({"tipo": args.tipo, "resumen": r["resumen"], "casos": casos}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"\nPruebas '{args.tipo}': {r['resumen']}")
    for c in casos:
        if c["estado"] != "sin ejecutar":
            print(f"  [{c['estado']:<8}] {c['id']:<11} {c['descripcion'][:60]}  -> {c['obtenido']}")
    return 0 if r["codigo_salida"] in (0, 5) else 1    # 5 = no hubo pruebas de ese tipo


if __name__ == "__main__":
    sys.exit(main())
