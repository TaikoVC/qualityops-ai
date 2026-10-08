"""Informe de calidad con formato fijo, basado en el informe de finalización de
pruebas de ISO/IEC/IEEE 29119-3:2021 (decisión D09).

Requisito que cubre: CAL-02 (establecer en un formato un informe de calidad).

Lee reports/metrics.json y reports/gate.json, pide la interpretación al AI
Advisor (LLM si está disponible; si no, reglas) y escribe:
  - reports/ai_analysis.json   (entrada y salida de la IA: evidencia de PRG-02)
  - reports/quality_report.md  (el informe)

Dictamen de liberación:
  - NO LIBERAR               si el quality gate bloquea.
  - LIBERAR CON CONDICIONES  si el gate aprueba pero hay métricas sin datos o
                             verificaciones de coherencia que fallan.
  - LIBERAR                  en otro caso.

Uso:
    python -m qualityops.report --metricas reports/metrics.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qualityops.ai_advisor import analizar, cliente_desde_entorno


def dictamen(gate: dict | None, analisis: dict) -> str:
    """Decide el estado de liberación con criterios explícitos."""
    if gate is None or not gate["aprobado"]:
        return "NO LIBERAR"
    hay_huecos = any(i["valoracion"] == "sin datos" for i in analisis["interpretaciones"])
    incoherente = not all(v["ok"] for v in analisis["verificaciones"])
    return "LIBERAR CON CONDICIONES" if hay_huecos or incoherente else "LIBERAR"


def _tabla(cabeceras: list[str], filas: list[list]) -> list[str]:
    lineas = ["| " + " | ".join(cabeceras) + " |", "|" + "---|" * len(cabeceras)]
    lineas += ["| " + " | ".join("—" if v is None else str(v) for v in f) + " |" for f in filas]
    return lineas + [""]


def _defectos_por_severidad(defectos: list[dict]) -> list[list]:
    filas = []
    for sev in ("critica", "mayor", "menor", "sin_clasificar"):
        del_sev = [d for d in defectos if d["severidad"] == sev]
        fases = {f: sum(1 for d in del_sev if d["fase"] == f) for f in ("revision", "pruebas", "produccion")}
        filas.append([sev, len(del_sev), fases["revision"], fases["pruebas"], fases["produccion"]])
    return filas


def _secciones_metricas(m: dict) -> list[str]:
    prod, proc, proy, est = m["producto"], m["proceso"], m["proyecto"], m["estimacion"]
    out = ["## 5. Métricas de producto", ""]
    out += _tabla(["Métrica", "Valor"], [
        ["Complejidad ciclomática (promedio / máximo)", f"{prod['complejidad']['promedio']} / {prod['complejidad']['maximo']}"],
        ["Cobertura de código", f"{prod['cobertura']['global_pct']} %"],
        ["Tamaño", f"{prod['lineas']['kloc']} KLOC ({prod['lineas']['n_archivos']} archivos)"],
        ["Densidad de defectos", f"{prod['densidad']['densidad_global']} def/KLOC (n = {prod['densidad']['n_defectos']})"],
    ])
    out += ["## 6. Métricas de proceso", ""]
    out += _tabla(["Métrica", "Valor", "n"], [
        ["MTTD (mediana, h)", proc["mttd"]["mediana_h"], proc["mttd"]["n"]],
        ["MTTR (mediana, h)", proc["mttr"]["mediana_h"], proc["mttr"]["n"]],
        ["Eficacia de pruebas (críticos, %)", proc["eficacia_pruebas"]["criticos"]["pct"],
         proc["eficacia_pruebas"]["criticos"]["con_fase_conocida"]],
    ])
    out += ["## 7. Métricas de proyecto", ""]
    out += _tabla(["Métrica", "Valor"], [
        ["Eficacia de la revisión (%)", proy["eficacia_revision"]["pct"]],
        ["Desviación de tiempo y esfuerzo (%)", proy["desviacion"]["desviacion_pct"]],
        ["Tareas a tiempo (%)", proy["plazos"]["pct_a_tiempo"]],
    ])
    out += ["## 8. Estimación (horas)", ""]
    out += _tabla(["Técnica", "Horas"], [
        ["Juicio de expertos", est["juicio_expertos"]["horas"]],
        ["Análoga", est["analoga"]["horas"]],
        ["Tres puntos (PERT)", f"{est['tres_puntos']['horas']} ± {est['tres_puntos']['sigma_h']}"],
        ["Puntos de función", f"{est['puntos_de_funcion']['horas']} ({est['puntos_de_funcion']['pf_sin_ajustar']} PF)"],
        ["Real (tareas terminadas)", proy["desviacion"]["real_h"]],
    ])
    return out


def generar_informe(m: dict, gate: dict | None, analisis: dict) -> str:
    """Arma el informe en Markdown con las secciones del formato fijo."""
    estado = dictamen(gate, analisis)
    p = m["pruebas"]
    out = [
        "# Informe de calidad — QualityOps AI",
        "",
        "_Formato basado en el informe de finalización de pruebas (ISO/IEC/IEEE 29119-3:2021)._",
        "",
        "## 1. Identificación",
        "",
    ]
    out += _tabla(["Campo", "Valor"], [
        ["Proyecto", m["repo"]], ["Commit analizado", m["commit"]], ["Fecha de generación", m["generado"]],
        ["Herramienta", f"{m['herramienta']['nombre']} {m['herramienta']['version']}"],
        ["Fuente de la interpretación", analisis["fuente"]],
    ])
    out += ["## 2. Resumen y dictamen de liberación", "", f"**Dictamen: {estado}**", ""]
    out += [f"- {r}" for r in analisis["recomendaciones"]] + [""]
    out += ["## 3. Resultados de las pruebas", ""]
    out += _tabla(["Total", "Aprobadas", "Fallidas", "Errores", "Omitidas"],
                  [[p["total"], p["aprobadas"], p["fallidas"], p["errores"], p.get("omitidas", 0)]])
    out += ["## 4. Criterios de salida (quality gate)", ""]
    out += _tabla(["Cumple", "Criterio", "Valor", "Umbral"],
                  [["Sí" if c["cumple"] else "No", c["criterio"], c["valor"], c["umbral"]]
                   for c in (gate or {"criterios": []})["criterios"]])
    out += _secciones_metricas(m)
    out += ["## 9. Defectos por severidad y fase de detección", ""]
    out += _tabla(["Severidad", "Total", "Revisión", "Pruebas", "Producción"], _defectos_por_severidad(m["defectos"]["defectos"]))
    out += ["## 10. Interpretación", ""]
    out += [f"- **{i['metrica']}** ({i['valoracion']}): {i['texto']}" for i in analisis["interpretaciones"]] + [""]
    if analisis.get("texto_llm"):
        out += ["### Interpretación del modelo de lenguaje", "", analisis["texto_llm"], ""]
    out += ["## 11. Verificaciones de coherencia", ""]
    out += _tabla(["Resultado", "Verificación"], [["OK" if v["ok"] else "FALLA", v["verificacion"]] for v in analisis["verificaciones"]])
    out += ["## 12. Aprobación", "", "Responsable: ______________________   Fecha: ____________", ""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genera el informe de calidad.")
    parser.add_argument("--metricas", default="reports/metrics.json", help="Ruta de metrics.json.")
    args = parser.parse_args(argv)

    ruta = Path(args.metricas)
    m = json.loads(ruta.read_text(encoding="utf-8"))
    ruta_gate = ruta.parent / "gate.json"
    gate = json.loads(ruta_gate.read_text(encoding="utf-8")) if ruta_gate.exists() else None

    analisis = analizar(m, gate, cliente_desde_entorno())
    (ruta.parent / "ai_analysis.json").write_text(json.dumps(analisis, indent=2, ensure_ascii=False), encoding="utf-8")
    (ruta.parent / "quality_report.md").write_text(generar_informe(m, gate, analisis), encoding="utf-8")
    print(f"Informe generado: {ruta.parent / 'quality_report.md'} · dictamen: {dictamen(gate, analisis)} "
          f"· interpretación: {analisis['fuente']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
