import matplotlib.pyplot as plt


def plot_signals(
        t,
        transmitted,
        received,
        correlation):


    plt.figure(figsize=(10,6))


    plt.subplot(3,1,1)
    plt.plot(t, transmitted)
    plt.title("Señal transmitida")
    plt.grid()


    plt.subplot(3,1,2)
    plt.plot(t, received)
    plt.title("Señal recibida con eco y ruido")
    plt.grid()


    plt.subplot(3,1,3)
    plt.plot(correlation)
    plt.title("Correlación")
    plt.grid()


    plt.tight_layout()

    plt.show()