"""Calcula la correlación de señales reales usando la FFT propia de FFT&DFT."""

import numpy as np
import sys
from pathlib import Path

# ==================================
# Importar FFT propia
# ==================================

# Localiza la implementación compartida a partir de la ubicación de este archivo.
RUTA_FFT = (
    Path(__file__).resolve().parent.parent
    /
    "FFT&DFT"
)

# Prioriza fft.py del proyecto al resolver la importación siguiente.
sys.path.insert(
    0, str(RUTA_FFT)
)

# Esta importación debe ir después de configurar la ruta de FFT&DFT.
from fft import fft_radix2


def ifft_radix2(X):

    """Calcula la transformada inversa a partir de fft_radix2.

    X es un espectro complejo de longitud potencia de dos, como el que devuelve
    fft_radix2. El resultado es un arreglo complejo de la misma longitud.
    Se usa la identidad IFFT(X) = conj(FFT(conj(X))) / N.
    """

    # La inversa se normaliza por la cantidad de coeficientes del espectro.
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


    """Estima el retardo de la señal recibida respecto a la transmitida.

    Las entradas son arreglos unidimensionales de muestras reales. Si X es la
    FFT de transmitida y Y la FFT de recibida, se calcula IFFT(Y * conj(X)).
    Devuelve la correlación lineal completa y el retardo del máximo en muestras;
    un retardo positivo indica que la señal recibida llega después.
    """


    # La correlación completa ocupa len(transmitida) + len(recibida) - 1 valores.

    N = (
        len(transmitida)
        +
        len(recibida)
        -
        1
    )


    # Se agregan ceros para evitar que los extremos se superpongan al calcular
    # la correlación con FFT. fft_radix2 completa hasta la siguiente potencia
    # de dos, de modo que X e Y terminan con la misma longitud.

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



    # El conjugado de X permite correlacionar recibida con transmitida.
    # Este orden produce retardos positivos para los ecos que llegan después.

    R = Y * np.conj(X)



    # Para señales reales, la parte imaginaria residual se debe al redondeo.
    correlacion = np.real(
        ifft_radix2(R)
    )


    # La IFFT coloca los retardos negativos al final. Se llevan al inicio y
    # luego se añaden los retardos desde cero hasta len(recibida) - 1.
    # Así se obtiene el mismo orden que np.correlate(..., mode="full"),
    # descartando las posiciones adicionales del relleno con ceros.

    correlacion = np.concatenate(
        (
            correlacion[-(len(transmitida)-1):],
            correlacion[:len(recibida)]
        )
    )


    # El pico más alto señala el desplazamiento con mayor coincidencia.
    indice_max = np.argmax(
        correlacion
    )


    # El retardo cero está en el índice len(transmitida) - 1 del arreglo ordenado.
    retardo = (
        indice_max -
        (len(transmitida)-1)
    )


    # Se devuelve la curva para graficarla y el retardo estimado para compararlo.
    return correlacion, retardo
