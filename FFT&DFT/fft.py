#n debe de ser potencia de 2 para radix-2 sino ocupamos hacer zero padding
import numpy as np

def _siguiente_potencia_de_2(n):
    # Calcula la siguiente potencia de 2 mayor o igual que n.
    potencia = 1
    while potencia < n:
        potencia *= 2
    return potencia


def fft_radix2(x):
    # Convierte la entrada a una secuencia compleja.
    x = np.asarray(x, dtype=complex)
    N_original = len(x)
    N_pad = _siguiente_potencia_de_2(N_original)

    # Si la longitud no es potencia de 2, se agrega padding con ceros.
    if N_pad != N_original:
        x = np.concatenate([x, np.zeros(N_pad - N_original, dtype=complex)])

    # Llama a la versión recursiva de la FFT.
    return _fft_recursiva(x)


def _fft_recursiva(x):
    N = len(x)

    # Caso base: una sola muestra, la transformada es la misma muestra.
    if N == 1:
        return x

    # La FFT radix-2 exige que N sea par y potencia de 2.
    if N % 2 != 0:
        raise ValueError("N debe ser potencia de 2 para radix-2.")

    # Se separa la señal en índices pares e impares.
    pares = _fft_recursiva(x[0::2])
    impares = _fft_recursiva(x[1::2])

    X = np.zeros(N, dtype=complex)
    mitad = N // 2

    # La operación de "mariposa" combina las dos mitades usando el factor de giro.
    for k in range(mitad):
        # W_N^k = exp(-j*2*pi*k/N)
        factor_giro = np.exp(-2j * np.pi * k / N) * impares[k]

        # F[k] = E[k] + W_N^k * O[k]
        # F[k + N/2] = E[k] - W_N^k * O[k]
        X[k] = pares[k] + factor_giro
        X[k + mitad] = pares[k] - factor_giro

    return X
