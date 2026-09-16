"""Simula un eco con retardo, atenuación y ruido gaussiano aditivo."""

import numpy as np


def generar_eco(
        señal,
        retardo,
        atenuacion=0.5,
        nivel_ruido=0.05):

    """Genera una señal recibida del mismo largo que la transmitida.

    señal:
        Arreglo unidimensional de muestras reales de la señal transmitida.
    retardo:
        Desplazamiento entero en muestras. Este recorte está pensado para
        un retardo positivo menor que la longitud de la señal.
    atenuacion:
        Factor que multiplica la amplitud del eco; 0.5 la reduce a la mitad.
    nivel_ruido:
        Desviación estándar del ruido gaussiano de media cero.

    Devuelve el eco desplazado y atenuado más el ruido. La parte del eco
    que sobrepasa el registro se pierde; no se amplía la señal de salida.
    """


    N = len(señal)

    # Las muestras anteriores a la llegada del eco empiezan en cero.
    eco = np.zeros(N)


    # Desplaza la señal hacia la derecha: las primeras N-retardo muestras
    # transmitidas se copian desde la posición retardo y se atenúan.
    # La cola que quedaría fuera de las N muestras se descarta.
    eco[retardo:] = (
        atenuacion *
        señal[:-retardo]
    )


    # randn genera ruido de media cero y desviación estándar uno.
    # Multiplicarlo por nivel_ruido ajusta su amplitud; cambia en cada llamada.
    ruido = (
        nivel_ruido *
        np.random.randn(N)
    )


    # El ruido se suma a todo el registro, incluso antes de que llegue el eco.
    señal_recibida = eco + ruido


    return señal_recibida