import numpy as np


def generar_eco(
        señal,
        retardo,
        atenuacion=0.5,
        nivel_ruido=0.05):

    """
    Genera una señal recibida simulada.

    señal:
        señal transmitida

    retardo:
        desplazamiento del eco en muestras

    atenuacion:
        reducción de amplitud del eco

    nivel_ruido:
        ruido gaussiano agregado
    """


    N = len(señal)

    eco = np.zeros(N)


    # Eco desplazado
    eco[retardo:] = (
        atenuacion *
        señal[:-retardo]
    )


    # Ruido
    ruido = (
        nivel_ruido *
        np.random.randn(N)
    )


    señal_recibida = eco + ruido


    return señal_recibida