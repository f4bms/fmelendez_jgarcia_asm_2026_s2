import sys
from pathlib import Path


# ==========================================
# Importar módulos de FFT&DFT
# ==========================================

RUTA_FFT = (
    Path(__file__).resolve().parent.parent
    /
    "FFT&DFT"
)

sys.path.append(
    str(RUTA_FFT)
)


from signals import (
    pulso_rectangular,
    secuencia_de_pulsos,
    chirp_lineal,
)


# ==========================================
# Importar módulos propios
# ==========================================

from echo_model import generar_eco

from correlation import (
    correlacion_directa
)

from fft_correlation import (
    correlacion_fft
)

from plots_echo import (
    guardar_grafica_eco
)



# ==========================================
# Parámetros del experimento
# ==========================================

fs = 8000

N = 512


# Retardo conocido del eco
RETARDO_ECO = 80


# Atenuación del eco
ATENUACION = 0.5


# Nivel de ruido
RUIDO = 0.05



# ==========================================
# Señales a evaluar
# ==========================================

signals = {

    "Pulso rectangular":
        pulso_rectangular(
            N,
            ancho_pulso=20
        ),


    "Secuencia de pulsos":
        secuencia_de_pulsos(
            N,
            ancho_pulso=10,
            num_pulsos=4,
            separacion=20
        ),


    "Chirp lineal":
        chirp_lineal(
            N,
            fs,
            f_inicio=300,
            f_fin=3000
        )
}



# ==========================================
# Experimento de detección de ecos
# ==========================================

for nombre, señal_tx in signals.items():

    print("\n==============================")
    print("Procesando:", nombre)


    # --------------------------------------
    # Generación del eco
    # --------------------------------------

    señal_rx = generar_eco(
        señal_tx,
        retardo=RETARDO_ECO,
        atenuacion=ATENUACION,
        nivel_ruido=RUIDO
    )



    # --------------------------------------
    # Correlación directa
    # --------------------------------------

    corr_directa, delay_directa = correlacion_directa(
        señal_tx,
        señal_rx
    )



    # --------------------------------------
    # Correlación mediante FFT
    # --------------------------------------

    corr_fft, delay_fft = correlacion_fft(
        señal_tx,
        señal_rx
    )



    # --------------------------------------
    # Resultados
    # --------------------------------------

    print(
        "Retardo real:",
        RETARDO_ECO,
        "muestras"
    )


    print(
        "Retardo correlación directa:",
        delay_directa,
        "muestras"
    )


    print(
        "Retardo correlación FFT:",
        delay_fft,
        "muestras"
    )



    # --------------------------------------
    # Guardar gráfica
    # --------------------------------------

    guardar_grafica_eco(
    nombre,
    señal_tx,
    señal_rx,
    corr_directa,
    corr_fft,
    RETARDO_ECO,
    delay_directa,
    delay_fft
    )   



print("\nExperimento terminado.")
print("Las gráficas fueron guardadas en graphics/")