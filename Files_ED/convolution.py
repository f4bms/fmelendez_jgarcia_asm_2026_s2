"""Convolución lineal de señales reales."""


def convolucion_directa(x, h):
    """Aplica y[n] = sum_k x[k] * h[n-k] y devuelve una lista.

    Las entradas son secuencias reales no vacías. Se consideran cero fuera
    de sus registros y la salida tiene len(x) + len(h) - 1 muestras.
    """
    x = [float(muestra) for muestra in x]
    h = [float(muestra) for muestra in h]
    if not x or not h:
        raise ValueError("Las señales no pueden estar vacías.")

    y = []
    for n in range(len(x) + len(h) - 1):
        suma = 0.0
        for k in range(len(x)):
            # h[n-k] expresa la inversión y el desplazamiento de h.
            indice_h = n - k
            if 0 <= indice_h < len(h):
                suma += x[k] * h[indice_h]
        y.append(suma)
    return y
