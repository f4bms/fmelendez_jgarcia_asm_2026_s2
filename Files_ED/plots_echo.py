"""Adaptador para guardar las gráficas compartidas en Files_ED/graphics."""

import sys
from pathlib import Path


# Resuelve la carpeta compartida sin depender del directorio de ejecución.
RUTA_FFT = Path(__file__).resolve().parent.parent / "FFT&DFT"
# Da prioridad al módulo graphics.py del proyecto al buscar la importación.
sys.path.insert(0, str(RUTA_FFT))

# El alias distingue la función compartida del adaptador definido más abajo.
from graphics import guardar_grafica_eco as _guardar_grafica_eco


# Los resultados de este experimento se guardan junto a sus propios códigos.
CARPETA_GRAFICAS = Path(__file__).resolve().parent / "graphics"


def guardar_grafica_eco(
    nombre,
    transmitida,
    recibida,
    corr_directa,
    corr_fft,
    retardo_real,
    retardo_directo,
    retardo_fft,
):
    """Guarda la comparación del eco mediante FFT&DFT/graphics.py.

    nombre identifica la señal y determina el nombre del archivo PNG.
    transmitida y recibida son las señales; corr_directa y corr_fft son sus
    curvas de correlación. Los tres retardos se expresan en muestras.
    Devuelve la ruta del PNG generado dentro de Files_ED/graphics.
    """
    # Delega el dibujo y el guardado al módulo compartido. Este adaptador
    # únicamente selecciona la carpeta de salida para el experimento de ecos.
    return _guardar_grafica_eco(
        nombre,
        transmitida,
        recibida,
        corr_directa,
        corr_fft,
        retardo_real,
        retardo_directo,
        retardo_fft,
        carpeta_graficas=CARPETA_GRAFICAS,
    )
