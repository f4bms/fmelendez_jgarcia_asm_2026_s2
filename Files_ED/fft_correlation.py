"""Correlación de señales reales mediante la FFT propia, sin operaciones NumPy."""

import sys
from pathlib import Path

# Localiza FFT&DFT independientemente de la carpeta desde la que se ejecute.
RUTA_FFT = Path(__file__).resolve().parent.parent / "FFT&DFT"
sys.path.insert(0, str(RUTA_FFT))

# Esta importación debe ir después de configurar la ruta de FFT&DFT.
from fft import fft_radix2


def ifft_radix2(X):
    """Calcula IFFT(X) = conjugado(FFT(conjugado(X))) / N.

    X debe tener longitud potencia de dos. Devuelve una lista compleja.
    Se reutiliza la FFT compartida y se conjuga y normaliza muestra por muestra.
    """
    N = len(X)
    if N == 0 or N & (N - 1):
        raise ValueError("La longitud del espectro debe ser una potencia de dos.")

    conjugados = []
    for valor in X:
        conjugados.append(complex(valor).conjugate())

    transformada = fft_radix2(conjugados)
    inversa = []
    for valor in transformada:
        inversa.append(valor.conjugate() / N)
    return inversa


def correlacion_fft(transmitida, recibida):
    """Devuelve la correlación lineal R_yx y el retardo de su máximo.

    Para x = transmitida e y = recibida:
        R_yx[m] = sum_n y[n] * conjugado(x[n-m])
                = (y * conjugado(x[-n]))[m].
    El teorema de convolución permite calcularla como IFFT(Y * conjugado(X)).
    Las entradas son señales reales y el retardo se expresa en muestras.
    """
    x = [float(muestra) for muestra in transmitida]
    y = [float(muestra) for muestra in recibida]
    if not x or not y:
        raise ValueError("Las señales no pueden estar vacías.")

    # El relleno evita la superposición circular. fft_radix2 agrega los ceros
    # restantes hasta la siguiente potencia de dos, igual para ambas señales.
    longitud_lineal = len(x) + len(y) - 1
    X = fft_radix2(x + [0.0] * (longitud_lineal - len(x)))
    Y = fft_radix2(y + [0.0] * (longitud_lineal - len(y)))

    R = []
    for k in range(len(X)):
        # Multiplicación en frecuencia, desarrollada con partes real e imaginaria:
        # (a + jb) * conjugado(c + jd) = (ac + bd) + j(bc - ad).
        a, b = Y[k].real, Y[k].imag
        c, d = X[k].real, X[k].imag
        R.append(complex(a * c + b * d, b * c - a * d))

    circular = ifft_radix2(R)
    correlacion = []
    # Los retardos negativos están al final de la IFFT. El módulo los ubica
    # allí; los no negativos quedan al principio. Funciona también con len(x)=1.
    for m in range(-(len(x) - 1), len(y)):
        indice = m % len(circular)
        # Las entradas reales solo dejan residuo imaginario por redondeo.
        correlacion.append(circular[indice].real)

    indice_max = 0
    for i in range(1, len(correlacion)):
        if correlacion[i] > correlacion[indice_max]:
            indice_max = i
    retardo = indice_max - (len(x) - 1)
    return correlacion, retardo
