# Bitácora de uso de IA en el desarrollo

Registro de cómo se usó IA (Claude, Anthropic) durante el desarrollo. Regla: la IA propone; el autor ejecuta, verifica la salida real y decide.

| Fecha | Sprint | Para qué se usó | Qué se aceptó | Qué se rechazó o corrigió | Verificación |
|---|---|---|---|---|---|
| 2026-10-04 | S0 | Análisis del plan maestro: requisitos, matriz, riesgos, ambigüedades, backlog, arquitectura | Backlog, matriz viva, orden motor → CI → dashboard | — | Revisión del autor |
| 2026-10-04 | S0 | Validación de la herramienta `metricas` y de dos reportes anteriores antes de reutilizarlos | Reutilizar minería SZZ y esquema de resultados; formato de informe 29119-3; tabla de normas | Textos de interpretación fijos de secrets-engine; versiones de normas desactualizadas (25010:2011, 90003:2004, IEEE 829-2008) | `docs/DECISIONES.md` (D07–D09) |
