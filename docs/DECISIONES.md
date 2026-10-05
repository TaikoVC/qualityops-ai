# Registro de decisiones

Cada decisión importante queda aquí con fecha, motivo y alternativa descartada. Sirve como evidencia del carácter sistemático (CAL-08).

| # | Fecha | Decisión | Motivo | Alternativa descartada |
|---|---|---|---|---|
| D01 | 2026-10-04 | QualityOps AI se analiza a sí mismo (dogfooding) | Los defectos y tiempos son reales; un solo proyecto mantiene el alcance pequeño. Justificación DevOps: el proyecto se desarrolla con CI y usa su propio pipeline para medir, validar y mejorar su calidad | Analizar un segundo proyecto (solo si después lo exige un requisito) |
| D02 | 2026-10-04 | Métricas calculadas de forma determinista; la IA interpreta | Los números deben ser reproducibles y verificables | Que la IA calcule las cifras |
| D03 | 2026-10-04 | AI Advisor desacoplado con respaldo por reglas desde el inicio | No hay API de IA con saldo; el sistema nunca debe fallar por falta de API | Depender de una API externa |
| D04 | 2026-10-04 | GitHub Projects como tablero Kanban | Enlaza requisito → issue → PR → commit → CI | Trello u hoja de cálculo |
| D05 | 2026-10-04 | Estimaciones registradas antes de escribir código | La desviación de tiempo solo es válida si la estimación es previa (lo prueba el timestamp del commit) | Estimar al final |
| D06 | 2026-10-04 | Motor + CI antes que dashboard | El CI y las métricas son el núcleo DevOps evaluado; el dashboard solo muestra el JSON | Empezar por la interfaz |
| D07 | 2026-10-04 | Defectos obtenidos del historial de Git (minería SZZ reutilizada de la herramienta `metricas`) + trailers `Severidad` y `Detectado-en` en cada `fix:` | Datos verificables por cualquiera con `git log`; evita un registro manual que podría parecer inventado | CSV de defectos llenado a mano |
| D08 | 2026-10-04 | Reutilizar de la herramienta `metricas` solo: minería SZZ, utilidades de tabla/guardado y el esquema de resultado por métrica. Reescribir interpretaciones como plantillas basadas en datos | La herramienta original está hecha para Go y sus textos de interpretación están escritos para secrets-engine; copiarlos sería afirmar cosas falsas | Copiar la herramienta completa |
| D09 | 2026-10-04 | Informe de calidad con formato fijo basado en ISO/IEC/IEEE 29119-3 (informe de finalización de pruebas) y dictamen de liberación | El informe del proyecto anterior describía la estructura en prosa, sin un formato verificable | Informe solo en prosa |
| D10 | 2026-10-04 | Mover el repositorio fuera de `C:\Windows\System32` | Carpeta protegida del sistema: sin permisos de escritura normales y riesgo para el equipo | Mantenerlo ahí |
| D11 | 2026-10-05 | T01 y T03 se registran como bloque conjunto (21:39–23:02, 1.38 h) repartido en proporción a su estimación (0.5 h c/u → 0.69 h c/u) | Se hicieron en el mismo bloque y no hay forma objetiva de separarlas; el reparto conserva el total real | Inventar una división de minutos |
| D12 | 2026-10-05 | Plantilla de PR en `docs/` y workflow de CI creado manualmente por el autor | Las herramientas de IA no pueden escribir en `.github/`; GitHub reconoce la plantilla en `docs/` | — |
| D13 | 2026-10-05 | Posicionar QualityOps AI como herramienta de validación preventiva integrable a cualquier repositorio **Python con Git y pytest** (las métricas de proceso sirven para cualquier lenguaje). Regla de diseño: todo el motor recibe `--repo`; no asume analizar este repositorio. Se agrega T26 (opcional) para demostrarlo en un segundo repositorio | Requisito del profesor: proyecto orientado a tecnologías DevOps, no una aplicación de negocio; permite demostrar portabilidad sin agregar alcance obligatorio | Herramienta acoplada a su propio repositorio |
