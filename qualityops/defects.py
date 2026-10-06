"""Minería de defectos sobre el historial de Git (variante del algoritmo SZZ).

Es la base común de: densidad de defectos (MET-P3), MTTD (MET-R1),
MTTR (MET-R2), eficacia de las pruebas (MET-R3) y eficacia de la revisión (MET-J1).

Adaptado de la herramienta `metricas` (minería SZZ que se aplicó antes a
docker/secrets-engine) a proyectos Python, con dos cambios (decisión D07):
  - Se leen los trailers `Severidad:` y `Detectado-en:` del commit de corrección.
  - Solo cuentan los defectos que tocan código de PRODUCTO (mismas reglas que
    la complejidad); los fix: que solo tocan pruebas o documentación se listan
    aparte como "fixes excluidos", no se esconden.

Definiciones (Śliwerski, Zimmermann y Zeller, 2005):
  - Defecto = commit no-merge cuyo asunto empieza con `fix:` o `fix(...):`.
  - Commit inductor = el commit más reciente, anterior al fix, que escribió
    alguna de las líneas que el fix modifica o borra (git blame sobre el padre).
  - MTTD (horas) = fecha del fix − fecha del commit inductor.
  - MTTR (horas) = fecha del merge del PR que integró el fix − fecha del fix.
    Un fix subido directo a main no tiene MTTR.
  - Fase de detección: la del trailer `Detectado-en:` si existe; si no, se
    deduce: revision (inductor y fix en el mismo PR), produccion (hubo un tag
    vX.Y.Z entre inductor y fix) o pruebas (en otro caso).

Uso rápido desde la terminal:
    python -m qualityops.defects --repo .
"""

from __future__ import annotations

import argparse
import os
import re
import statistics
import subprocess
from datetime import datetime
from pathlib import PurePosixPath

from qualityops.product_metrics import CARPETAS_EXCLUIDAS, es_archivo_de_prueba

FIX_RE = re.compile(r"^fix(\([^)]*\))?!?:", re.IGNORECASE)
TAG_RELEASE_RE = re.compile(r"^v\d+\.\d+\.\d+$")
FASES_VALIDAS = {"revision", "pruebas", "produccion"}
SEVERIDADES_VALIDAS = {"critica", "mayor", "menor"}

# Separadores poco comunes para leer la salida de git sin confundir campos.
SEP_CAMPO, SEP_REGISTRO = "\x1f", "\x1e"


# --------------------------------------------------------------------------
# Acceso a git
# --------------------------------------------------------------------------
def _git(repo, *args) -> str:
    """Ejecuta un comando de git de SOLO LECTURA en `repo` y devuelve su salida.

    GIT_OPTIONAL_LOCKS=0 evita que git cree archivos de bloqueo (.git/index.lock).
    """
    entorno = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    proceso = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=off", *args],
                             capture_output=True, text=True, encoding="utf-8",
                             env=entorno, check=False)
    return proceso.stdout if proceso.returncode == 0 else ""


def _fecha(texto: str) -> datetime:
    return datetime.fromisoformat(texto.strip())


def _horas(desde: datetime, hasta: datetime) -> float:
    return round((hasta - desde).total_seconds() / 3600, 2)


def _normalizar(texto: str) -> str:
    """'Crítica ' -> 'critica', 'Revisión' -> 'revision' (sin acentos, minúsculas)."""
    texto = texto.strip().lower()
    for con, sin in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        texto = texto.replace(con, sin)
    return texto


def es_codigo_de_producto(ruta: str) -> bool:
    """Misma regla que la complejidad: .py fuera de pruebas y carpetas excluidas."""
    partes = PurePosixPath(ruta).parts
    return (ruta.endswith(".py")
            and not any(p in CARPETAS_EXCLUIDAS for p in partes[:-1])
            and not es_archivo_de_prueba(PurePosixPath(ruta)))


# --------------------------------------------------------------------------
# Lectura del historial
# --------------------------------------------------------------------------
def _commits(repo) -> list[dict]:
    """Commits sin merges, con fecha, asunto y trailers de calidad."""
    formato = SEP_CAMPO.join([
        "%H", "%aI", "%s",
        "%(trailers:key=Severidad,valueonly,separator=%x2C)",
        "%(trailers:key=Detectado-en,valueonly,separator=%x2C)",
    ]) + SEP_REGISTRO
    salida = _git(repo, "log", "--no-merges", f"--format={formato}", "HEAD")
    commits = []
    for registro in salida.split(SEP_REGISTRO):
        campos = registro.strip("\n").split(SEP_CAMPO)
        if len(campos) != 5:
            continue
        h, fecha, asunto, severidad, fase = campos
        commits.append({"hash": h, "fecha": _fecha(fecha), "asunto": asunto,
                        "severidad": _normalizar(severidad), "fase": _normalizar(fase)})
    return commits


def _merges(repo) -> list[dict]:
    """Merges de PR en la rama principal con los commits que integró cada uno."""
    salida = _git(repo, "log", "--merges", "--first-parent", "--format=%H|%P|%cI", "HEAD")
    merges = []
    for linea in salida.splitlines():
        h, padres, fecha = linea.split("|")
        p1, p2 = padres.split()[:2]
        miembros = set(_git(repo, "rev-list", f"{p1}..{p2}").split())
        merges.append({"hash": h, "fecha": _fecha(fecha), "miembros": miembros})
    return merges


def _tags_release(repo) -> list[dict]:
    """Tags de versión vX.Y.Z con su fecha (cada tag = una salida a 'producción')."""
    salida = _git(repo, "for-each-ref", "--format=%(refname:short)|%(creatordate:iso-strict)", "refs/tags")
    tags = []
    for linea in salida.splitlines():
        nombre, fecha = linea.split("|")
        if TAG_RELEASE_RE.match(nombre):
            tags.append({"tag": nombre, "fecha": _fecha(fecha)})
    return sorted(tags, key=lambda t: t["fecha"])


def _archivos_del_commit(repo, h: str) -> list[str]:
    return [a for a in _git(repo, "show", "--format=", "--name-only", h).splitlines() if a.strip()]


def _candidatos_inductores(repo, fix: str, archivo: str) -> set[str]:
    """Commits que escribieron las líneas que el fix modifica o borra en `archivo`."""
    diff = _git(repo, "diff", "-U0", f"{fix}^", fix, "--", archivo)
    candidatos = set()
    for m in re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+", diff, re.MULTILINE):
        inicio, cantidad = int(m.group(1)), int(m.group(2) or "1")
        if cantidad == 0:      # el hunk solo agrega líneas: no hay línea "culpable"
            continue
        # --porcelain da el hash COMPLETO de cada línea (incluido el commit raíz).
        blame = _git(repo, "blame", "--porcelain", "-L", f"{inicio},{inicio + cantidad - 1}",
                     f"{fix}^", "--", archivo)
        candidatos |= set(re.findall(r"^([0-9a-f]{40}) ", blame, re.MULTILINE))
    return candidatos


def _inductor(repo, fix: dict, archivos: list[str], fechas: dict) -> dict | None:
    """El candidato más reciente anterior al fix (criterio de SZZ)."""
    candidatos = set()
    for archivo in archivos:
        candidatos |= _candidatos_inductores(repo, fix["hash"], archivo)
    candidatos.discard(fix["hash"])
    previos = [(fechas[c], c) for c in candidatos if c in fechas and fechas[c] <= fix["fecha"]]
    if not previos:
        return None
    fecha, h = max(previos)
    return {"hash": h, "fecha": fecha}


# --------------------------------------------------------------------------
# Clasificación
# --------------------------------------------------------------------------
def _fase(fix: dict, inductor: dict | None, merge: dict | None, tags: list[dict]) -> tuple[str, str]:
    """Devuelve (fase, fuente). Fuente = 'trailer' o 'automatica'."""
    if fix["fase"] in FASES_VALIDAS:
        return fix["fase"], "trailer"
    if inductor is None:
        return "desconocida", "automatica"
    if merge and inductor["hash"] in merge["miembros"]:
        return "revision", "automatica"
    if any(inductor["fecha"] <= t["fecha"] <= fix["fecha"] for t in tags):
        return "produccion", "automatica"
    return "pruebas", "automatica"


def _registro_defecto(repo, fix: dict, archivos: list[str], contexto: dict) -> dict:
    """Arma el registro de UN defecto: inductor, MTTD, MTTR, fase y severidad."""
    inductor = _inductor(repo, fix, archivos, contexto["fechas"])
    merge = next((m for m in contexto["merges"] if fix["hash"] in m["miembros"]), None)
    fase, fuente = _fase(fix, inductor, merge, contexto["tags"])
    severidad = fix["severidad"] if fix["severidad"] in SEVERIDADES_VALIDAS else "sin_clasificar"
    return {
        "fix": fix["hash"][:7],
        "asunto": fix["asunto"],
        "fecha_fix": fix["fecha"].isoformat(),
        "archivos": archivos,
        "inductor": inductor["hash"][:7] if inductor else None,
        "fecha_inductor": inductor["fecha"].isoformat() if inductor else None,
        "mttd_horas": _horas(inductor["fecha"], fix["fecha"]) if inductor else None,
        "merge": merge["hash"][:7] if merge else None,
        "mttr_horas": _horas(fix["fecha"], merge["fecha"]) if merge else None,
        "fase": fase,
        "fuente_fase": fuente,
        "severidad": severidad,
    }


def minar_defectos(repo) -> dict:
    """Recorre el historial y devuelve un registro por defecto de producto."""
    commits = _commits(repo)
    contexto = {
        "fechas": {c["hash"]: c["fecha"] for c in commits},
        "merges": _merges(repo),
        "tags": _tags_release(repo),
    }
    defectos, excluidos = [], []
    for fix in (c for c in commits if FIX_RE.match(c["asunto"])):
        archivos = [a for a in _archivos_del_commit(repo, fix["hash"]) if es_codigo_de_producto(a)]
        if archivos:
            defectos.append(_registro_defecto(repo, fix, archivos, contexto))
        else:
            excluidos.append({"fix": fix["hash"][:7], "asunto": fix["asunto"],
                              "motivo": "no modifica código de producto"})
    return {
        "commit_analizado": _git(repo, "rev-parse", "--short", "HEAD").strip(),
        "n_commits": len(commits),
        "n_merges": len(contexto["merges"]),
        "tags_release": [t["tag"] for t in contexto["tags"]],
        "n_defectos": len(defectos),
        "defectos": defectos,
        "fixes_excluidos": excluidos,
    }


def _imprimir(repo) -> None:
    """Muestra el resultado de la minería en la terminal (evidencia E11)."""
    r = minar_defectos(repo)
    print(f"\nMinería de defectos (SZZ) — commit {r['commit_analizado']}")
    print(f"Commits sin merge: {r['n_commits']} · merges de PR: {r['n_merges']} · "
          f"tags de versión: {', '.join(r['tags_release']) or 'ninguno'}")
    print(f"Defectos de producto: {r['n_defectos']} · fixes excluidos: {len(r['fixes_excluidos'])}\n")
    for d in r["defectos"]:
        print(f"  {d['fix']}  {d['severidad']:<14} {d['fase']:<11} ({d['fuente_fase']})  "
              f"MTTD {d['mttd_horas']} h · MTTR {d['mttr_horas']} h · inductor {d['inductor']}")
        print(f"           {d['asunto']}")
    for e in r["fixes_excluidos"]:
        print(f"  [excluido] {e['fix']}  {e['asunto']}  ({e['motivo']})")
    mttd = [d["mttd_horas"] for d in r["defectos"] if d["mttd_horas"] is not None]
    if mttd:
        print(f"\nMTTD mediana: {statistics.median(mttd)} h (n = {len(mttd)})")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Minería de defectos del historial de Git.")
    parser.add_argument("--repo", default=".", help="Ruta del repositorio a analizar.")
    _imprimir(parser.parse_args().repo)
