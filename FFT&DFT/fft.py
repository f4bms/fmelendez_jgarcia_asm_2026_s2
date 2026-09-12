#n debe de ser potencia de 2 para radix-2 sino ocupamos hacer zero padding
import numpy as np


def _siguiente_potencia_de_2(n):
    potencia = 1
    while potencia < n:
        potencia *= 2
    return potencia


def fft_radix2(x):
    x = np.asarray(x, dtype=complex)
    N_original = len(x)
    N_pad = _siguiente_potencia_de_2(N_original)

    if N_pad != N_original:
        x = np.concatenate([x, np.zeros(N_pad - N_original, dtype=complex)])

    return _fft_recursiva(x)


def _fft_recursiva(x):
    N = len(x)
    if N == 1:
        return x

    if N % 2 != 0:
        raise ValueError("N debe ser potencia de 2 para radix-2.")

    pares = _fft_recursiva(x[0::2])
    impares = _fft_recursiva(x[1::2])

    X = np.zeros(N, dtype=complex)
    mitad = N // 2

    for k in range(mitad):
        # W_N^k = exp(-j*2*pi*k/N)
        factor_giro = np.exp(-2j * np.pi * k / N) * impares[k]

        # op mariposa
        X[k] = pares[k] + factor_giro
        X[k + mitad] = pares[k] - factor_giro

    return X
