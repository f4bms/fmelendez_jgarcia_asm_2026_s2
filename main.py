from signal_generator import generate_step_signal
from echo_model import create_echo
from correlation import calculate_correlation
from visualization import plot_signals


# Generar señal
t, signal = generate_step_signal()


# Crear eco
received, real_delay = create_echo(signal)


# Encontrar eco mediante correlación
corr, estimated_delay = calculate_correlation(
    signal,
    received
)


print("-------------------------")
print("Retardo real:")
print(real_delay)

print("Retardo estimado:")
print(estimated_delay)

print("-------------------------")


plot_signals(
    t,
    signal,
    received,
    corr
)