"""Ejecuta la detección de ecos para las señales de prueba configuradas.

Genera una señal transmitida y su eco, estima el retardo mediante correlación
directa y mediante FFT, y guarda una gráfica para comparar ambos resultados.
"""

import sys
from pathlib import Path


# ==========================================
# Importar módulos de FFT&DFT
# ==========================================

# La ruta parte de este archivo, por lo que no depende de la carpeta de ejecución.
RUTA_FFT = (
    Path(__file__).resolve().parent.parent
    /
    "FFT&DFT"
)

# Los módulos del proyecto frente a otros con los mismos nombres.
sys.path.insert(
    0, str(RUTA_FFT)
)

# Generadores compartidos con la etapa de análisis de señales en FFT&DFT.
from signals import (
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

# Usa FFT&DFT/graphics.py y guarda los PNG en Files_ED/graphics.
from plots_echo import (
    guardar_grafica_eco
)



# ==========================================
# Parámetros del experimento
# ==========================================

# Frecuencia de muestreo en Hz: se toman 8000 muestras por segundo.
fs = 8000

# Cantidad de muestras por señal; su duración es N/fs = 0.064 segundos.
N = 512


# Retardo conocido del eco en muestras: 80/fs equivale a 10 milisegundos.
RETARDO_ECO = 80


# Factor que multiplica la amplitud transmitida: 0.5 representa la mitad.
ATENUACION = 0.5


# Desviación estándar del ruido gaussiano; no es una relación señal/ruido en dB.
RUIDO = 0.05



# ==========================================
# Señales a evaluar
# ==========================================

# Cada nombre identifica una señal y también se usa para nombrar su gráfica.
signals = {
    # Barrido de frecuencia ascendente definido entre 300 y 3000 Hz.
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

    # El eco se calcula mediante la convolución explícita con h[n] = a*delta[n-d].
    # La señal recibida contiene ese eco más ruido gaussiano.
    señal_rx = generar_eco(
        señal_tx,
        retardo=RETARDO_ECO,
        atenuacion=ATENUACION,
        nivel_ruido=RUIDO
    )

    # --------------------------------------
    # Correlación directa
    # --------------------------------------

    # Evalúa la sumatoria R_yx[m] = sum_n recibida[n] * transmitida[n-m].
    # Como las señales son reales, el conjugado de transmitida es ella misma.
    # Devuelve la correlación completa y el retardo del máximo en muestras.
    corr_directa, delay_directa = correlacion_directa(
        señal_tx,
        señal_rx
    )

    # --------------------------------------
    # Correlación mediante FFT
    # --------------------------------------

    # Calcula la misma correlación en frecuencia usando la FFT del proyecto.
    # El resultado debe coincidir con el método directo salvo redondeo numérico.
    corr_fft, delay_fft = correlacion_fft(
        señal_tx,
        señal_rx
    )

    # --------------------------------------
    # Resultados
    # --------------------------------------

    # Se compara el retardo estimado con el usado para construir el eco.
    # Todos los retardos se muestran en muestras; para segundos, dividir por fs.
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

    # Guarda la señal transmitida, la recibida y las dos correlaciones,
    # incluyendo los retardos detectados y el retardo de referencia.
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
