# Electronic Nose App


***

### Dibuat oleh:

- Rafi Sadad Ar-Rabbani (2042241105)
- Reksa Putra A (2042241126)
- Luthfiana Alzenayu Gyonina (2042241117)

***

**Ini adalah proyek mata kuliah Sistem Pengolahan Sinyal di Departemen Teknik Instrumentasi ITS.**
Aplikasi ini digunakan untuk visualisasi dan pengolahan data sensor gas (electronic nose).
_Berikut adalah panduan instalasi dan menjalankan aplikasi dari nol._

Tentu, ini adalah draft **README.md** yang lengkap, terstruktur, dan disesuaikan dengan arsitektur sistem IoT (Arduino + Rust + Python + InfluxDB) yang ada di file-file kamu.

Kamu bisa copy-paste ini langsung ke file `README.md` di root folder project kamu.

-----

# 👃 Electronic Nose (E-Nose) System

Sistem Electronic Nose berbasis IoT yang terdistribusi untuk akuisisi, pengolahan, penyimpanan, dan visualisasi data sensor gas secara *real-time*.

## 📋 Fungsi & Fitur Utama

Sistem ini terdiri dari 4 komponen utama yang saling terhubung:

1.  **Embedded (Arduino Uno R4 WiFi):** Membaca sensor gas (MQ/MICS) dan mengontrol aktuator (pompa/fan), lalu mengirim data mentah via TCP.
2.  **Backend (Rust):** Server performa tinggi yang menerima data dari Arduino, menyimpannya ke database, dan mem-broadcast data ke Frontend.
3.  **Database (InfluxDB):** Time-series database untuk menyimpan history data sensor secara efisien.
4.  **Frontend (Python/Qt):** Aplikasi Desktop GUI untuk memvisualisasikan grafik secara *real-time*, mengontrol sampling, dan mengekspor data (CSV).

-----

## 🛠️ Prerequisites (Prasyarat)

Sebelum memulai, pastikan software berikut sudah terinstall di komputer kamu:

1.  **Docker Desktop** (Wajib untuk Database)
      * Download: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2.  **Rust Toolchain** (Untuk Backend)
      * Windows: Download `rustup-init.exe` dari [rust-lang.org](https://www.rust-lang.org/tools/install)
3.  **Python 3.8+** (Untuk Frontend)
      * Pastikan centang "Add Python to PATH" saat install.
4.  **Arduino IDE** (Untuk upload kode ke mikrokontroler)
      * Install Board Package: `Arduino UNO R4 Boards`.

-----

## ⚙️ Setup & Installation

Ikuti langkah-langkah ini secara berurutan:

### 1\. Setup Database (InfluxDB)

Kita menggunakan Docker agar tidak perlu install manual.

```bash
# Di terminal (root folder project)
docker-compose up -d
```

  * **Verifikasi:** Buka browser ke `http://localhost:8086`.
  * **Login Default:** Username: `admin`, Password: `adminpassword` (Sesuai `docker-compose.yml`).

### 2\. Setup Backend (Rust)

Backend bertugas menjembatani Arduino dan Python.

```bash
cd backend
cargo build
# Tunggu sampai proses download dependencies dan compile selesai
```

### 3\. Setup Frontend (Python)

Disarankan menggunakan virtual environment.

```bash
cd frontend

# Buat virtual environment
python -m venv venv

# Aktifkan venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4\. Setup Embedded (Arduino)

**⚠️ PENTING:** Konfigurasi IP Address.

1.  Buka Command Prompt (Windows), ketik `ipconfig`. Catat **IPv4 Address** komputer kamu (misal: `192.168.1.37`).
2.  Buka file `embedded/main.ino` di Arduino IDE.
3.  Edit baris berikut:
    ```cpp
    const char* ssid = "NAMA_WIFI_KAMU";
    const char* pass = "PASSWORD_WIFI_KAMU";
    const char* RUST_IP = "192.168.1.37"; // <--- GANTI DENGAN IP KOMPUTER KAMU
    ```
4.  Upload sketch ke Arduino Uno R4 WiFi.

-----

## 🚀 How to Run (Cara Menjalankan)

Nyalakan sistem dengan urutan berikut agar koneksi berhasil:

### Langkah 1: Jalankan Database

Pastikan container Docker sudah berjalan (biasanya otomatis jika sudah `up -d`, cek di aplikasi Docker Desktop).

### Langkah 2: Jalankan Backend Server

Buka terminal baru:

```bash
cd backend
cargo run
```

*Tunggu sampai muncul pesan: "Listening for Arduino on port 8081" & "Listening for Frontend on port 8082".*

### Langkah 3: Nyalakan Arduino

Reset atau colokkan power Arduino.

  * Lihat Serial Monitor di Arduino IDE.
  * Tunggu sampai muncul: `WiFi Connected!`

### Langkah 4: Jalankan Frontend GUI

Buka terminal baru (pastikan ada di folder `frontend` dan venv aktif):

```bash
cd frontend
python main.py
```

-----

## 🎮 Cara Menggunakan Aplikasi

1.  **Koneksi:**
      * Di panel kiri ("Connection Settings"), isi **Backend IP** dengan `127.0.0.1` (karena GUI dan Backend di satu PC).
      * Pilih Source: **Backend (Rust)**.
      * Klik **Connect**. Status harusnya berubah jadi hijau (Connected).
2.  **Sampling:**
      * Isi **Sample Name** (contoh: "Kopi Gayo").
      * Klik **Start Sampling**.
      * Grafik akan bergerak real-time dan motor di alat akan menyala sesuai fase (Pre-cond, Ramp, Hold, dll).
3.  **Simpan:**
      * Setelah selesai, klik **Save Data** untuk menyimpan ke CSV/JSON.

-----

## ❓ Troubleshooting

  * **Error: `The system cannot find the file specified` saat `docker-compose up`:**
      * Pastikan aplikasi **Docker Desktop** sudah dibuka dan statusnya "Engine Running".
  * **Arduino tidak connect ke Backend:**
      * Matikan **Firewall** Windows sebentar atau Allow Access untuk program Backend saat muncul pop-up.
      * Pastikan IP di `main.ino` sama persis dengan IP komputer server.
      * Pastikan Laptop dan Arduino connect ke WiFi yang sama.
  * **Python Error `Module not found`:**
      * Pastikan sudah mengaktifkan virtual environment (`venv\Scripts\activate`) sebelum `python main.py`.
