#include <math.h>
#include "driver/adc.h"

// ======================================================================
// Radar acustico monoestatico - ESP32-WROOM-32 + MAX4466
// ======================================================================
// Integra en un solo microcontrolador lo que Transmition.ino solo hace
// a medias (transmitir el chirp). Este sketch NO modifica Transmition.ino;
// reutiliza sus mismos parametros y su misma generacion de chirp, y agrega:
//
//   1) Adquisicion del eco mediante ADC (microfono MAX4466).
//   2) FFT radix-2 propia (iterativa, in-place) - sin librerias de alto nivel.
//   3) Correlacion cruzada en el dominio de la frecuencia, equivalente a
//      Files_ED/fft_correlation.py (R = IFFT(Y * conj(X))).
//   4) Estimacion del retardo (tiempo de vuelo) y calculo de distancia
//      d = vs * tau / 2.
//   5) Visualizacion por terminal serial.
//
// Conexion sugerida del MAX4466: OUT -> GPIO34 (ADC1, solo entrada),
// VCC -> 3V3, GND -> GND.

// ---------------- Pines ----------------
const int PIN_DAC     = 25; // Parlante / transductor (salida del chirp)
const int PIN_TRIGGER = 4;  // Flanco de referencia t0 (para verificar con osciloscopio)
const int PIN_MIC     = 34; // Salida del MAX4466 (GPIO34 = ADC1_CH6)
const adc1_channel_t CANAL_MIC = ADC1_CHANNEL_6; // Canal de driver correspondiente a GPIO34

// ---------------- Parametros del chirp transmitido ----------------
// Identicos a los de Transmition.ino: la plantilla usada en la correlacion
// debe coincidir exactamente con lo que realmente se transmite.
const uint32_t FS = 32000;
const float F_INICIO = 1500.0;
const float F_FIN = 11000.0;
const int N = 20;
const float DURACION = (float)N / FS;

const uint32_t PERIODO_MUESTRA_US = 1000000UL / FS; // ~31 us entre muestras
const uint32_t PAUSA_ENTRE_PULSOS_MS = 2000;

// ---------------- Parametros de adquisicion del eco ----------------
// N + RX_LEN - 1 = 1024 (potencia de 2 exacta): la correlacion lineal
// completa cabe en la FFT sin relleno adicional y sin ambiguedad circular.
// Ventana de recepcion -> 1005/32000 s ~= 31.4 ms -> rango maximo ~5.3 m.
const int RX_LEN = 1005;
const int FFT_LEN = 1024;

const float VELOCIDAD_SONIDO = 343.0; // m/s (aire ~20 C)
const int MUESTRAS_CALIBRACION = 200;  // para estimar el nivel DC del MAX4466
const int MARGEN_MUESTRAS = 5;         // ignora el acople directo cerca de m=0 (~3 cm)

// Rango valido de retardos: el chirp de referencia (N muestras) debe caber
// completo dentro de la ventana recibida, es decir m <= RX_LEN - N.
const int LAG_MAXIMO = RX_LEN - N;

// El pico de correlacion debe superar el promedio del resto de la curva por
// este factor para considerarse un eco real y no solo ruido de fondo.
const float UMBRAL_DETECCION = 1.5f;

// Si esta en true, cada ciclo vuelca la curva de correlacion completa por
// Serial en formato "nombre:valor" para verla en el Serial Plotter. Alarga
// bastante cada ciclo (~1000 lineas), asi que se puede poner en false una
// vez validado el sistema.
const bool GRAFICAR_CORRELACION = true;

// ---------------- Buffers ----------------
uint8_t chirp_buffer[N]; // Igual que en Transmition.ino (para el DAC)
float   chirp_ref[N];    // Misma forma de onda, centrada en 0 (plantilla x[n])
float   rx_buffer[RX_LEN];

float fft_re[FFT_LEN];
float fft_im[FFT_LEN];
float fft2_re[FFT_LEN];
float fft2_im[FFT_LEN];

// ======================================================================
// Generacion y transmision del chirp (misma logica que Transmition.ino)
// ======================================================================
void generarChirp() {
  float k = (F_FIN - F_INICIO) / DURACION; // tasa de barrido (Hz/s)

  for (int n = 0; n < N; n++) {
    float t = (float)n / FS;
    float fase = 2.0 * PI * (F_INICIO * t + 0.5 * k * t * t);
    float muestra = sinf(fase);
    chirp_buffer[n] = 127 + (uint8_t)(127.0 * muestra);
    chirp_ref[n] = muestra; // referencia x[n] usada en la correlacion
  }
}

void transmitirChirp() {
  digitalWrite(PIN_TRIGGER, HIGH); // Flanco de subida = t0

  uint32_t siguiente_muestra_us = micros();
  for (int n = 0; n < N; n++) {
    while ((int32_t)(micros() - siguiente_muestra_us) < 0) {
      // espera activa hasta el instante exacto de esta muestra
    }
    dacWrite(PIN_DAC, chirp_buffer[n]);
    siguiente_muestra_us += PERIODO_MUESTRA_US;
  }

  dacWrite(PIN_DAC, 127);
  digitalWrite(PIN_TRIGGER, LOW);
}

// ======================================================================
// Adquisicion del eco
// ======================================================================

// Promedia MUESTRAS_CALIBRACION lecturas en silencio para estimar el
// nivel DC de reposo del MAX4466 (aprox. VCC/2) y poder centrar la senal.
float medirNivelDC() {
  long suma = 0;
  for (int i = 0; i < MUESTRAS_CALIBRACION; i++) {
    suma += adc1_get_raw(CANAL_MIC);
    delayMicroseconds(PERIODO_MUESTRA_US);
  }
  return (float)suma / MUESTRAS_CALIBRACION;
}

// Captura RX_LEN muestras con el mismo periodo nominal usado al transmitir,
// comenzando justo despues de terminar el chirp. Devuelve la duracion real
// de la ventana (en us) para poder detectar si el ADC no llego al periodo.
uint32_t adquirirEco(float nivel_dc) {
  uint32_t inicio_us = micros();
  uint32_t siguiente_muestra_us = inicio_us;

  for (int n = 0; n < RX_LEN; n++) {
    while ((int32_t)(micros() - siguiente_muestra_us) < 0) {
      // espera activa hasta el instante exacto de esta muestra
    }
    int cruda = adc1_get_raw(CANAL_MIC);
    rx_buffer[n] = (float)cruda - nivel_dc; // senal centrada en 0
    siguiente_muestra_us += PERIODO_MUESTRA_US;
  }

  return micros() - inicio_us;
}

// ======================================================================
// FFT radix-2 iterativa (in-place) y su inversa
// ======================================================================
void fft_iterativa(float *re, float *im, int n) {
  // Permutacion bit-reversal.
  int j = 0;
  for (int i = 1; i < n; i++) {
    int bit = n >> 1;
    for (; j & bit; bit >>= 1) {
      j ^= bit;
    }
    j ^= bit;
    if (i < j) {
      float tmp = re[i]; re[i] = re[j]; re[j] = tmp;
      tmp = im[i]; im[i] = im[j]; im[j] = tmp;
    }
  }

  // Mariposas de Cooley-Tukey.
  for (int len = 2; len <= n; len <<= 1) {
    float ang = -2.0f * PI / len; // W_N^k = exp(-j*2*pi*k/N)
    float wr = cosf(ang);
    float wi = sinf(ang);
    for (int i = 0; i < n; i += len) {
      float cur_wr = 1.0f, cur_wi = 0.0f;
      for (int k = 0; k < len / 2; k++) {
        float ur = re[i + k];
        float ui = im[i + k];
        float vr = re[i + k + len / 2] * cur_wr - im[i + k + len / 2] * cur_wi;
        float vi = re[i + k + len / 2] * cur_wi + im[i + k + len / 2] * cur_wr;

        re[i + k] = ur + vr;
        im[i + k] = ui + vi;
        re[i + k + len / 2] = ur - vr;
        im[i + k + len / 2] = ui - vi;

        float nwr = cur_wr * wr - cur_wi * wi;
        float nwi = cur_wr * wi + cur_wi * wr;
        cur_wr = nwr;
        cur_wi = nwi;
      }
    }
  }
}

// IFFT(X) = conj(FFT(conj(X))) / N, igual criterio que
// Files_ED/fft_correlation.py::ifft_radix2, reutilizando la misma FFT.
void ifft_iterativa(float *re, float *im, int n) {
  for (int i = 0; i < n; i++) im[i] = -im[i];
  fft_iterativa(re, im, n);
  for (int i = 0; i < n; i++) {
    re[i] = re[i] / n;
    im[i] = -im[i] / n;
  }
}

// ======================================================================
// Correlacion cruzada mediante FFT (equivalente a correlacion_fft)
// ======================================================================
// R_yx[m] = sum_n y[n] * conj(x[n-m]) = IFFT( FFT(y) * conj(FFT(x)) ).
// Devuelve el retardo (en muestras dentro de rx_buffer) donde la
// correlacion es maxima, ignorando el acople directo cerca de m=0.
int correlacionEcoFFT() {
  for (int i = 0; i < FFT_LEN; i++) {
    fft_re[i] = (i < N) ? chirp_ref[i] : 0.0f;
    fft_im[i] = 0.0f;
  }
  fft_iterativa(fft_re, fft_im, FFT_LEN); // X = FFT(x)

  for (int i = 0; i < FFT_LEN; i++) {
    fft2_re[i] = (i < RX_LEN) ? rx_buffer[i] : 0.0f;
    fft2_im[i] = 0.0f;
  }
  fft_iterativa(fft2_re, fft2_im, FFT_LEN); // Y = FFT(y)

  // R[k] = Y[k] * conj(X[k]) = (ac+bd) + j(bc-ad), con Y=a+jb, X=c+jd.
  for (int k = 0; k < FFT_LEN; k++) {
    float a = fft2_re[k], b = fft2_im[k];
    float c = fft_re[k],  d = fft_im[k];
    fft2_re[k] = a * c + b * d;
    fft2_im[k] = b * c - a * d;
  }

  ifft_iterativa(fft2_re, fft2_im, FFT_LEN);

  // FFT_LEN = N + RX_LEN - 1 exacto, por lo que los indices 0..RX_LEN-1
  // ya son el resultado lineal (sin ambiguedad circular). Los indices
  // RX_LEN..FFT_LEN-1 corresponden a retardos negativos (no causales)
  // y se descartan.
  //
  // Ademas, solo se buscan lags donde el chirp de referencia (N muestras)
  // cabe COMPLETO dentro de la ventana recibida, es decir m <= RX_LEN - N.
  // Para m > RX_LEN - N el traslape es parcial (menos de N terminos), lo
  // que produce una cola de alta varianza cerca del borde que no representa
  // un eco real y puede generar falsos maximos.
  int mejor_indice = MARGEN_MUESTRAS;
  float mejor_valor = fft2_re[MARGEN_MUESTRAS];
  for (int m = MARGEN_MUESTRAS + 1; m <= LAG_MAXIMO; m++) {
    if (fft2_re[m] > mejor_valor) {
      mejor_valor = fft2_re[m];
      mejor_indice = m;
    }
  }

  if (GRAFICAR_CORRELACION) {
    // Se grafica solo el rango valido (0..LAG_MAXIMO), el mismo que usa la
    // busqueda del pico. Se omite la cola de traslape parcial (m > LAG_MAXIMO)
    // porque no representa un eco real y solo confunde la lectura del grafico.
    for (int m = 0; m <= LAG_MAXIMO; m++) {
      Serial.print("correlacion:");
      Serial.print(fft2_re[m], 1);
      Serial.print(",pico:");
      Serial.println((m == mejor_indice) ? fft2_re[m] : 0.0f, 1);
    }
  }

  return mejor_indice;
}

// ======================================================================
// Estimacion de tiempo de vuelo y distancia
// ======================================================================
// rx_buffer empieza justo al terminar de transmitir (duracion N/FS desde
// t0), por lo que el retardo total desde t0 es esa duracion mas el
// desplazamiento (lag) encontrado dentro de la ventana de recepcion.
float calcularRetardo(int lag_en_rx) {
  return ((float)N + (float)lag_en_rx) / FS;
}

float calcularDistancia(float tau) {
  return (VELOCIDAD_SONIDO * tau) / 2.0f;
}

// ======================================================================
// Programa principal
// ======================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(PIN_TRIGGER, OUTPUT);
  digitalWrite(PIN_TRIGGER, LOW);

  // Configuracion directa del driver ADC (evita el overhead de analogRead(),
  // que reconfigura el canal en cada llamada y no alcanza a muestrear a FS).
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_config_channel_atten(CANAL_MIC, ADC_ATTEN_DB_11);

  generarChirp();

  Serial.println("Radar acustico listo:");
  Serial.print("  Banda del chirp: "); Serial.print(F_INICIO); Serial.print(" - "); Serial.print(F_FIN); Serial.println(" Hz");
  Serial.print("  fs: "); Serial.print(FS); Serial.println(" Hz");
  Serial.print("  Ventana de recepcion: "); Serial.print(RX_LEN); Serial.println(" muestras");
  Serial.print("  Rango maximo aproximado: ");
  Serial.print(VELOCIDAD_SONIDO * ((float)RX_LEN / FS) / 2.0f, 2);
  Serial.println(" m");
}

void loop() {
  float nivel_dc = medirNivelDC();

  Serial.print("Nivel DC del MAX4466: ");
  Serial.print(nivel_dc, 1);
  Serial.print(" cuentas (~");
  Serial.print(nivel_dc * 3.3f / 4095.0f, 3);
  Serial.println(" V en reposo)");

  transmitirChirp();
  uint32_t duracion_us = adquirirEco(nivel_dc);

  int lag = correlacionEcoFFT();
  float tau = calcularRetardo(lag);
  float distancia = calcularDistancia(tau);

  // Compara el pico de correlacion contra el promedio del resto de la curva
  // (fft2_re todavia tiene la correlacion de este ciclo, la dejo correlacionEcoFFT()).
  // Un pico que no sobresale del promedio es indistinguible de ruido: no hay
  // manera confiable de decir que ahi hay un eco real.
  float suma_corr = 0.0f;
  for (int m = MARGEN_MUESTRAS; m <= LAG_MAXIMO; m++) {
    suma_corr += fft2_re[m];
  }
  float promedio_corr = suma_corr / (LAG_MAXIMO - MARGEN_MUESTRAS + 1);
  float pico_corr = fft2_re[lag];
  float razon = pico_corr / promedio_corr;
  bool senal_identificada = razon > UMBRAL_DETECCION;

  Serial.print(senal_identificada ? ">>> Eco IDENTIFICADO" : ">>> Eco NO identificado (parece ruido)");
  Serial.print(" (pico/promedio = "); Serial.print(razon, 2); Serial.println(")");

  Serial.print(">>> Retardo estimado: ");
  Serial.print(tau * 1000.0f, 3);
  Serial.print(" ms | Distancia estimada: ");
  Serial.print(distancia, 3);
  Serial.println(" m");

  uint32_t esperado_us = (uint32_t)RX_LEN * PERIODO_MUESTRA_US;
  if (duracion_us > esperado_us + esperado_us / 10) {
    Serial.println("Aviso: el ADC no alcanzo el periodo de muestreo esperado; considere reducir FS.");
  }

  delay(PAUSA_ENTRE_PULSOS_MS);
}
