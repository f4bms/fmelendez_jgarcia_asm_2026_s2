import numpy as np
import sys
from pathlib import Path


# ==================================
# Importar FFT propia
# ==================================

RUTA_FFT = (
    Path(__file__).resolve().parent.parent
    /
    "FFT&DFT"
)

sys.path.append(
    str(RUTA_FFT)
)


from fft import fft_radix2



def ifft_radix2(X):

    """
    Implementación de IFFT
    usando la FFT propia.
    """

    N = len(X)


    return (
        np.conj(
            fft_radix2(
                np.conj(X)
            )
        )
        /
        N
    )



def correlacion_fft(
        transmitida,
        recibida):


    """
    Correlación mediante FFT.

    Rxy = IFFT(X * conj(Y))
    """


    # Tamaño necesario para correlación lineal

    N = (
        len(transmitida)
        +
        len(recibida)
        -
        1
    )


    # FFT con zero padding

    X = fft_radix2(
        np.pad(
            transmitida,
            (0, N-len(transmitida))
        )
    )


    Y = fft_radix2(
        np.pad(
            recibida,
            (0, N-len(recibida))
        )
    )



    # Producto en frecuencia

    R = Y * np.conj(X)



    correlacion = np.real(
        ifft_radix2(R)
    )


    # Convertir correlación circular
    # a representación centrada

    correlacion = np.concatenate(
        (
            correlacion[-(len(transmitida)-1):],
            correlacion[:len(recibida)]
        )
    )


    indice_max = np.argmax(
        correlacion
    )


    retardo = (
        indice_max -
        (len(transmitida)-1)
    )


    return correlacion, retardo