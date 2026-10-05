# Normas y referencias aplicadas

Regla: una norma solo se menciona en el reporte si aparece en esta tabla con **cómo se aplicó** y **dónde está la evidencia**.
Si no se aplicó realmente, no se cita como aplicada (puede citarse como "referencia conceptual").

| Norma (versión vigente) | Qué establece | Cómo se aplica en QualityOps AI | Requisito | Evidencia |
|---|---|---|---|---|
| ISO/IEC 25010:2023 — Modelo de calidad del producto (SQuaRE) | 9 características de calidad del producto con sus subcaracterísticas | Se evalúan **idoneidad funcional** (completitud, corrección, pertinencia) y **fiabilidad** (ausencia de fallos, disponibilidad, tolerancia a fallos, recuperabilidad), cada una con una medida real del proyecto | CAL-06 | Tabla ISO 25010 del reporte (T16) |
| ISO/IEC 25023:2016 — Medición de la calidad del producto | Medidas cuantitativas para las características de 25010 | Base de las fórmulas de la tabla anterior (p. ej., completitud funcional = funciones implementadas / especificadas) | CAL-06 | `docs/` + reporte |
| IEEE 730-2014 — Procesos de aseguramiento de la calidad del software | Contenido de un plan SQA: actividades, responsables, estándares, métricas, herramientas | Plan SQA resumido: pruebas, lint, revisión por PR, quality gates, métricas y registros | CAL-05 | Capítulo SQA del reporte |
| ISO/IEC/IEEE 29119-3:2021 — Documentación de pruebas | Estructura de documentos de prueba, incluido el **informe de finalización de pruebas** | Formato fijo del informe de calidad que genera el programa en cada ejecución | CAL-02 | `reports/quality_report.md` (T12) |
| ISO/IEC/IEEE 12207:2017 — Procesos del ciclo de vida del software | Procesos técnicos y de gestión del ciclo de vida | Mapeo de cada etapa del pipeline (desarrollo, verificación, integración, gestión de configuración, liberación) a sus procesos | CAL-08 | Diagrama del pipeline (T20) |
| ISO/IEC/IEEE 90003:2018 — Aplicación de ISO 9001:2015 al software | Gestión de calidad basada en procesos, prevención y mejora continua | Fundamento del enfoque preventivo (quality gates antes de integrar) y de la mejora continua (métricas → acciones) | CAL-07 | Capítulo de enfoque preventivo |
| ISO/IEC 20926:2009 — Método IFPUG de medición del tamaño funcional | Conteo de puntos de función (EI, EO, EQ, ILF, EIF) | Técnica de estimación por puntos de función | EST-4 | Tabla de estimación (T15) |

## Referencias técnicas (no son normas, pero sustentan umbrales)

| Referencia | Uso |
|---|---|
| McCabe (1976) | Complejidad ciclomática; umbral ≤ 10 bajo riesgo |
| Arguelles et al. (2020), Google Testing Blog | Cobertura: 60 % aceptable, 75 % encomiable, 90 % ejemplar |
| McConnell (2004), *Code Complete* | Densidad de defectos de referencia en la industria |
| Forsgren et al. (2018–2019), DORA / *Accelerate* | MTTR y prácticas DevOps de alto desempeño |
| Jones (2008) | Eficiencia de eliminación de defectos (eficacia de pruebas y de revisión) |
| Śliwerski, Zimmermann y Zeller (2005), SZZ | Identificación del commit que introdujo cada defecto |
| PMI, *PMBOK Guide* | Juicio de expertos, estimación análoga y de tres puntos (PERT) — **verificar edición al redactar referencias** |
| Conventional Commits 1.0.0, SemVer 2.0.0 | Convenciones de commits y versiones que hacen medible el historial |

## Pendiente de verificar al redactar el reporte

- Revisar los nombres oficiales en español de las subcaracterísticas de ISO/IEC 25010:2023.
- Confirmar edición del PMBOK que se citará.
