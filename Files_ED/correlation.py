import numpy as np


def correlacion_directa(
        transmitida,
        recibida):


    correlacion = np.correlate(
        recibida,
        transmitida,
        mode="full"
    )


    indice_max = np.argmax(
        correlacion
    )


    # Corrección del índice
    retardo = (
        indice_max -
        (len(transmitida)-1)
    )


    return correlacion, retardo