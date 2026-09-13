import matplotlib.pyplot as plt
from pathlib import Path


CARPETA_GRAFICAS = (
    Path(__file__).resolve().parent
    /
    "graphics"
)

CARPETA_GRAFICAS.mkdir(
    exist_ok=True
)



def guardar_grafica_eco(
        nombre,
        transmitida,
        recibida,
        corr_directa,
        corr_fft,
        retardo_real,
        retardo_directo,
        retardo_fft):


    fig, axes = plt.subplots(
        4,
        1,
        figsize=(8, 10)
    )


    # ==================================
    # Señal transmitida
    # ==================================

    axes[0].plot(
        transmitida
    )

    axes[0].set_title(
        f"{nombre} - Señal transmitida"
    )

    axes[0].set_xlabel(
        "Muestra n"
    )

    axes[0].set_ylabel(
        "Amplitud"
    )

    axes[0].grid()



    # ==================================
    # Señal recibida con eco
    # ==================================

    axes[1].plot(
        recibida
    )

    axes[1].set_title(
        f"{nombre} - Señal recibida con eco"
    )

    axes[1].set_xlabel(
        "Muestra n"
    )

    axes[1].set_ylabel(
        "Amplitud"
    )

    axes[1].grid()



    # ==================================
    # Correlación directa
    # ==================================

    axes[2].plot(
        corr_directa
    )


    indice_directo = (
        retardo_directo
        +
        len(transmitida)
        -
        1
    )


    axes[2].axvline(
        indice_directo,
        linestyle="--",
        label=(
            f"Detectado={retardo_directo}\n"
            f"Real={retardo_real}"
        )
    )


    axes[2].set_title(
        "Correlación directa"
    )

    axes[2].set_xlabel(
        "Índice"
    )

    axes[2].set_ylabel(
        "Magnitud"
    )

    axes[2].legend()

    axes[2].grid()



    # ==================================
    # Correlación mediante FFT
    # ==================================

    axes[3].plot(
        corr_fft
    )


    indice_fft = (
        retardo_fft
        +
        len(transmitida)
        -
        1
    )


    axes[3].axvline(
        indice_fft,
        linestyle="--",
        label=(
            f"Detectado={retardo_fft}\n"
            f"Real={retardo_real}"
        )
    )


    axes[3].set_title(
        "Correlación mediante FFT"
    )

    axes[3].set_xlabel(
        "Índice"
    )

    axes[3].set_ylabel(
        "Magnitud"
    )

    axes[3].legend()

    axes[3].grid()



    # Ajustar espacios

    fig.tight_layout()



    # ==================================
    # Nombre del archivo
    # ==================================

    nombre_archivo = (
        nombre.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
    )



    fig.savefig(
        CARPETA_GRAFICAS /
        f"{nombre_archivo}.png",
        dpi=150
    )


    plt.close(fig)


    print(
        f"Gráfica guardada: {nombre_archivo}.png"
    )