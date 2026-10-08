# Matriz viva de cumplimiento — QualityOps AI

> Regla: una fila solo pasa a **Cumple** cuando existe evidencia real (archivo, captura, log o commit) y se anota su referencia.
> Estados: ⬜ Pendiente · 🟨 En progreso · 🟧 Parcial · ✅ Cumple · ❌ No cumple
> Última actualización: 2026-10-08 00:55 — T13/T14 integrados (PR #36, 03ca184).

| ID | Requisito | Implementación | Evidencia (ID / archivo / commit) | Criterio de aceptación | Estado |
|---|---|---|---|---|---|
| DOC-01 | Portada | Plantilla UTCJ | — | Datos completos (título, materia, prof., nombre–matrícula, fecha) | ⬜ |
| DOC-02 | Introducción | Reporte | — | 0.5–1 página: DevOps, IA, calidad | ⬜ |
| DOC-03 | Índice tabulado | Índice automático de Word | — | Actualizado, con puntos guía y páginas | ⬜ |
| DOC-04 | Imágenes explicadas | Pie + párrafo por imagen | E13 | ≥ 10 imágenes explicadas | ⬜ |
| DOC-05 | Conclusión | Reporte | — | Resultados reales, límites, siguientes pasos | ⬜ |
| DOC-06 | ≥ 10 hojas con tablas e imágenes | Reporte 15–18 pág. | E13 | ≥ 10 pág. de contenido, ≥ 8 tablas | ⬜ |
| DOC-07 | Plantilla UTCJ + referencias | `PlantillaInvestigacion.docx` | — | Formato respetado; referencias APA | ⬜ |
| DOC-08 | Trabajo individual | Repo personal | E01 (1 contribuidor) | Un solo autor en `git shortlog -s` | 🟨 |
| DOC-09 | Normas aplicadas, claras y puntuales | `docs/NORMAS.md`: norma → qué establece → cómo se aplicó → evidencia | — | Cada norma citada tiene aplicación y evidencia; versiones vigentes | 🟨 |
| PRG-01 | Tecnologías DevOps | GitHub Actions (`.github/workflows/ci.yml`) en cada PR y push a main + quality gate + ruleset `proteger-main` | E08, E08b, E08e, PR #35 | Workflow corre en cada PR/push | ✅ |
| PRG-02 | IA en frameworks | `ai_advisor.py` + `AI_LOG.md` | E10 | Entrada y salida de IA visibles | ⬜ |
| PRG-03 | Automatización | Pipeline ruff → pruebas/métricas → quality gate → resumen en Actions → artefacto | E08, E08c, E08d | Pasos visibles en el log | ✅ |
| PRG-04 | Validación de software | pytest + ruff | E05, E05b | Pruebas verdes, ruff limpio | 🟨 |
| PRG-05 | GitHub + repositorio | Repo + README + issues | E00, E00c, E01, 9823160 | URL accesible, README reproducible | 🟨 (falta sección Uso del README) |
| PRG-06 | Ejecución y salida | CLI `python -m qualityops` → `reports/metrics.json` (hecho, T08) + dashboard Streamlit (pendiente, T18) | E04, E04b | Salida real visible en CLI y dashboard | 🟨 |
| PRG-07 | Métricas | Motor `qualityops/` | E04b, E05–E12 | Todas las MET calculadas | 🟨 |
| PRG-08 | Proyecto DevOps justificado | Capítulo de justificación | — | Justificación + métricas reales del proyecto analizado | ⬜ |
| PRG-09 | Revisión en clase | `docs/DEMO.md` | — | Demo ensayada < 5 min | ⬜ |
| CAL-01 | Calidad y grado de cumplimiento | Semáforo + % calculado | E14 | % calculado por el programa | ⬜ |
| CAL-02 | Informe de calidad en formato | `report.py` → `quality_report.md` con formato fijo ISO/IEC/IEEE 29119-3 + dictamen | — | Generado en local y en CI; incluye todas las secciones del formato | ⬜ |
| CAL-03 | Requisitos explícitos | Tabla RF/RNF | — | ID, descripción, prioridad, criterio | ⬜ |
| CAL-04 | Requisitos de usuario y negocio | Historia + expectativas | — | ≥ 1 historia, ≥ 3 expectativas medibles | ⬜ |
| CAL-05 | Aseguramiento de calidad | Pruebas + ruff + revisión por PR + CI + quality gate | E05, E05b, E08 | Pipeline verde en v1.0 | 🟨 |
| CAL-06 | Idoneidad funcional y fiabilidad | Tabla ISO/IEC 25010:2023 con medidas ISO/IEC 25023 | — | Subcaracterísticas con valor real | ⬜ |
| CAL-07 | Enfoque preventivo | Quality gate en el CI + ruleset que exige el check `calidad` para integrar a main | E08a (demostración), E08, E08b | ≥ 1 bloqueo real en CI y su corrección (aún no ocurre) | 🟨 |
| CAL-08 | Carácter sistemático | Kanban + DoD + trazabilidad | E02, E02b | Requisito → issue → commit → evidencia | 🟨 |
| MET-00 | Métricas aplicando IA | Cálculo determinista + IA interpreta/verifica | E10 | Interpretación coherente con valores | ⬜ |
| MET-P1 | Complejidad ciclomática | `qualityops/product_metrics.py` (radon, por función; promedio, mediana, máximo, CC ≤ 10) | E07, 19d18b6, PR #28 | Coincide con `radon cc -s` por función | ✅ |
| MET-P2 | Cobertura | `qualityops/coverage_metrics.py` (pytest-cov, global y por archivo, solo código de producto) | E06, 6ad52ac, PR #29 | Coincide con `coverage report` | ✅ |
| MET-P3 | Densidad de defectos | `qualityops/density.py`: defectos de producto (minería SZZ) / KLOC (radon), global y por archivo | E11b, E11c, PR #31 | Fórmula probada; SLOC coincide con `radon raw`. Valor actual 0.0 (n = 0 defectos reales); se recalcula en cada ejecución | ✅ |
| MET-R1 | MTTD | `process_metrics.py`: promedio y mediana (fecha fix − fecha commit inductor SZZ) | E11, E11d | Fórmula probada; valor real con n > 0 | 🟨 (calculado, n = 0) |
| MET-R2 | MTTR | `process_metrics.py`: promedio y mediana (fecha merge − fecha fix) | E11, E11d | Fórmula probada; valor real con n > 0 | 🟨 (calculado, n = 0) |
| MET-R3 | Eficacia de pruebas | `process_metrics.py`: críticos antes de producción / críticos con fase conocida | E11, E11d | Fórmula probada; valor real con n > 0 | 🟨 (calculado, n = 0) |
| MET-J1 | Eficacia de revisión | `project_metrics.py`: defectos en revisión / defectos con fase conocida | E11, E11d | Fórmula probada; valor real con n > 0 | 🟨 (calculado, n = 0) |
| MET-J2 | Desviación tiempo/esfuerzo por módulo | `project_metrics.py` + `data/time_log.csv` (estimación en 76f14fb, antes del código) | E11d | Desviación por módulo y total con datos reales | ✅ |
| MET-J3 | Plazos (+ satisfacción opcional) | `project_metrics.py`: fecha real de cierre vs fecha del sprint (`pyproject.toml`) | E11d | % de tareas a tiempo con datos reales | ✅ |
| EST-1 | Juicio de expertos | `data/time_log.csv` (columna más probable) | E12 | Horas por tarea/módulo + justificación | 🟨 |
| EST-2 | Estimación análoga | `estimation.py` | E12 | Referencia + factor de ajuste | ⬜ |
| EST-3 | Tres puntos (PERT) | `estimation.py` | E12 | O, M, P, E y σ | ⬜ |
| EST-4 | Puntos de función | `estimation.py` | E12 | Conteo, pesos, PF sin ajustar (y ajustados) | ⬜ |
| PRO-01 | Kanban | GitHub Projects | E02 | Capturas por sprint | 🟨 |
| PRO-02 | Commits por cambio | Git + PR con merge commit | E00c, E02b | Mensajes con ID de tarea | 🟨 |
| PRO-03 | Evidencia por sprint | `docs/EVIDENCIAS.md` | — | E01–E14 con archivo y fecha | ⬜ |
| PRO-04 | Bitácora de IA | `docs/AI_LOG.md` | — | Entradas por sprint | 🟨 |

**Grado de cumplimiento actual:** 7 / 44 (15.9 %) Cumple · 17 en progreso. Nada se marca Cumple hasta tener evidencia.
