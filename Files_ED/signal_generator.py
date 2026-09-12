import numpy as np
from parameters import (
    FS,
    DURATION,
    AMPLITUDE,
    PULSE_WIDTH,
    PERIOD
)


def generate_square_pulse():

    t = np.arange(
        0,
        DURATION,
        1/FS
    )


    signal = np.zeros(len(t))


    pulse_samples = int(
        PULSE_WIDTH * FS
    )


    period_samples = int(
        PERIOD * FS
    )


    for i in range(len(t)):

        position = i % period_samples


        if position < pulse_samples:
            signal[i] = AMPLITUDE


    return t, signal