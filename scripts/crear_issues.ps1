# Crea un issue de GitHub por cada tarea de data/time_log.csv.
# Requisitos: GitHub CLI instalado (winget install GitHub.cli) y sesión iniciada (gh auth login).
# Uso, desde la raíz del repositorio:   .\scripts\crear_issues.ps1
Import-Csv -Path "data/time_log.csv" -Encoding UTF8 | ForEach-Object {
    # Cuerpo del issue: requisitos que cubre, módulo, estimación y sprint planeado
    $cuerpo = @"
**Requisitos:** $($_.requisitos)
**Módulo:** $($_.modulo)
**Estimación (optimista / más probable / pesimista, h):** $($_.optimista_h) / $($_.mas_probable_h) / $($_.pesimista_h)
**Sprint planeado:** $($_.sprint_planeado)

**Criterio de terminado:** ver docs/00_DIAGNOSTICO.md, sección 6 (backlog).
"@
    gh issue create --repo TaikoVC/qualityops-ai --title "$($_.tarea) - $($_.descripcion)" --body $cuerpo
}
