/*
 * HARDWARE UNIT TEST - E-NOSE ZIZU
 * --------------------------------
 * Gunakan kode ini untuk memverifikasi wiring dan kesehatan komponen
 * sebelum menjalankan program utama (Main Logic).
 * * CARA PAKAI:
 * 1. Upload Sketch.
 * 2. Buka Serial Monitor (Baudrate 9600).
 * 3. Ketik perintah menu (1, 2, 3, atau 4) lalu tekan ENTER.
 */

#include <Wire.h>
#include "Multichannel_Gas_GMXXX.h"

// ==================== DEFINISI PIN (Sesuai Kode Utama) ====================
// Sensor
GAS_GMXXX<TwoWire> gas;
#define MICS_PIN    A1
#define VCC         5.0

// Motor Kipas (Fan)
const int PWM_KIPAS   = 6;
const int DIR_KIPAS_1 = 9;
const int DIR_KIPAS_2 = 10;

// Motor Pompa (Pump)
const int PWM_POMPA   = 5;
const int DIR_POMPA_1 = 7;
const int DIR_POMPA_2 = 8;

void setup() {
  Serial.begin(9600);
  while (!Serial); // Tunggu Serial Monitor terbuka

  Serial.println("\n\n========================================");
  Serial.println("🛠️  E-NOSE HARDWARE DIAGNOSTIC TOOL");
  Serial.println("========================================");

  // 1. Setup Pin Motor
  pinMode(DIR_KIPAS_1, OUTPUT); 
  pinMode(DIR_KIPAS_2, OUTPUT); 
  pinMode(PWM_KIPAS, OUTPUT);
  
  pinMode(DIR_POMPA_1, OUTPUT); 
  pinMode(DIR_POMPA_2, OUTPUT); 
  pinMode(PWM_POMPA, OUTPUT);
  
  stopAll();
  Serial.println("✅ Pin Motor Dikonfigurasi.");

  // 2. Setup I2C GM-XXX
  Wire.begin();
  // Coba inisialisasi sensor gas
  Serial.print("⏳ Menghubungkan ke GM-XXX (0x08)... ");
  gas.begin(Wire, 0x08); 
  Serial.println("OK"); // Asumsi library tidak memblokir jika gagal, kita cek data nanti

  printMenu();
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    
    // Abaikan karakter newline/enter
    if (cmd == '\n' || cmd == '\r') return;

    Serial.println("\n👉 Perintah Diterima: " + String(cmd));

    switch (cmd) {
      case '1': testKipas(); break;
      case '2': testPompa(); break;
      case '3': testSensorGMXXX(); break;
      case '4': testSensorMiCS(); break;
      case 'h': printMenu(); break;
      default: Serial.println("❌ Perintah tidak dikenal. Ketik 'h' untuk menu."); break;
    }
    
    // Kembalikan menu setelah test selesai
    Serial.println("\n✅ Test Selesai.");
    printMenu();
  }
}

// ==================== FUNGSI TEST ====================

void printMenu() {
  Serial.println("\n--- MENU DIAGNOSTIK ---");
  Serial.println("[1] Test KIPAS (Maju 3s -> Stop -> Mundur 3s)");
  Serial.println("[2] Test POMPA (Hisap 3s -> Stop -> Buang 3s)");
  Serial.println("[3] Baca Sensor GM-XXX (Sekali baca)");
  Serial.println("[4] Baca Sensor MiCS-5524 (Sekali baca)");
  Serial.println("-----------------------");
  Serial.print("Pilih menu: ");
}

void stopAll() {
  analogWrite(PWM_KIPAS, 0);
  analogWrite(PWM_POMPA, 0);
  digitalWrite(DIR_KIPAS_1, LOW);
  digitalWrite(DIR_KIPAS_2, LOW);
  digitalWrite(DIR_POMPA_1, LOW);
  digitalWrite(DIR_POMPA_2, LOW);
}

void testKipas() {
  Serial.println("🌀 [TEST KIPAS]");
  
  // Arah NORMAL (Misal: Hisap/Masuk)
  Serial.println("   ➡ Arah MAJU (Normal)...");
  digitalWrite(DIR_KIPAS_1, HIGH);
  digitalWrite(DIR_KIPAS_2, LOW);
  analogWrite(PWM_KIPAS, 200); // Speed medium-high
  delay(3000);
  
  stopAll();
  Serial.println("   ⏹ Stop 1 detik...");
  delay(1000);

  // Arah REVERSE (Misal: Buang/Purge)
  Serial.println("   ⬅ Arah MUNDUR (Purge/Buang)...");
  digitalWrite(DIR_KIPAS_1, LOW);
  digitalWrite(DIR_KIPAS_2, HIGH);
  analogWrite(PWM_KIPAS, 200);
  delay(3000);

  stopAll();
  Serial.println("   ✅ Kipas Berhenti.");
}

void testPompa() {
  Serial.println("💧 [TEST POMPA]");
  
  // Arah NORMAL (Hisap ke chamber)
  Serial.println("   ➡ Arah MAJU (Hisap)...");
  digitalWrite(DIR_POMPA_1, HIGH);
  digitalWrite(DIR_POMPA_2, LOW);
  analogWrite(PWM_POMPA, 255); // Full speed
  delay(3000);
  
  stopAll();
  Serial.println("   ⏹ Stop 1 detik...");
  delay(1000);

  // Arah REVERSE (Buang dari chamber - PENTING UNTUK PURGE)
  Serial.println("   ⬅ Arah MUNDUR (Purge/Buang)...");
  digitalWrite(DIR_POMPA_1, LOW);
  digitalWrite(DIR_POMPA_2, HIGH);
  analogWrite(PWM_POMPA, 255);
  delay(3000);

  stopAll();
  Serial.println("   ✅ Pompa Berhenti.");
}

void testSensorGMXXX() {
  Serial.println("📊 [TEST SENSOR GM-XXX]");
  
  // Baca raw values
  uint32_t no2 = gas.measure_NO2();
  uint32_t eth = gas.measure_C2H5OH();
  uint32_t voc = gas.measure_VOC();
  uint32_t co  = gas.measure_CO();

  Serial.print("   NO2 Raw: "); Serial.println(no2);
  Serial.print("   ETH Raw: "); Serial.println(eth);
  Serial.print("   VOC Raw: "); Serial.println(voc);
  Serial.print("   CO  Raw: "); Serial.println(co);

  if (no2 == 0 && eth == 0 && voc == 0 && co == 0) {
    Serial.println("   ⚠️ PERINGATAN: Semua data 0. Cek kabel I2C (SDA/SCL)!");
  } else {
    Serial.println("   ✅ Data I2C diterima.");
  }
}

void testSensorMiCS() {
  Serial.println("👃 [TEST SENSOR MiCS-5524]");
  
  int raw = analogRead(MICS_PIN);
  float voltage = raw * (VCC / 1023.0);
  
  Serial.print("   Pin: A1 | Raw ADC: "); Serial.print(raw);
  Serial.print(" | Voltage: "); Serial.print(voltage); Serial.println(" V");

  if (raw < 10) {
    Serial.println("   ⚠️ Nilai sangat rendah. Sensor mungkin belum terpasang atau warming up.");
  } else if (raw > 1000) {
    Serial.println("   ⚠️ Nilai saturasi (Max). Cek short circuit.");
  } else {
    Serial.println("   ✅ Pembacaan Analog Normal.");
  }
}