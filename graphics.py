#script para generar las gráficas de las señales y sus espectros

import numpy as np
import matplotlib.pyplot as plt

from fft import fft_radix2
from signals import (
    tono_puro,
    suma_de_tonos,
    senal_con_ruido,
    pulso_rectangular,
    secuencia_de_pulsos,
)

# datos que se deben de modificar según lo que se quiera analizar
fs = 8000
N = 256

senales = {
    "Tono puro (500 Hz)": tono_puro(N, fs, f0=500),
    "Suma de tonos (300, 800, 1500 Hz)": suma_de_tonos(N, fs, [300, 800, 1500]),
    "Tono con ruido (SNR 10 dB)": senal_con_ruido(tono_puro(N, fs, f0=500), snr_db=10),
    "Pulso rectangular (unico)": pulso_rectangular(N, ancho_pulso=20),
    "Secuencia de 4 pulsos": secuencia_de_pulsos(
        N, ancho_pulso=10, num_pulsos=4, separacion=20
    ),
}

for nombre, x in senales.items():
    X = fft_radix2(x)
    N_fft = len(X)
    frecuencias = np.fft.fftfreq(N_fft, d=1 / fs)

    mitad = N_fft // 2
    frecuencias_pos = frecuencias[:mitad]
    magnitud = np.abs(X[:mitad])
    fase = np.angle(X[:mitad])

    fig, (ax_tiempo, ax_mag, ax_fase) = plt.subplots(3, 1, figsize=(8, 8))

    ax_tiempo.plot(x)
    ax_tiempo.set_title(f"{nombre} — dominio del tiempo")
    ax_tiempo.set_xlabel("Muestra n")
    ax_tiempo.set_ylabel("Amplitud")

    ax_mag.plot(frecuencias_pos, magnitud)
    ax_mag.set_title("Magnitud |X(f)|")
    ax_mag.set_xlabel("Frecuencia (Hz)")
    ax_mag.set_ylabel("Magnitud")

    ax_fase.plot(frecuencias_pos, fase)
    ax_fase.set_title("Fase ∠X(f)")
    ax_fase.set_xlabel("Frecuencia (Hz)")
    ax_fase.set_ylabel("Fase (rad)")

    fig.tight_layout()
    nombre_archivo = nombre.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
    fig.savefig(f"espectro_{nombre_archivo}.png", dpi=150)
    plt.close(fig)
    print(f"Gráfica guardada: espectro_{nombre_archivo}.png")