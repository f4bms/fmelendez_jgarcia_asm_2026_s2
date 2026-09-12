
import numpy as np

#implementation of the DTF

def dft(x):
    x = np.asarray(x, dtype=complex)
    N = len(x)
    X = np.zeros(N, dtype=complex)

    for k in range(N):
        suma = 0.0 + 0.0j
        for n in range(N):
            angulo = -2j * np.pi * k * n / N
            suma += x[n] * np.exp(angulo)
        X[k] = suma

    return X