#include <math.h>

// pines
const int PIN_DAC = 25;
const int PIN_TRIGGER = 4;

// parámetros 
const uint32_t FS = 32000;
const float F_INICIO = 1500.0;
const float F_FIN = 11000.0;
const int N = 20;
const float DURACION = (float)N / FS;

// buffer precalculado del chirp
uint8_t chirp_buffer[N];

const uint32_t PERIODO_MUESTRA_US = 1000000UL / FS; // ~31.25 us entre muestras
const uint32_t PAUSA_ENTRE_PULSOS_MS = 2000; // pausa entre repeticiones

void generarChirp() {
  float k = (F_FIN - F_INICIO) / DURACION; // tasa de barrido (Hz/s)

  for (int n = 0; n < N; n++) {
    float t = (float)n / FS;
    float fase = 2.0 * PI * (F_INICIO * t + 0.5 * k * t * t);
    chirp_buffer[n] = 127 + (uint8_t)(127.0 * sinf(fase));
  }
}

void transmitirChirp() {
  digitalWrite(PIN_TRIGGER, HIGH); // Flanco de subida = t0 para el receptor

  uint32_t siguiente_muestra_us = micros();
  for (int n = 0; n < N; n++) {
    while ((int32_t)(micros() - siguiente_muestra_us) < 0) {
      // espera activa hasta el instante exacto de esta muestra
    }
    dacWrite(PIN_DAC, chirp_buffer[n]);
    siguiente_muestra_us += PERIODO_MUESTRA_US;
  }

  dacWrite(PIN_DAC, 127);            // vuelta a "silencio" (0V AC tras el capacitor)
  digitalWrite(PIN_TRIGGER, LOW);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(PIN_TRIGGER, OUTPUT);
  digitalWrite(PIN_TRIGGER, LOW);

  generarChirp();

  Serial.println("Chirp generado:");
  Serial.print("  Banda: "); Serial.print(F_INICIO); Serial.print(" - "); Serial.print(F_FIN); Serial.println(" Hz");
  Serial.print("  fs: "); Serial.print(FS); Serial.println(" Hz");
  Serial.print("  N: "); Serial.println(N);
  Serial.print("  Duracion: "); Serial.print(DURACION * 1000.0); Serial.println(" ms");
}

void loop() {
  Serial.println(">>> Transmitiendo chirp...");
  transmitirChirp();

  delay(PAUSA_ENTRE_PULSOS_MS);
}