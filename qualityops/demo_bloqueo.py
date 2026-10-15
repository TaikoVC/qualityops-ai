"""Cambio de demostracion: funcion demasiado compleja (CC 11) para que el gate la bloquee."""


def clasificar_pedido(monto, cliente, urgente, internacional, cupon, dia):
    """Clasifica un pedido con muchas decisiones (mala practica intencional)."""
    puntos = 0
    if monto > 1000:
        puntos += 3
    elif monto > 500:
        puntos += 2
    if cliente == "vip":
        puntos += 2
    if urgente:
        puntos += 1
    if internacional:
        puntos += 1
    if cupon and monto > 100:
        puntos -= 1
    if dia in ("sabado", "domingo"):
        puntos += 1
    if puntos > 5:
        return "prioridad alta"
    if puntos > 2:
        return "prioridad media"
    return "prioridad baja"
