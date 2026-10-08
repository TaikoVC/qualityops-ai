"""Pruebas de qualityops.process_metrics y qualityops.project_metrics (T13, T14).

Los datos de entrada son fijos, así los resultados se calculan a mano.
"""

from qualityops.process_metrics import calcular_proceso
from qualityops.project_metrics import (
    calcular_proyecto,
    cumplimiento_plazos,
    desviacion_por_modulo,
    eficacia_revision,
)

# 4 defectos: 2 críticos (uno atrapado en pruebas, otro escapado a producción).
MINERIA = {"defectos": [
    {"severidad": "critica", "fase": "pruebas", "mttd_horas": 3.0, "mttr_horas": 1.5},
    {"severidad": "critica", "fase": "produccion", "mttd_horas": 2.0, "mttr_horas": None},
    {"severidad": "menor", "fase": "revision", "mttd_horas": 0.5, "mttr_horas": 0.5},
    {"severidad": "sin_clasificar", "fase": "desconocida", "mttd_horas": None, "mttr_horas": None},
]}


def test_mttd_y_mttr():
    p = calcular_proceso(MINERIA)
    assert p["mttd"] == {"n": 3, "promedio_h": round((3 + 2 + 0.5) / 3, 2), "mediana_h": 2.0}
    assert p["mttr"] == {"n": 2, "promedio_h": 1.0, "mediana_h": 1.0}


def test_eficacia_de_pruebas_solo_criticos():
    p = calcular_proceso(MINERIA)["eficacia_pruebas"]
    assert p["criticos"] == {"antes_de_produccion": 1, "con_fase_conocida": 2, "pct": 50.0}
    # Con todas las severidades: 2 de 3 con fase conocida (la desconocida no cuenta).
    assert p["todas_las_severidades"]["pct"] == round(100 * 2 / 3, 2)


def test_sin_defectos_no_inventa_valores():
    p = calcular_proceso({"defectos": []})
    assert p["mttd"]["promedio_h"] is None
    assert p["eficacia_pruebas"]["criticos"]["pct"] is None
    assert eficacia_revision({"defectos": []})["pct"] is None


def test_eficacia_de_revision():
    assert eficacia_revision(MINERIA) == {"en_revision": 1, "con_fase_conocida": 3, "pct": round(100 / 3, 2)}


TAREAS = [
    {"tarea": "T1", "modulo": "a", "mas_probable_h": "1.0", "real_h": "1.5", "sprint_planeado": "S0", "fin": "2026-10-04 22:00"},
    {"tarea": "T2", "modulo": "a", "mas_probable_h": "1.0", "real_h": "0.5", "sprint_planeado": "S1A", "fin": "2026-10-06 10:00"},
    {"tarea": "T3", "modulo": "b", "mas_probable_h": "2.0", "real_h": "1.0", "sprint_planeado": "S1D-S3B", "fin": "2026-10-07 09:00"},
    {"tarea": "T4", "modulo": "b", "mas_probable_h": "4.0", "real_h": "", "sprint_planeado": "S2A", "fin": ""},
]
CALENDARIO = {"S0": "2026-10-04", "S1A": "2026-10-05", "S3B": "2026-10-07"}


def test_desviacion_por_modulo():
    d = desviacion_por_modulo(TAREAS)
    assert d["tareas_terminadas"] == 3                       # T4 no está terminada
    assert d["por_modulo"]["a"] == {"tareas": 2, "estimado_h": 2.0, "real_h": 2.0, "desviacion_pct": 0.0}
    assert d["por_modulo"]["b"]["desviacion_pct"] == -50.0   # 1 h real vs 2 h estimadas
    assert (d["estimado_h"], d["real_h"], d["desviacion_pct"]) == (4.0, 3.0, -25.0)


def test_plazos_por_fecha_real():
    p = cumplimiento_plazos(TAREAS, CALENDARIO)
    assert p == {"evaluadas": 3, "a_tiempo": 2, "tarde": ["T2"], "pct_a_tiempo": round(200 / 3, 2)}


def test_calcular_proyecto_sin_datos_de_gestion(tmp_path):
    r = calcular_proyecto({"defectos": []}, tmp_path)
    assert r["desviacion"]["tareas_terminadas"] == 0
    assert r["plazos"]["pct_a_tiempo"] is None
