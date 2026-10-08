"""Genera las gráficas del reporte a partir de los datos reales del proyecto (T21).

Todas las cifras salen de archivos que produce o mantiene el propio proyecto:
  - reports/metrics.json          (python -m qualityops --repo . --salida reports)
  - data/time_log.csv             (registro de tiempos estimados y reales)
  - docs/MATRIZ_CUMPLIMIENTO.md   (matriz viva de cumplimiento)
  - data/ci_runs.json             (opcional: gh run list -L 100 --json ... > data/ci_runs.json)

Uso (desde la raíz del repositorio; requiere matplotlib, que NO es dependencia del producto):
    pip install matplotlib
    python docs/reporte/graficas.py
Las imágenes se escriben en docs/reporte/figuras/.
"""

import csv
import json
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo archivos PNG
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(__file__).resolve().parent / "figuras"

# Paleta: un tono para magnitud, segundo tono para comparar, verde/rojo solo para estado.
AZUL, NARANJA, VERDE, ROJO, GRIS = "#2a78d6", "#eb6834", "#008300", "#e34948", "#8a8984"
TEXTO, TEXTO_2 = "#0b0b0b", "#52514e"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": "#c9c8c3",
    "axes.labelcolor": TEXTO_2, "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 10,
    "axes.titleweight": "bold", "axes.titlecolor": TEXTO, "figure.dpi": 200,
})


def _guardar(fig, nombre: str) -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(SALIDA / nombre, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  ", SALIDA / nombre)


def cobertura_por_archivo(m: dict, umbral: float) -> None:
    """Barras horizontales: % de líneas ejecutadas por archivo vs. el umbral del gate."""
    filas = sorted(m["producto"]["cobertura"]["por_archivo"], key=lambda f: f["pct"])
    nombres = [f["archivo"].replace("qualityops/", "") for f in filas]
    valores = [f["pct"] for f in filas]
    colores = [ROJO if v < umbral else AZUL for v in valores]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.barh(nombres, valores, color=colores, height=0.62, edgecolor="white", linewidth=1)
    ax.axvline(umbral, color=TEXTO_2, linestyle="--", linewidth=1)
    ax.text(umbral + 0.8, len(nombres) - 0.6, f"umbral {umbral:.0f} %", color=TEXTO_2, fontsize=8)
    for y, v in enumerate(valores):
        ax.text(v + 0.8, y, f"{v:.1f}", va="center", fontsize=7.5, color=TEXTO)
    ax.set_xlim(0, 108)
    ax.set_xlabel("Cobertura de líneas (%)")
    glob = m["producto"]["cobertura"]["global_pct"]
    ax.set_title(f"Cobertura por archivo (global {glob:.2f} %, commit {m['commit']})")
    _guardar(fig, "g1_cobertura_por_archivo.png")


def distribucion_complejidad(m: dict, umbral: int) -> None:
    """Histograma: cuántas funciones tienen cada valor de complejidad ciclomática."""
    cc = Counter(f["cc"] for f in m["producto"]["complejidad"]["funciones"])
    xs = list(range(1, max(max(cc), umbral + 1) + 1))
    ys = [cc.get(x, 0) for x in xs]
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.bar(xs, ys, color=[ROJO if x > umbral else AZUL for x in xs], width=0.7, edgecolor="white")
    ax.axvline(umbral + 0.5, color=TEXTO_2, linestyle="--", linewidth=1)
    ax.text(umbral + 0.6, max(ys) * 0.9, f"umbral McCabe\nCC ≤ {umbral}", color=TEXTO_2, fontsize=8)
    for x, y in zip(xs, ys):
        if y:
            ax.text(x, y + 0.4, str(y), ha="center", fontsize=7.5, color=TEXTO)
    c = m["producto"]["complejidad"]
    ax.set_xticks(xs)
    ax.set_xlabel("Complejidad ciclomática de la función")
    ax.set_ylabel("Funciones")
    ax.set_title(f"Distribución de la complejidad ({c['n_funciones']} funciones; "
                 f"promedio {c['promedio']}, máximo {c['maximo']})")
    _guardar(fig, "g2_distribucion_complejidad.png")


def densidad_por_archivo(m: dict) -> None:
    """Defectos por KLOC en los archivos que tienen al menos un defecto, y el global."""
    d = m["producto"]["densidad"]
    filas = [f for f in d["por_archivo"] if f["defectos"]]
    nombres = [f"{f['archivo'].replace('qualityops/', '')}\n({f['defectos']} def. / {f['sloc']} SLOC)" for f in filas]
    valores = [f["densidad"] for f in filas]
    nombres.append(f"GLOBAL\n({d['n_defectos']} def. / {d['sloc']} SLOC)")
    valores.append(d["densidad_global"])
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    ax.barh(nombres, valores, color=[AZUL] * len(filas) + [NARANJA], height=0.55, edgecolor="white")
    for y, v in enumerate(valores):
        ax.text(v + 0.2, y, f"{v:.2f}", va="center", fontsize=8, color=TEXTO)
    ax.set_xlabel("Defectos por KLOC")
    ax.invert_yaxis()
    ax.set_title("Densidad de defectos por archivo afectado y global")
    _guardar(fig, "g3_densidad_defectos.png")


def tiempos_defectos(m: dict) -> None:
    """MTTD y MTTR de cada defecto real (horas), en barras agrupadas."""
    defs = sorted(m["defectos"]["defectos"], key=lambda x: x["fecha_fix"])
    etiquetas = [f"{x['fix']}\n{x['severidad']} · {x['fase']}" for x in defs]
    xs = range(len(defs))
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    ax.bar([x - 0.18 for x in xs], [x["mttd_horas"] for x in defs], 0.34, color=AZUL, label="Detección (MTTD)")
    ax.bar([x + 0.18 for x in xs], [x["mttr_horas"] for x in defs], 0.34, color=NARANJA, label="Reparación (MTTR)")
    for i, x in enumerate(defs):
        ax.text(i - 0.18, x["mttd_horas"] + 0.005, f"{x['mttd_horas']:.2f}", ha="center", fontsize=7.5)
        ax.text(i + 0.18, x["mttr_horas"] + 0.005, f"{x['mttr_horas']:.2f}", ha="center", fontsize=7.5)
    ax.set_xticks(list(xs), etiquetas)
    ax.set_ylabel("Horas")
    ax.set_ylim(0, max(max(x["mttd_horas"], x["mttr_horas"]) for x in defs) * 1.25)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.32))
    ax.set_title("Tiempo de detección y de reparación de cada defecto real")
    _guardar(fig, "g4_tiempos_defectos.png")


def desviacion_por_modulo(m: dict) -> None:
    """Horas estimadas (más probable) vs. reales por módulo de las tareas terminadas."""
    d = m["proyecto"]["desviacion"]
    mods = sorted(d["por_modulo"].items(), key=lambda kv: kv[1]["estimado_h"], reverse=True)
    nombres = [k for k, _ in mods]
    est = [v["estimado_h"] for _, v in mods]
    real = [v["real_h"] for _, v in mods]
    ys = range(len(mods))
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.barh([y - 0.2 for y in ys], est, 0.38, color=GRIS, label="Estimado (más probable)")
    ax.barh([y + 0.2 for y in ys], real, 0.38, color=AZUL, label="Real")
    for y, (_, v) in enumerate(mods):
        ax.text(max(v["estimado_h"], v["real_h"]) + 0.04, y, f"{v['desviacion_pct']:+.0f} %", va="center", fontsize=7.5)
    ax.set_yticks(list(ys), nombres)
    ax.invert_yaxis()
    ax.set_xlabel("Horas")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title(f"Desviación por módulo ({d['tareas_terminadas']} tareas terminadas; total {d['desviacion_pct']:+.1f} %)")
    _guardar(fig, "g5_desviacion_por_modulo.png")


def estimaciones_vs_real(m: dict, tareas: list[dict]) -> None:
    """Las cuatro técnicas de estimación frente a las horas reales registradas."""
    e = m["estimacion"]
    base = [t for t in tareas if "después de la línea base" not in t.get("nota", "")]
    hechas = [t for t in base if t.get("real_h")]
    real = sum(float(t["real_h"]) for t in hechas)
    etiquetas = ["Juicio de\nexpertos", "Tres puntos\n(PERT)", "Análoga", "Puntos de\nfunción",
                 f"Real registrado\n({len(hechas)} de {len(base)} tareas)"]
    valores = [e["juicio_expertos"]["horas"], e["tres_puntos"]["horas"], e["analoga"]["horas"],
               e["puntos_de_funcion"]["horas"], round(real, 2)]
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.bar(etiquetas, valores, color=[GRIS, GRIS, AZUL, AZUL, NARANJA], width=0.6, edgecolor="white")
    lo, hi = e["tres_puntos"]["rango_95_h"]
    ax.errorbar(1, e["tres_puntos"]["horas"], yerr=[[e["tres_puntos"]["horas"] - lo], [hi - e["tres_puntos"]["horas"]]],
                color=TEXTO, capsize=4, linewidth=1)
    for x, v in enumerate(valores):
        tope = hi if x == 1 else v  # la etiqueta de PERT va arriba de su rango de 95 %
        ax.text(x, tope + 0.6, f"{v:.2f} h", ha="center", fontsize=8)
    ax.set_ylim(0, hi * 1.15)
    ax.set_ylabel("Horas")
    ax.set_title("Estimación del proyecto completo por técnica vs. horas reales registradas")
    _guardar(fig, "g6_estimaciones_vs_real.png")


def cumplimiento_matriz(ruta: Path) -> None:
    """Estado de los requisitos de la matriz viva, agrupados por categoría."""
    estados = {"✅": "Cumple", "🟨": "En progreso", "🟧": "Parcial", "⬜": "Pendiente", "❌": "No cumple"}
    colores = {"Cumple": VERDE, "En progreso": "#eda100", "Parcial": NARANJA, "Pendiente": "#d6d5cf", "No cumple": ROJO}
    conteo: dict[str, Counter] = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        mm = re.match(r"^\| ([A-Z]{3})-[A-Z0-9]+ \|.*\| ([^|]+) \|$", linea)
        if mm:
            simbolo = next((s for s in estados if mm.group(2).strip().startswith(s)), None)
            if simbolo:
                conteo.setdefault(mm.group(1), Counter())[estados[simbolo]] += 1
    cats = ["DOC", "PRG", "CAL", "MET", "EST", "PRO"]
    nombres = {"DOC": "Documento", "PRG": "Programa", "CAL": "Calidad", "MET": "Métricas",
               "EST": "Estimación", "PRO": "Proceso"}
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    izquierda = [0] * len(cats)
    for estado in ["Cumple", "En progreso", "Parcial", "Pendiente", "No cumple"]:
        vals = [conteo.get(c, Counter())[estado] for c in cats]
        if any(vals):
            ax.barh([nombres[c] for c in cats], vals, left=izquierda, color=colores[estado], label=estado,
                    edgecolor="white", linewidth=1.5, height=0.6)
            for i, v in enumerate(vals):
                if v:
                    ax.text(izquierda[i] + v / 2, i, str(v), ha="center", va="center", fontsize=8,
                            color="white" if estado in ("Cumple", "No cumple") else TEXTO)
            izquierda = [a + b for a, b in zip(izquierda, vals)]
    total = sum(sum(c.values()) for c in conteo.values())
    cumple = sum(c["Cumple"] for c in conteo.values())
    ax.invert_yaxis()
    ax.set_xlabel("Requisitos")
    ax.legend(frameon=False, fontsize=8, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    ax.set_title(f"Grado de cumplimiento por categoría: {cumple}/{total} ({100 * cumple / total:.1f} %) cumplen")
    _guardar(fig, "g7_cumplimiento_matriz.png")


def ejecuciones_ci(ruta: Path) -> None:
    """Resultado de las ejecuciones del pipeline (gh run list), por tipo de evento."""
    runs = [r for r in json.loads(ruta.read_text(encoding="utf-8")) if r.get("status") == "completed"]
    eventos = sorted({r["event"] for r in runs})
    resultados = ["success", "failure", "cancelled"]
    colores = {"success": VERDE, "failure": ROJO, "cancelled": GRIS}
    nombres = {"success": "Éxito", "failure": "Falla", "cancelled": "Cancelada"}
    fig, ax = plt.subplots(figsize=(6.4, 2.4))
    izquierda = [0] * len(eventos)
    for res in resultados:
        vals = [sum(1 for r in runs if r["event"] == ev and r["conclusion"] == res) for ev in eventos]
        if any(vals):
            ax.barh(eventos, vals, left=izquierda, color=colores[res], label=nombres[res], height=0.55,
                    edgecolor="white", linewidth=1.5)
            for i, v in enumerate(vals):
                if v:
                    ax.text(izquierda[i] + v / 2, i, str(v), ha="center", va="center", color="white", fontsize=8)
            izquierda = [a + b for a, b in zip(izquierda, vals)]
    ok = sum(1 for r in runs if r["conclusion"] == "success")
    ax.set_xlabel("Ejecuciones del job «calidad»")
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.3))
    ax.set_title(f"Ejecuciones del pipeline: {ok}/{len(runs)} exitosas ({100 * ok / len(runs):.1f} %)")
    _guardar(fig, "g8_ejecuciones_ci.png")


def main() -> None:
    import tomllib

    m = json.loads((RAIZ / "reports" / "metrics.json").read_text(encoding="utf-8"))
    umbrales = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["qualityops"]["umbrales"]
    with (RAIZ / "data" / "time_log.csv").open(encoding="utf-8", newline="") as f:
        tareas = list(csv.DictReader(f))
    print(f"Gráficas a partir de reports/metrics.json (commit {m['commit']}):")
    cobertura_por_archivo(m, umbrales["cobertura_minima"])
    distribucion_complejidad(m, umbrales["complejidad_maxima"])
    densidad_por_archivo(m)
    tiempos_defectos(m)
    desviacion_por_modulo(m)
    estimaciones_vs_real(m, tareas)
    cumplimiento_matriz(RAIZ / "docs" / "MATRIZ_CUMPLIMIENTO.md")
    if (RAIZ / "data" / "ci_runs.json").exists():
        ejecuciones_ci(RAIZ / "data" / "ci_runs.json")


if __name__ == "__main__":
    main()
