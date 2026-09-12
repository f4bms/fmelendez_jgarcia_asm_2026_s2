import numpy as np
from parameters import FS, ECHO_DELAY, NOISE_LEVEL


def create_echo(signal):

    delay_samples = int(ECHO_DELAY * FS)

    # Crear señal retrasada
    echo = np.zeros(len(signal))

    echo[delay_samples:] = signal[:-delay_samples]


    # Agregar ruido
    noise = np.random.normal(
        0,
        NOISE_LEVEL,
        len(signal)
    )

    received = echo + noise


    return received, delay_samples