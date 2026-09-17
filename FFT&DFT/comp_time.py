# Compara el tiempo que tarda la DFT directa contra la FFT radix-2 para señales de distintos tamaños.
# La idea es ver cómo cambia el rendimiento a medida que crece N.

import time
import matplotlib.pyplot as plt
from pathlib import Path

from dft import dft
from fft import fft_radix2
from signals import senal_de_prueba_benchmark

# Carpeta donde se guarda la gráfica final
CARPETA_GRAFICAS = Path(__file__).resolve().parent / "graphics"
CARPETA_GRAFICAS.mkdir(exist_ok=True)

# Tamaños de señal a probar.
# N crece en potencias de 2 para comparar mejor el comportamiento.
tamanos_N = [64, 128, 256, 512, 1024, 2048]

tiempos_dft = []
tiempos_fft = []
tiempos_numpy = []

# Se prueba cada tamaño de señal y se mide cuánto tarda cada método.
for N in tamanos_N:
    x = senal_de_prueba_benchmark(N)

    # Medir tiempo de la DFT directa.
    inicio = time.perf_counter()
    dft(x)
    tiempos_dft.append(time.perf_counter() - inicio)

    # Medir tiempo de la FFT propia.
    inicio = time.perf_counter()
    fft_radix2(x)
    tiempos_fft.append(time.perf_counter() - inicio)

    # Mostrar resultados por consola.
    print(f"N={N:5d} | DFT directa: {tiempos_dft[-1]:.5f}s | "
          f"FFT propia: {tiempos_fft[-1]:.5f}s | ")

# Se usa escala logarítmica para comparar mejor la tendencia de crecimiento.
plt.figure(figsize=(7, 5))
plt.loglog(tamanos_N, tiempos_dft, "o-", label="DFT directa (O(N²))")
plt.loglog(tamanos_N, tiempos_fft, "s-", label="FFT radix-2 propia (O(N log N))")
plt.xlabel("N (tamaño de la señal)")
plt.ylabel("Tiempo de ejecución (s)")
plt.title("Comparación de tiempos: DFT directa vs. FFT radix-2")
plt.legend()
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(CARPETA_GRAFICAS / "comparacion_tiempos.png", dpi=150)
print("\nGráfica guardada como comparacion_tiempos.png")