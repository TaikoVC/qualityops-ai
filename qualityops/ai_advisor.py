"""AI Advisor: interpreta las métricas, verifica su coherencia y recomienda acciones.

Requisitos que cubre: PRG-02 (IA en el framework) y MET-00 (calcular las
métricas aplicando la IA).

Principio (decisión D02): las CIFRAS las calcula el motor de forma determinista;
la IA NO calcula números, los interpreta. Por eso este módulo:
  1. Siempre ejecuta verificaciones de coherencia deterministas sobre metrics.json
     (por ejemplo, que la cobertura global sea líneas ejecutadas / ejecutables).
  2. Interpreta cada métrica con REGLAS basadas en referencias publicadas
     (McCabe, Google Testing Blog, DORA, Jones). Es la ruta de respaldo.
  3. Si hay un modelo de lenguaje disponible (variable ANTHROPIC_API_KEY y el
     paquete `anthropic` instalado), le envía el resumen de métricas y las
     verificaciones para que redacte la interpretación; si falla por cualquier
     motivo, se usa la ruta por reglas (decisión D03: la app nunca se cae por la IA).

El resultado indica siempre su "fuente": "reglas" o "llm".
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable

# Modelo configurable sin tocar el código (variable de entorno opcional).
MODELO_POR_DEFECTO = os.environ.get("QUALITYOPS_MODELO", "claude-sonnet-4-5")


# --------------------------------------------------------------------------
# 1. Verificaciones de coherencia (deterministas)
# --------------------------------------------------------------------------
def _cerca(a, b, tolerancia=0.01) -> bool:
    return a is None and b is None or (a is not None and b is not None and abs(a - b) <= tolerancia)


def verificar_coherencia(m: dict) -> list[dict]:
    """Comprueba que los valores de metrics.json sean consistentes entre sí."""
    cob, lin, den, pru = (m["producto"]["cobertura"], m["producto"]["lineas"],
                          m["producto"]["densidad"], m["pruebas"])
    cob_calc = round(100 * cob["lineas_ejecutadas"] / cob["lineas_ejecutables"], 2) if cob["lineas_ejecutables"] else None
    den_calc = round(den["n_defectos"] / lin["kloc"], 2) if lin["kloc"] else None
    suma = pru["aprobadas"] + pru["fallidas"] + pru["errores"] + pru.get("omitidas", 0)
    return [
        {"verificacion": "Cobertura = ejecutadas / ejecutables × 100", "ok": _cerca(cob["global_pct"], cob_calc)},
        {"verificacion": "KLOC = SLOC / 1000", "ok": _cerca(lin["kloc"], round(lin["sloc"] / 1000, 3), 0.001)},
        {"verificacion": "Densidad = defectos / KLOC", "ok": _cerca(den["densidad_global"], den_calc)},
        {"verificacion": "Pruebas: aprobadas + fallidas + errores + omitidas = total", "ok": suma == pru["total"]},
        {"verificacion": "Defectos de la minería = defectos usados en la densidad",
         "ok": m["defectos"]["n_defectos"] == den["n_defectos"]},
    ]


# --------------------------------------------------------------------------
# 2. Interpretación por reglas (ruta de respaldo, siempre disponible)
# --------------------------------------------------------------------------
def _nivel(valor, cortes: list[tuple[float, str]], mayor_es_mejor=True) -> str:
    """Devuelve la etiqueta del primer corte que cumple el valor."""
    for corte, etiqueta in cortes:
        if (valor >= corte) if mayor_es_mejor else (valor <= corte):
            return etiqueta
    return "mejorable"


def _interp_producto(m: dict) -> list[dict]:
    cc, cob, den = m["producto"]["complejidad"], m["producto"]["cobertura"], m["producto"]["densidad"]
    salida = []
    if cc["maximo"] is not None:
        salida.append({"metrica": "Complejidad ciclomática",
                       "valoracion": _nivel(cc["maximo"], [(10, "buena"), (20, "aceptable")], mayor_es_mejor=False),
                       "texto": f"Promedio {cc['promedio']} y máximo {cc['maximo']}; {cc['en_bajo_riesgo']} de "
                                f"{cc['n_funciones']} funciones con CC ≤ 10 (bajo riesgo según McCabe, 1976)."})
    if cob["global_pct"] is not None:
        bajos = [a["archivo"] for a in cob["por_archivo"] if a["pct"] is not None and a["pct"] < 60]
        salida.append({"metrica": "Cobertura de código",
                       "valoracion": _nivel(cob["global_pct"], [(90, "ejemplar"), (75, "encomiable"), (60, "aceptable")]),
                       "texto": f"{cob['global_pct']} % global (Google Testing Blog: 60 aceptable, 75 encomiable, 90 ejemplar)."
                                # Los nombres van entre comillas invertidas para que el Markdown no
                                # convierta "__main__.py" en negritas ("main.py").
                                + (f" Archivos con menos de 60 %: {', '.join(f'`{b}`' for b in bajos)}." if bajos else "")})
    texto_den = (f"{den['densidad_global']} defectos/KLOC con {den['n_defectos']} defectos registrados."
                 + (" Con n = 0 la densidad no demuestra ausencia de defectos; solo que ninguno se registró."
                    if den["n_defectos"] == 0 else ""))
    salida.append({"metrica": "Densidad de defectos",
                   "valoracion": "sin datos" if den["n_defectos"] == 0 else _nivel(den["densidad_global"], [(10, "baja")], False),
                   "texto": texto_den})
    return salida


def _interp_proceso(m: dict) -> list[dict]:
    p = m["proceso"]
    if p["n_defectos"] == 0:
        return [{"metrica": "MTTD, MTTR y eficacia de las pruebas", "valoracion": "sin datos",
                 "texto": "Aún no hay defectos en el historial (n = 0): las fórmulas están implementadas y probadas, "
                          "pero no hay valores reales que interpretar."}]
    efi = p["eficacia_pruebas"]["criticos"]["pct"]
    return [
        {"metrica": "MTTD", "valoracion": "informativa",
         "texto": f"Mediana {p['mttd']['mediana_h']} h (n = {p['mttd']['n']}) entre la introducción y la corrección."},
        {"metrica": "MTTR", "valoracion": "informativa" if p["mttr"]["n"] == 0 else
         _nivel(p["mttr"]["mediana_h"], [(1, "élite (DORA)"), (24, "alta (DORA)")], False),
         "texto": f"Mediana {p['mttr']['mediana_h']} h (n = {p['mttr']['n']}) del fix al merge."},
        {"metrica": "Eficacia de las pruebas", "valoracion": "sin datos" if efi is None else _nivel(efi, [(85, "buena")]),
         "texto": f"{efi} % de defectos críticos atrapados antes de producción (Jones, 2008: DRE promedio ≈ 85 %)."},
    ]


def _interp_proyecto(m: dict) -> list[dict]:
    d, pl = m["proyecto"]["desviacion"], m["proyecto"]["plazos"]
    salida = []
    if d["desviacion_pct"] is not None:
        sentido = "menos" if d["desviacion_pct"] < 0 else "más"
        salida.append({"metrica": "Desviación de tiempo y esfuerzo",
                       "valoracion": "equilibrada" if abs(d["desviacion_pct"]) <= 25 else "alta",
                       "texto": f"{d['desviacion_pct']} %: se usaron {d['real_h']} h reales contra {d['estimado_h']} h "
                                f"estimadas en {d['tareas_terminadas']} tareas ({sentido} esfuerzo del previsto)."})
    if pl["pct_a_tiempo"] is not None:
        salida.append({"metrica": "Cumplimiento de plazos",
                       "valoracion": _nivel(pl["pct_a_tiempo"], [(80, "bueno"), (60, "aceptable")]),
                       "texto": f"{pl['pct_a_tiempo']} % de tareas cerradas en la fecha de su sprint; "
                                f"tarde: {', '.join(pl['tarde']) or 'ninguna'}."})
    return salida


def _recomendaciones(interpretaciones: list[dict], gate: dict | None) -> list[str]:
    recs = []
    if gate and not gate["aprobado"]:
        recs.append("Corregir los criterios del quality gate que fallan antes de integrar el cambio.")
    for i in interpretaciones:
        if i["valoracion"] in ("mejorable", "alta", "aceptable"):
            recs.append(f"Revisar {i['metrica'].lower()}: {i['texto']}")
        if i["valoracion"] == "sin datos":
            recs.append(f"{i['metrica']}: mantener la convención `fix:` con trailers para que el historial genere datos.")
    return recs or ["Mantener los umbrales actuales; no se detectan riesgos con los datos disponibles."]


def interpretar_por_reglas(m: dict, gate: dict | None = None) -> dict:
    interpretaciones = _interp_producto(m) + _interp_proceso(m) + _interp_proyecto(m)
    return {"fuente": "reglas", "interpretaciones": interpretaciones,
            "recomendaciones": _recomendaciones(interpretaciones, gate)}


# --------------------------------------------------------------------------
# 3. Ruta con modelo de lenguaje (opcional) y orquestación
# --------------------------------------------------------------------------
def construir_prompt(m: dict, verificaciones: list[dict]) -> str:
    """Prompt fijo: la IA interpreta, no recalcula."""
    resumen = {k: m[k] for k in ("pruebas", "proceso", "proyecto", "estimacion") if k in m}
    resumen["producto"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("funciones", "por_archivo")}
                           for k, v in m["producto"].items()}
    return ("Eres un revisor de calidad de software. Con las métricas siguientes (ya calculadas; NO las "
            "recalcules ni inventes otras) escribe en español: 1) una interpretación breve de cada métrica "
            "citando su referencia, 2) los 3 riesgos principales y 3) 3 acciones concretas. Si un valor es "
            "null o n = 0, dilo explícitamente.\n\nVerificaciones de coherencia:\n"
            + json.dumps(verificaciones, ensure_ascii=False) + "\n\nMétricas:\n" + json.dumps(resumen, ensure_ascii=False))


def cliente_desde_entorno() -> Callable[[str], str] | None:
    """Devuelve una función prompt -> texto si hay llave y paquete; si no, None."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic  # dependencia opcional: solo si se quiere usar un LLM
    except ImportError:
        return None
    cliente = anthropic.Anthropic()

    def llamar(prompt: str) -> str:
        respuesta = cliente.messages.create(model=MODELO_POR_DEFECTO, max_tokens=1500,
                                            messages=[{"role": "user", "content": prompt}])
        return respuesta.content[0].text

    return llamar


def analizar(m: dict, gate: dict | None = None, cliente: Callable[[str], str] | None = None) -> dict:
    """Punto de entrada: verificaciones + interpretación (LLM si está disponible, si no reglas)."""
    verificaciones = verificar_coherencia(m)
    resultado = interpretar_por_reglas(m, gate)
    resultado["verificaciones"] = verificaciones
    if cliente is not None:
        prompt = construir_prompt(m, verificaciones)
        try:
            texto = cliente(prompt)
            if texto and texto.strip():
                resultado.update(fuente="llm", texto_llm=texto.strip(), prompt=prompt)
        except Exception as error:  # noqa: BLE001  cualquier fallo de la IA -> se queda la ruta por reglas
            resultado["error_llm"] = f"{type(error).__name__}: {error}"
    return resultado
