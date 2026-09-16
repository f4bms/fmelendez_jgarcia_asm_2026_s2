"""Método directo de referencia para estimar el retardo de un eco."""

import numpy as np


def correlacion_directa(
        transmitida,
        recibida):
    """Correlaciona la señal recibida con la transmitida.

    Las entradas son arreglos unidimensionales de muestras. Devuelve la
    correlación completa y el retardo de su máximo, expresado en muestras.
    Un retardo positivo significa que la señal recibida llega después.
    """

    # El orden de las entradas fija el signo del retardo. El modo "full"
    # incluye los desplazamientos desde -(len(transmitida) - 1)
    # hasta len(recibida) - 1.
    correlacion = np.correlate(
        recibida,
        transmitida,
        mode="full"
    )


    # Busca el desplazamiento donde las señales presentan mayor coincidencia.
    indice_max = np.argmax(
        correlacion
    )


    # Un índice del arreglo no es todavía un retardo: el cero está ubicado
    # en len(transmitida) - 1, por lo que se resta ese desplazamiento.
    retardo = (
        indice_max -
        (len(transmitida)-1)
    )


    # La curva sirve para las gráficas y el retardo para evaluar la detección.
    return correlacion, retardo