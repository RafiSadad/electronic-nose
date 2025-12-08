"""
Global Stylesheet (Floral/Cute Theme)
Theme: Pastel Pink, Soft White, & Floral Accents
"""

# PALET WARNA BUNGA:
# Background Utama: #FFF0F5 (Lavender Blush / Pink Pucat)
# Panel/Widget: #FFFFFF (White) dengan border Pink
# Teks Utama: #5D4037 (Coklat Kayu - lebih lembut dari hitam)
# Aksen Utama (Tombol): #FF80AB (Pink Azalea)
# Aksen Hover: #F50057 (Pink Mawar)
# Highlight/Selection: #FFC1E3 (Pink Pastel)

STYLESHEET = """
/* === GLOBAL WIDGET SETTINGS === */
QWidget {
    background-color: #FFF0F5; /* Latar belakang pink sangat muda */
    color: #5D4037;            /* Teks warna coklat tua (agar tidak terlalu tajam) */
    font-family: "Segoe UI", "Comic Sans MS", sans-serif; /* Font sedikit santai */
    font-size: 14px;
}

/* === MAIN WINDOW === */
QMainWindow {
    background-color: #FFE4E1; /* Misty Rose */
}

/* === GROUP BOX (Kontainer Panel) === */
QGroupBox {
    background-color: #FFFFFF;
    border: 2px solid #F8BBD0; /* Border Pink Lembut */
    border-radius: 15px;       /* Sudut sangat bulat (Cute) */
    margin-top: 25px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center; /* Judul di tengah */
    padding: 5px 15px;
    background-color: #FF80AB; /* Judul background pink cerah */
    color: #FFFFFF;            /* Teks judul putih */
    border-radius: 10px;
}

/* === BUTTONS (Tombol) === */
QPushButton {
    background-color: #FF80AB; /* Pink Azalea */
    color: #FFFFFF;
    border: none;
    border-radius: 12px;       /* Tombol bulat */
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #FF4081; /* Pink lebih tua saat hover */
    margin-top: 2px;           /* Efek tekan sedikit */
}
QPushButton:pressed {
    background-color: #C51162; /* Merah Mawar Gelap */
}
QPushButton:disabled {
    background-color: #E0E0E0;
    color: #9E9E9E;
}

/* === INPUT FIELDS === */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #FFFFFF;
    color: #5D4037;
    border: 2px solid #F48FB1; /* Border Pink */
    border-radius: 8px;
    padding: 5px;
    selection-background-color: #F06292;
}
QLineEdit:focus, QSpinBox:focus {
    border: 2px solid #E91E63; /* Border jadi pink tua saat diketik */
}

/* === TABLE WIDGET (Tabel Data) === */
QTableWidget {
    background-color: #FFFFFF;
    gridline-color: #F8BBD0;   /* Garis tabel pink lembut */
    border: 2px solid #F48FB1;
    border-radius: 10px;
    color: #5D4037;
}
QTableWidget::item {
    padding: 5px;
    border-bottom: 1px solid #FFF0F5;
}
QTableWidget::item:selected {
    background-color: #F8BBD0; /* Highlight baris warna pink susu */
    color: #880E4F;            /* Teks highlight merah marun */
}

/* Header Tabel */
QHeaderView::section {
    background-color: #FFC1E3; /* Header pink pastel */
    color: #880E4F;            /* Teks header gelap */
    padding: 6px;
    border: none;
    font-weight: bold;
    border-bottom: 2px solid #F06292;
}
QTableCornerButton::section {
    background-color: #FFC1E3;
    border: none;
}

/* === LABELS (Teks Biasa) === */
QLabel {
    color: #5D4037;
}

/* === SCROLL BARS (Agar tidak kaku) === */
QScrollBar:vertical {
    border: none;
    background: #FFF0F5;
    width: 12px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #F48FB1;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""