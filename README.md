# 👃 Electronic Nose (E-Nose) App

**Dibuat oleh:**
* Rafi Sadad Ar-Rabbani (2042241105)
* Reksa Putra A (2042241126)
* Luthfiana Alzenayu Gyonina (2042241117)

---

**Proyek Mata Kuliah Sistem Pengolahan Sinyal**
Departemen Teknik Instrumentasi, Institut Teknologi Sepuluh Nopember (ITS).

Aplikasi ini digunakan untuk visualisasi dan pengolahan data sensor gas (*electronic nose*) berbasis Arduino Uno R4 WiFi. Aplikasi dilengkapi dengan integrasi **GNUPLOT** untuk visualisasi sinyal dan **Edge Impulse** untuk Machine Learning.

---

## 📋 Fungsi & Fitur Utama

Sistem ini terdiri dari 4 komponen utama yang saling terhubung:
1.  **Embedded (Arduino Uno R4 WiFi):** Membaca 7 parameter sensor gas (MQ/MICS) dan mengontrol aktuator (pompa/fan).
2.  **Backend (Rust):** Server performa tinggi (TCP) untuk komunikasi data dua arah.
3.  **Frontend (Python/Qt):** GUI Desktop untuk kontrol sampling, visualisasi *real-time*, dan ekspor data.
4.  **Database (InfluxDB):** Penyimpanan data *time-series* jangka panjang.

---

## 🛠️ Prerequisites (Prasyarat)

Pastikan software berikut sudah terinstall:
1.  **Docker Desktop** (Wajib untuk Database)
2.  **Rust Toolchain** (Untuk Backend)
3.  **Python 3.8+** (Untuk Frontend)
4.  **Gnuplot** (Wajib untuk visualisasi grafik akhir)
    * *Windows:* Download dari [SourceForge](https://sourceforge.net/projects/gnuplot/). Saat install, **WAJIB** centang *"Add to PATH"*.

---

## 🚀 Cara Menjalankan (Quick Start)

**Langkah 1: Nyalakan Database**
```bash
docker-compose up -d
````

**Langkah 2: Jalankan Backend**

```bash
cd backend
cargo run
```

**Langkah 3: Jalankan Frontend GUI**

```bash
cd frontend
python main.py
```

*(Pastikan Arduino sudah menyala dan terhubung ke WiFi yang sama dengan Laptop)*

-----

## 🎮 Cara Penggunaan & Output

### A. Sampling Data

1.  Isi **Sample Name** (contoh: "Kopi Gayo") dan pilih **Jenis Bunga**.
2.  Klik **Start Sampling**.
3.  Grafik *real-time* akan muncul, dan motor/pompa pada alat akan bekerja sesuai siklus *Pre-cond, Ramp, Hold, Purge*.
4.  Klik **Stop** jika proses pengambilan data selesai.

### B. Menyimpan & Visualisasi (Output)

Klik tombol **💾 Save Data** untuk menyimpan hasil sampling. Aplikasi akan melakukan dua hal:

1.  **Menyimpan File CSV:** Data mentah disimpan ke folder `data/` dengan format `.csv`.
2.  **Visualisasi GNUPLOT Otomatis:**
      * Aplikasi akan menanyakan: *"Buka grafik di GNUPLOT?"*.
      * Jika **Yes**, grafik respons sensor yang rapi (format PNG) akan langsung muncul di dalam jendela aplikasi.
      * Grafik ini wajib disertakan dalam Laporan EAS.

-----

## ☁️ Integrasi Edge Impulse

Aplikasi ini mendukung ekspor data khusus untuk platform Machine Learning **Edge Impulse**.

**Cara Upload:**

1.  Lakukan sampling data seperti biasa.
2.  Klik tombol **🚀 Upload to Edge Impulse**.
3.  Aplikasi akan otomatis:
      * Membuat file **JSON** (bukan CSV) yang sesuai dengan standar *Data Acquisition Format* Edge Impulse.
      * Menampilkan lokasi file JSON tersebut.
      * Membuka browser otomatis ke halaman **Edge Impulse Studio**.
4.  Di browser (halaman *Upload Data*), pilih file JSON yang baru saja dibuat, lalu klik **Upload**.
5.  Data grafik akan langsung muncul di Edge Impulse tanpa perlu konfigurasi kolom manual.

-----

## ❓ Troubleshooting Umum

  * **Error: `gnuplot not found`**
      * Pastikan Gnuplot sudah diinstall dan opsi *"Add to PATH"* dicentang. Coba restart VS Code/Terminal.
  * **Browser tidak terbuka saat klik Edge Impulse:**
      * Cek koneksi internet. File JSON tetap tersimpan di folder `data/`, Anda bisa upload manual ke [studio.edgeimpulse.com](https://studio.edgeimpulse.com).
  * **Grafik Real-time diam:**
      * Cek apakah Arduino terhubung ke WiFi (lihat Serial Monitor Arduino).
      * Pastikan IP di kode Arduino (`main.ino`) sama dengan IP Laptop.

<!-- end list -->

```

Di video berikut ini Anda dapat melihat bagaimana cara menghubungkan perangkat kustom ke Edge Impulse menggunakan data forwarding yang konsepnya mirip dengan ekspor CSV/JSON [Data Collection to Edge Impulse](https://www.youtube.com/watch?v=rszoQsMIIAI).

Video ini relevan karena mendemonstrasikan alur kerja pengumpulan data sensor (mirip dengan E-Nose Anda) dan cara mengunggahnya ke Edge Impulse untuk analisis lebih lanjut.


http://googleusercontent.com/youtube_content/0
```
