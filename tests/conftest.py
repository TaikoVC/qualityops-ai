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
