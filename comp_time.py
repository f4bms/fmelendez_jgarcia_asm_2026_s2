import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from dft import dft
from fft import fft_radix2

CARPETA_GRAFICAS = Path(__file__).resolve().parent / "graphics"
CARPETA_GRAFICAS.mkdir(exist_ok=True)

tamanos_N = [64, 128, 256, 512, 1024, 2048]

tiempos_dft = []
tiempos_fft = []
tiempos_numpy = []

for N in tamanos_N:
    n = np.arange(N)
    x = np.sin(2 * np.pi * 5 * n / N) + 0.3 * np.random.randn(N)

    inicio = time.perf_counter()
    dft(x)
    tiempos_dft.append(time.perf_counter() - inicio)

    inicio = time.perf_counter()
    fft_radix2(x)
    tiempos_fft.append(time.perf_counter() - inicio)

    print(f"N={N:5d} | DFT directa: {tiempos_dft[-1]:.5f}s | "
          f"FFT propia: {tiempos_fft[-1]:.5f}s | ")

# --- Gráfica log-log ---
plt.figure(figsize=(7, 5))
plt.loglog(tamanos_N, tiempos_dft, "o-", label="DFT directa (O(N²))")
plt.loglog(tamanos_N, tiempos_fft, "s-", label="FFT radix-2 propia (O(N log N))")
plt.xlabel("N (tamaño de la señal)")
plt.ylabel("Tiempo de ejecución (s)")
plt.title("Comparación de tiempos: DFT directa vs. FFT radix-2")
plt.legend()
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(CARPETA_GRAFICAS /"comparacion_tiempos.png", dpi=150)
print("\nGráfica guardada como comparacion_tiempos.png")