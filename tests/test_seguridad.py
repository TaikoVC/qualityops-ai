"""Pruebas del módulo de seguridad (T32) y del Centro de pruebas (T34).

Los escáneres reales (Bandit, pip-audit, detect-secrets) se reemplazan por salidas
conocidas para probar la política y la verificación de la IA sin red ni demoras.
"""

import json

import pytest

from qualityops import centro_pruebas, seguridad

BAJO = {"herramienta": "bandit", "id": "B603", "severidad": "LOW", "archivo": "a.py", "linea": 1, "descripcion": "x"}
MEDIO = {**BAJO, "id": "B314", "severidad": "MEDIUM"}
DEP = {"herramienta": "pip-audit", "id": "CVE-2026-1111", "severidad": "DEPENDENCIA",
       "paquete": "pillow", "version": "12.3.0", "corregida_en": "13.0.0"}
SECRETO = {"herramienta": "detect-secrets", "id": "Secret Keyword", "severidad": "SECRETO", "archivo": "a.py", "linea": 3}


@pytest.mark.seguridad
@pytest.mark.parametrize(("codigo", "deps", "secretos", "aprobado"), [
    ([BAJO], [], [], True),          # solo hallazgos bajos: se reportan, no bloquean
    ([MEDIO], [], [], False),
    ([], [DEP], [], False),
    ([], [], [SECRETO], False),
])
def test_cp_seg_06_politica_del_gate_de_seguridad(codigo, deps, secretos, aprobado):
    """CP-SEG-06: el gate de seguridad bloquea por severidad media/alta, dependencia vulnerable o secreto."""
    assert seguridad.politica(codigo, deps, secretos)["aprobado"] is aprobado


@pytest.mark.seguridad
def test_cp_seg_07_detecta_identificadores_inventados_por_la_ia():
    """CP-SEG-07: la IA no puede citar CVE o reglas que los escáneres no encontraron."""
    resultado = {"codigo": [MEDIO], "dependencias": [DEP]}
    texto = "Prioridad 1: CVE-2026-1111 en pillow. Prioridad 2: B314. También CVE-2025-9999 y B999."
    assert seguridad.ids_inventados(texto, resultado) == ["B999", "CVE-2025-9999"]


@pytest.mark.componente
def test_analisis_completo_con_escaneres_simulados(tmp_path, monkeypatch):
    """El módulo arma hallazgos, resumen, gate e IA a partir de las salidas JSON de los escáneres."""
    (tmp_path / "requirements.txt").write_text("pillow==12.3.0\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    salidas = {
        "bandit": {"results": [{"test_id": "B314", "issue_severity": "MEDIUM", "issue_confidence": "HIGH",
                                "filename": "./app.py", "line_number": 1, "issue_text": "XML", "issue_cwe": {"id": 20}}]},
        "pip_audit": {"dependencies": [{"name": "pillow", "version": "12.3.0",
                                        "vulns": [{"id": "CVE-2026-1111", "fix_versions": ["13.0.0"]}]}]},
        "detect_secrets": {"results": {}},
    }
    monkeypatch.setattr(seguridad, "_ejecutar", lambda comando, cwd: json.dumps(salidas[comando[2]]))
    r = seguridad.analizar(tmp_path, usar_ia=False)
    assert r["resumen"] == {"codigo_por_severidad": {"MEDIUM": 1}, "dependencias_por_paquete": {"pillow 12.3.0": 1},
                            "secretos": 0}
    assert r["gate"]["aprobado"] is False and r["codigo"][0]["archivo"] == "app.py"

    r["ia"] = seguridad.analizar_con_ia(r, cliente=lambda prompt: "Actualizar pillow por CVE-2026-1111 y corregir B314.")
    assert r["ia"]["fuente"] == "llm" and r["ia"]["coherente"] is True
    assert "BLOQUEADO" in seguridad.resumen_markdown(r)


@pytest.mark.componente
def test_la_ia_que_falla_no_rompe_el_escaneo():
    """Si la IA falla, el resultado lo dice y el dictamen no cambia."""
    def falla(_):
        raise TimeoutError("sin respuesta")
    ia = seguridad.analizar_con_ia({"codigo": [], "dependencias": [], "resumen": {"dependencias_por_paquete": {},
                                    "secretos": 0}, "gate": {"aprobado": True}}, cliente=falla)
    assert ia["fuente"] == "error" and "TimeoutError" in ia["error"]


@pytest.mark.unitaria
def test_resultado_obtenido_de_un_caso():
    """El Centro de pruebas llena el resultado obtenido de cada caso a partir de JUnit."""
    pruebas = [{"prueba": "test_cp_fun_01_valores[74.99-False]", "resultado": "aprobada"},
               {"prueba": "test_cp_fun_01_valores[75.0-True]", "resultado": "fallida"},
               {"prueba": "test_cp_hv_10_api", "resultado": "omitida"}]
    assert centro_pruebas.resultado_de_caso({"id": "CP-FUN-01"}, pruebas)["estado"] == "falla"
    assert centro_pruebas.resultado_de_caso({"id": "CP-HV-10"}, pruebas)["estado"] == "omitida"
    assert centro_pruebas.resultado_de_caso({"id": "CP-NF-01"}, pruebas)["estado"] == "sin ejecutar"
    manual = {"id": "CP-MAN-01", "modo": "manual", "obtenido": "aprobado = False", "estado": "pasa"}
    assert centro_pruebas.resultado_de_caso(manual, pruebas) == {"obtenido": "aprobado = False", "estado": "pasa"}


@pytest.mark.unitaria
def test_cada_caso_automatico_tiene_su_prueba():
    """Todo caso automático del catálogo apunta a una prueba que existe (el catálogo no miente)."""
    from pathlib import Path
    texto = "\n".join(p.read_text(encoding="utf-8") for p in Path(__file__).parent.glob("test_*.py"))
    casos = centro_pruebas.cargar_catalogo()
    assert len(casos) >= 40
    for caso in casos:
        assert {"id", "tipo", "descripcion", "entrada", "pasos", "esperado"} <= set(caso), caso["id"]
        if caso["modo"] == "automatico":
            nombre = caso.get("prueba") or centro_pruebas.prefijo_de_prueba(caso["id"])
            assert f"def {nombre}" in texto, caso["id"]
