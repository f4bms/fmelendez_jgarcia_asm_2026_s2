"""Funciones compartidas para graficar señales, espectros y ecos."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from fft import fft_radix2
from signals import (
    tono_puro,
    suma_de_tonos,
    senal_con_ruido,
    pulso_rectangular,
    secuencia_de_pulsos,
    chirp_lineal,
)

CARPETA_GRAFICAS = Path(__file__).resolve().parent / "graphics"


def _guardar_figura(fig, nombre, carpeta_graficas):
    carpeta_graficas = Path(carpeta_graficas)
    carpeta_graficas.mkdir(parents=True, exist_ok=True)
    nombre_archivo = (
        nombre.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
    )
    ruta = carpeta_graficas / f"{nombre_archivo}.png"
    try:
        fig.tight_layout()
        fig.savefig(ruta, dpi=150)
    finally:
        plt.close(fig)
    print(f"Gráfica guardada: {nombre_archivo}.png")
    return ruta


def guardar_grafica_senal(nombre, x, fs, *, carpeta_graficas=CARPETA_GRAFICAS):
    """Guarda la señal en el tiempo y la magnitud y fase de su FFT."""
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

    return _guardar_figura(fig, nombre, carpeta_graficas)


def guardar_grafica_eco(
    nombre,
    transmitida,
    recibida,
    corr_directa,
    corr_fft,
    retardo_real,
    retardo_directo,
    retardo_fft,
    *,
    carpeta_graficas=CARPETA_GRAFICAS,
):
    """Guarda las señales y sus correlaciones para la detección de ecos."""
    fig, axes = plt.subplots(4, 1, figsize=(8, 10))

    for ax, senal, titulo in (
        (axes[0], transmitida, f"{nombre} - Señal transmitida"),
        (axes[1], recibida, f"{nombre} - Señal recibida con eco"),
    ):
        ax.plot(senal)
        ax.set_title(titulo)
        ax.set_xlabel("Muestra n")
        ax.set_ylabel("Amplitud")
        ax.grid()

    for ax, correlacion, retardo, titulo in (
        (axes[2], corr_directa, retardo_directo, "Correlación directa"),
        (axes[3], corr_fft, retardo_fft, "Correlación mediante FFT"),
    ):
        ax.plot(correlacion)
        indice = retardo + len(transmitida) - 1
        ax.axvline(
            indice,
            linestyle="--",
            label=f"Detectado={retardo}\nReal={retardo_real}",
        )
        ax.set_title(titulo)
        ax.set_xlabel("Índice")
        ax.set_ylabel("Magnitud")
        ax.legend()
        ax.grid()

    return _guardar_figura(fig, nombre, carpeta_graficas)


def main():
    # Datos que se deben modificar según lo que se quiera analizar.
    fs = 8000
    N = 256

    signals = {
        "Tono puro (500 Hz)": tono_puro(N, fs, f0=500),
        "Suma de tonos (300, 800, 1500 Hz)": suma_de_tonos(N, fs, [300, 800, 1500]),
        "Tono con ruido (SNR 10 dB)": senal_con_ruido(tono_puro(N, fs, f0=500), snr_db=10),
        "Pulso rectangular (unico)": pulso_rectangular(N, ancho_pulso=20),
        "Secuencia de 4 pulsos": secuencia_de_pulsos(
            N, ancho_pulso=10, num_pulsos=4, separacion=20
        ),
        "Chirp lineal (300-3000 Hz)": chirp_lineal(N, fs, f_inicio=300, f_fin=3000),
    }

    for nombre, x in signals.items():
        guardar_grafica_senal(nombre, x, fs)


if __name__ == "__main__":
    main()
