# QualityOps AI

Herramienta académica **DevOps + IA** que mide, valida y reporta la calidad de su propio código
en cada cambio (*dogfooding*): ejecuta pruebas, calcula métricas de producto, proceso y proyecto,
aplica *quality gates* en GitHub Actions y genera un informe de calidad con interpretación asistida por IA.

> Proyecto individual — Estándares y Métricas para el Desarrollo de Software — UTCJ, DSM51.
> Autor: Ivan Valle Cortes (24110751).

## Estado

🚧 Sprint 0 — estructura inicial. Aún no hay código funcional.
El avance real se registra en [`docs/MATRIZ_CUMPLIMIENTO.md`](docs/MATRIZ_CUMPLIMIENTO.md) y en [`CHANGELOG.md`](CHANGELOG.md).

## Requisitos

- Python 3.14 (probado localmente con 3.14.3)
- Git

## Instalación (Windows / PowerShell)

```powershell
git clone https://github.com/TaikoVC/qualityops-ai.git
cd qualityops-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Uso

_Se completará en el Sprint 1 (CLI `python -m qualityops`) y el Sprint 2 (dashboard `streamlit run app.py`)._

## Convención de trabajo (obligatoria)

Estas reglas existen porque las métricas de proceso (MTTD, MTTR, eficacia de pruebas y de revisión)
se calculan **automáticamente a partir del historial de Git**. Si no se respetan, los datos no son medibles.

1. **Una tarea = una rama = un Pull Request.** Rama: `T04-complejidad`. El PR enlaza su issue (`Closes #4`).
2. **Conventional Commits.** `feat:`, `fix:`, `test:`, `docs:`, `ci:`, `refactor:`, `chore:`.
3. **Todo defecto real se corrige con un commit `fix:`** que incluya estas líneas (trailers) en el cuerpo:

   ```
   fix(product_metrics): evita división entre cero cuando no hay líneas de código

   Severidad: critica | mayor | menor
   Detectado-en: revision | pruebas | produccion
   Evidencia: <URL de la ejecución de Actions, del comentario del PR o captura en evidence/>
   Refs: #<issue>
   ```

4. **Los PR se integran con "Create a merge commit"** (no *squash*, no *rebase*): el merge commit es la fecha de reparación (MTTR).
5. **"Producción" = una versión etiquetada** (`v0.1.0`, …, `v1.0.0`). Un defecto corregido después de un tag que lo contenía cuenta como escapado a producción.
6. **Nunca se reescribe el historial** (`push --force`, `rebase` de ramas publicadas): borraría evidencia.

## Estructura

```
qualityops/   motor de métricas (Sprint 1)
tests/        pruebas automatizadas (Sprint 1)
data/         datos de gestión reales (estimaciones y tiempos)
reports/      salidas generadas (no se versionan)
docs/         matriz de cumplimiento, normas, decisiones, evidencias, bitácora de IA
evidence/     capturas de pantalla (E01_..., E02_...)
```
