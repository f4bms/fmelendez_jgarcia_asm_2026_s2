import numpy as np

# Esta función implementa la Transformada Discreta de Fourier (DFT) simple. Se toma una señal x[n] y calcula sus componentes frecuenciales X[k].
# Se hace con dos ciclos anidados, por eso su costo es O(N²).

def dft(x):
    # Convierte la entrada a un arreglo complejo para operar con números complejos.
    x = np.asarray(x, dtype=complex)
    N = len(x)
    X = np.zeros(N, dtype=complex)

    # k representa cada frecuencia que queremos calcular.
    for k in range(N):
        suma = 0.0 + 0.0j

        # n recorre cada muestra de la señal para sumar su contribución.
        for n in range(N):
            angulo = -2j * np.pi * k * n / N
            suma += x[n] * np.exp(angulo)
        X[k] = suma

    return X