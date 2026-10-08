# Registro de evidencias

Nombre de archivo: `evidence/E##_descripcion_AAAA-MM-DD_HHMM.png`. Una fila por captura o log. Nunca se borra una evidencia.

| ID | Evidencia | Archivo | Fecha y hora | Commit / ejecución | Requisitos |
|---|---|---|---|---|---|
| E00 | Entorno inicial: versiones de Python y Git, `git init`, venv | `evidence/E00_entorno_2026-10-04_2139.png` | 2026-10-04 21:39 | — | PRG-05 |
| E00b | Instalación de dependencias con Python 3.14.3 y versiones resultantes | `evidence/E00b_pip_install_1_2026-10-04_2310.png`, `evidence/E00b_pip_install_2_2026-10-04_2310.png` | 2026-10-04 ~23:10 | — | PRG-06 |
| E00c | Primer push y `git log` | `evidence/E00c_primer_push_2026-10-04_2302.png` | 2026-10-04 23:02 | 76f14fb | PRG-05, PRO-02 |
| E01 | Repositorio GitHub con estructura, README y 1 contribuidor | `evidence/E01_repo_github_1_2026-10-05.png`, `evidence/E01_repo_github_2_readme_2026-10-05.png` | 2026-10-05 ~00:00 | 9823160 | PRG-05, DOC-08 |
| E02 | Tablero Kanban con 25 issues (T01–T25), columnas y WIP = 2; tomado durante T02 | `evidence/E02_kanban_durante_T02_2026-10-05_0050.png` | 2026-10-05 ~00:50 | — | PRO-01, CAL-08 |
| E02c | Tablero Kanban público, columnas ordenadas, T01–T03 en Done (cierre de S0); #2 cerrado 2026-10-05T06:55:23Z | `evidence/E02c_kanban_final_S0_2026-10-05_0110.png` | 2026-10-05 ~01:10 | 3a8a2d5 | PRO-01, CAL-08 |
| E02b | Primer PR (#26) integrado con merge commit | `evidence/E02b_primer_pr_merge_2026-10-05_0057.png` | 2026-10-05 00:57 | 2c456f0 → 3a8a2d5 | PRO-02, CAL-08 |
| E03 | Diagramas generados con Graphviz desde código versionado: arquitectura, pipeline CI y ciclo de vida del defecto | `docs/diagramas/arquitectura.png`, `pipeline.png`, `ciclo_defecto.png` (fuentes `.dot`) | 2026-10-08 | T20 | DOC-04, CAL-08 |
| E04 | pytest (17/17) y ruff limpio — T08 | `evidence/E04_pytest_ruff_T08_2026-10-06_1222.png` | 2026-10-06 12:22 | 1b1c11e + cambios de T08 | PRG-04, PRG-06 |
| E04b | Ejecución de la CLI `python -m qualityops` y primeras líneas de `reports/metrics.json` (17/17 pruebas, cobertura 81.88 %, CC máx. 9, 0.449 KLOC, 0 defectos) | `evidence/E04b_cli_metrics_json_T08_2026-10-06_1222.png` | 2026-10-06 12:22 | 1b1c11e + cambios de T08 (sin commit aún) | PRG-06, PRG-07 |
| E05 | Salida de pytest (5/5) y ruff limpio — T04 | `evidence/E05_pytest_ruff_T04_2026-10-05.png` | 2026-10-05 ~10:20 | 19d18b6 | PRG-04, CAL-05 |
| E05b | Salida de pytest (8/8) y ruff limpio — T05 | `evidence/E05b_pytest_ruff_T05_2026-10-05.png` | 2026-10-05 ~10:40 | 6ad52ac | PRG-04, CAL-05 |
| E06 | Cobertura de QualityOps vs. `coverage report` (coinciden por archivo; global 80.62 %) | `evidence/E06_cobertura_vs_coverage_T05_2026-10-05.png` | 2026-10-05 ~10:40 | 6ad52ac | MET-P2 |
| E07 | Complejidad por función de QualityOps vs. `radon cc -s` (7/7 coinciden) | `evidence/E07_complejidad_vs_radon_T04_2026-10-05.png` | 2026-10-05 ~10:20 | 19d18b6 | MET-P1 |
| E08a | Quality gate local: con umbral de DEMOSTRACIÓN (cobertura ≥ 95 %) → BLOQUEADO, código 1; con umbral real (≥ 75 %) → APROBADO, código 0. CLI: 24/24 pruebas, cobertura 83.52 %, CC máx. 9, 0.5 KLOC | `evidence/E08a_cli_T09T10_2026-10-06_1240.png`, `evidence/E08a_gate_demo_y_real_2026-10-06_1240.png` | 2026-10-06 ~12:40 | 8d4f922 + cambios de T09/T10 | CAL-07, PRG-04 |
| E08 | GitHub Actions, PR #35: job `calidad` en verde (34 s) y resumen del quality gate APROBADO (25/25 pruebas, cobertura 83.88 %, CC máx. 9) | `evidence/E08_actions_summary_gate_T11_2026-10-08_0010.png` | 2026-10-08 ~00:10 | 6f91847 | PRG-01, PRG-03, CAL-05 |
| E08b | Ruleset `proteger-main` activo (4 reglas: PR obligatorio, check `calidad` obligatorio, sin force push) | `evidence/E08b_ruleset_proteger_main_2026-10-08_0020.png` | 2026-10-08 ~00:20 | — | CAL-07 |
| E08c | Artefacto `reportes-calidad` publicado por el pipeline | `evidence/E08c_actions_artefacto_T11_2026-10-08_0010.png` | 2026-10-08 ~00:10 | 6f91847 | PRG-03 |
| E08d | Log del pipeline paso a paso (ruff, métricas: 0.518 KLOC en 8 archivos, 0 defectos; gate; artefacto) | `evidence/E08d_actions_pasos_log_T11_2026-10-08_0010.png` | 2026-10-08 ~00:10 | 6f91847 | PRG-03, PRG-06 |
| E08e | `gh pr checks --watch`: 1 check exitoso | `evidence/E08e_gh_pr_checks_T11_2026-10-08_0010.png` | 2026-10-08 ~00:10 | 6f91847 | PRG-01 |
| E11 | Minería de defectos sobre el propio repo: 8 commits, 3 merges, 0 tags, 0 defectos (aún no hay commits `fix:`); 13/13 pruebas | `evidence/E11_mineria_defectos_T06_2026-10-05_2115.png` | 2026-10-05 21:15 | a7f8d76 | MET-P3, MET-R1..R3, MET-J1 |
| E11b | Densidad de defectos por archivo y global (0 defectos / 0.387 KLOC = 0.0) | `evidence/E11b_densidad_T07_2026-10-05_2132.png` | 2026-10-05 21:32 | fe34430 | MET-P3 |
| E11c | `radon raw -s`: SLOC por archivo coincide con la densidad (91, 163, 37, 95) | `evidence/E11c_radon_raw_sloc_T07_2026-10-05_2132.png` | 2026-10-05 21:32 | fe34430 | MET-P3 |
| E11d | CLI con métricas de proceso y proyecto: 32/32 pruebas, cobertura 85.68 %, 0.615 KLOC, MTTD/MTTR sin datos (n = 0), desviación −52.8 % (11 tareas), plazos 54.55 % | `evidence/E11d_cli_proceso_proyecto_T13T14_2026-10-08_0035.png` | 2026-10-08 ~00:35 | 415d819 + cambios de T13/T14 | MET-R1..R3, MET-J1..J3 |
| E08f | CI verde en PR #36 antes del merge (primera vez con `main` protegida) | `evidence/E08f_gh_pr_checks_T13T14_2026-10-08_0037.png` | 2026-10-08 00:37 | 1b871e5 | PRG-01, CAL-07 |
| E12 | Estimaciones (4 técnicas) | | | | EST-1..4 |
| E10 | Resumen de Actions del PR #38: gate APROBADO + informe de calidad completo (12 secciones, fuente: reglas, verificaciones de coherencia OK) | `evidence/E10_actions_PR38_summary_1..4_2026-10-08_0120.png` | 2026-10-08 ~01:20 | cf916cb | CAL-02, PRG-02, MET-00 |
| E10b | Checks verdes del PR #38 y primer intento de merge fallido por 502 de GitHub | `evidence/E10b_checks_y_merge_502_PR38_2026-10-08_0122.png` | 2026-10-08 01:22 | cf916cb | PRG-01 |
| E10c | Informe generado localmente (lectura en PowerShell sin `-Encoding UTF8`, por eso los acentos se ven mal; el archivo es UTF-8) | `evidence/E10c_informe_local_powershell_2026-10-08_0115.png` | 2026-10-08 01:15 | 6de8c75 + cambios | CAL-02 |
| E12 | CLI con las 4 técnicas: juicio 22.5 h · PERT 24.79 h · PF 4.24 h · análoga 4.79 h; 44/44 pruebas; gate APROBADO | `evidence/E12_cli_estimacion_4_tecnicas_2026-10-08_0114.png` | 2026-10-08 01:14 | 6de8c75 + cambios | EST-1..4 |
| E15 | **Defecto real 1** detectado en revisión del PR #38: `qualityops/__main__.py` se mostraba como **main.py** | `evidence/E15_defecto1_markdown_main_py_PR38_2026-10-08_0120.png` | 2026-10-08 01:20 | cf916cb (inductor) | MET-J1, MET-R1 |
| E15b | Informe corregido en Actions: `qualityops/__main__.py` y defecto 1 en la tabla (menor, revisión) | `evidence/E15b_informe_corregido_PR38_2026-10-08_0135.png` | 2026-10-08 ~01:35 | a6139f9 | MET-J1 |
| E15c | Commit de corrección con trailers `Severidad`, `Detectado-en`, `Evidencia`, `Refs` | `evidence/E15c_commit_fix_con_trailers_2026-10-08_0131.png` | 2026-10-08 01:31 | a6139f9 | PRO-02, CAL-08 |
| E11e | Minería sobre main: 1 defecto real (menor, revisión por trailer), MTTD 0.22 h, MTTR 0.13 h, inductor cf916cb | `evidence/E11e_mineria_1_defecto_real_2026-10-08_0140.png` | 2026-10-08 ~01:40 | 054a942 | MET-P3, MET-R1, MET-R2, MET-J1 |
| E09a–h | Dashboard Streamlit, 6 pestañas: resumen con quality gate, matriz de cumplimiento calculada, producto, funciones más complejas, proceso, proyecto, estimación y AI Advisor | `evidence/E09a…E09h_dashboard_*_2026-10-08_0215.png` | 2026-10-08 ~02:15 | c8b2162 | PRG-06, CAL-01 |
| E10d | Actions del PR #39: el informe declara fuente `reglas` (GitHub Models no respondió) | `evidence/E10d_actions_PR39_fuente_reglas_2026-10-08_0225.png` | 2026-10-08 ~02:25 | c8b2162 | PRG-02, MET-00 |
| E10e | Actions del PR #39: interpretación por reglas en el informe | `evidence/E10e_actions_PR39_interpretacion_2026-10-08_0225.png` | 2026-10-08 ~02:25 | c8b2162 | MET-00 |
| E10f | Actions del PR #39: artefacto `reportes-calidad` y avisos del run | `evidence/E10f_actions_PR39_artefacto_avisos_2026-10-08_0225.png` | 2026-10-08 ~02:25 | c8b2162 | PRG-03 |
| E10g | **Defecto real 3** corregido: el informe muestra la fila *Intento de LLM* con el motivo del fallo | `evidence/E10g_informe_intento_llm_PR39_2026-10-08_0240.png` | 2026-10-08 ~02:40 | a02edd4 | MET-J1, CAL-02 |
| E10m | Gemini `gemini-3.8-flash` agota 90 s de espera con el prompt del informe → ruta por reglas (tolerancia a fallos) | `evidence/E10m_timeout_gemini_3.8_flash_2026-10-08_0325.png` | 2026-10-08 ~03:25 | 71f84cb (antes del commit) | CAL-06, PRG-02 |
| E10j | **Defecto real 4**: pytest tarda 105 s porque una prueba llamaba a la API real de Gemini | `evidence/E10j_pytest_105s_2026-10-08.png` | 2026-10-08 ~03:20 | antes de 71f84cb | CAL-05, MET-R1 |
| E10l | Defecto 4 corregido (56 pruebas en 30 s), commit `fix(tests)` con trailers y error 404 detallado de un modelo inexistente | `evidence/E10l_commit_fix_defecto4_y_404_modelo_2026-10-08_0335.png` | 2026-10-08 ~03:35 | 71f84cb | PRO-02, CAL-08 |
| E10h | CLI + quality gate + informe con **fuente `llm`, proveedor `gemini`** (56/56 pruebas, cobertura 88.73 %, CC máx. 9, 1.066 KLOC, 3 defectos, densidad 2.81 def/KLOC, MTTD 0.23 h, MTTR 0.07 h) | `evidence/E10h_cli_gate_report_llm_gemini_2026-10-08_0350.png` | 2026-10-08 ~03:50 | 71f84cb + cambios | PRG-02, MET-00, PRG-06 |
| E10i | Sección 10 del informe: interpretación por reglas + interpretación del modelo de lenguaje | `evidence/E10i_informe_seccion10_llm_2026-10-08_0350.png` | 2026-10-08 ~03:50 | 71f84cb + cambios | MET-00, CAL-02 |
| E10k | Summary de Actions del PR #40: job `calidad` verde, *Intento de LLM: usado*, dictamen LIBERAR CON CONDICIONES | `evidence/E10k_actions_PR40_intento_llm_usado_2026-10-08_0353.png` | 2026-10-08 03:52 (UTC 09:52) | 436e614 | PRG-01, PRG-02, PRG-03, CAL-02 |
| E11f | Minería sobre main: 3 defectos reales de producto (1 menor/revisión, 1 mayor/pruebas, 1 menor/revisión) con inductor, MTTD y MTTR | `evidence/E11f_mineria_3_defectos_reales_2026-10-08_0300.png` | 2026-10-08 ~03:00 | 78be41c | MET-P3, MET-R1, MET-R2, MET-J1 |
| E08g | El ruleset impide el merge del PR #41 mientras el check obligatorio «calidad» no termina («the base branch policy prohibits the merge») | `evidence/E08g_ruleset_bloquea_merge_sin_check_PR41_2026-10-08.png` | 2026-10-08 ~07:25 | c4232f6 | CAL-07, PRG-01 |
| E17a | **Bloqueo real en CI**: `gh pr checks --watch` del PR #42 con el check «calidad» fallido (49 s) | `evidence/E17a_gh_pr_checks_rojo_PR42_2026-10-08.png` | 2026-10-08 | 5576e4f | CAL-07 |
| E17b | Summary del PR #42: Quality gate BLOQUEADO; pruebas 56/56 y cobertura 86.3 % aprueban, complejidad máxima 11 > 10 falla | `evidence/E17b_actions_gate_bloqueado_cc11_PR42_2026-10-08.png` | 2026-10-08 | 5576e4f | CAL-07, PRG-03 |
| E17c | PR #42: «All checks have failed», check «calidad» *Required* y botón de merge deshabilitado | `evidence/E17c_pr42_merge_deshabilitado_2026-10-08.png` | 2026-10-08 | 5576e4f | CAL-07 |
| E17d | Informe del PR #42 con dictamen NO LIBERAR y la recomendación de corregir los criterios que fallan | `evidence/E17d_actions_dictamen_no_liberar_PR42_2026-10-08.png` | 2026-10-08 | 5576e4f | CAL-02, CAL-07 |
| E13 | Reporte final | | | | DOC-01..09 |
| E14 | Matriz de cumplimiento final | | | | CAL-01 |
