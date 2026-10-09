# Matriz viva de cumplimiento — QualityOps AI

> Regla: una fila solo pasa a **Cumple** cuando existe evidencia real (archivo, captura, log o commit) y se anota su referencia.
> Estados: ⬜ Pendiente · 🟨 En progreso · 🟧 Parcial · ✅ Cumple · ❌ No cumple
> Última actualización: 2026-10-08 — reporte final (T21), ejecución final sobre 9d93529 (E16a, E16b).

| ID | Requisito | Implementación | Evidencia (ID / archivo / commit) | Criterio de aceptación | Estado |
|---|---|---|---|---|---|
| DOC-01 | Portada | Plantilla UTCJ | Reporte final (E13): portada | Datos completos (título, materia, prof., nombre–matrícula, fecha) | ✅ |
| DOC-02 | Introducción | Reporte | Reporte final (E13): I. Introducción | 0.5–1 página: DevOps, IA, calidad | ✅ |
| DOC-03 | Índice tabulado | Índice con hipervínculos, puntos guía y página + índices de figuras y tablas | Reporte final (E13): II. Índice | Actualizado, con puntos guía y páginas | ✅ |
| DOC-04 | Imágenes explicadas | Pie + «Qué muestra / Qué demuestra / Cómo se generó» por imagen | Reporte final (E13), E03 | ≥ 10 imágenes explicadas | ✅ |
| DOC-05 | Conclusión | Reporte | Reporte final (E13): III. Conclusión | Resultados reales, límites, siguientes pasos | ✅ |
| DOC-06 | ≥ 10 hojas con tablas e imágenes | Capítulo 6 (requisitos explícitos) con tablas y capturas por módulo | Reporte final (E13): cap. 6 | ≥ 10 pág. de contenido, ≥ 8 tablas | ✅ |
| DOC-07 | Plantilla UTCJ + referencias | `PlantillaInvestigacion.docx` | Reporte final (E13): IV. Referencias (APA) | Formato respetado; referencias APA | ✅ |
| DOC-08 | Trabajo individual | Repo personal | E01; `git shortlog -sne`: Ivan Valle (commits) y TaikoVC (su cuenta de GitHub, merges) | Un solo autor en `git shortlog -s` | ✅ |
| DOC-09 | Normas aplicadas, claras y puntuales | `docs/NORMAS.md`: norma → qué establece → cómo se aplicó → evidencia | Reporte final (E13): cap. 11.3 | Cada norma citada tiene aplicación y evidencia; versiones vigentes | ✅ |
| PRG-01 | Tecnologías DevOps | GitHub Actions (`.github/workflows/ci.yml`) en cada PR y push a main + quality gate + ruleset `proteger-main` | E08, E08b, E08e, PR #35 | Workflow corre en cada PR/push | ✅ |
| PRG-02 | IA en frameworks | `ai_advisor.py`: verificación de coherencia + interpretación por reglas + LLM Gemini (AI Studio, secreto `GEMINI_API_KEY` en CI) con respaldo automático + `docs/AI_LOG.md` | E10h, E10i, E10k, PR #40, D19 | Entrada y salida de un LLM real visibles en CI | ✅ |
| PRG-03 | Automatización | Pipeline ruff → pruebas/métricas → quality gate → resumen en Actions → artefacto | E08, E08c, E08d | Pasos visibles en el log | ✅ |
| PRG-04 | Validación de software | pytest (56 pruebas) + ruff en local y en cada PR | E05, E05b, E10h, E10k | Pruebas verdes, ruff limpio | ✅ |
| PRG-05 | GitHub + repositorio | Repo + README (instalación, uso y convenciones) + issues | E00, E00c, E01, README | URL accesible, README reproducible | ✅ |
| PRG-06 | Ejecución y salida | CLI `python -m qualityops` → `reports/metrics.json` + informe + dashboard Streamlit (`app.py`, 6 pestañas) | E04b, E09a–h, E10h | Salida real visible en CLI y dashboard | ✅ |
| PRG-07 | Métricas | Motor `qualityops/` | E16a (todas las métricas en la ejecución final, commit 9d93529) | Todas las MET calculadas | ✅ |
| PRG-08 | Proyecto DevOps justificado | Capítulo de justificación | Reporte final (E13): cap. 1.3 | Justificación + métricas reales del proyecto analizado | ✅ |
| PRG-09 | Revisión en clase | Guion de demostración | Reporte final (E13): cap. 14 | Demo ensayada < 5 min | 🟨 (guion listo; ensayo pendiente) |
| CAL-01 | Calidad y grado de cumplimiento | Semáforo + % calculado por `dashboard.resumen_matriz` a partir de esta matriz | E09a, E09b | % calculado por el programa | ✅ |
| CAL-02 | Informe de calidad en formato | `qualityops/report.py` → `reports/quality_report.md` (12 secciones, ISO/IEC/IEEE 29119-3) + dictamen; publicado en el resumen de Actions | E10, E15b | Generado en local y en CI con todas las secciones | ✅ |
| CAL-03 | Requisitos explícitos | 15 RF + 10 RNF con prioridad, criterio y evidencia | Reporte final (E13): cap. 6 | ID, descripción, prioridad, criterio | ✅ |
| CAL-04 | Requisitos de usuario y negocio | 5 historias de usuario + 9 expectativas con indicador | Reporte final (E13): cap. 7 | ≥ 1 historia, ≥ 3 expectativas medibles | ✅ |
| CAL-05 | Aseguramiento de calidad | Pruebas + ruff + revisión por PR + CI + quality gate (plan SQA, cap. 8) | E05, E08, E16b (main en verde) | Pipeline verde en v1.0 | 🟨 (se confirma con el tag v1.0.0) |
| CAL-06 | Idoneidad funcional y fiabilidad | Tabla ISO/IEC 25010:2023 con medidas al estilo ISO/IEC 25023 | Reporte final (E13): cap. 9, E16b | Subcaracterísticas con valor real | ✅ |
| CAL-07 | Enfoque preventivo | Quality gate en el CI + ruleset que exige el check `calidad` para integrar a main | E08a, E08b, E08g, E17a–E17d (PR #42 bloqueado por CC 11, cerrado sin merge) | ≥ 1 bloqueo real en CI | ✅ |
| CAL-08 | Carácter sistemático | Kanban + ciclo repetible + trazabilidad + decisiones | E02, E02b, Reporte final (E13): cap. 11 | Requisito → issue → commit → evidencia | ✅ |
| MET-00 | Métricas aplicando IA | Cálculo determinista + IA que interpreta (Gemini) y 5 verificaciones de coherencia | E10h, E10i | Interpretación coherente con valores | ✅ |
| MET-P1 | Complejidad ciclomática | `qualityops/product_metrics.py` (radon, por función; promedio, mediana, máximo, CC ≤ 10) | E07, 19d18b6, PR #28 | Coincide con `radon cc -s` por función | ✅ |
| MET-P2 | Cobertura | `qualityops/coverage_metrics.py` (pytest-cov, global y por archivo, solo código de producto) | E06, 6ad52ac, PR #29 | Coincide con `coverage report` | ✅ |
| MET-P3 | Densidad de defectos | `qualityops/density.py`: defectos de producto (minería SZZ) / KLOC (radon), global y por archivo | E11b, E11c, E11f, E10h | Valor real: 3 defectos / 1.066 KLOC = 2.81 def/KLOC | ✅ |
| MET-R1 | MTTD | `process_metrics.py`: promedio y mediana (fecha fix − fecha commit inductor SZZ) | E11f, E10h | Valor real: 0.23 h (n = 3) | ✅ |
| MET-R2 | MTTR | `process_metrics.py`: promedio y mediana (fecha merge − fecha fix) | E11f, E10h | Valor real: promedio 0.07 h, mediana 0.05 h (n = 3) | ✅ |
| MET-R3 | Eficacia de pruebas | `process_metrics.py`: críticos antes de producción / críticos con fase conocida (+ todas las severidades) | E11f | Con defectos críticos reales: aún 0 críticos (todas las severidades: 3/3 = 100 % antes de producción) | 🟨 (0 críticos) |
| MET-J1 | Eficacia de revisión | `project_metrics.py`: defectos en revisión / defectos con fase conocida | E11f, E15, E10g | Valor real: 66.67 % (2 de 3) | ✅ |
| MET-J2 | Desviación tiempo/esfuerzo por módulo | `project_metrics.py` + `data/time_log.csv` (estimación en 76f14fb, antes del código) | E11d | Desviación por módulo y total con datos reales | ✅ |
| MET-J3 | Plazos (+ satisfacción opcional) | `project_metrics.py`: fecha real de cierre vs fecha del sprint (`pyproject.toml`) | E11d | % de tareas a tiempo con datos reales | ✅ |
| EST-1 | Juicio de expertos | `estimation.py` sobre `data/time_log.csv` (línea base en 76f14fb) | E12 | 22.5 h | ✅ |
| EST-2 | Estimación análoga | `estimation.py` + `data/estimacion.json` (referencia: herramienta `metricas`, 4.5 h, 103 PF, factor 1.13) | E12 | 4.79 h con referencia y factor justificados (D16) | ✅ |
| EST-3 | Tres puntos (PERT) | `estimation.py`: E = (O + 4M + P)/6 por tarea, σ combinada | E12 | 24.79 h ± 1.35 h | ✅ |
| EST-4 | Puntos de función | `estimation.py`: 97 PF sin ajustar (IFPUG/ISO 20926) × 0.0437 h/PF | E12 | 4.24 h; conteo documentado en `data/estimacion.json` | ✅ |
| PRO-01 | Kanban | GitHub Projects (Backlog, Ready, In Progress con WIP 2, Review/Validate, Done) | E02, E02c (cierre S0), E02d (tablero final: 18 en Done) | Capturas por sprint | ✅ |
| PRO-02 | Commits por cambio | Git + PR con merge commit + Conventional Commits | E00c, E02b, E15c; tabla de PRs (cap. 8.2) | Mensajes con ID de tarea | ✅ |
| PRO-03 | Evidencia por sprint | `docs/EVIDENCIAS.md` | E00–E17d | E01–E14 con archivo y fecha | 🟨 (falta E14: captura de la matriz final) |
| PRO-04 | Bitácora de IA | `docs/AI_LOG.md` (incluye errores de la IA y su corrección) | `docs/AI_LOG.md` | Entradas por sprint | ✅ |

**Grado de cumplimiento actual:** 40 / 44 (90.9 %) Cumple · 4 en progreso. Nada se marca Cumple hasta tener evidencia.
