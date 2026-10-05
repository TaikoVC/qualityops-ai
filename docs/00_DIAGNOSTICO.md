# QualityOps AI — Diagnóstico inicial del proyecto

> Fecha: domingo 4 de octubre de 2026, 20:50 (hora de Ciudad Juárez).
> Fuente: *Plan Maestro QualityOps AI* (requisitos literales, sección 2) + plantilla `PlantillaInvestigacion.docx`.
> Estado: **nada está implementado ni verificado todavía.** Todo lo que aparece abajo es plan, no resultado.

Tiempo real disponible hasta el cierre técnico (miércoles 7, ~20:00): **≈ 2 h hoy + 8 h lunes + 8 h martes + 5 h miércoles ≈ 23 h**, documentación incluida. Todo el plan está dimensionado a eso.

---

## 1. Lista de requisitos

Cada requisito tiene un ID que se usará en issues, commits, evidencias y en la matriz viva.

### 1.1 Reporte académico (DOC)

| ID | Requisito (literal o derivado) | Origen |
|---|---|---|
| DOC-01 | Portada | Literal |
| DOC-02 | Introducción | Literal |
| DOC-03 | Índice tabulado | Literal |
| DOC-04 | Imágenes explicadas (cada imagen con pie y párrafo que la explique) | Literal |
| DOC-05 | Conclusión | Literal |
| DOC-06 | Mínimo 10 hojas con tablas e imágenes explicadas | Literal (punto 1.3) |
| DOC-07 | Usar la plantilla UTCJ (portada: título, materia, prof., nombre–matrícula, fecha; referencias) | Tuyo |
| DOC-08 | Trabajo individual | Literal (nota final) |

### 1.2 Programa (PRG)

| ID | Requisito | Origen |
|---|---|---|
| PRG-01 | Programa enfocado a tecnologías DevOps | Literal |
| PRG-02 | IA aplicada en frameworks | Literal |
| PRG-03 | Automatización | Literal |
| PRG-04 | Validación de software | Literal |
| PRG-05 | GitHub + repositorio | Literal |
| PRG-06 | Ejecución del código y mostrar la salida | Literal |
| PRG-07 | Métricas | Literal |
| PRG-08 | Aplicarse a un proyecto desarrollable en DevOps **y justificarlo** (si no, "no se aceptará") | Literal (nota final) |
| PRG-09 | Funcionalidad revisada en clase (demo en vivo) | Literal (nota final) |

### 1.3 Calidad de software (CAL)

| ID | Requisito | Origen |
|---|---|---|
| CAL-01 | Calidad de software y grado de cumplimiento | Literal 1.1 |
| CAL-02 | Informe de calidad en un formato | Literal 1.2 |
| CAL-03 | Requisitos explícitos | Literal 1.3 |
| CAL-04 | Requisitos del usuario y expectativas del negocio | Literal 1.4 |
| CAL-05 | Aseguramiento de la calidad | Literal 1.5 |
| CAL-06 | Características: idoneidad funcional y fiabilidad | Literal 1.6 |
| CAL-07 | Enfoque preventivo | Literal 1.7 |
| CAL-08 | Carácter sistemático | Literal 1.8 |

### 1.4 Métricas (MET)

| ID | Requisito | Tipo |
|---|---|---|
| MET-00 | Calcular las métricas aplicando la IA | Transversal |
| MET-P1 | Complejidad ciclomática | Producto |
| MET-P2 | Cobertura de código | Producto |
| MET-P3 | Densidad de defectos (por KLOC) | Producto |
| MET-R1 | Tiempo medio de detección (MTTD) | Proceso |
| MET-R2 | Tiempo medio de reparación/recuperación (MTTR) | Proceso |
| MET-R3 | Eficacia de las pruebas (críticos detectados antes de producción) | Proceso |
| MET-J1 | Eficacia de la revisión | Proyecto |
| MET-J2 | Desviación de tiempo y esfuerzo por módulo (+ densidad de defectos por módulo, metodología ágil) | Proyecto |
| MET-J3 | Plazos de entrega y satisfacción del usuario (aparece en la descripción de métricas de proyecto, no como viñeta) | Proyecto (implícito) |

### 1.5 Estimación (EST)

| ID | Técnica |
|---|---|
| EST-1 | Juicio de expertos |
| EST-2 | Estimación análoga |
| EST-3 | Estimación de tres puntos (PERT) |
| EST-4 | Puntos de función |

### 1.6 Reglas de proceso (PRO) — tuyas y del plan

| ID | Regla |
|---|---|
| PRO-01 | Kanban (Backlog → Ready → In Progress → Review/Validate → Done, WIP ≤ 2) |
| PRO-02 | Cada cambio importante = commit descriptivo |
| PRO-03 | Evidencia real (capturas, logs, diagramas) por sprint |
| PRO-04 | Registro de uso de IA durante el desarrollo |
| PRO-05 | Código comentado y explicable |
| PRO-06 | Nada se marca Done sin evidencia |

---

## 2. Matriz Requisito → Implementación → Evidencia → Criterio de aceptación

La versión viva está en `MATRIZ_CUMPLIMIENTO.md` (irá dentro del repo en `docs/`). Resumen:

| ID | Implementación | Evidencia | Criterio de aceptación |
|---|---|---|---|
| DOC-01…05 | Plantilla UTCJ llenada | Reporte .docx/.pdf | Las 5 secciones existen; índice automático actualizado |
| DOC-06 | Reporte con ≥ 10 páginas de **contenido** (sin contar portada ni índice) | PDF final | ≥ 10 páginas de contenido, ≥ 8 tablas, ≥ 10 imágenes con pie y explicación |
| DOC-08 | Repo personal, commits solo tuyos | Historial de Git | `git shortlog -s` muestra un solo autor |
| PRG-01 | CI/CD con GitHub Actions + quality gates | `ci.yml` + ejecuciones | Workflow corre en cada push |
| PRG-02 | `ai_advisor.py` usa un LLM para interpretar el JSON de métricas (con respaldo por reglas) + bitácora de IA en desarrollo | `reports/ai_analysis.md`, `docs/AI_LOG.md`, captura | Se ve la entrada (JSON) y la salida (texto) de la IA |
| PRG-03 | Pipeline automático: lint → pruebas → cobertura → complejidad → gate → informe | Log de Actions | Todos los pasos aparecen en el log |
| PRG-04 | pytest + ruff + quality gate | Salida de pytest/ruff | Pruebas pasan; ruff sin errores |
| PRG-05 | Repo GitHub con README, issues, tablero | URL + capturas | Repo accesible; README permite instalar y ejecutar |
| PRG-06 | CLI `python -m qualityops` + dashboard Streamlit | Capturas de terminal y dashboard | Salida real visible en ambos |
| PRG-07/08 | La herramienta se aplica a un proyecto real (ver ambigüedad A1) | Sección de justificación | Justificación escrita + métricas reales de ese proyecto |
| PRG-09 | Guion de demo de 5 min | `docs/DEMO.md` | Demo ensayada desde cero en < 5 min |
| CAL-01 | Matriz de cumplimiento con semáforo + % de cumplimiento calculado | Tabla + pestaña del dashboard | % = requisitos "Cumple" / total, calculado por el programa |
| CAL-02 | `report.py` genera `reports/quality_report.md` (formato fijo) | Archivo generado + artefacto de CI | El informe se genera solo en cada ejecución |
| CAL-03 | Especificación de requisitos explícitos RF/RNF en tabla | Capítulo del reporte | Cada RF/RNF con ID, descripción, prioridad, criterio |
| CAL-04 | Historia de usuario + expectativas del negocio + criterios de aceptación | Capítulo del reporte | Al menos 1 historia, 3 expectativas medibles |
| CAL-05 | Pruebas automatizadas, lint, revisión, CI | Logs | Pipeline verde en la versión final |
| CAL-06 | Tabla ISO/IEC 25010: idoneidad funcional (completitud, corrección, pertinencia) y fiabilidad (madurez, disponibilidad, tolerancia a fallos, recuperabilidad) medidas con datos del proyecto | Tabla + métricas | Cada subcaracterística con métrica y valor real |
| CAL-07 | Quality gates que **bloquean** el pipeline si no se cumplen umbrales | `ci.yml` + captura de ejecución bloqueada y corregida | Existe al menos 1 ejecución roja por gate y su corrección |
| CAL-08 | Kanban + DoD + trazabilidad issue → commit → CI → evidencia | Tablero, commits `#issue`, registro de evidencias | Cada requisito traza a issue y commit |
| MET-00 | Cálculo determinista con herramientas + IA que interpreta, verifica coherencia y recomienda | E10 | Ver ambigüedad A3 |
| MET-P1 | Radon `cc` por función + promedio | JSON + tabla | Valores coinciden con `radon cc` en terminal |
| MET-P2 | pytest-cov (JSON) global y por módulo | Reporte coverage | Coincide con `coverage report` |
| MET-P3 | defectos registrados / KLOC (LOC de Radon `raw`) | `data/defects.csv` + cálculo | Fórmula probada con pytest |
| MET-R1 | promedio(detectado − introducido) | `defects.csv` con timestamps verificables en Git/Actions | Cada defecto con commit/ejecución de referencia |
| MET-R2 | promedio(corregido − detectado) | Ídem | Ídem |
| MET-R3 | críticos detectados antes de "producción" / críticos totales × 100 | `defects.csv` (columna fase) | Fórmula probada |
| MET-J1 | defectos detectados en revisión / defectos detectados antes de pruebas × 100 | `defects.csv` | Fórmula probada |
| MET-J2 | (real − estimado) / estimado × 100 por módulo + densidad por módulo | `data/time_log.csv` | Estimaciones registradas **antes** de programar |
| MET-J3 | % de tareas terminadas en su sprint planeado (+ encuesta opcional) | Tablero + tabla | Ver ambigüedad A6 |
| EST-1…4 | `estimation.py` con las 4 técnicas sobre el mismo alcance + tabla comparativa | Pestaña/tabla + capítulo | 4 valores, misma unidad (horas), comparados con el real |
| PRO-01…06 | Tablero GitHub Projects, commits, `docs/EVIDENCIAS.md`, `docs/AI_LOG.md`, `CHANGELOG.md` | Repo | Revisado en Sprint 3D |

---

## 3. Riesgos para llegar a tiempo

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | **Documentación al final**: el plan deja solo 2 h el miércoles para ≥ 10 páginas | Alta | Alto | Cada sprint termina con 20–30 min de documentación en la plantilla. El miércoles solo se ensambla y pule |
| R2 | **Métricas de proceso sin datos reales**: si casi no hay defectos, MTTD/MTTR quedan vacíos o tentados a inventarse | Alta | Alto | Registrar **desde hoy** cada fallo real (prueba roja, CI rojo, error de ruff, bug). Timestamps verificables con Git/Actions. Si n es pequeño, se reporta tal cual y se explica |
| R3 | **Desviación de tiempo inválida**: si las estimaciones se escriben después de programar, la métrica es falsa | Alta | Alto | Registrar la estimación por juicio de expertos **hoy, antes de escribir código** y hacer commit (el timestamp lo prueba) |
| R4 | **API de IA no disponible** (requiere llave y saldo) | Media | Medio | Decidir el lunes. Ruta de respaldo por reglas + bitácora de IA en desarrollo. La app nunca falla por falta de API |
| R5 | **Adaptar la herramienta del otro chat** consume más tiempo que escribir lo mínimo o mete complejidad | Media | Medio | Revisarla hoy/mañana temprano y tomar solo las funciones que cubren requisitos. Límite: 1 h de adaptación |
| R6 | Ambigüedad de requisitos → rechazo del profesor ("no se aceptará") | Media | Alto | Usar la interpretación más amplia (sección 4) y una justificación DevOps explícita. Si puedes, confirmar A1/A2 con el profesor el lunes |
| R7 | Windows: rutas, activación de venv, codificación de consola | Media | Bajo | Comandos para PowerShell; el CI corre en Ubuntu, así que se prueba en ambos |
| R8 | Cobertura baja por la UI de Streamlit | Alta | Bajo | La lógica vive en `qualityops/`; `app.py` solo muestra. Se excluye la UI de la cobertura y **se declara** en el reporte |
| R9 | Scope creep (gráficas bonitas, login, deploy en la nube) | Media | Alto | Alcance congelado hoy. Cualquier extra va a columna "Después de entregar" |
| R10 | Formato Word con la plantilla (índice, numeración, pies de figura) consume horas | Media | Medio | Usar estilos de título de la plantilla desde el primer capítulo; índice automático |
| R11 | Revisión de código en trabajo individual (no hay segundo revisor) | Alta | Medio | Ver ambigüedad A5: PR + autorrevisión con checklist + revisión de IA, registrada |

---

## 4. Requisitos ambiguos e interpretación más segura

| # | Requisito | Lecturas posibles | Interpretación más segura (recomendada) |
|---|---|---|---|
| A1 | "Desarrollar y aplicar algún proyecto que se pueda desarrollar en DevOps, se debe justificar" | (a) QualityOps es el proyecto DevOps; (b) QualityOps debe aplicarse a otro proyecto | **Ambas**: QualityOps se desarrolla con DevOps **y** se analiza a sí mismo (dogfooding: sus defectos y tiempos son reales). Opcional, si alcanza: correrlo también sobre un segundo proyecto pequeño. **Decisión tuya** (ver al final) |
| A2 | "Requisitos explícitos (Mínimo 10 hojas con tablas y con imágenes explicadas)" | (a) el reporte completo ≥ 10 hojas; (b) el apartado de requisitos explícitos ≥ 10 hojas | Reporte de **15–18 páginas** con ≥ 10 de contenido, y un capítulo propio de "Requisitos explícitos" (RF/RNF en tablas). Así cumple ambas lecturas razonables sin relleno. Si puedes preguntarle al profesor, pregúntale |
| A3 | "Calcular las métricas aplicando la IA" | (a) la IA hace los cálculos; (b) la IA ayuda a obtener/interpretar | Cálculo **determinista** con herramientas (Radon, coverage, fórmulas probadas) para que los números sean confiables, **y** la IA: (1) recibe el JSON y lo interpreta, (2) verifica que los valores sean coherentes con las fórmulas, (3) recomienda acciones. Se muestra entrada y salida de la IA. Así se puede defender: "la IA no inventa números, los analiza" |
| A4 | "Desviación de tiempo y esfuerzo: … tiempo real de ejecución entre cada módulo para obtener el porcentaje de la densidad de defectos mediante la metodología ágil" (redacción confusa) | (a) estimado vs real por módulo; (b) densidad de defectos por módulo; (c) tiempo de ejecución del código | Una sola tabla por módulo: **horas estimadas, horas reales, desviación %, defectos, KLOC, densidad** + tiempo de ejecución de pruebas por módulo (`pytest --durations`). Cubre las tres lecturas |
| A5 | "Eficacia de la revisión" en trabajo individual | Requiere revisor humano | Cada cambio importante va por Pull Request con checklist de autorrevisión + revisión asistida por IA + ruff. Los defectos encontrados ahí se registran con fase = "revisión". Se declara honestamente que el revisor es el autor asistido por IA |
| A6 | "Satisfacción del cliente o usuario" y "plazos de entrega" (descripción de métricas de proyecto) | Solo contexto vs métricas exigidas | Incluir **cumplimiento de plazos** (% de tareas terminadas en el sprint planeado; sale del tablero, cuesta poco). Satisfacción: encuesta de 5 preguntas a 2–3 compañeros tras ver la demo (opcional, prioridad baja, datos reales) |
| A7 | "Producción" en eficacia de pruebas | No hay producción real | Definir "producción" = versión etiquetada `v1.0` en `main`. Defectos hallados después de la etiqueta = escapados |
| A8 | "Índice tabulado" | Índice manual con tabulaciones vs automático | Índice automático de Word con puntos guía (es tabulado y se actualiza solo) |
| A9 | "Informe de calidad en un formato" | Documento del reporte vs salida del programa | **Ambos**: el programa genera `quality_report.md` con formato fijo, y el reporte académico lo incluye |
| A10 | "IA en frameworks" | IA dentro del framework vs IA para desarrollar | Ambas: IA integrada en la app (AI Advisor) + IA usada en desarrollo (bitácora `AI_LOG.md` con prompts y qué se aceptó/rechazó) |

---

## 5. MVP mínimo funcionando

El MVP está "terminado" cuando **todo esto** se ejecuta desde cero siguiendo el README:

1. `python -m qualityops` analiza el proyecto y genera `reports/metrics.json` + `reports/quality_report.md`.
2. Métricas de producto: complejidad (por función y promedio), cobertura (global y por módulo), LOC/KLOC, densidad de defectos.
3. Métricas de proceso: MTTD, MTTR, eficacia de pruebas, leídas de `data/defects.csv`.
4. Métricas de proyecto: eficacia de revisión, desviación por módulo, cumplimiento de plazos, leídas de `data/time_log.csv` y `data/defects.csv`.
5. Las 4 técnicas de estimación calculadas desde `data/estimation.json`.
6. Quality gate: falla (código de salida ≠ 0) si cobertura < umbral, complejidad máxima > umbral o ruff tiene errores.
7. GitHub Actions corre lint → pruebas → análisis → gate y publica el informe como artefacto.
8. AI Advisor: interpreta `metrics.json`; si no hay API, usa reglas y lo indica.
9. Dashboard Streamlit con pestañas: Resumen/cumplimiento, Producto, Proceso, Proyecto, Estimación, IA.
10. Pruebas unitarias de cada fórmula.

**Fuera del MVP (no se hace):** login, base de datos, deploy en la nube, multiusuario, subir proyectos por la web, gráficas avanzadas, Docker.

---

## 6. Backlog inicial de Kanban (orden de prioridad)

> **Nota (2026-10-04 22:10):** tras las decisiones D07–D09 (`docs/DECISIONES.md`) el backlog vigente, con numeración actualizada (T01–T25) y estimaciones optimista/más probable/pesimista, es `data/time_log.csv`. La tabla de abajo se conserva como versión inicial.

Estimaciones en horas = juicio de expertos inicial (se registran hoy para medir desviación). Tú puedes ajustarlas **antes** del commit de esta noche; después ya no se tocan.

| Prio | ID | Tarea | Req. | Est. (h) | Criterio de terminado |
|---|---|---|---|---|---|
| 1 | T01 | Repo GitHub + estructura + venv + README mínimo | PRG-05 | 0.5 | `git log` con primer commit; repo visible en GitHub |
| 2 | T02 | Tablero Kanban (GitHub Projects) con este backlog como issues | PRO-01, CAL-08 | 0.5 | Captura del tablero con columnas y tareas |
| 3 | T03 | Registrar estimaciones iniciales + plantillas `defects.csv` y `time_log.csv` | MET-J2, EST-1 | 0.5 | Commit con estimaciones antes del primer código |
| 4 | T04 | Métricas de producto: complejidad + LOC (Radon) | MET-P1 | 1.0 | Prueba pasa; valor coincide con `radon cc` en terminal |
| 5 | T05 | Cobertura (pytest-cov JSON) | MET-P2 | 0.75 | % coincide con `coverage report` |
| 6 | T06 | Densidad de defectos | MET-P3 | 0.5 | Fórmula con prueba unitaria |
| 7 | T07 | CLI `python -m qualityops` → `metrics.json` | PRG-06 | 0.75 | Se genera el JSON; captura de terminal |
| 8 | T08 | ruff + config de pytest/coverage en `pyproject.toml` | PRG-04 | 0.25 | `ruff check .` sin errores |
| 9 | T09 | Quality gate con umbrales | CAL-07 | 0.75 | Exit code ≠ 0 al violar umbral (probado) |
| 10 | T10 | GitHub Actions CI | PRG-01, PRG-03 | 1.0 | Ejecución verde + captura; 1 ejecución roja por gate y su corrección |
| 11 | T11 | Generador `quality_report.md` | CAL-02 | 0.75 | Se genera en local y como artefacto de CI |
| 12 | T12 | Métricas de proceso: MTTD, MTTR, eficacia de pruebas | MET-R1..3 | 1.0 | Pruebas de fórmulas pasan; valores desde datos reales |
| 13 | T13 | Métricas de proyecto: eficacia de revisión, desviación, plazos | MET-J1..3 | 1.0 | Ídem |
| 14 | T14 | Módulo de estimación: 4 técnicas | EST-1..4 | 1.25 | Tabla comparativa con pruebas de PERT y PF |
| 15 | T15 | AI Advisor + respaldo por reglas | PRG-02, MET-00 | 1.5 | Captura de entrada/salida; app funciona sin API |
| 16 | T16 | Dashboard Streamlit (6 pestañas, solo lectura del JSON) | PRG-06 | 2.0 | Capturas de cada pestaña |
| 17 | T17 | Matriz de cumplimiento calculada (semáforo + %) | CAL-01 | 0.75 | % calculado por el programa, visible en dashboard |
| 18 | T18 | Tabla ISO 25010 (idoneidad funcional y fiabilidad) | CAL-06 | 0.5 | Cada subcaracterística con métrica real |
| 19 | T19 | Diagramas: arquitectura + flujo del pipeline | DOC-04 | 0.5 | 2 imágenes en `docs/diagrams/` |
| 20 | T20 | Reporte: capítulos en plantilla (incremental por sprint) | DOC-01..07 | 4.0 | ≥ 10 páginas de contenido |
| 21 | T21 | Ejecución desde cero en carpeta limpia + etiqueta `v1.0` | Criterio de éxito | 0.5 | README seguido paso a paso sin errores |
| 22 | T22 | QA final: revisar matriz requisito por requisito | Todos | 1.0 | 100 % filas con evidencia o justificación |
| 23 | T23 | Guion de demo de 5 min | PRG-09 | 0.25 | Ensayo cronometrado |
| 24 | T24 | (Opcional) Encuesta de satisfacción | MET-J3 | 0.5 | Respuestas reales tabuladas |
| — | — | **Total estimado** | | **≈ 22 h** (21.5 sin T24) | Cabe en ~23 h casi sin holgura: por eso T24 es opcional |

---

## 7. Arquitectura mínima recomendada

```
                ┌──────────────────────────── GitHub ────────────────────────────┐
  push / PR ──► │  GitHub Actions: ruff → pytest+cov → python -m qualityops → gate │ ──► artefacto: quality_report.md
                └──────────────────────────────────────────────────────────────────┘
                                                │ (mismo código)
  Local:                                        ▼
  python -m qualityops ──► qualityops/ (motor)
                             ├─ product_metrics   ← radon, coverage.json, defects.csv
                             ├─ process_metrics   ← defects.csv
                             ├─ project_metrics   ← time_log.csv, defects.csv
                             ├─ estimation        ← estimation.json
                             ├─ quality_gate      ← umbrales en pyproject.toml
                             ├─ ai_advisor        ← metrics.json → LLM o reglas
                             └─ report            → reports/metrics.json + quality_report.md
                                                │
  streamlit run app.py ─────────────────────────┘  (solo lee reports/*.json y muestra)
```

Principios: un solo lenguaje (Python), un solo repositorio, un JSON como contrato entre motor, CI, IA y dashboard. El dashboard no calcula nada; así la lógica es probable con pytest y la UI no baja la cobertura.

---

## 8. Estructura inicial de carpetas y archivos

```
qualityops-ai/
├── .github/workflows/ci.yml        # pipeline CI (T10)
├── qualityops/                     # motor (toda la lógica, probada)
│   ├── __init__.py
│   ├── __main__.py                 # CLI: python -m qualityops
│   ├── product_metrics.py
│   ├── process_metrics.py
│   ├── project_metrics.py
│   ├── estimation.py
│   ├── quality_gate.py
│   ├── ai_advisor.py
│   └── report.py
├── tests/                          # una prueba por módulo
├── data/
│   ├── defects.csv                 # registro real de defectos (con timestamps y commit)
│   ├── time_log.csv                # estimado vs real por tarea/módulo
│   └── estimation.json             # entradas de las 4 técnicas
├── reports/                        # SALIDA generada (se ignora en Git salvo snapshot final)
├── docs/
│   ├── MATRIZ_CUMPLIMIENTO.md      # matriz viva
│   ├── EVIDENCIAS.md               # índice E01–E14 → archivo, fecha, commit
│   ├── AI_LOG.md                   # bitácora de uso de IA en el desarrollo
│   ├── DEMO.md                     # guion de demo
│   └── diagrams/
├── evidence/                       # capturas: E05_pytest_2026-10-05_1630.png
├── app.py                          # dashboard Streamlit
├── pyproject.toml                  # config de ruff, pytest, coverage y umbrales
├── requirements.txt
├── CHANGELOG.md
├── .gitignore
└── README.md
```

Esta noche solo se crean las carpetas, README, `.gitignore`, `requirements.txt`, `docs/*.md` y los CSV vacíos con encabezados. Los `.py` se crean en su sprint.

Esquema propuesto de `data/defects.csv`:
`id, titulo, modulo, severidad(critica|mayor|menor), fase_deteccion(revision|pruebas|ci|produccion), introducido_en, detectado_en, corregido_en, commit_origen, commit_correccion, evidencia`

Esquema de `data/time_log.csv`:
`tarea, modulo, estimado_h, real_h, sprint_planeado, sprint_real, inicio, fin`

---

## 9. Dependencias mínimas

| Paquete | Para qué | Requisito |
|---|---|---|
| Python 3.11 o 3.12 | Lenguaje | — |
| `pytest` | Pruebas | PRG-04, CAL-05 |
| `pytest-cov` (incluye coverage) | Cobertura | MET-P2 |
| `radon` | Complejidad ciclomática y LOC | MET-P1, MET-P3 |
| `ruff` | Lint / revisión automática | CAL-07, MET-J1 |
| `streamlit` (trae pandas) | Dashboard | PRG-06 |
| `anthropic` (opcional) | AI Advisor | PRG-02, MET-00 |
| Git + cuenta GitHub | Repo, Actions, Projects | PRG-05 |

Las versiones se fijan en `requirements.txt` con las que **realmente** instale pip en tu equipo (no voy a inventar números de versión).

---

## 10. Orden exacto de los primeros sprints

Ajuste respecto al plan maestro: **el motor y el CI van antes que el dashboard**. Razón: el CI y las métricas son lo que el profesor evalúa como DevOps; el dashboard es solo una vista y depende del JSON.

| Cuándo | Sprint | Tareas | Salida verificable |
|---|---|---|---|
| Dom 20:50–23:00 | **S0 Arranque** | T01, T02, T03 + `MATRIZ_CUMPLIMIENTO.md` al repo + recibir herramienta del otro chat | Primer commit; tablero; estimaciones con timestamp; capturas E01, E02 |
| Lun 15:00–17:00 | S1A Producto | T04, T05, T06 (+ revisar/adaptar herramienta) | Complejidad, cobertura y densidad con pruebas; captura E05–E07 |
| Lun 17:15–19:30 | S1B CLI + gate | T07, T08, T09, T11 | `metrics.json` + `quality_report.md` en local; E04 |
| Lun 19:45–21:30 | S1C CI | T10 | Actions verde + 1 bloqueo de gate corregido; E08 |
| Lun 21:45–23:00 | S1D Evidencia + doc | T19 + capítulos: problema/usuario, justificación DevOps, arquitectura | ~3 páginas en plantilla |
| Mar 15:00–17:00 | S2A Proceso/Proyecto | T12, T13 | Métricas de proceso y proyecto con datos reales; E11 |
| Mar 17:15–19:00 | S2B Estimación | T14, T18 | Tabla de 4 técnicas; E12 |
| Mar 19:15–21:00 | S2C IA | T15 | AI Advisor o respaldo documentado; E10 |
| Mar 21:15–23:00 | S2D Dashboard | T16, T17 + doc de métricas | Capturas E09; ~4 páginas más |
| Mié 15:00–16:30 | S3A Cierre técnico | T21 (desde cero, `v1.0`) | Versión congelada |
| Mié 16:30–19:00 | S3B Documentación | T20 completo | Reporte ≥ 10 páginas de contenido |
| Mié 19:00–20:00 | S3C QA | T22, T23 | Matriz 100 % revisada |
| Mié 20:00–23:00 | Reserva | Solo correcciones | — |
| Jue 8 | Contingencia | Entrega | — |

Al final de cada sprint: actualizar `time_log.csv` (hora real), `defects.csv` (si hubo fallos), tablero, matriz, y commit.
