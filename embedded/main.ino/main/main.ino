// ===================================================================================
// E-NOSE ZIZU — FINAL VERSION (UNO R4 WiFi)
// LOGIC: HOLD 2 MENIT | PURGE 4 MENIT | LEVEL 1-5 OTOMATIS
// HARDWARE: MiCS-5524 (Analog) + GM-XXX (I2C) + 2 MOTOR (KIPAS & POMPA)
// ===================================================================================

#include <WiFiS3.h>
#include <Wire.h>
#include "Multichannel_Gas_GMXXX.h"


// ==================== 1. KONFIGURASI WIFI & SERVER ====================
// Gunakan nama WiFi versi 2.4GHz (Arduino tidak support 5GHz!)
const char* ssid     = "Start-up";       // <--- JANGAN PAKAI YANG _5G
const char* pass     = "Warkop123";      // Password WiFi

// IP Laptop (Tetap sama, karena satu Router)
const char* RUST_IP  = "192.168.1.91";   
const int   RUST_PORT = 8081;

WiFiClient client;

// ==================== 2. KONFIGURASI SENSOR ====================
GAS_GMXXX<TwoWire> gas;

// Konfigurasi MiCS-5524
#define MICS_PIN    A1
#define RLOAD       820.0    // Nilai Resistor beban (Ohm)
#define VCC         5.0      // Tegangan referensi (Volt)
float R0_mics = 100000.0;    // Nilai awal R0 (akan dikalibrasi di setup)

// ==================== 3. KONFIGURASI MOTOR (HARDWARE TETAP) ====================
// Mapping Pin Motor Driver L298N
const int PWM_KIPAS   = 10;
const int DIR_KIPAS_1 = 12;
const int DIR_KIPAS_2 = 13;

const int PWM_POMPA   = 11;
const int DIR_POMPA_1 = 8;
const int DIR_POMPA_2 = 9;

// ==================== 4. STATE MACHINE & LOGIKA LEVEL ====================
enum State { IDLE, PRE_COND, RAMP_UP, HOLD, PURGE, RECOVERY, DONE };
State currentState = IDLE;

unsigned long stateTime = 0;
int currentLevel = 0;  // Level internal 0-4 (di Rust terbaca 1-5)
const int speeds[5] = {51, 102, 153, 204, 255}; // Level kecepatan Kipas
bool samplingActive = false;

// ==================== 5. TIMING (SESUAI REQUEST ZIZU) ====================
const unsigned long T_PRECOND  = 15000;   // 15 detik (Pemanasan awal)
const unsigned long T_RAMP     = 3000;    // 3 detik (Naik perlahan)
const unsigned long T_HOLD     = 120000;  // 2 MENIT (Sampling Data Utama)
const unsigned long T_PURGE    = 240000;  // 4 MENIT (Pembersihan Chamber)
const unsigned long T_RECOVERY = 10000;   // 10 detik (Istirahat antar level)
unsigned long lastSend = 0;

// ==================== FUNGSI KONTROL MOTOR ====================
void kipas(int speed, bool buang = false) {
  digitalWrite(DIR_KIPAS_1, buang ? LOW : HIGH);
  digitalWrite(DIR_KIPAS_2, buang ? HIGH : LOW);
  analogWrite(PWM_KIPAS, speed);
}

void pompa(int speed) {
  digitalWrite(DIR_POMPA_1, HIGH);
  digitalWrite(DIR_POMPA_2, LOW);
  analogWrite(PWM_POMPA, speed);
}

void stopAll() { 
  analogWrite(PWM_KIPAS, 0); 
  analogWrite(PWM_POMPA, 0); 
}

void rampKipas(int target) {
  static int cur = 0;
  // Naik/Turun secara bertahap agar halus
  if (cur < target) cur += 15;
  else if (cur > target) cur -= 15;
  
  cur = constrain(cur, 0, 255);
  kipas(cur);
}

// ==================== RUMUS MiCS-5524 (VALIDATED) ====================
float calculateRs() {
  int raw = analogRead(MICS_PIN);
  if (raw < 10) return -1; // Sensor mungkin dicabut/error
  
  float Vout = raw * (VCC / 1023.0);
  if (Vout >= VCC || Vout <= 0) return -1;
  
  // Rumus: Rs = Rload * (Vcc - Vout) / Vout
  return RLOAD * ((VCC - Vout) / Vout);
}

float ppmFromRatio(float ratio, String gasType) {
  if (ratio <= 0 || R0_mics == 0) return -1;
  float ppm = 0.0;
  
  // Rumus regresi logaritmik berdasarkan datasheet MiCS-5524
  if (gasType == "CO")          ppm = pow(10, (log10(ratio) - 0.35) / -0.85);
  else if (gasType == "C2H5OH") ppm = pow(10, (log10(ratio) - 0.15) / -0.65);
  else if (gasType == "VOC")    ppm = pow(10, (log10(ratio) + 0.1) / -0.75);
  
  return (ppm >= 0 && ppm <= 5000) ? ppm : -1;
}

// ==================== SETUP PROGRAM ====================
void setup() {
  Serial.begin(9600);
  
  // Setup Pin Motor
  pinMode(DIR_KIPAS_1, OUTPUT); pinMode(DIR_KIPAS_2, OUTPUT); pinMode(PWM_KIPAS, OUTPUT);
  pinMode(DIR_POMPA_1, OUTPUT); pinMode(DIR_POMPA_2, OUTPUT); pinMode(PWM_POMPA, OUTPUT);
  stopAll();

  // Setup I2C Sensor GM-XXX
  Wire.begin();
  gas.begin(Wire, 0x08);

  // Kalibrasi R0 MiCS-5524 (Di udara bersih saat startup)
  Serial.println("Kalibrasi R0 MiCS-5524...");
  delay(2000);
  float Rs_air = calculateRs();
  if (Rs_air > 0) {
    R0_mics = Rs_air;
    Serial.print("✅ R0 Terukur: "); Serial.print(R0_mics/1000.0, 2); Serial.println(" kΩ");
  } else {
    Serial.println("⚠️ Gagal Kalibrasi, menggunakan Default: 100 kΩ");
  }

  // Koneksi WiFi
  Serial.print("Menghubungkan ke WiFi: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) { 
    Serial.print("."); 
    delay(500); 
  }
  Serial.println("\n✅ WiFi Connected!");
  Serial.print("IP Arduino: "); Serial.println(WiFi.localIP());
  Serial.print("Target Backend: "); Serial.print(RUST_IP); Serial.print(":"); Serial.println(RUST_PORT);
  
  Serial.println("E-NOSE ZIZU READY — Menunggu Perintah START_SAMPLING");
}

// ==================== LOOP UTAMA ====================
void loop() {
  // 1. Cek Perintah dari Serial/Backend (jika nanti dikembangkan 2 arah)
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n'); 
    cmd.trim();
    if (cmd == "START_SAMPLING") startSampling();
    else if (cmd == "STOP_SAMPLING") stopSampling();
  }

  // 2. Kirim Data ke Backend (Interval 250ms)
  if (millis() - lastSend >= 250) { 
    lastSend = millis(); 
    sendSensorData(); 
  }

  // 3. Jalankan Logika State Machine
  if (samplingActive) runFSM();
}

// ==================== LOGIKA STATE MACHINE ====================
void startSampling() {
  if (!samplingActive) {
    samplingActive = true;
    currentLevel = 0;
    changeState(PRE_COND);
    Serial.println("🚀 SAMPLING DIMULAI — MODE ZIZU (5 LEVEL)");
  }
}

void stopSampling() {
  samplingActive = false;
  currentLevel = 0;
  changeState(IDLE);
  stopAll();
  Serial.println("🛑 SAMPLING DIHENTIKAN");
}

void changeState(State s) {
  currentState = s;
  stateTime = millis();
  String names[] = {"IDLE","PRE-COND","RAMP_UP","HOLD","PURGE","RECOVERY","DONE"};
  Serial.println("FSM -> " + names[s] + " | Level " + String(currentLevel + 1));
}

void runFSM() {
  unsigned long elapsed = millis() - stateTime;
  
  switch (currentState) {
    case PRE_COND: 
      // Pemanasan: Kipas pelan, Pompa mati
      kipas(120); pompa(0); 
      if (elapsed >= T_PRECOND) changeState(RAMP_UP); 
      break;
      
    case RAMP_UP: 
      // Transisi naik: Kipas ramping naik sesuai level
      rampKipas(speeds[currentLevel]); pompa(0); 
      if (elapsed >= T_RAMP) changeState(HOLD); 
      break;
      
    case HOLD: 
      // Sampling Stabil (2 Menit): Kipas konstan, Pompa mati
      kipas(speeds[currentLevel]); pompa(0); 
      if (elapsed >= T_HOLD) changeState(PURGE); 
      break;
      
    case PURGE: 
      // Pembersihan (4 Menit): Kipas Max (Reverse/Buang), Pompa Max
      kipas(255, true); pompa(255); 
      if (elapsed >= T_PURGE) changeState(RECOVERY); 
      break;
      
    case RECOVERY: 
      // Istirahat (10 Detik): Semua mati
      stopAll(); 
      if (elapsed >= T_RECOVERY) {
        currentLevel++;
        if (currentLevel >= 5) { 
          changeState(DONE); 
          samplingActive = false; 
          Serial.println("🏁 SELESAI SEMUA 5 LEVEL!"); 
        } else {
          changeState(RAMP_UP);
        }
      } 
      break;
      
    case IDLE: 
    case DONE: 
      stopAll(); 
      break;
  }
}

// ==================== KIRIM DATA KE BACKEND ====================
void sendSensorData() {
  // 1. Baca GM-XXX (Sensor Digital)
  // Logic: Jika nilai > 30000 biasanya error/warming up, kita kasih -1.0
  float no2 = (gas.measure_NO2()    < 30000) ? gas.measure_NO2()    / 1000.0 : -1.0;
  float eth = (gas.measure_C2H5OH() < 30000) ? gas.measure_C2H5OH() / 1000.0 : -1.0;
  float voc = (gas.measure_VOC()    < 30000) ? gas.measure_VOC()    / 1000.0 : -1.0;
  float co  = (gas.measure_CO()     < 30000) ? gas.measure_CO()     / 1000.0 : -1.0;

  // 2. Baca MiCS-5524 (Sensor Analog)
  float Rs = calculateRs();
  float co_mics  = (Rs > 0) ? ppmFromRatio(Rs / R0_mics, "CO")     : -1.0;
  float eth_mics = (Rs > 0) ? ppmFromRatio(Rs / R0_mics, "C2H5OH") : -1.0;
  float voc_mics = (Rs > 0) ? ppmFromRatio(Rs / R0_mics, "VOC")    : -1.0;

  // 3. Format String Data (PROTOCOL: SENSOR:val,val,...)
  // Urutan HARUS sama dengan Backend Rust: no2, eth, voc, co, co_mics, eth_mics, voc_mics, state, level
  String data = "SENSOR:";
  data += String(no2,3) + "," + String(eth,3) + "," + String(voc,3) + "," + String(co,3) + ",";
  data += String(co_mics,3) + "," + String(eth_mics,3) + "," + String(voc_mics,3) + ",";
  data += String(currentState) + "," + String(currentLevel);

  // 4. Kirim via TCP
  if (client.connect(RUST_IP, RUST_PORT)) {
    client.print(data + "\n");
    client.stop(); // Close connection (Stateless/Short-lived connection)
  }
}