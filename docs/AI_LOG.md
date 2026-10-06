# Bitácora de uso de IA en el desarrollo

Registro de cómo se usó IA (Claude, Anthropic) durante el desarrollo. Regla: la IA propone; el autor ejecuta, verifica la salida real y decide.

| Fecha | Sprint | Para qué se usó | Qué se aceptó | Qué se rechazó o corrigió | Verificación |
|---|---|---|---|---|---|
| 2026-10-04 | S0 | Análisis del plan maestro: requisitos, matriz, riesgos, ambigüedades, backlog, arquitectura | Backlog, matriz viva, orden motor → CI → dashboard | — | Revisión del autor |
| 2026-10-04 | S0 | Validación de la herramienta `metricas` y de dos reportes anteriores antes de reutilizarlos | Reutilizar minería SZZ y esquema de resultados; formato de informe 29119-3; tabla de normas | Textos de interpretación fijos de secrets-engine; versiones de normas desactualizadas (25010:2011, 90003:2004, IEEE 829-2008) | `docs/DECISIONES.md` (D07–D09) |
| 2026-10-05 | S1A | T04: generar `product_metrics.py` y sus pruebas | Cálculo con radon por función; exclusión de pruebas/.venv | Primera versión tenía `analizar_complejidad` con CC 11 (> 10); se dividió antes de entregarla | El autor comparó cada función contra `radon cc -s` (E07) |
| 2026-10-05 | S1A | T05: generar `coverage_metrics.py` y sus pruebas | Ejecución de pytest-cov en proceso aparte; filtro a código de producto | ruff (PLW1510, RUF010) marcó dos detalles; se corrigieron antes de entregar | El autor comparó contra `coverage report` (E06) |
| 2026-10-05 | S1B | T06: adaptar la minería SZZ de la herramienta `metricas` a Python + trailers | Inductor por `git blame`, fases, severidad, fixes excluidos | En el entorno de la IA falló la prueba del commit raíz (blame marca el límite con `^`); se cambió a `--porcelain`. `minar_defectos` tenía CC 17; se dividió | Pendiente: ejecución del autor |
