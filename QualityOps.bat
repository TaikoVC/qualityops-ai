@echo off
REM Abre QualityOps AI (dashboard + Centro de pruebas) con doble clic, sin recordar comandos.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creando el entorno virtual por primera vez...
  python -m venv .venv
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)
".venv\Scripts\python.exe" -m streamlit run app.py
