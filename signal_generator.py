import numpy as np
from parameters import FS, DURATION, AMPLITUDE


def generate_step_signal():

    t = np.arange(
        0,
        DURATION,
        1/FS
    )

    # Escalón unitario
    signal = AMPLITUDE * np.ones(len(t))

    return t, signal