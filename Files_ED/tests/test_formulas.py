"""Pruebas de las fórmulas; se pueden ejecutar sin instalar NumPy.

Desde la raíz: python -B -S -m unittest discover -s Files_ED/tests -v
"""

import cmath
import math
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from convolution import convolucion_directa
from correlation import correlacion_directa
from echo_model import generar_eco
from fft_correlation import correlacion_fft, fft_radix2, ifft_radix2


class FormulasTest(unittest.TestCase):
    def assert_secuencias_cercanas(self, actual, esperado):
        self.assertEqual(len(actual), len(esperado))
        for a, b in zip(actual, esperado):
            self.assertLessEqual(abs(a - b), 1e-10)

    def test_convolucion_con_resultado_conocido(self):
        self.assertEqual(
            convolucion_directa([1, 2, 3], [4, 5]), [4, 13, 22, 15]
        )

    def test_correlacion_con_resultado_conocido_y_signo_del_retardo(self):
        for metodo in (correlacion_directa, correlacion_fft):
            with self.subTest(metodo=metodo.__name__):
                curva, retardo = metodo([1, 2], [0, 1, 2])
                self.assert_secuencias_cercanas(curva, [0, 2, 5, 2])
                self.assertEqual(retardo, 1)
                curva, retardo = metodo([0, 1, 2], [1, 2])
                self.assert_secuencias_cercanas(curva, [2, 5, 2, 0])
                self.assertEqual(retardo, -1)

    def test_correlacion_equivale_a_convolucion_con_senal_invertida(self):
        rng = random.Random(42)
        # Incluye el caso de una muestra y longitudes diferentes/no potencia de dos.
        for nx, ny in ((1, 1), (1, 3), (5, 1), (2, 9), (9, 2), (7, 13), (31, 48)):
            with self.subTest(nx=nx, ny=ny):
                x = [rng.uniform(-1, 1) for _ in range(nx)]
                y = [rng.uniform(-1, 1) for _ in range(ny)]
                esperado = convolucion_directa(y, x[::-1])
                retardo_esperado = max(range(len(esperado)), key=esperado.__getitem__) - (nx - 1)
                for metodo in (correlacion_directa, correlacion_fft):
                    curva, retardo = metodo(x, y)
                    self.assert_secuencias_cercanas(curva, esperado)
                    self.assertEqual(retardo, retardo_esperado)

    def test_fft_coincide_con_sumatoria_dft(self):
        rng = random.Random(7)
        for longitud in (1, 3, 7, 8, 16):
            with self.subTest(longitud=longitud):
                x = [complex(rng.random(), rng.random()) for _ in range(longitud)]
                N = 1
                while N < longitud:
                    N *= 2
                # Referencia independiente: DFT directa, sin descomposición radix-2.
                esperado = [
                    sum(x[n] * cmath.exp(-2j * math.pi * k * n / N)
                        for n in range(longitud))
                    for k in range(N)
                ]
                self.assert_secuencias_cercanas(fft_radix2(x), esperado)

    def test_inversa_coincide_con_sumatoria_idft(self):
        X = [1 + 2j, 3 - 1j, -2 + 4j, 5]
        N = len(X)
        esperado = [
            sum(X[k] * cmath.exp(2j * math.pi * k * n / N) for k in range(N)) / N
            for n in range(N)
        ]
        self.assert_secuencias_cercanas(ifft_radix2(X), esperado)

    def test_teorema_convolucion_y_multiplicacion_en_frecuencia(self):
        x, h = [1, -2, 3, 0.5], [2, 1, -1]
        esperado = convolucion_directa(x, h)
        N = len(esperado)
        X = fft_radix2(x + [0.0] * (N - len(x)))
        H = fft_radix2(h + [0.0] * (N - len(h)))
        producto = [X[k] * H[k] for k in range(len(X))]
        self.assert_secuencias_cercanas(ifft_radix2(producto)[:N], esperado)

    def test_eco_es_convolucion_con_impulso_y_recorte(self):
        self.assertEqual(generar_eco([1, 2, 3, 4], 2, 0.5, 0), [0, 0, 0.5, 1])
        self.assertEqual(generar_eco([1, 2, 3], 0, 0.5, 0), [0.5, 1, 1.5])
        self.assertEqual(generar_eco([1, 2, 3], 5, 0.5, 0), [0, 0, 0])

    def test_chirp_con_ruido_detecta_80_muestras(self):
        N, fs = 512, 8000
        pendiente = (3000 - 300) / (N / fs)
        x = [math.sin(2 * math.pi * (300 * (n / fs) + 0.5 * pendiente * (n / fs) ** 2))
             for n in range(N)]
        estado = random.getstate()
        try:
            random.seed(2026)
            y = generar_eco(x, 80, 0.5, 0.05)
        finally:
            random.setstate(estado)
        directa, retardo_directo = correlacion_directa(x, y)
        fft, retardo_fft = correlacion_fft(x, y)
        self.assert_secuencias_cercanas(directa, fft)
        self.assertEqual(retardo_directo, 80)
        self.assertEqual(retardo_fft, 80)

    def test_entradas_invalidas(self):
        for funcion in (convolucion_directa, correlacion_directa, correlacion_fft):
            for x, y in (([], [1]), ([1], [])):
                with self.subTest(funcion=funcion.__name__, x=x, y=y):
                    with self.assertRaises(ValueError):
                        funcion(x, y)
        with self.assertRaises(ValueError):
            fft_radix2([])
        for espectro in ([], [1, 2, 3]):
            with self.assertRaises(ValueError):
                ifft_radix2(espectro)
        with self.assertRaises(ValueError):
            generar_eco([1, 2], -1)
        with self.assertRaises(TypeError):
            generar_eco([1, 2], 0.5)
        with self.assertRaises(ValueError):
            generar_eco([1, 2], 0, nivel_ruido=-1)


if __name__ == "__main__":
    unittest.main()
