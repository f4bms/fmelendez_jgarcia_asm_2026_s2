"""FFT radix-2 propia con listas y aritmética compleja de Python, sin NumPy."""

from cmath import exp
from math import pi


def _siguiente_potencia_de_2(n):
    potencia = 1
    while potencia < n:
        potencia *= 2
    return potencia


def fft_radix2(x):
    """Devuelve la FFT como lista compleja; agrega ceros hasta una potencia de dos."""
    x = [complex(muestra) for muestra in x]
    if not x:
        raise ValueError("La señal no puede estar vacía.")

    N_pad = _siguiente_potencia_de_2(len(x))
    x.extend([0j] * (N_pad - len(x)))
    return _fft_recursiva(x)


def _fft_recursiva(x):
    N = len(x)
    if N == 1:
        return x
    if N % 2 != 0:
        raise ValueError("N debe ser potencia de 2 para radix-2.")

    # Separación de la sumatoria de la DFT en muestras pares e impares.
    pares = _fft_recursiva(x[0::2])
    impares = _fft_recursiva(x[1::2])

    X = [0j] * N
    mitad = N // 2
    for k in range(mitad):
        # Factor de giro W_N^k = exp(-j*2*pi*k/N).
        factor_giro = exp(-2j * pi * k / N) * impares[k]
        # Mariposa radix-2: X[k] = E[k] + W_N^k O[k].
        X[k] = pares[k] + factor_giro
        X[k + mitad] = pares[k] - factor_giro
    return X
