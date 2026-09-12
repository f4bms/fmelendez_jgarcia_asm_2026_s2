import numpy as np


# señal senoidal de una sola frecuencia f0 (Hz), muestreada a fs (Hz)
def tono_puro(N, fs, f0, amplitud=1.0):
    n = np.arange(N)
    t = n / fs
    return amplitud * np.sin(2 * np.pi * f0 * t)


#Suma de varias senoidales de distinta frecuencia
def suma_de_tonos(N, fs, frecuencias, amplitudes=None):
    if amplitudes is None:
        amplitudes = [1.0] * len(frecuencias)

    n = np.arange(N)
    t = n / fs
    x = np.zeros(N)
    for f, a in zip(frecuencias, amplitudes):
        x += a * np.sin(2 * np.pi * f * t)
    return x

#señal con ruido blanco gaussiano,relación señal a ruidoen dB
def senal_con_ruido(x, snr_db=20.0):
    potencia_senal = np.mean(x ** 2)
    potencia_ruido = potencia_senal / (10 ** (snr_db / 10))
    ruido = np.sqrt(potencia_ruido) * np.random.randn(len(x))
    return x + ruido

    #un solo pulso rectangular corto centrado dentro de una señal de N muestras
def pulso_rectangular(N, ancho_pulso, amplitud=1.0):
    x = np.zeros(N)
    inicio = N // 2 - ancho_pulso // 2
    x[inicio:inicio + ancho_pulso] = amplitud
    return x

#secuencia de pulsos rectangulares idénticos, igualmente espaciados -LA QUE YO PIENSO QUE NOS PUEDE SERVIR PARA EL PROYECTO
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



#este chirp es un barrido lineal de frecuencia, que va desde f_inicio hasta f_fin en N muestras
#esta señal es la más compleja, pero es la que más papers tratan para lo q estamos haciendo.
def chirp_lineal(N, fs, f_inicio, f_fin, amplitud=1.0):
    n = np.arange(N)
    t = n / fs
    duracion = N / fs
    k = (f_fin - f_inicio) / duracion
    fase = 2 * np.pi * (f_inicio * t + 0.5 * k * t ** 2)
    return amplitud * np.sin(fase)
