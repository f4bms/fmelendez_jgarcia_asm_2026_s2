from signal_generator import generate_square_pulse
from echo_model import create_echo
from correlation import calculate_correlation
from fft_correlation import fft_correlation
from distance import calculate_distance
from visualization import plot_signals


# 1. Generar señal
t, signal = generate_square_pulse()


# 2. Crear eco
received, real_delay = create_echo(signal)


# 3. Correlación directa
corr_direct, delay_direct = calculate_correlation(
    signal,
    received
)


# 4. Correlación FFT
corr_fft, delay_fft = fft_correlation(
    signal,
    received
)


# 5. Calcular distancia usando el retardo encontrado
distance = calculate_distance(delay_fft)


print("-------------------------")
print("Retardo real:", real_delay)
print("Retardo correlación directa:", delay_direct)
print("Retardo correlación FFT:", delay_fft)
print(f"Distancia estimada: {distance:.2f} m")
print("-------------------------")


plot_signals(
    t,
    signal,
    received,
    corr_fft
)