# Matriz viva de cumplimiento — QualityOps AI

> Regla: una fila solo pasa a **Cumple** cuando existe evidencia real (archivo, captura, log o commit) y se anota su referencia.
> Estados: ⬜ Pendiente · 🟨 En progreso · 🟧 Parcial · ✅ Cumple · ❌ No cumple
> Última actualización: 2026-10-05 10:50 — T05 integrado (PR #29, c7edea1).

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
| PRG-01 | Tecnologías DevOps | GitHub Actions + quality gates | E08 | Workflow en cada push | ⬜ |
| PRG-02 | IA en frameworks | `ai_advisor.py` + `AI_LOG.md` | E10 | Entrada y salida de IA visibles | ⬜ |
| PRG-03 | Automatización | Pipeline lint→test→análisis→gate→informe | E08 | Pasos visibles en log | ⬜ |
| PRG-04 | Validación de software | pytest + ruff | E05, E05b | Pruebas verdes, ruff limpio | 🟨 |
| PRG-05 | GitHub + repositorio | Repo + README + issues | E00, E00c, E01, 9823160 | URL accesible, README reproducible | 🟨 (falta sección Uso del README) |
| PRG-06 | Ejecución y salida | CLI + Streamlit | E04, E09 | Capturas reales | ⬜ |
| PRG-07 | Métricas | Motor `qualityops/` | E05–E12 | Todas las MET calculadas | ⬜ |
| PRG-08 | Proyecto DevOps justificado | Capítulo de justificación | — | Justificación + métricas reales del proyecto analizado | ⬜ |
| PRG-09 | Revisión en clase | `docs/DEMO.md` | — | Demo ensayada < 5 min | ⬜ |
| CAL-01 | Calidad y grado de cumplimiento | Semáforo + % calculado | E14 | % calculado por el programa | ⬜ |
| CAL-02 | Informe de calidad en formato | `report.py` → `quality_report.md` con formato fijo ISO/IEC/IEEE 29119-3 + dictamen | — | Generado en local y en CI; incluye todas las secciones del formato | ⬜ |
| CAL-03 | Requisitos explícitos | Tabla RF/RNF | — | ID, descripción, prioridad, criterio | ⬜ |
| CAL-04 | Requisitos de usuario y negocio | Historia + expectativas | — | ≥ 1 historia, ≥ 3 expectativas medibles | ⬜ |
| CAL-05 | Aseguramiento de calidad | Pruebas + lint + CI + revisión | E05, E08 | Pipeline verde en v1.0 | ⬜ |
| CAL-06 | Idoneidad funcional y fiabilidad | Tabla ISO/IEC 25010:2023 con medidas ISO/IEC 25023 | — | Subcaracterísticas con valor real | ⬜ |
| CAL-07 | Enfoque preventivo | Quality gate bloqueante | E08 | ≥ 1 bloqueo real y su corrección | ⬜ |
| CAL-08 | Carácter sistemático | Kanban + DoD + trazabilidad | E02, E02b | Requisito → issue → commit → evidencia | 🟨 |
| MET-00 | Métricas aplicando IA | Cálculo determinista + IA interpreta/verifica | E10 | Interpretación coherente con valores | ⬜ |
| MET-P1 | Complejidad ciclomática | `qualityops/product_metrics.py` (radon, por función; promedio, mediana, máximo, CC ≤ 10) | E07, 19d18b6, PR #28 | Coincide con `radon cc -s` por función | ✅ |
| MET-P2 | Cobertura | `qualityops/coverage_metrics.py` (pytest-cov, global y por archivo, solo código de producto) | E06, 6ad52ac, PR #29 | Coincide con `coverage report` | ✅ |
| MET-P3 | Densidad de defectos | commits `fix:` (minería SZZ) / KLOC (radon) | E11 | Fórmula probada | ⬜ |
| MET-R1 | MTTD | promedio(fecha fix − fecha commit inductor SZZ) | E11 | Verificable con `git log`/`git blame` | ⬜ |
| MET-R2 | MTTR | promedio(fecha merge del PR − fecha fix) | E11 | Verificable con `git log --merges` | ⬜ |
| MET-R3 | Eficacia de pruebas | críticos detectados antes de un tag / críticos totales (trailers `Severidad`, `Detectado-en`) | E11 | Fórmula probada | ⬜ |
| MET-J1 | Eficacia de revisión | defectos con `Detectado-en: revision` / defectos con fase conocida | E11 | Fórmula probada | ⬜ |
| MET-J2 | Desviación tiempo/esfuerzo + densidad por módulo | `data/time_log.csv` (estimado vs real por módulo) | Estimación en commit 76f14fb (2026-10-04 23:02), antes de cualquier código | Estimación con commit previo al código | 🟨 |
| MET-J3 | Plazos (+ satisfacción opcional) | Tablero / encuesta | — | % tareas en sprint planeado | ⬜ |
| EST-1 | Juicio de expertos | `data/time_log.csv` (columna más probable) | E12 | Horas por tarea/módulo + justificación | 🟨 |
| EST-2 | Estimación análoga | `estimation.py` | E12 | Referencia + factor de ajuste | ⬜ |
| EST-3 | Tres puntos (PERT) | `estimation.py` | E12 | O, M, P, E y σ | ⬜ |
| EST-4 | Puntos de función | `estimation.py` | E12 | Conteo, pesos, PF sin ajustar (y ajustados) | ⬜ |
| PRO-01 | Kanban | GitHub Projects | E02 | Capturas por sprint | 🟨 |
| PRO-02 | Commits por cambio | Git + PR con merge commit | E00c, E02b | Mensajes con ID de tarea | 🟨 |
| PRO-03 | Evidencia por sprint | `docs/EVIDENCIAS.md` | — | E01–E14 con archivo y fecha | ⬜ |
| PRO-04 | Bitácora de IA | `docs/AI_LOG.md` | — | Entradas por sprint | 🟨 |

**Grado de cumplimiento actual:** 2 / 44 (4.5 %) Cumple · 10 en progreso. Nada se marca Cumple hasta tener evidencia.
