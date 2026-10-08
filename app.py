"""Dashboard de QualityOps AI (T18). Ejecutar con:  streamlit run app.py

Solo MUESTRA lo que generó el pipeline (python -m qualityops, quality_gate y report).
La carpeta de reportes se puede cambiar con la variable QUALITYOPS_REPORTS.
"""

import os
from pathlib import Path

import streamlit as st

from qualityops.dashboard import (
    cargar_reportes,
    resumen_matriz,
    tabla_desviacion,
    tabla_estimacion,
)
from qualityops.report import estado_llm

CARPETA = Path(os.environ.get("QUALITYOPS_REPORTS", "reports"))
MATRIZ = Path(os.environ.get("QUALITYOPS_MATRIZ", "docs/MATRIZ_CUMPLIMIENTO.md"))

st.set_page_config(page_title="QualityOps AI", layout="wide")
st.title("QualityOps AI — Dashboard de calidad")

datos = cargar_reportes(CARPETA)
m, gate, ia = datos["metrics"], datos["gate"], datos["ai_analysis"]
if m is None:
    st.warning("No hay reports/metrics.json. Ejecuta primero:  python -m qualityops --repo . --salida reports")
    st.stop()

st.caption(f"Repositorio {m['repo']} · commit {m['commit']} · generado {m['generado']}")
resumen, producto, proceso, proyecto, estimacion, tab_ia = st.tabs(
    ["Resumen y cumplimiento", "Producto", "Proceso", "Proyecto", "Estimación", "AI Advisor"])

with resumen:
    if gate:
        st.subheader(f"Quality gate: {'APROBADO' if gate['aprobado'] else 'BLOQUEADO'}")
        st.dataframe(gate["criterios"], use_container_width=True)
    matriz = resumen_matriz(MATRIZ)
    st.subheader("Grado de cumplimiento de los requisitos")
    # Sin "delta": la flecha de Streamlit indica un cambio, y aquí es un porcentaje fijo.
    st.metric("Requisitos que cumplen", f"{matriz['por_estado'].get('Cumple', 0)} / {matriz['total']} "
              f"({matriz['pct_cumple']} %)")
    st.bar_chart(matriz["por_estado"])
    st.dataframe(matriz["filas"], use_container_width=True)

with producto:
    prod = m["producto"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cobertura", f"{prod['cobertura']['global_pct']} %")
    c2.metric("CC promedio / máx.", f"{prod['complejidad']['promedio']} / {prod['complejidad']['maximo']}")
    c3.metric("Tamaño", f"{prod['lineas']['kloc']} KLOC")
    c4.metric("Densidad de defectos", f"{prod['densidad']['densidad_global']} def/KLOC")
    st.subheader("Cobertura por archivo (%)")
    st.bar_chart({a["archivo"]: a["pct"] for a in prod["cobertura"]["por_archivo"]})
    st.subheader("Funciones más complejas")
    st.dataframe(sorted(prod["complejidad"]["funciones"], key=lambda f: -f["cc"])[:10], use_container_width=True)

with proceso:
    proc = m["proceso"]
    c1, c2, c3 = st.columns(3)
    c1.metric("MTTD (mediana)", f"{proc['mttd']['mediana_h']} h", f"n = {proc['mttd']['n']}")
    c2.metric("MTTR (mediana)", f"{proc['mttr']['mediana_h']} h", f"n = {proc['mttr']['n']}")
    c3.metric("Eficacia de pruebas (críticos)", f"{proc['eficacia_pruebas']['criticos']['pct']} %")
    st.subheader("Defectos minados del historial de Git")
    st.dataframe(m["defectos"]["defectos"], use_container_width=True)

with proyecto:
    proy = m["proyecto"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Eficacia de la revisión", f"{proy['eficacia_revision']['pct']} %")
    c2.metric("Desviación total", f"{proy['desviacion']['desviacion_pct']} %")
    c3.metric("Tareas a tiempo", f"{proy['plazos']['pct_a_tiempo']} %")
    st.subheader("Estimado vs real por módulo (horas)")
    st.dataframe(tabla_desviacion(m), use_container_width=True)

with estimacion:
    st.subheader("Cuatro técnicas de estimación vs horas reales")
    filas = tabla_estimacion(m)
    st.dataframe(filas, use_container_width=True)
    st.bar_chart({f["técnica"]: f["horas"] for f in filas if f["horas"] is not None})

with tab_ia:
    if ia is None:
        st.info("Ejecuta  python -m qualityops.report  para generar la interpretación.")
    else:
        st.subheader(f"Interpretación (fuente: {ia['fuente']})")
        st.caption(f"Intento de LLM: {estado_llm(ia)}")
        for i in ia["interpretaciones"]:
            st.markdown(f"- **{i['metrica']}** ({i['valoracion']}): {i['texto']}")
        if ia.get("texto_llm"):
            st.markdown(ia["texto_llm"])
        st.subheader("Verificaciones de coherencia")
        st.dataframe(ia["verificaciones"], use_container_width=True)
