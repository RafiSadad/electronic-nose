// ===================================================================================
// E-NOSE ZIZU — FINAL BIDIRECTIONAL (UNO R4 WiFi)
// FITUR: 
// 1. Kontrol Start/Stop dari Aplikasi Python (via WiFi)
// 2. Logika ZIZU: Hold 2 Menit | Purge 4 Menit | 5 Level Otomatis
// 3. Koneksi Stabil (Persistent TCP Connection)
// ===================================================================================

#include <WiFiS3.h>
#include <Wire.h>
#include "Multichannel_Gas_GMXXX.h"

// ==================== 1. KONFIGURASI JARINGAN (SUDAH SESUAI) ====================
const char* ssid     = "Start-up";       // WiFi 2.4GHz
const char* pass     = "Warkop123";      // Password
const char* RUST_IP  = "192.168.1.91";   // IP Laptop Kamu
const int   RUST_PORT = 8081;            // Port Backend

WiFiClient client;
bool isConnected = false; // Status koneksi ke Backend

// ==================== 2. KONFIGURASI SENSOR ====================
GAS_GMXXX<TwoWire> gas;

// MiCS-5524
#define MICS_PIN    A1
#define RLOAD       820.0
#define VCC         5.0
float R0_mics = 100000.0;

// ==================== 3. KONFIGURASI MOTOR ====================
const int PWM_KIPAS   = 10;
const int DIR_KIPAS_1 = 12;
const int DIR_KIPAS_2 = 13;

const int PWM_POMPA   = 11;
const int DIR_POMPA_1 = 8;
const int DIR_POMPA_2 = 9;

// ==================== 4. STATE MACHINE ====================
enum State { IDLE, PRE_COND, RAMP_UP, HOLD, PURGE, RECOVERY, DONE };
State currentState = IDLE;

unsigned long stateTime = 0;
int currentLevel = 0;
const int speeds[5] = {51, 102, 153, 204, 255};
bool samplingActive = false;

// ==================== 5. TIMING (ZIZU VERSION) ====================
const unsigned long T_PRECOND  = 15000;   // 15 Detik
const unsigned long T_RAMP     = 3000;    // 3 Detik
const unsigned long T_HOLD     = 120000;  // 2 MENIT
const unsigned long T_PURGE    = 240000;  // 4 MENIT
const unsigned long T_RECOVERY = 10000;   // 10 Detik
unsigned long lastSend = 0;

// ==================== FUNGSI HARDWARE ====================
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
  if (cur < target) cur += 15;
  else if (cur > target) cur -= 15;
  cur = constrain(cur, 0, 255);
  kipas(cur);
}

// ==================== RUMUS SENSOR ====================
float calculateRs() {
  int raw = analogRead(MICS_PIN);
  if (raw < 10) return -1;
  float Vout = raw * (VCC / 1023.0);
  if (Vout >= VCC || Vout <= 0) return -1;
  return RLOAD * ((VCC - Vout) / Vout);
}

float ppmFromRatio(float ratio, String gasType) {
  if (ratio <= 0 || R0_mics == 0) return -1;
  float ppm = 0.0;
  if (gasType == "CO")          ppm = pow(10, (log10(ratio) - 0.35) / -0.85);
  else if (gasType == "C2H5OH") ppm = pow(10, (log10(ratio) - 0.15) / -0.65);
  else if (gasType == "VOC")    ppm = pow(10, (log10(ratio) + 0.1) / -0.75);
  return (ppm >= 0 && ppm <= 5000) ? ppm : -1;
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(9600);
  
  // Init Pin
  pinMode(DIR_KIPAS_1, OUTPUT); pinMode(DIR_KIPAS_2, OUTPUT); pinMode(PWM_KIPAS, OUTPUT);
  pinMode(DIR_POMPA_1, OUTPUT); pinMode(DIR_POMPA_2, OUTPUT); pinMode(PWM_POMPA, OUTPUT);
  stopAll();

  // Init Sensor
  Wire.begin();
  gas.begin(Wire, 0x08);

  // Kalibrasi Awal
  delay(2000);
  float Rs_air = calculateRs();
  if (Rs_air > 0) {
    R0_mics = Rs_air;
    Serial.print("Calibrated R0: "); Serial.println(R0_mics);
  }

  // Koneksi WiFi
  Serial.print("Connecting to WiFi: "); Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) { 
    Serial.print("."); 
    delay(500); 
  }
  Serial.println("\n✅ WiFi Connected!");
  Serial.print("Backend Target: "); Serial.print(RUST_IP); Serial.print(":"); Serial.println(RUST_PORT);
}

// ==================== MAIN LOOP (2 ARAH) ====================
void loop() {
  // 1. Jaga Koneksi Tetap Hidup (Persistent)
  if (!client.connected()) {
    isConnected = false;
    // Coba reconnect setiap 2 detik jika putus
    static unsigned long lastReconnect = 0;
    if (millis() - lastReconnect > 2000) {
      lastReconnect = millis();
      Serial.println("Connecting to Backend...");
      if (client.connect(RUST_IP, RUST_PORT)) {
        isConnected = true;
        Serial.println("✅ Connected to Backend! Ready for Command.");
      }
    }
  } else {
    isConnected = true;
  }

  // 2. BACA PERINTAH DARI APLIKASI (VIA WIFI)
  if (client.available()) {
    String cmd = client.readStringUntil('\n');
    cmd.trim();
    Serial.print("📥 Command Received: "); Serial.println(cmd);
    
    if (cmd == "START_SAMPLING") startSampling();
    else if (cmd == "STOP_SAMPLING") stopSampling();
  }
  
  // Cek juga dari Serial Monitor (Backup manual)
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "START_SAMPLING") startSampling();
    else if (cmd == "STOP_SAMPLING") stopSampling();
  }

  // 3. KIRIM DATA SENSOR (Setiap 250ms)
  if (millis() - lastSend >= 250) { 
    lastSend = millis(); 
    sendSensorData(); 
  }

  // 4. JALANKAN MESIN UTAMA
  if (samplingActive) runFSM();
}

// ==================== LOGIKA KONTROL ====================
void startSampling() {
  if (!samplingActive) {
    samplingActive = true;
    currentLevel = 0;
    changeState(PRE_COND);
    Serial.println("🚀 STATUS: SAMPLING STARTED");
  }
}

void stopSampling() {
  samplingActive = false;
  currentLevel = 0;
  changeState(IDLE);
  stopAll();
  Serial.println("🛑 STATUS: SAMPLING STOPPED");
}

void changeState(State s) {
  currentState = s;
  stateTime = millis();
  String names[] = {"IDLE","PRE-COND","RAMP_UP","HOLD","PURGE","RECOVERY","DONE"};
  // Kirim log status ke Serial Monitor juga
  Serial.println("FSM -> " + names[s] + " | Level: " + String(currentLevel + 1));
}

void runFSM() {
  unsigned long e = millis() - stateTime;
  
  switch (currentState) {
    case PRE_COND: 
      kipas(120); pompa(0); 
      if (e >= T_PRECOND) changeState(RAMP_UP); 
      break;
      
    case RAMP_UP: 
      rampKipas(speeds[currentLevel]); pompa(0); 
      if (e >= T_RAMP) changeState(HOLD); 
      break;
      
    case HOLD: 
      kipas(speeds[currentLevel]); pompa(0); 
      if (e >= T_HOLD) changeState(PURGE); 
      break;
      
    case PURGE: 
      kipas(255, true); pompa(255); 
      if (e >= T_PURGE) changeState(RECOVERY); 
      break;
      
    case RECOVERY: 
      stopAll(); 
      if (e >= T_RECOVERY) {
        currentLevel++;
        if (currentLevel >= 5) { 
          changeState(DONE); 
          samplingActive = false; 
          Serial.println("🏁 ALL LEVELS DONE"); 
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

// ==================== PENGIRIMAN DATA ====================
void sendSensorData() {
  // Baca Data
  float no2 = (gas.measure_NO2()    < 30000) ? gas.measure_NO2()    / 1000.0 : -1.0;
  float eth = (gas.measure_C2H5OH() < 30000) ? gas.measure_C2H5OH() / 1000.0 : -1.0;
  float voc = (gas.measure_VOC()    < 30000) ? gas.measure_VOC()    / 1000.0 : -1.0;
  float co  = (gas.measure_CO()     < 30000) ? gas.measure_CO()     / 1000.0 : -1.0;

  float Rs = calculateRs();
  float co_mics  = (Rs > 0) ? ppmFromRatio(Rs / R0_mics, "CO")     : -1.0;
  float eth_mics = (Rs > 0) ? ppmFromRatio(Rs / R0_mics, "C2H5OH") : -1.0;
  float voc_mics = (Rs > 0) ? ppmFromRatio(Rs / R0_mics, "VOC")    : -1.0;

  // Format String
  String data = "SENSOR:";
  data += String(no2,3) + "," + String(eth,3) + "," + String(voc,3) + "," + String(co,3) + ",";
  data += String(co_mics,3) + "," + String(eth_mics,3) + "," + String(voc_mics,3) + ",";
  data += String(currentState) + "," + String(currentLevel);

  // Kirim jika Terhubung (Tanpa menutup koneksi!)
  if (client.connected()) {
    client.print(data + "\n");
  }
}