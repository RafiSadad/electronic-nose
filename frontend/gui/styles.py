"""
Global Stylesheet (Dark Theme) - FIXED CONTRAST
"""

# Warna Palette (Untuk referensi)
# Background Gelap: #1e1e1e (Deep Dark), #2b2b2b (Panel), #3d3d3d (Widget)
# Teks: #ffffff (White), #b0b0b0 (Light Gray)
# Aksen: #0078d4 (Blue), #d83b01 (Orange Red/Stop)

STYLESHEET = """
/* === GLOBAL WIDGET SETTINGS === */
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;  /* PENTING: Paksa semua teks jadi putih */
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}

/* === MAIN WINDOW & PANELS === */
QMainWindow {
    background-color: #1e1e1e;
}

/* === GROUP BOX (Kontainer Panel) === */
QGroupBox {
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    margin-top: 24px;
    font-weight: bold;
    color: #ffffff; /* Judul GroupBox Putih */
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    left: 10px;
    color: #4cc2ff; /* Warna judul cyan muda agar kontras */
}

/* === BUTTONS (Tombol) === */
QPushButton {
    background-color: #3d3d3d;
    color: #ffffff;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #4d4d4d;
    border: 1px solid #0078d4;
}
QPushButton:pressed {
    background-color: #0078d4;
    color: white;
}
QPushButton:disabled {
    background-color: #252525;
    color: #707070;
    border: 1px solid #303030;
}

/* === INPUT FIELDS (QLineEdit, QSpinBox, dll) === */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #1e1e1e; /* Input field lebih gelap */
    color: #ffffff;            /* Teks input putih */
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 4px;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #0078d4;
}

/* === TABLE WIDGET (Ini yang paling sering bermasalah) === */
QTableWidget {
    background-color: #1e1e1e;
    color: #ffffff;            /* Isi tabel putih */
    gridline-color: #353535;
    border: 1px solid #353535;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
}
QTableWidget::item {
    padding: 5px;
}
QTableWidget::item:selected {
    background-color: #0078d4;
}

/* Header Tabel */
QHeaderView::section {
    background-color: #3d3d3d;
    color: #ffffff;
    padding: 4px;
    border: 1px solid #2b2b2b;
    font-weight: bold;
}
QTableCornerButton::section {
    background-color: #3d3d3d;
    border: 1px solid #2b2b2b;
}

/* === LABELS === */
QLabel {
    color: #ffffff; /* Label normal putih */
}

/* === COMBO BOX DROP DOWN === */
QComboBox QAbstractItemView {
    background-color: #2b2b2b;
    color: #ffffff;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
    border: 1px solid #3d3d3d;
}

/* === SCROLL BARS (Opsional: Mempercantik Scrollbar) === */
QScrollBar:vertical {
    border: none;
    background: #1e1e1e;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #4d4d4d;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""