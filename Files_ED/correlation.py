"""Correlación directa de señales reales."""


def correlacion_directa(transmitida, recibida):
    """Devuelve R_yx[m] y el retardo de su máximo, expresado en muestras.

    x es la señal transmitida y y la recibida:
        R_yx[m] = sum_n y[n] * conjugado(x[n-m]).
    Para estas señales reales, conjugado(x[n-m]) = x[n-m].
    Las muestras fuera de cada registro se consideran cero.
    """
    # Usa números de Python evita operar con escalares NumPy.
    x = [float(muestra) for muestra in transmitida]
    y = [float(muestra) for muestra in recibida]
    if not x or not y:
        raise ValueError("Las señales no pueden estar vacías.")

    correlacion = []
    # Todos los retardos de la correlación lineal, incluidos los negativos.
    for m in range(-(len(x) - 1), len(y)):
        suma = 0.0
        for n in range(len(y)):
            indice_x = n - m
            if 0 <= indice_x < len(x):
                suma += y[n] * x[indice_x]
        correlacion.append(suma)

    # Busca el máximo explícitamente; en un empate se conserva el primero.
    indice_max = 0
    for i in range(1, len(correlacion)):
        if correlacion[i] > correlacion[indice_max]:
            indice_max = i

    # El primer elemento corresponde al retardo -(len(x) - 1).
    retardo = indice_max - (len(x) - 1)
    return correlacion, retardo
