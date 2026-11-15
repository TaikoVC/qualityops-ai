"""Configuración común de las pruebas (T33).

Las pruebas escritas antes de T33 (Sprints 1-3) se etiquetan aquí según su TIPO, sin tocar
cada archivo. Las pruebas nuevas declaran su tipo con `pytestmark` dentro del archivo.
Así se puede ejecutar cualquier tipo por separado:  python -m pytest -m unitaria
"""

import pytest

# Archivo de pruebas anterior -> tipo(s) de prueba que contiene.
TIPOS_POR_ARCHIVO = {
    "test_quality_gate.py": ["unitaria"],
    "test_product_metrics.py": ["unitaria"],
    "test_density.py": ["unitaria"],
    "test_estimation.py": ["unitaria"],
    "test_process_project_metrics.py": ["unitaria"],
    "test_defects.py": ["unitaria"],
    "test_coverage_metrics.py": ["componente"],
    "test_ai_advisor_report.py": ["componente"],
    "test_cli.py": ["integracion"],
    "test_dashboard.py": ["interfaz"],
}


def pytest_collection_modifyitems(items):
    for item in items:
        for tipo in TIPOS_POR_ARCHIVO.get(item.path.name, []):
            item.add_marker(getattr(pytest.mark, tipo))


# Variables que una persona tiene cargadas en su sesión para las pruebas en vivo del hipervisor.
# Si se quedan cargadas, la API en memoria exigiría el token y el dashboard vendría con el secreto
# lleno: las pruebas dependerían del equipo. Se quitan en todas las pruebas que NO son de hipervisor.
VARIABLES_DE_SESION = ("QUALITYOPS_API_TOKEN", "PVE_TOKEN_SECRET", "PVE_URL", "PVE_TOKEN_ID", "PVE_CA")


@pytest.fixture(autouse=True)
def aislar_variables_de_sesion(request, monkeypatch):
    if request.node.get_closest_marker("hipervisor") is None:
        for variable in VARIABLES_DE_SESION:
            monkeypatch.delenv(variable, raising=False)
