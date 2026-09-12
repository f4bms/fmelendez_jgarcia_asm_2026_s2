import numpy as np

def fft_correlation(signal, received):

    # Tamaño necesario para evitar pérdida de información
    N = len(signal) + len(received) - 1


    # FFT de ambas señales
    X = np.fft.fft(signal, N)

    Y = np.fft.fft(received, N)


    # Correlación en frecuencia
    R = X * np.conj(Y)


    # Regresar al dominio temporal
    correlation = np.fft.ifft(R)


    # Nos quedamos con la parte real
    correlation = np.real(correlation)


    delay = np.argmax(
        correlation
    )


    return correlation, delay