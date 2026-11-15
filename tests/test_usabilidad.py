"""Pruebas de USABILIDAD automatizadas del dashboard (T34), con el banco de pruebas de Streamlit.

Se automatizan heurísticas de usabilidad de Nielsen (1994) que sí se pueden comprobar:
visibilidad del estado del sistema, reconocer antes que recordar y eficiencia de uso.
La parte subjetiva (opinión del usuario) se cubre con la prueba manual CP-MAN-03.
"""

import json
import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app.py"
pytestmark = pytest.mark.usabilidad


@pytest.fixture
def reportes_de_ejemplo(tmp_path, monkeypatch):
    from test_dashboard import MATRIZ, METRICAS
    (tmp_path / "metrics.json").write_text(json.dumps(METRICAS), encoding="utf-8")
    (tmp_path / "matriz.md").write_text(MATRIZ, encoding="utf-8")
    monkeypatch.setenv("QUALITYOPS_REPORTS", str(tmp_path))
    monkeypatch.setenv("QUALITYOPS_MATRIZ", str(tmp_path / "matriz.md"))
    return tmp_path


def test_cp_usa_01_sin_reportes_orienta_al_usuario(tmp_path, monkeypatch):
    """CP-USA-01: sin datos no hay error: un aviso dice qué ejecutar y las pestañas nuevas siguen disponibles."""
    monkeypatch.setenv("QUALITYOPS_REPORTS", str(tmp_path))
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception
    assert "python -m qualityops" in app.warning[0].value
    assert [b.label for b in app.button] == ["▶ Ejecutar pruebas", "🔍 Escanear vulnerabilidades",
                                             "🔗 Verificar comunicación"]


def test_cp_usa_02_todo_esta_a_la_vista_en_pestanas(reportes_de_ejemplo):
    """CP-USA-02: 9 pestañas con nombres en español y un botón por acción; nada exige recordar comandos."""
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception
    assert [t.label for t in app.tabs] == [
        "Resumen y cumplimiento", "Producto", "Proceso", "Proyecto", "Estimación", "AI Advisor",
        "🧪 Centro de pruebas", "🛡️ Seguridad", "🖥️ Hipervisor"]
    assert len(app.selectbox) == 1 and "humo" in app.selectbox[0].options[1]
    # El secreto del token se escribe en un campo oculto (tipo contraseña).
    assert any(t.label.startswith("Secreto del token") for t in app.text_input)


def test_cp_usa_03_el_dashboard_carga_rapido(reportes_de_ejemplo):
    """CP-USA-03: el dashboard se dibuja en menos de 5 segundos."""
    inicio = time.perf_counter()
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception and time.perf_counter() - inicio < 5


def test_boton_hipervisor_sin_secreto_avisa(reportes_de_ejemplo):
    """Prevención de errores: verificar sin secreto muestra un mensaje claro en lugar de fallar."""
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    app.button(key="btn_hipervisor").click().run()
    assert not app.exception
    assert any("secreto" in e.value for e in app.error)


def test_salida_de_comandos_con_acentos_en_windows(monkeypatch):
    """Defecto 7: con la codificación de Windows (cp1252) la salida del comando quedaba en None
    y el botón «Verificar comunicación» mostraba un TypeError. Ahora se lee siempre como texto."""
    from qualityops.vistas import _correr
    monkeypatch.setenv("PYTHONIOENCODING", "cp1252")
    proceso = _correr("hipervisor", "--help")
    assert proceso.returncode == 0 and "también" in proceso.stdout
