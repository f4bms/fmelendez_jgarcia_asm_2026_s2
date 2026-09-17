"""Simula el eco mediante convolución con un impulso atenuado y retrasado."""

from operator import index
from random import gauss

from convolution import convolucion_directa


def generar_eco(señal, retardo, atenuacion=0.5, nivel_ruido=0.05):
    """Calcula recibida[n] = (señal * h)[n] + ruido[n].

    h[n] = atenuacion * delta[n-retardo] representa el trayecto del eco.
    retardo es un entero no negativo en muestras; nivel_ruido es la
    desviación estándar del ruido gaussiano de media cero.
    La salida conserva las primeras len(señal) muestras de la convolución.
    """
    N = len(señal)
    if N == 0:
        raise ValueError("La señal no puede estar vacía.")
    retardo = index(retardo)
    if retardo < 0:
        raise ValueError("El retardo no puede ser negativo.")
    if nivel_ruido < 0:
        raise ValueError("El nivel de ruido no puede ser negativo.")

    # Respuesta al impulso: solo hay una muestra no nula en n = retardo.
    h = [0.0] * (retardo + 1)
    h[retardo] = float(atenuacion)

    # Se evalúa explícitamente sum_k señal[k] * h[n-k].
    eco_completo = convolucion_directa(señal, h)

    señal_recibida = []
    for n in range(N):
        # La parte del eco posterior a la ventana de N muestras se descarta.
        ruido = gauss(0.0, nivel_ruido)
        señal_recibida.append(eco_completo[n] + ruido)
    return señal_recibida
