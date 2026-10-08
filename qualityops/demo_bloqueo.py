"""DEMOSTRACIÓN del enfoque preventivo (CAL-07). NO se integra a main.

Esta función tiene complejidad ciclomática 11 (10 decisiones + 1), por encima
del umbral de McCabe (<= 10) configurado en pyproject.toml. Sirve para probar
que el pipeline bloquea el PR antes de que el código llegue a main.
"""


def clasificar_calificacion(valor: int) -> str:
    """Convierte una calificación numérica en texto con una cadena de if/elif."""
    if valor >= 100:
        return "perfecta"
    elif valor >= 95:
        return "excelente"
    elif valor >= 90:
        return "muy buena"
    elif valor >= 85:
        return "buena"
    elif valor >= 80:
        return "aceptable"
    elif valor >= 75:
        return "suficiente"
    elif valor >= 70:
        return "regular"
    elif valor >= 60:
        return "baja"
    elif valor >= 50:
        return "muy baja"
    elif valor >= 0:
        return "reprobada"
    return "inválida"
