"""Pruebas de seguridad automatizadas (T32): detección de vulnerabilidades + análisis con IA.

Tres escáneres, cada uno cubre un tipo de riesgo distinto:
  1. SAST (análisis estático del código)       -> Bandit: patrones inseguros en el código
     Python (subprocesos, XML sin protección, URLs sin validar, secretos en código...).
  2. SCA (análisis de composición/dependencias) -> pip-audit: dependencias con CVE
     publicados en la base de datos de vulnerabilidades de PyPI (OSV).
  3. Secretos                                   -> detect-secrets: llaves, tokens o
     contraseñas escritos en archivos del repositorio.

Política del GATE DE SEGURIDAD:
  BLOQUEA si hay  - algún hallazgo de Bandit de severidad MEDIA o ALTA,
                  - alguna dependencia con vulnerabilidad conocida,
                  - algún secreto detectado.
  Los hallazgos de severidad BAJA se reportan pero no bloquean (se revisan y justifican).

La IA (Gemini, la misma configuración que el AI Advisor) prioriza los hallazgos y
propone cómo corregirlos. Igual que en el AI Advisor, la IA NO decide: el dictamen lo da
la política anterior, y se verifica que la IA no mencione identificadores (CVE, reglas)
que no estén en los resultados de los escáneres.

Uso:
    python -m qualityops.seguridad --repo .                  # -> reports/seguridad.json
    python -m qualityops.seguridad --repo . --resumen "$GITHUB_STEP_SUMMARY"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil

# Bandit B404: se usa solo con listas de argumentos fijas, nunca con shell=True
import subprocess  # nosec B404
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from qualityops.ai_advisor import cliente_desde_entorno
from qualityops.product_metrics import encontrar_archivos_python

SEVERIDADES_QUE_BLOQUEAN = {"MEDIUM", "HIGH"}


def _ejecutar(comando: list[str], cwd: Path) -> str:
    """Corre un escáner instalado en el mismo entorno de Python y devuelve su salida (JSON)."""
    # Bandit B603: argumentos fijos
    proceso = subprocess.run(comando, cwd=cwd, capture_output=True, text=True,  # nosec B603
                             encoding="utf-8", errors="replace", check=False,
                             env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    return proceso.stdout


def escanear_codigo(repo: Path) -> list[dict]:
    """SAST con Bandit sobre el código de PRODUCTO (los mismos archivos que miden las métricas:
    sin pruebas, documentación ni entornos virtuales)."""
    archivos = [str(a.relative_to(repo)) for a in encontrar_archivos_python(repo)]
    if not archivos:
        return []
    salida = _ejecutar([sys.executable, "-m", "bandit", "-f", "json", "-q", *archivos], repo)
    datos = json.loads(salida or "{}")
    return [{"herramienta": "bandit", "id": r["test_id"], "severidad": r["issue_severity"],
             "confianza": r["issue_confidence"], "archivo": r["filename"].removeprefix("./"),
             "linea": r["line_number"], "descripcion": r["issue_text"], "cwe": r.get("issue_cwe", {}).get("id")}
            for r in datos.get("results", [])]


def escanear_dependencias(repo: Path) -> list[dict]:
    """SCA con pip-audit sobre requirements.txt (incluye dependencias transitivas)."""
    requisitos = repo / "requirements.txt"
    if not requisitos.exists():
        return []
    salida = _ejecutar([sys.executable, "-m", "pip_audit", "-r", str(requisitos), "-f", "json",
                        "--progress-spinner", "off"], repo)
    datos = json.loads(salida or "{}")
    hallazgos = []
    for dep in datos.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            hallazgos.append({"herramienta": "pip-audit", "id": vuln["id"], "severidad": "DEPENDENCIA",
                              "paquete": dep["name"], "version": dep["version"],
                              "corregida_en": ", ".join(vuln.get("fix_versions", [])) or "sin corrección"})
    return hallazgos


def escanear_secretos(repo: Path) -> list[dict]:
    """Busca secretos en los archivos versionados con detect-secrets."""
    if shutil.which("git") is None:
        return []
    salida = _ejecutar([sys.executable, "-m", "detect_secrets", "scan", "--exclude-files",
                        r"(^|/)(\.venv|venv|evidence|reports)/|\.(png|jpg|docx|pdf)$"], repo)
    datos = json.loads(salida or "{}")
    return [{"herramienta": "detect-secrets", "id": s["type"], "severidad": "SECRETO",
             "archivo": archivo, "linea": s["line_number"]}
            for archivo, lista in datos.get("results", {}).items() for s in lista]


def politica(codigo: list[dict], dependencias: list[dict], secretos: list[dict]) -> dict:
    """Aplica la política del gate de seguridad y devuelve el dictamen con sus criterios."""
    graves = [h for h in codigo if h["severidad"] in SEVERIDADES_QUE_BLOQUEAN]
    criterios = [
        {"criterio": "Código sin hallazgos de severidad media o alta (Bandit)",
         "valor": len(graves), "cumple": not graves},
        {"criterio": "Dependencias sin vulnerabilidades conocidas (pip-audit)",
         "valor": len(dependencias), "cumple": not dependencias},
        {"criterio": "Sin secretos en el repositorio (detect-secrets)",
         "valor": len(secretos), "cumple": not secretos},
    ]
    return {"aprobado": all(c["cumple"] for c in criterios), "criterios": criterios}


def resumen_hallazgos(codigo: list[dict], dependencias: list[dict], secretos: list[dict]) -> dict:
    return {"codigo_por_severidad": dict(Counter(h["severidad"] for h in codigo)),
            "dependencias_por_paquete": dict(Counter(f"{h['paquete']} {h['version']}" for h in dependencias)),
            "secretos": len(secretos)}


# --------------------------------------------------------------------------
# Análisis con IA (opcional) + verificación de que no invente identificadores
# --------------------------------------------------------------------------
PATRON_ID = re.compile(r"\b(CVE-\d{4}-\d{3,}|GHSA-[\w-]{14}|PYSEC-\d{4}-\d+|B\d{3})\b")


def construir_prompt(resultado: dict) -> str:
    codigo = [{k: h[k] for k in ("id", "severidad", "archivo", "linea", "descripcion")} for h in resultado["codigo"]]
    deps = resultado["resumen"]["dependencias_por_paquete"]
    ejemplos = sorted({h["id"] for h in resultado["dependencias"]})[:5]
    return ("Eres un analista de seguridad de aplicaciones. Con los hallazgos REALES de los escáneres "
            "(no inventes otros ni otros identificadores) escribe en español: 1) los hallazgos ordenados por "
            "prioridad con una frase de por qué importan, 2) la corrección concreta para cada uno (código o "
            "versión a la que actualizar), 3) qué hallazgos de severidad baja pueden aceptarse y con qué "
            "justificación. Sé breve.\n\nDictamen del gate (no lo cambies): "
            + ("APROBADO" if resultado["gate"]["aprobado"] else "BLOQUEADO")
            + "\n\nHallazgos de código (Bandit):\n" + json.dumps(codigo, ensure_ascii=False)
            + "\n\nDependencias vulnerables (pip-audit), paquete -> número de vulnerabilidades:\n"
            + json.dumps(deps, ensure_ascii=False) + "\nEjemplos de identificadores: " + ", ".join(ejemplos)
            + f"\n\nSecretos detectados: {resultado['resumen']['secretos']}")


def ids_inventados(texto: str, resultado: dict) -> list[str]:
    """Identificadores que la IA menciona y que NO aparecen en los resultados de los escáneres."""
    conocidos = {h["id"] for h in resultado["codigo"] + resultado["dependencias"]}
    return sorted({i for i in PATRON_ID.findall(texto) if i not in conocidos})


def analizar_con_ia(resultado: dict, cliente=None) -> dict:
    """Agrega la interpretación de la IA si hay llave; si falla o no hay, lo dice."""
    cliente = cliente if cliente is not None else cliente_desde_entorno()
    if cliente is None:
        return {"fuente": "no configurado", "texto": None}
    try:
        texto = cliente(construir_prompt(resultado)).strip()
    except Exception as error:  # noqa: BLE001  la seguridad no depende de la IA
        return {"fuente": "error", "texto": None, "error": f"{type(error).__name__}: {error}"}
    inventados = ids_inventados(texto, resultado)
    return {"fuente": "llm", "texto": texto, "ids_no_verificados": inventados,
            "coherente": not inventados}


def analizar(repo: Path, usar_ia: bool = True) -> dict:
    repo = Path(repo).resolve()
    codigo, dependencias, secretos = escanear_codigo(repo), escanear_dependencias(repo), escanear_secretos(repo)
    resultado = {"generado": datetime.now().astimezone().isoformat(timespec="seconds"), "repo": repo.name,
                 "codigo": codigo, "dependencias": dependencias, "secretos": secretos,
                 "resumen": resumen_hallazgos(codigo, dependencias, secretos),
                 "gate": politica(codigo, dependencias, secretos)}
    resultado["ia"] = analizar_con_ia(resultado) if usar_ia else {"fuente": "omitida", "texto": None}
    return resultado


def resumen_markdown(r: dict) -> str:
    dictamen = "✅ APROBADO" if r["gate"]["aprobado"] else "❌ BLOQUEADO"
    filas = [f"| {'✅' if c['cumple'] else '❌'} | {c['criterio']} | {c['valor']} |" for c in r["gate"]["criterios"]]
    totales = (f"Código por severidad: {r['resumen']['codigo_por_severidad']} · "
               f"dependencias: {r['resumen']['dependencias_por_paquete'] or 'ninguna vulnerable'}")
    texto = [f"## Gate de seguridad — {dictamen}", "", "| | Criterio | Hallazgos |", "|---|---|---|", *filas, "",
             totales, ""]
    if r["ia"].get("texto"):
        texto += ["### Análisis de la IA", "", r["ia"]["texto"], ""]
    return "\n".join(texto)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pruebas de seguridad de QualityOps AI.")
    parser.add_argument("--repo", default=".", help="Proyecto a escanear.")
    parser.add_argument("--salida", default="reports", help="Carpeta donde se guarda seguridad.json.")
    parser.add_argument("--sin-ia", action="store_true", help="No llamar al modelo de lenguaje.")
    parser.add_argument("--resumen", help="Archivo Markdown donde AGREGAR el resultado (p. ej. $GITHUB_STEP_SUMMARY).")
    args = parser.parse_args(argv)

    r = analizar(Path(args.repo), usar_ia=not args.sin_ia)
    print(f"\nPruebas de seguridad — {r['repo']}")
    print(f"  Código (Bandit):        {r['resumen']['codigo_por_severidad'] or 'sin hallazgos'}")
    for h in r["codigo"]:
        print(f"      {h['severidad']:<6} {h['id']}  {h['archivo']}:{h['linea']}  {h['descripcion'][:70]}")
    print(f"  Dependencias (pip-audit): {r['resumen']['dependencias_por_paquete'] or 'sin vulnerabilidades'}")
    print(f"  Secretos (detect-secrets): {r['resumen']['secretos']}")
    print(f"  Análisis de IA: {r['ia']['fuente']}")
    for c in r["gate"]["criterios"]:
        print(f"  [{'OK  ' if c['cumple'] else 'FALLA'}] {c['criterio']}: {c['valor']}")
    print(f"\nGate de seguridad: {'APROBADO' if r['gate']['aprobado'] else 'BLOQUEADO'}\n")

    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "seguridad.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.resumen:
        with open(args.resumen, "a", encoding="utf-8") as archivo:
            archivo.write(resumen_markdown(r))
    return 0 if r["gate"]["aprobado"] else 1


if __name__ == "__main__":
    sys.exit(main())
