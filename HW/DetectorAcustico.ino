#include <math.h>
#include "driver/adc.h"

// Radar acustico monoestatico - ESP32-WROOM-32 + MAX4466

// ---------------- Pines ----------------
const int PIN_DAC     = 25; // Parlante / transductor (salida del chirp)
const int PIN_TRIGGER = 4;  // Flanco de referencia t0 (para verificar con osciloscopio)
const int PIN_MIC     = 34; // Salida del MAX4466 (GPIO34 = ADC1_CH6)
const adc1_channel_t CANAL_MIC = ADC1_CHANNEL_6;

// ---------------- Parametros del chirp transmitido ----------------
const uint32_t FS = 32000;
const float F_INICIO = 1500.0;
const float F_FIN = 11000.0;
const int N = 20;
const float DURACION = (float)N / FS;

// Periodo EXACTO entre muestras, sin truncar (31.25 us, no 31 us).
const double PERIODO_MUESTRA_US = 1000000.0 / FS;
const uint32_t PAUSA_ENTRE_PULSOS_MS = 2000;

// ---------------- Parametros de adquisicion del eco ----------------
// N + RX_LEN - 1 = 512 (potencia de 2 exacta). Ventana de recepcion ->
// 493/32000 s ~= 15.4 ms -> rango maximo ~2.64 m, con margen holgado
// sobre el rango objetivo del proyecto (30-60 cm).
const int RX_LEN = 493;
const int FFT_LEN = 512;
const float VELOCIDAD_SONIDO = 343.0; // m/s (aire ~20 C)
const int MUESTRAS_CALIBRACION = 200;  // para estimar el nivel DC del MAX4466
const int MARGEN_MUESTRAS = 5;         // ignora el acople directo cerca de m=0 (~3 cm)

const int LAG_MAXIMO = RX_LEN - N;

// El pico de correlacion debe superar el RMS del resto de la curva por
// este factor para considerarse un eco real y no solo ruido de fondo.
// Calibrado con datos reales: en 5 ciclos de solo ruido (bocina
// desconectada) el maximo pico/RMS observado fue 3.66 -- se sube el
// umbral por encima de eso con margen de seguridad.
const float UMBRAL_DETECCION = 4.5f;

// ---------------- Verificacion de consistencia entre ciclos ----------------
// Un eco real (de un objeto que no se mueve) deberia caer en
// practicamente la misma posicion (mismo lag) ciclo tras ciclo. El ruido
// de fondo que cruza el umbral por azar, no -- va a aparecer en
// posiciones distintas cada vez. Por eso no se acepta un candidato como
// eco real hasta que se repita en la misma posicion varios ciclos
// seguidos.
const int TOLERANCIA_LAG_MUESTRAS = 3;   // cuantas muestras de diferencia se toleran entre ciclos
const int CONSISTENCIA_REQUERIDA = 3;    // ciclos consecutivos consistentes para confirmar

static int lag_anterior = -1;
static int contador_consistencia = 0;

const bool GRAFICAR_CORRELACION = true;

// Si la duracion real de la ventana se desvia de la nominal por mas de
// este porcentaje, se avisa que la correlacion puede estar degradada
// (no solo el calculo de distancia, que ya se autocorrige).
const float TOLERANCIA_DESFASE_PORCENTUAL = 5.0f;

// ---------------- Buffers ----------------
uint8_t chirp_buffer[N];
float   chirp_ref[N];
float   rx_buffer[RX_LEN];

float fft_re[FFT_LEN];
float fft_im[FFT_LEN];
float fft2_re[FFT_LEN];
float fft2_im[FFT_LEN];

// ======================================================================
// Generacion y transmision del chirp
// ======================================================================
void generarChirp() {
  float k = (F_FIN - F_INICIO) / DURACION;

  for (int n = 0; n < N; n++) {
    float t = (float)n / FS;
    float fase = 2.0 * PI * (F_INICIO * t + 0.5 * k * t * t);
    float muestra = sinf(fase);
    chirp_buffer[n] = 127 + (uint8_t)(127.0 * muestra);
    chirp_ref[n] = muestra;
  }
}

void transmitirChirp() {
  digitalWrite(PIN_TRIGGER, HIGH);

  double siguiente_muestra_ideal_us = (double)micros();
  for (int n = 0; n < N; n++) {
    while ((int32_t)(micros() - (uint32_t)siguiente_muestra_ideal_us) < 0) {
      // espera activa hasta el instante exacto de esta muestra
    }
    dacWrite(PIN_DAC, chirp_buffer[n]);
    siguiente_muestra_ideal_us += PERIODO_MUESTRA_US;
  }

  dacWrite(PIN_DAC, 127);
  digitalWrite(PIN_TRIGGER, LOW);
}

// ======================================================================
// Adquisicion del eco
// ======================================================================
float medirNivelDC() {
  long suma = 0;
  for (int i = 0; i < MUESTRAS_CALIBRACION; i++) {
    suma += adc1_get_raw(CANAL_MIC);
    delayMicroseconds((uint32_t)PERIODO_MUESTRA_US);
  }
  return (float)suma / MUESTRAS_CALIBRACION;
}

// Captura RX_LEN muestras y devuelve la duracion REAL de la ventana (us).
// Esa duracion real es la que se usa despues para convertir lag->tiempo,
// en vez de asumir ciegamente el FS nominal.
uint32_t adquirirEco(float nivel_dc) {
  uint32_t inicio_us = micros();
  double siguiente_muestra_ideal_us = (double)inicio_us;

  for (int n = 0; n < RX_LEN; n++) {
    while ((int32_t)(micros() - (uint32_t)siguiente_muestra_ideal_us) < 0) {
      // espera activa hasta el instante exacto de esta muestra
    }
    int cruda = adc1_get_raw(CANAL_MIC);
    rx_buffer[n] = (float)cruda - nivel_dc;
    siguiente_muestra_ideal_us += PERIODO_MUESTRA_US;
  }

  return micros() - inicio_us;
}

// ======================================================================
// FFT radix-2 iterativa (in-place) y su inversa
// ======================================================================
void fft_iterativa(float *re, float *im, int n) {
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

  for (int len = 2; len <= n; len <<= 1) {
    float ang = -2.0f * PI / len;
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

void ifft_iterativa(float *re, float *im, int n) {
  for (int i = 0; i < n; i++) im[i] = -im[i];
  fft_iterativa(re, im, n);
  for (int i = 0; i < n; i++) {
    re[i] = re[i] / n;
    im[i] = -im[i] / n;
  }
}

// ======================================================================
// Correlacion cruzada mediante FFT
// ======================================================================
int correlacionEcoFFT() {
  for (int i = 0; i < FFT_LEN; i++) {
    fft_re[i] = (i < N) ? chirp_ref[i] : 0.0f;
    fft_im[i] = 0.0f;
  }
  fft_iterativa(fft_re, fft_im, FFT_LEN);

  for (int i = 0; i < FFT_LEN; i++) {
    fft2_re[i] = (i < RX_LEN) ? rx_buffer[i] : 0.0f;
    fft2_im[i] = 0.0f;
  }
  fft_iterativa(fft2_re, fft2_im, FFT_LEN);

  for (int k = 0; k < FFT_LEN; k++) {
    float a = fft2_re[k], b = fft2_im[k];
    float c = fft_re[k],  d = fft_im[k];
    fft2_re[k] = a * c + b * d;
    fft2_im[k] = b * c - a * d;
  }

  ifft_iterativa(fft2_re, fft2_im, FFT_LEN);

  int mejor_indice = MARGEN_MUESTRAS;
  float mejor_valor = fft2_re[MARGEN_MUESTRAS];
  for (int m = MARGEN_MUESTRAS + 1; m <= LAG_MAXIMO; m++) {
    if (fft2_re[m] > mejor_valor) {
      mejor_valor = fft2_re[m];
      mejor_indice = m;
    }
  }

  if (GRAFICAR_CORRELACION) {
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
// Estimacion de tiempo de vuelo y distancia (auto-calibrada)
// ======================================================================
// periodo_real_us: duracion real de la ventana / RX_LEN, medido en cada
// ciclo -- no se asume el FS nominal, se usa lo que realmente paso.
float calcularRetardo(int lag_en_rx, double periodo_real_us) {
  float t_transmision = (float)N / FS;             // el TX si cumple su timing (N es chico)
  float t_dentro_ventana = (float)(lag_en_rx * periodo_real_us) / 1.0e6f;
  return t_transmision + t_dentro_ventana;
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

  adc1_config_width(ADC_WIDTH_BIT_10);           // menos bits = conversion mas rapida
  adc1_config_channel_atten(CANAL_MIC, ADC_ATTEN_DB_11);

  generarChirp();

  Serial.println("Radar acustico listo (v2):");
  Serial.print("  Banda del chirp: "); Serial.print(F_INICIO); Serial.print(" - "); Serial.print(F_FIN); Serial.println(" Hz");
  Serial.print("  fs nominal: "); Serial.print(FS); Serial.println(" Hz");
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
  Serial.print(nivel_dc * 3.3f / 1023.0f, 3); // 10 bits -> 0-1023
  Serial.println(" V en reposo)");

  transmitirChirp();
  uint32_t duracion_us = adquirirEco(nivel_dc);

  // Periodo real medido, usado para convertir lag -> tiempo -> distancia.
  double periodo_real_us = (double)duracion_us / (double)RX_LEN;
  double periodo_nominal_us = PERIODO_MUESTRA_US;
  float desfase_pct = 100.0f * (float)(fabs(periodo_real_us - periodo_nominal_us) / periodo_nominal_us);

  int lag = correlacionEcoFFT();
  float tau = calcularRetardo(lag, periodo_real_us);
  float distancia = calcularDistancia(tau);

  // Umbral pico/RMS: mas robusto que pico/promedio para una curva que
  // oscila alrededor de cero cuando solo hay ruido.
  float suma_cuadrados = 0.0f;
  for (int m = MARGEN_MUESTRAS; m <= LAG_MAXIMO; m++) {
    suma_cuadrados += fft2_re[m] * fft2_re[m];
  }
  float rms_piso = sqrtf(suma_cuadrados / (LAG_MAXIMO - MARGEN_MUESTRAS + 1));
  float pico_corr = fft2_re[lag];
  float razon = (rms_piso > 1e-6f) ? (pico_corr / rms_piso) : 0.0f;
  bool candidato_valido = razon > UMBRAL_DETECCION;

  // Verificacion de consistencia: solo cuenta como el "mismo" candidato
  // si esta a pocas muestras del lag del ciclo anterior.
  if (candidato_valido) {
    if (lag_anterior >= 0 && abs(lag - lag_anterior) <= TOLERANCIA_LAG_MUESTRAS) {
      contador_consistencia++;
    } else {
      contador_consistencia = 1; // nuevo candidato, reinicia el conteo
    }
    lag_anterior = lag;
  } else {
    contador_consistencia = 0;
    lag_anterior = -1;
  }

  bool eco_confirmado = candidato_valido && (contador_consistencia >= CONSISTENCIA_REQUERIDA);

  if (eco_confirmado) {
    Serial.print(">>> ECO CONFIRMADO");
  } else if (candidato_valido) {
    Serial.print(">>> candidato a eco (");
    Serial.print(contador_consistencia);
    Serial.print("/");
    Serial.print(CONSISTENCIA_REQUERIDA);
    Serial.print(" ciclos consistentes)");
  } else {
    Serial.print(">>> Eco NO identificado (parece ruido)");
  }
  Serial.print(" (pico/RMS = "); Serial.print(razon, 2); Serial.println(")");

  Serial.print(">>> Retardo estimado: ");
  Serial.print(tau * 1000.0f, 3);
  Serial.print(" ms | Distancia estimada: ");
  Serial.print(distancia, 3);
  Serial.println(" m");

  Serial.print(">>> Periodo real de muestreo RX: ");
  Serial.print(periodo_real_us, 2);
  Serial.print(" us (nominal ");
  Serial.print(periodo_nominal_us, 2);
  Serial.print(" us, desfase ");
  Serial.print(desfase_pct, 1);
  Serial.println("%)");

  if (desfase_pct > TOLERANCIA_DESFASE_PORCENTUAL) {
    Serial.println("Aviso: el ADC se desvio bastante del periodo nominal.");
    Serial.println("La distancia ya esta autocorregida, pero un desfase grande");
    Serial.println("puede degradar la forma del pico de correlacion. Si persiste,");
    Serial.println("considere bajar aun mas la resolucion del ADC (9 bits).");
  }

  delay(PAUSA_ENTRE_PULSOS_MS);
}