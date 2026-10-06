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
| E03 | Diagrama de arquitectura | | | | DOC-04 |
| E04 | pytest (17/17) y ruff limpio — T08 | `evidence/E04_pytest_ruff_T08_2026-10-06_1222.png` | 2026-10-06 12:22 | 1b1c11e + cambios de T08 | PRG-04, PRG-06 |
| E04b | Ejecución de la CLI `python -m qualityops` y primeras líneas de `reports/metrics.json` (17/17 pruebas, cobertura 81.88 %, CC máx. 9, 0.449 KLOC, 0 defectos) | `evidence/E04b_cli_metrics_json_T08_2026-10-06_1222.png` | 2026-10-06 12:22 | 1b1c11e + cambios de T08 (sin commit aún) | PRG-06, PRG-07 |
| E05 | Salida de pytest (5/5) y ruff limpio — T04 | `evidence/E05_pytest_ruff_T04_2026-10-05.png` | 2026-10-05 ~10:20 | 19d18b6 | PRG-04, CAL-05 |
| E05b | Salida de pytest (8/8) y ruff limpio — T05 | `evidence/E05b_pytest_ruff_T05_2026-10-05.png` | 2026-10-05 ~10:40 | 6ad52ac | PRG-04, CAL-05 |
| E06 | Cobertura de QualityOps vs. `coverage report` (coinciden por archivo; global 80.62 %) | `evidence/E06_cobertura_vs_coverage_T05_2026-10-05.png` | 2026-10-05 ~10:40 | 6ad52ac | MET-P2 |
| E07 | Complejidad por función de QualityOps vs. `radon cc -s` (7/7 coinciden) | `evidence/E07_complejidad_vs_radon_T04_2026-10-05.png` | 2026-10-05 ~10:20 | 19d18b6 | MET-P1 |
| E08 | GitHub Actions (verde y bloqueo corregido) | | | | PRG-01, PRG-03, CAL-07 |
| E09 | Dashboard | | | | PRG-06 |
| E10 | AI Advisor: entrada y salida | | | | PRG-02, MET-00 |
| E11 | Minería de defectos sobre el propio repo: 8 commits, 3 merges, 0 tags, 0 defectos (aún no hay commits `fix:`); 13/13 pruebas | `evidence/E11_mineria_defectos_T06_2026-10-05_2115.png` | 2026-10-05 21:15 | a7f8d76 | MET-P3, MET-R1..R3, MET-J1 |
| E11b | Densidad de defectos por archivo y global (0 defectos / 0.387 KLOC = 0.0) | `evidence/E11b_densidad_T07_2026-10-05_2132.png` | 2026-10-05 21:32 | fe34430 | MET-P3 |
| E11c | `radon raw -s`: SLOC por archivo coincide con la densidad (91, 163, 37, 95) | `evidence/E11c_radon_raw_sloc_T07_2026-10-05_2132.png` | 2026-10-05 21:32 | fe34430 | MET-P3 |
| E12 | Estimaciones (4 técnicas) | | | | EST-1..4 |
| E13 | Reporte final | | | | DOC-01..09 |
| E14 | Matriz de cumplimiento final | | | | CAL-01 |
