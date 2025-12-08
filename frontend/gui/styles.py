"""
Global Stylesheet & Color Palette (Nord Theme)
Agar tampilan aplikasi konsisten dan modern.
"""

# --- PALET WARNA (NORD THEME) ---
COLORS = {
    'background': '#ECEFF4',    # Light Grey (Background Utama)
    'surface':    '#FFFFFF',    # White (Panel/Card)
    'primary':    '#5E81AC',    # Blue (Tombol Utama)
    'secondary':  '#88C0D0',    # Cyan (Highlight)
    'text':       '#2E3440',    # Dark Grey (Teks Utama)
    'text_light': '#D8DEE9',    # Light Grey (Teks di Background Gelap)
    'success':    '#A3BE8C',    # Green (Connected)
    'warning':    '#EBCB8B',    # Yellow (Waiting)
    'danger':     '#BF616A',    # Red (Disconnected/Stop)
    'border':     '#D8DEE9',    # Border Color
}

# --- STATUS COLORS (Untuk Indikator Bulat) ---
STATUS_COLORS = {
    'connected':    COLORS['success'],
    'disconnected': COLORS['danger'],
    'sampling':     COLORS['primary'],
    'warning':      COLORS['warning']
}

# --- GLOBAL STYLESHEET (QSS) ---
STYLESHEET = f"""
    /* === GLOBAL SETTINGS === */
    QMainWindow {{
        background-color: {COLORS['background']};
    }}
    QWidget {{
        font-family: "Segoe UI";
        font-size: 14px;
        color: {COLORS['text']};
    }}

    /* === GROUP BOX (Panel Kotak) === */
    QGroupBox {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        margin-top: 10px; /* Space for title */
        padding-top: 15px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        left: 10px;
        color: {COLORS['primary']};
        font-weight: bold;
    }}

    /* === BUTTONS === */
    QPushButton {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['primary']};
        color: {COLORS['primary']};
        border-radius: 5px;
        padding: 5px 15px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLORS['primary']};
        color: {COLORS['surface']};
    }}
    QPushButton:pressed {{
        background-color: #4C566A; /* Darker click */
        color: {COLORS['surface']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['background']};
        border: 1px solid {COLORS['border']};
        color: #999;
    }}

    /* Tombol Khusus: Upload & Connect (Solid Color) */
    QPushButton#primaryBtn {{
        background-color: {COLORS['primary']};
        color: {COLORS['surface']};
        border: none;
    }}
    QPushButton#primaryBtn:hover {{
        background-color: {COLORS['secondary']};
    }}

    /* Tombol Start (Green) */
    QPushButton#startButton {{
        background-color: {COLORS['success']};
        color: {COLORS['text']};
        border: none;
    }}
    QPushButton#startButton:hover {{
        background-color: #8FBC8B; 
    }}

    /* Tombol Stop (Red) */
    QPushButton#stopButton {{
        background-color: {COLORS['danger']};
        color: {COLORS['surface']};
        border: none;
    }}
    QPushButton#stopButton:hover {{
        background-color: #A6545E;
    }}

    /* === INPUT FIELDS (LineEdit, ComboBox, SpinBox) === */
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 4px;
        selection-background-color: {COLORS['primary']};
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {COLORS['primary']};
    }}

    /* === TABLE WIDGET === */
    QTableWidget {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        gridline-color: {COLORS['border']};
        selection-background-color: {COLORS['secondary']};
        selection-color: {COLORS['text']};
    }}
    QHeaderView::section {{
        background-color: {COLORS['background']};
        padding: 5px;
        border: none;
        border-bottom: 2px solid {COLORS['border']};
        font-weight: bold;
        color: {COLORS['text']};
    }}

    /* === TAB WIDGET === */
    QTabWidget::pane {{ 
        border: 1px solid {COLORS['border']};
        background: {COLORS['surface']};
        border-radius: 5px;
    }}
    QTabBar::tab {{
        background: {COLORS['background']};
        border: 1px solid {COLORS['border']};
        padding: 8px 12px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }}
    QTabBar::tab:selected {{
        background: {COLORS['surface']};
        border-bottom-color: {COLORS['surface']}; /* Blend with pane */
        color: {COLORS['primary']};
        font-weight: bold;
    }}

    /* === SCROLL BAR (Modern Thin) === */
    QScrollBar:vertical {{
        border: none;
        background: {COLORS['background']};
        width: 8px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #BCC3D1;
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""