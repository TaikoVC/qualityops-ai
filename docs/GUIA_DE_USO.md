# Guía de uso: cómo aplicar QualityOps AI a tu repositorio

QualityOps AI mide, valida y reporta la calidad de **cualquier repositorio Python con Git**. No modifica tu proyecto:
lo lee, ejecuta sus pruebas y escribe los resultados en una carpeta aparte.

Hay dos formas de usarlo. Empieza por la A (cinco minutos, en tu equipo); cuando funcione, pasa a la B (en cada Pull Request).

| | A. Local | B. En el CI de tu repositorio |
|---|---|---|
| Para qué | Ver las métricas de tu proyecto ahora | Bloquear automáticamente los cambios que bajan la calidad |
| Dónde corre | Tu computadora | GitHub Actions, en cada push y Pull Request |
| Qué necesitas | Python 3.11+ (probado con 3.14) y Git | Copiar un archivo YAML a tu repositorio |

---

## 1. Requisitos de tu proyecto

| Requisito | Por qué | Si no se cumple |
|---|---|---|
| Código Python (`*.py`) | La complejidad y las líneas se miden con radon | No hay métricas de producto |
| Pruebas que corran con `python -m pytest` **desde la raíz** del proyecto | La cobertura se mide ejecutándolas | Pruebas = 0 y el gate bloquea (exige al menos una prueba) |
| Las dependencias de tu proyecto instaladas **en el mismo Python** que QualityOps | Las pruebas se ejecutan con ese intérprete | Las pruebas fallan por `ModuleNotFoundError` |
| Repositorio Git con **todo** su historial (no un clon `--depth 1`) | La minería de defectos lee commits, merges y tags | Defectos, MTTD y MTTR quedan en 0 / sin datos |
| Commits de corrección con el formato `fix: …` (Conventional Commits) | Así se reconocen los defectos | Defectos = 0 (no se inventan) |

Carpetas que **no** cuentan como producto: `tests/`, `test/`, `docs/`, `.venv/`, `venv/`, `build/`, `dist/`, cachés y archivos `test_*.py`, `*_test.py`, `conftest.py`.

---

## 2. Opción A: analizar tu repositorio en tu equipo

```powershell
# 1) Descargar la herramienta (una sola vez), en una carpeta APARTE de tu proyecto
git clone https://github.com/TaikoVC/qualityops-ai.git
cd qualityops-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1            # Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt

# 2) Instalar en ESTE mismo entorno lo que necesitan las pruebas de tu proyecto
python -m pip install -r C:\ruta\a\tu-proyecto\requirements.txt   # si tu proyecto lo tiene
# (si tu proyecto es un paquete instalable:  python -m pip install -e C:\ruta\a\tu-proyecto)

# 3) Medir, validar e informar
python -m qualityops --repo C:\ruta\a\tu-proyecto --salida reports_tu_proyecto
python -m qualityops.quality_gate --metricas reports_tu_proyecto/metrics.json --config C:\ruta\a\tu-proyecto\pyproject.toml
python -m qualityops.report --metricas reports_tu_proyecto/metrics.json

# 4) Ver los resultados en el dashboard
$env:QUALITYOPS_REPORTS = "reports_tu_proyecto"
streamlit run app.py
```

> Usa una carpeta de salida distinta por proyecto (`reports_tu_proyecto`) para no mezclar resultados.
> Si tu proyecto no tiene `pyproject.toml`, el gate usa los umbrales por defecto (cobertura ≥ 75 %, CC ≤ 10).

---

## 3. Dónde ver cada resultado

| Resultado | Archivo / lugar | Lo produce |
|---|---|---|
| Resumen de todas las métricas | Terminal + `metrics.json` | `python -m qualityops` |
| Dictamen del gate (APROBADO / BLOQUEADO) y criterio por criterio | Terminal + `gate.json`; código de salida 0 / 1 | `python -m qualityops.quality_gate` |
| Informe de calidad de 12 secciones (ISO/IEC/IEEE 29119-3) con dictamen de liberación | `quality_report.md` | `python -m qualityops.report` |
| Interpretación (reglas o LLM), verificaciones de coherencia, motivo si la IA falló | `ai_analysis.json` y sección 10 del informe | `python -m qualityops.report` |
| Vista gráfica (6 pestañas) | `http://localhost:8501` | `streamlit run app.py` |
| Solo una métrica | Terminal | `python -m qualityops.product_metrics --repo R` (o `coverage_metrics`, `defects`, `density`) |
| En el CI | Pestaña *Actions* → run → *Summary*; artefacto `reportes-calidad` | Workflow (opción B) |

---

## 4. Opción B: integrarlo al CI de tu repositorio

1. Copia [`docs/ejemplos/qualityops-ci.yml`](ejemplos/qualityops-ci.yml) a tu repositorio como `.github/workflows/qualityops.yml`.
2. El workflow instala las dependencias de tus pruebas desde `requirements.txt`; si no existe y tu proyecto es un paquete (`pyproject.toml` o `setup.py`), lo instala con `pip install -e`. Si necesitas algo más, agrégalo en ese paso.
3. Revisa la sección `on:` del archivo: se ejecuta en cada Pull Request y en cada push a `main` o `master`; si tu rama principal se llama distinto, cámbiala ahí.
4. Haz commit en una rama y abre un Pull Request: el job **calidad** corre solo y publica el gate y el informe en el *Summary*.
5. Recomendado: en *Settings → Rules → Rulesets* crea una regla para `main` que exija Pull Request y el check **calidad**. Así un cambio en rojo no se puede integrar.

El workflow descarga tu proyecto y la herramienta **en carpetas separadas** (`proyecto/` y `qualityops-ai/`), para que el código de QualityOps no se cuente como parte de tu proyecto, y usa una **versión fija** de la herramienta (`ref: v1.0.1`): tus resultados no cambian si la herramienta se actualiza.

---

## 5. Configuración opcional en tu proyecto

Todo es opcional: sin estos archivos, la métrica correspondiente se reporta como «sin datos», nunca con un valor inventado.

| Qué | Dónde | Habilita |
|---|---|---|
| Umbrales propios | `pyproject.toml` → `[tool.qualityops.umbrales]` con `cobertura_minima = 75.0` y `complejidad_maxima = 10` | Gate a la medida |
| Severidad y fase de cada defecto | Trailers al final del commit `fix:` → `Severidad: critica\|mayor\|menor` y `Detectado-en: revision\|pruebas\|produccion` | Eficacia de pruebas y de revisión exactas |
| Versiones en producción | Tags `vX.Y.Z` | Defectos «escapados a producción» |
| MTTR | Integrar los fixes por Pull Request con *merge commit* | Tiempo de reparación |
| Tiempos y plazos | `data/time_log.csv` (columnas: `tarea, descripcion, modulo, requisitos, optimista_h, mas_probable_h, pesimista_h, sprint_planeado, issue, inicio, fin, real_h, sprint_real, pr, nota`) y `[tool.qualityops.calendario]` en `pyproject.toml` (`S1 = "2026-10-05"`) | Desviación por módulo, plazos, juicio de expertos y PERT |
| Puntos de función y análoga | `data/estimacion.json` (ver el de este repositorio como ejemplo) | Estimación por PF y análoga |

### Cambiar los umbrales del gate

Cada proyecto decide sus umbrales en su propio `pyproject.toml`; no hay que tocar el código de la herramienta:

```toml
[tool.qualityops.umbrales]
cobertura_minima = 75.0      # porcentaje mínimo de líneas cubiertas
complejidad_maxima = 10      # CC máxima permitida por función (McCabe: 10)
```

Recomendación: empieza con los valores por defecto. Si tu proyecto ya tiene funciones más complejas (por ejemplo, docker/secrets-engine usa un límite de 16 en gocyclo), sube el límite **solo con una justificación escrita** (en un registro de decisiones) y bájalo poco a poco conforme refactorices. Así el gate no bloquea todo el primer día pero sigue evitando que la complejidad crezca.

Ejemplo de commit de corrección:

```text
fix(api): el total no incluía el IVA

Severidad: mayor
Detectado-en: revision
```

---

## 6. La llave de IA (opcional)

- **Cada usuario usa su propia llave.** Nunca compartas ni reutilices la de otra persona: la llave identifica a su dueño y consume su cuota. Las llaves no viajan con el código ni con los *forks*.
- **Obtenerla:** <https://aistudio.google.com> → *Get API key* → *Create API key* (gratuita).
- **Local** (no se guarda en ningún archivo):
  ```powershell
  $env:GEMINI_API_KEY = Read-Host "Pega tu llave (no se guarda)"
  python -m qualityops.report --metricas reports_tu_proyecto/metrics.json
  ```
- **En el CI de tu repositorio:** `gh secret set GEMINI_API_KEY` (pide la llave sin mostrarla). El workflow la lee de `secrets.GEMINI_API_KEY`.
- **Sin llave**, o si el servicio falla, el informe se genera con la ruta por reglas y lo dice en la fila «Intento de LLM». Las métricas nunca dependen de la IA.
- Solo se envían métricas agregadas; nunca código ni datos personales.
- Cambiar el modelo: `$env:QUALITYOPS_MODELO_GEMINI = "gemini-3.5-flash-lite"`; cambiar la espera máxima: `$env:QUALITYOPS_TIMEOUT_S = "180"`.

---

## 7. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Pruebas: 0/0` y el gate bloquea | pytest no encuentra pruebas desde la raíz, o no está instalado | Corre `python -m pytest` dentro de tu proyecto; instala tus dependencias en el mismo entorno |
| Muchas pruebas con error `ModuleNotFoundError` | Faltan dependencias del proyecto | `pip install -r requirements.txt` (o `pip install -e .`) en el entorno de QualityOps |
| `Defectos: 0` aunque hubo correcciones | Los commits no empiezan con `fix:` o el clon es superficial | Usa Conventional Commits; clona con historial completo (`fetch-depth: 0` en CI) |
| El gate falla por complejidad | Alguna función tiene CC > 10 | Divide la función o ajusta `complejidad_maxima` en tu `pyproject.toml` (con justificación) |
| `interpretación: reglas` y `error_llm` | Llave inválida, modelo inexistente (404) o servicio saturado (503/timeout) | Revisa la llave; prueba otro modelo con `QUALITYOPS_MODELO_GEMINI` |
| La herramienta mide su propio código | La clonaste dentro de tu proyecto | Ponla en una carpeta aparte (opción A) o usa el workflow con dos checkouts (opción B) |
| Las pruebas tardan más de 10 minutos | Límite de seguridad de la ejecución | Ejecuta un subconjunto o aumenta `TIEMPO_MAXIMO` en `coverage_metrics.py` |

---

## 8. Guía rápida de comandos

| Comando | Qué hace |
|---|---|
| `python -m qualityops --repo R --salida S` | Todas las métricas de R en `S/metrics.json` |
| `python -m qualityops.quality_gate --metricas S/metrics.json [--config R/pyproject.toml]` | Aplica el gate; código 0 = aprobado, 1 = bloqueado |
| `python -m qualityops.report --metricas S/metrics.json` | Informe de calidad + interpretación |
| `python -m qualityops.product_metrics --repo R` | Complejidad por función y líneas |
| `python -m qualityops.coverage_metrics --repo R` | Pruebas y cobertura por archivo |
| `python -m qualityops.defects --repo R` | Defectos del historial con MTTD, MTTR e inductor |
| `python -m qualityops.density --repo R` | Densidad de defectos por archivo |
| `$env:QUALITYOPS_REPORTS = "S"; streamlit run app.py` | Dashboard con los resultados de S |
| `python -m pytest -q` y `ruff check .` | Pruebas y linter de la propia herramienta |

Demostración real sobre un repositorio ajeno: ver el capítulo «Implementación en otro repositorio» del reporte (`docs/reporte/`).
