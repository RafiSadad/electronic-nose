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

***

## 🖥️ Persyaratan Sistem

- Windows 10/11, macOS, atau Linux
- Internet untuk download tools


## 🧩 Software yang Dibutuhkan

1. **Python** (versi 3.8 atau lebih baru)
2. **Git** (opsional namun sangat dianjurkan)
3. **Visual Studio Code** (VS Code) (opsional, untuk pengeditan \& pengembangan)

***

## ⬇️ Cara Instalasi

### 1. Download \& Install Python

- Download dari [python.org](https://www.python.org/downloads/)
- Saat instalasi, **ceklist "Add Python to PATH"**
- Setelah install, cek di terminal:

```bash
python --version
```


### 2. (Opsional) Download \& Install Git

- Download dari [git-scm.com](https://git-scm.com/)
- Install dan klik Next hingga selesai
- Cek:

```bash
git --version
```


### 3. Clone Project (atau Download ZIP)

Via Git:

```bash
git clone <ALAMAT_REPOSITORY>
cd electronic-nose-gui
```

Atau unzip file jika download manual.

***

### 4. Masuk ke Folder Frontend

```bash
cd frontend
```


***

### 5. Buat \& Aktifkan Virtual Environment

#### Windows (Command Prompt atau PowerShell):

```bash
python -m venv venv
venv\Scripts\activate
```


#### macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Jika aktif, akan muncul tanda `(venv)` di awal command line.

***

### 6. Install Dependencies yang Dibutuhkan

Jalankan:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

_**Jika dependencies belum ada file `requirements.txt`, install manual:**_

```bash
pip install PySide6 pyqtgraph pyserial numpy
```


***

## 🚦 Cara Menjalankan Aplikasi

Masih di folder `frontend` dan venv aktif:

```bash
python main.py
```

- Aplikasi GUI akan muncul dengan tampilan visualisasi data sensor gas.
- Untuk testing, bisa pakai _Simulation Mode_ tanpa Arduino.

***

## ❓ Troubleshooting / FAQ

- **Python tidak dikenali:** Ulangi instalasi Python dan pastikan centang "Add to PATH"
- **pip tidak ada:** Gunakan `python -m ensurepip`
- **Error library:** Gunakan ulang `pip install -r requirements.txt`
- **GUI tidak muncul:** Pastikan semua sesuai langkah di atas, dan ada `(venv)` di terminal.

***

## 💻 Keterangan Tambahan

- Jika ingin pengembangan lanjut, gunakan VS Code (`code .` dari folder project)
- Folder `backend` disiapkan untuk integrasi Rust ke depannya

***

**_Deskripsi serta detail fitur aplikasi akan diupdate mengikuti progress pengembangan._**

***


[^1][^2][^3][^4][^5]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://www.pythonguis.com/tutorials/pyside6-plotting-pyqtgraph/

[^2]: https://www.geeksforgeeks.org/python/create-virtual-environment-using-venv-python/

[^3]: https://www.freecodecamp.org/news/how-to-structure-your-readme-file/

[^4]: https://stackoverflow.com/questions/68006243/how-to-install-pyside6

[^5]: https://gist.github.com/MichaelCurrin/3a4d14ba1763b4d6a1884f56a01412b7?permalink_comment_id=4166464

[^6]: https://realpython.com/readme-python-project/

[^7]: https://www.makeareadme.com

[^8]: https://github.com/othneildrew/Best-README-Template

[^9]: https://packaging.python.org/guides/making-a-pypi-friendly-readme/

[^10]: https://www.pyopensci.org/python-package-guide/tutorials/add-readme.html

[^11]: https://www.pythonguis.com/tutorials/pyside6-embed-pyqtgraph-custom-widgets/

[^12]: https://www.youtube.com/watch?v=aoEMJJLUdJM

[^13]: https://git.ifas.rwth-aachen.de/templates/ifas-python-template/-/blob/master/README.md

[^14]: https://pyqtgraph.readthedocs.io/en/latest/getting_started/how_to_use.html

[^15]: https://realpython.com/python-virtual-environments-a-primer/

[^16]: https://www.youtube.com/watch?v=12trn2NKw5I

[^17]: https://dev.to/sumonta056/github-readme-template-for-personal-projects-3lka

[^18]: https://www.youtube.com/watch?v=i-utZN_NP6c

[^19]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

[^20]: https://www.pyqtgraph.org

