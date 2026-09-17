# Acoustic-Radar

Primer proyecto del curso de Análisis de Señales Mixtas.

## Descripción del proyecto

Sistema de radar acústico capaz de detectar un objeto y estimar su distancia mediante el análisis del eco producido por una señal acústica conocida.

## Etapa 1: Investigación de conceptos y herramientas

## Etapa 2: Implementación de la DFT y FFT

En esta etapa se desarrollaron las funciones de:

- DFT directa
- FFT radix-2
- señales de prueba básicas (seno, suma de tonos, pulso rectangular, secuencia de pulsos, chirp)
- comparación de tiempos de ejecución para distintos tamaños de señal
- visualización de magnitud y fase del espectro

La carpeta FFT&DFT incluye los módulos:

- dft.py: implementación de la transformada discreta de Fourier
- fft.py: FFT radix-2 propia
- signals.py: generadores de señales
- graphics.py: exportación de gráficas de tiempo y frecuencia
- comp_time.py: benchmarking de tiempos entre DFT y FFT

---

## Etapa 3: Detección de eco y estimación de distancia

Se modela un eco acústico con:

- retardo temporal
- atenuación
- ruido gaussiano aditivo

La señal recibida se compara contra la transmitida usando:

- correlación directa
- correlación mediante FFT

Esto permite estimar el retardo del eco y, conociendo la velocidad del sonido, aproximar la distancia del objeto.

La carpeta Files_ED contiene:

- echo_model.py: generación del eco simulado
- correlation.py: método directo de correlación
- fft_correlation.py: correlación basada en FFT propia
- plots_echo.py: adaptación para guardar gráficas comparativas
- main.py: experimento principal con varias señales de prueba

---

## Ejecución

El proyecto se ejecuta con el Makefile principal:

```bash
make all
```

Este comando ejecuta las siguientes tareas:

- genera gráficas de FFT/DFT y análisis espectral
- compara tiempos de ejecución entre DFT y FFT
- ejecuta el experimento de detección de ecos

También puede ejecutarse cada bloque por separado:

```bash
make graphics
make comp_time
make files_ed
```

---

## Estructura del repositorio

```text
Acoustic-Radar/
├── Makefile
├── README.md
├── FFT&DFT/
│   ├── dft.py
│   ├── fft.py
│   ├── signals.py
│   ├── graphics.py
│   ├── comp_time.py
│   └── graphics/
├── Files_ED/
│   ├── main.py
│   ├── echo_model.py
│   ├── correlation.py
│   ├── fft_correlation.py
│   ├── plots_echo.py
│   └── graphics/
└── ...
```

---

## Resultados esperados

Durante la ejecución se generan imágenes en las carpetas graphics de cada módulo:

- comparacion_tiempos.png: rendimiento de DFT vs FFT
- gráficos de señales, magnitud y fase
- gráficos de eco y correlación para cada señal de prueba

Esto permite visualizar tanto el comportamiento espectral como la capacidad del sistema para detectar ecos y estimar retardos.

---