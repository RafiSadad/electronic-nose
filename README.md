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

## 🚀 Cara Menjalankan (Step-by-Step)

Ikuti urutan ini agar sistem berjalan lancar:

### Langkah 1: Nyalakan Database (InfluxDB)
Buka terminal di folder root proyek, lalu jalankan:
```bash
docker-compose up -d
````

*Tunggu hingga status Docker "Running".*

### Langkah 2: Jalankan Backend Server

Buka terminal baru, masuk ke folder backend:

```bash
cd backend
cargo run
```

*Tunggu sampai muncul pesan: `Listening for Arduino on port 8081...`*

### Langkah 3: Jalankan Frontend GUI

Buka terminal baru, masuk ke folder frontend:

```bash
cd frontend
python main.py
```

### Langkah 4: Nyalakan Alat (Arduino)

Hubungkan Arduino ke Power/USB. Pastikan Arduino terhubung ke WiFi yang sama dengan laptop.
*Lihat Serial Monitor Arduino untuk memastikan koneksi: `Connected to Backend!`*

-----

## 📊 Cara Monitoring Database (InfluxDB)

Data yang diambil oleh sensor tersimpan secara otomatis di InfluxDB. Berikut cara melihatnya:

1.  **Buka Dashboard:**
    Buka browser dan akses: [http://localhost:8086](https://www.google.com/search?q=http://localhost:8086)

2.  **Login:**
    Gunakan kredensial default berikut (sesuai `docker-compose.yml`):

      * **Username:** `admin`
      * **Password:** `adminpassword`

3.  **Melihat Data Masuk (Data Explorer):**

      * Klik menu **Data Explorer** (ikon grafik di sidebar kiri).
      * Di bagian **"From"**, pilih bucket: `electronic_nose`.
      * Di bagian **"Filter"**, klik `_measurement` -\> `sensor_reading`.
      * Pilih field yang ingin dilihat (misal: `no2`, `eth`, `voc`).
      * Klik tombol **Submit** di pojok kanan atas.
      * Grafik data historis akan muncul di layar.

-----

## 🎮 Panduan Penggunaan Aplikasi

### 1\. Sampling Data

  * Isi **Sample Name** (contoh: "Kopi Gayo").
  * Pilih **Jenis Sampel**.
  * Klik tombol **▶ Start**.
  * Sistem akan menjalankan fase otomatis: *Pre-condition -\> Ramp Up -\> Hold -\> Purge*.
  * Grafik di layar akan bergerak secara *real-time*.

### 2\. Menyimpan Data (CSV + Gnuplot)

Jika sampling selesai, klik tombol **💾 Save Data**.

  * Aplikasi akan menyimpan file `.csv` di folder `frontend/data/`.
  * Akan muncul *pop-up*: **"Buka grafik di GNUPLOT?"**.
  * Pilih **Yes** untuk menampilkan grafik respons sinyal berkualitas tinggi (PNG) langsung di dalam aplikasi.

### 3\. Ekspor ke Edge Impulse (Machine Learning)

Untuk kebutuhan *training* AI:

  * Klik tombol **🚀 Upload to Edge Impulse**.
  * Aplikasi akan membuat file `.json` khusus format Edge Impulse.
  * Browser akan otomatis terbuka ke halaman **Edge Impulse Studio**.
  * Upload file `.json` yang baru dibuat ke sana.

-----

## ❓ Troubleshooting

**Masalah: InfluxDB Error / Gagal Login**

  * Jika login gagal atau bucket tidak ditemukan, kemungkinan setup awal Docker belum sempurna.
  * **Solusi:** Reset database dengan perintah:
    ```bash
    docker-compose down -v
    docker-compose up -d
    ```

**Masalah: Grafik Gnuplot Tidak Muncul**

  * Pastikan Gnuplot sudah terinstall.
  * Cek apakah perintah `gnuplot --version` bisa jalan di terminal. Jika tidak, install ulang Gnuplot dan pastikan centang **"Add to PATH"**.
     * Pastikan Gnuplot sudah diinstall dan opsi *"Add to PATH"* dicentang. Coba restart VS Code/Terminal.
     * 
**Masalah: Arduino Tidak Konek**

  * Pastikan IP Address laptop sudah benar dimasukkan ke file `main.ino`.
  * Matikan Firewall Windows sementara jika koneksi backend terblokir.


  * **Browser tidak terbuka saat klik Edge Impulse:**
      * Cek koneksi internet. File JSON tetap tersimpan di folder `data/`, Anda bisa upload manual ke [studio.edgeimpulse.com](https://studio.edgeimpulse.com).
      
  * **Grafik Real-time diam:**
      * Cek apakah Arduino terhubung ke WiFi (lihat Serial Monitor Arduino).
      * Pastikan IP di kode Arduino (`main.ino`) sama dengan IP Laptop.

<!-- end list -->
