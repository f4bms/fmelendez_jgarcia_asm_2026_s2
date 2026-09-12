import numpy as np


def calculate_correlation(signal, received):

    correlation = np.correlate(
        received,
        signal,
        mode="full"
    )

    delay = np.argmax(correlation)

    return correlation, delay