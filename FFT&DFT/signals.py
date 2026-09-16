import numpy as np

# Este archivo genera señales básicas utilizadas para pruebas de FFT, DFT y análisis espectral.
# Cada función crea un tipo de señal distinta, útil para comparar cómo se comportan en frecuencia.


# Señal senoidal de una sola frecuencia f0 (Hz), muestreada a fs (Hz).
def tono_puro(N, fs, f0, amplitud=1.0):
    n = np.arange(N)
    t = n / fs
    return amplitud * np.sin(2 * np.pi * f0 * t)


# Suma de varias senoidales de distinta frecuencia.
def suma_de_tonos(N, fs, frecuencias, amplitudes=None):
    if amplitudes is None:
        amplitudes = [1.0] * len(frecuencias)

    n = np.arange(N)
    t = n / fs
    x = np.zeros(N)
    for f, a in zip(frecuencias, amplitudes):
        x += a * np.sin(2 * np.pi * f * t)
    return x


# Señal con ruido blanco gaussiano, con una relación señal a ruido dada en dB.
def senal_con_ruido(x, snr_db=20.0):
    potencia_senal = np.mean(x ** 2)
    potencia_ruido = potencia_senal / (10 ** (snr_db / 10))
    ruido = np.sqrt(potencia_ruido) * np.random.randn(len(x))
    return x + ruido


# Señal de prueba para benchmarking: combina una senoide con un ruido leve.
# Es útil para comparar tiempos de ejecución de FFT y DFT porque es repetible y realista.
def senal_de_prueba_benchmark(N, f0=5.0, snr_db=20.0):
    n = np.arange(N)
    x = np.sin(2 * np.pi * f0 * n / N)
    return senal_con_ruido(x, snr_db=snr_db)


# Genera un solo pulso rectangular centrado dentro de la señal.
def pulso_rectangular(N, ancho_pulso, amplitud=1.0):
    x = np.zeros(N)
    inicio = N // 2 - ancho_pulso // 2
    x[inicio:inicio + ancho_pulso] = amplitud
    return x


# Genera varios pulsos rectangulares iguales y separados entre sí.
# Es una señal útil para analizar ecos, detección de retrasos o patrones repetitivos.
def secuencia_de_pulsos(N, ancho_pulso, num_pulsos, separacion, amplitud=1.0, inicio=0):
    x = np.zeros(N)
    pos = inicio
    for _ in range(num_pulsos):
        fin_pulso = min(pos + ancho_pulso, N)
        if pos >= N:
            break
        x[pos:fin_pulso] = amplitud
        pos += ancho_pulso + separacion
    return x


# Chirp lineal: la frecuencia cambia de forma progresiva de f_inicio a f_fin.
# Esta señal es muy usada en procesamiento de señales porque tiene un espectro dinámico.
def chirp_lineal(N, fs, f_inicio, f_fin, amplitud=1.0):
    n = np.arange(N)
    t = n / fs
    duracion = N / fs
    k = (f_fin - f_inicio) / duracion
    fase = 2 * np.pi * (f_inicio * t + 0.5 * k * t ** 2)
    return amplitud * np.sin(fase)
