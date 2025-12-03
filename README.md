# 👃 Electronic Nose (E-Nose) App

**Dibuat oleh:**
* Rafi Sadad Ar-Rabbani (2042241105)
* Reksa Putra A (2042241126)
* Luthfiana Alzenayu Gyonina (2042241117)

---

**Proyek Mata Kuliah Sistem Pengolahan Sinyal**
Departemen Teknik Instrumentasi, Institut Teknologi Sepuluh Nopember (ITS).

Aplikasi Desktop GUI yang terintegrasi penuh untuk sistem Electronic Nose. Mendukung akuisisi data sensor gas secara *real-time*, penyimpanan database *time-series*, visualisasi sinyal (Gnuplot), dan ekspor dataset untuk Machine Learning (Edge Impulse).

---

## 📋 Arsitektur Sistem

Sistem ini terdiri dari 4 layanan yang bekerja secara paralel:

1.  **Frontend (Python/Qt):** Antarmuka pengguna untuk kontrol alat dan visualisasi.
2.  **Backend (Rust):** Server TCP performa tinggi yang menjembatani Arduino dan Database.
3.  **Database (InfluxDB):** Menyimpan histori data sensor secara permanen.
4.  **Embedded (Arduino Uno R4):** Membaca 7 sensor gas dan mengontrol aktuator (Fan/Pompa).

---

## 🛠️ Prerequisites (Prasyarat)

Pastikan software berikut sudah terinstall sebelum menjalankan program:

1.  **Docker Desktop** (Wajib untuk Database)
    * [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
2.  **Rust Toolchain** (Untuk menjalankan Backend)
    * [Download Rustup](https://www.rust-lang.org/tools/install)
3.  **Python 3.8+** (Untuk menjalankan Frontend)
    * [Download Python](https://www.python.org/downloads/) *(Centang "Add to PATH" saat install)*
4.  **Gnuplot** (Wajib untuk fitur visualisasi grafik akhir)
    * [Download Gnuplot](https://sourceforge.net/projects/gnuplot/)
    * *⚠️ PENTING: Saat instalasi, centang opsi **"Add application directory to your PATH environment variable"**.*

---

## ⚙️ Setup & Installation (Satu Kali Saja)

Ikuti langkah ini saat pertama kali setup proyek di komputer baru.

### 1. Setup Database (InfluxDB)
Buka terminal di folder root proyek:
```bash
docker-compose up -d
````

*Tunggu hingga status container "Running" di Docker Desktop.*

### 2\. Setup Backend (Rust)

```bash
cd backend
cargo build
```

*Tunggu proses download dependencies selesai (bisa memakan waktu beberapa menit).*

### 3\. Setup Frontend (Python Virtual Environment)

Ini adalah langkah krusial agar library Python tidak konflik dengan sistem.

**Windows:**

```bash
cd frontend
python -m venv venv           # Membuat virtual environment
venv\Scripts\activate         # Mengaktifkan venv (Prompt akan berubah jadi (venv))
pip install -r requirements.txt # Install library yang dibutuhkan
```

**Linux / Mac:**

```bash
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4\. Setup Arduino

1.  Buka `embedded/main.ino` dengan Arduino IDE.
2.  Cari baris `const char* RUST_IP = "..."`
3.  Ganti dengan IPv4 Laptop Anda (Cek di CMD dengan ketik `ipconfig`).
4.  Upload ke board Arduino Uno R4 WiFi.

-----

## 🚀 Cara Menjalankan (Setiap Kali Pakai)

Ikuti urutan ini agar sistem berjalan lancar. Gunakan 3 Terminal berbeda.

### Terminal 1: Backend

```bash
cd backend
cargo run
```

*Tunggu pesan: `Listening for Arduino on port 8081...`*

### Terminal 2: Frontend

```bash
cd frontend
# Pastikan venv aktif dulu!
venv\Scripts\activate   # (Windows)
# source venv/bin/activate # (Mac/Linux)

python main.py
```

### Hardware: Arduino

Hubungkan ke listrik/USB. Pastikan terhubung ke WiFi yang sama.

-----

## 🎮 Panduan Penggunaan Aplikasi

### A. Sampling Data

1.  Isi **Sample Name** (contoh: "Kopi Gayo").
2.  Pilih **Jenis Sampel**.
3.  Klik tombol **▶ Start**.
4.  Sistem akan menjalankan fase otomatis: *Pre-condition -\> Ramp Up -\> Hold -\> Purge*.
5.  Grafik di layar akan bergerak secara *real-time*.

### B. Menyimpan & Visualisasi (Output)

Klik tombol **💾 Save Data** setelah sampling selesai.

  * **Output:** File `.csv` tersimpan di folder `frontend/data/`.
  * **Visualisasi:** Akan muncul pop-up **"Buka grafik di GNUPLOT?"**. Pilih **Yes** untuk melihat grafik kualitas tinggi di dalam aplikasi.

### C. Ekspor ke Edge Impulse (AI/ML)

Untuk training Machine Learning:

1.  Klik tombol **🚀 Upload to Edge Impulse**.
2.  Aplikasi membuat file `.json` (format khusus Edge Impulse).
3.  Browser otomatis terbuka ke halaman **Edge Impulse Studio**.
4.  Upload file `.json` tersebut ke sana.

-----

## 📊 Monitoring Database (InfluxDB)

Data juga tersimpan permanen di database. Cara cek manual:

1.  Buka Browser: [http://localhost:8086](https://www.google.com/search?q=http://localhost:8086)
2.  Login:
      * **User:** `admin`
      * **Pass:** `adminpassword`
3.  Masuk menu **Data Explorer** (icon grafik).
4.  Pilih Bucket `electronic_nose` -\> Measurement `sensor_reading`.
5.  Klik **Submit** untuk melihat grafik historis semua sensor.

-----

## ❓ Troubleshooting

**1. Error: "ModuleNotFoundError" saat jalankan python main.py**

  * **Penyebab:** Virtual environment belum aktif.
  * **Solusi:** Jalankan `venv\Scripts\activate` dulu sebelum run python.

**2. Error: "gnuplot not found"**

  * **Penyebab:** Gnuplot belum install atau belum masuk PATH.
  * **Solusi:** Install ulang Gnuplot, pastikan centang "Add to PATH". Restart terminal.

**3. InfluxDB Gagal Login / Error 401**

  * **Penyebab:** Setup awal Docker korup.
  * **Solusi:** Reset total database dengan perintah:
    ```bash
    docker-compose down -v
    docker-compose up -d
    ```

**4. Grafik Real-time Diam**

  * **Penyebab:** Arduino tidak kirim data.
  * **Solusi:** Cek Serial Monitor Arduino. Pastikan muncul "Connected to Backend". Cek apakah IP Laptop berubah (kalau pindah WiFi, IP sering ganti). Update IP di `main.ino`.

<!-- end list -->

```
```
