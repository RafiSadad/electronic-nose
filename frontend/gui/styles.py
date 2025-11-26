"""Application styling and themes (Cute Edition 🌸)"""

STYLESHEET = """
    QMainWindow {
        background-color: #FFF0F5;  /* Lavender Blush */
    }
    
    QWidget {
        background-color: #FFF0F5;
        color: #555555;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Group Box yang Cute */
    QGroupBox {
        background-color: white;
        color: #FF69B4; /* Hot Pink Text */
        border: 2px solid #FFB7B2;
        border-radius: 15px;
        margin-top: 15px;
        padding: 15px;
        font-weight: bold;
        font-size: 12px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
        background-color: white;
        border-radius: 5px;
        color: #FF69B4;
    }
    
    /* Tombol-tombol Gemoy */
    QPushButton {
        background-color: #FFB7B2; /* Pastel Red */
        color: white;
        border: none;
        border-radius: 12px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 12px;
    }
    
    QPushButton:hover {
        background-color: #FF9AA2;
        margin-top: -2px; /* Efek naik dikit pas di hover */
    }
    
    QPushButton:pressed {
        background-color: #E2F0CB;
        color: #555;
        margin-top: 2px;
    }
    
    QPushButton:disabled {
        background-color: #E0E0E0;
        color: #A0A0A0;
    }
    
    /* Tombol Start Spesial */
    QPushButton#startButton {
        background-color: #B5EAD7; /* Mint Green */
        color: #444;
    }
    
    QPushButton#startButton:hover {
        background-color: #A3E4D7;
    }
    
    /* Tombol Stop Spesial */
    QPushButton#stopButton {
        background-color: #FFDAC1; /* Peach */
        color: #444;
    }
    
    QPushButton#stopButton:hover {
        background-color: #FFCBA4;
    }
    
    /* Input Fields */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        border: 2px solid #E2F0CB;
        border-radius: 10px;
        padding: 8px;
        background-color: white;
        font-size: 12px;
        color: #555;
        selection-background-color: #FF9AA2;
    }
    
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #FF9AA2;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    /* Labels */
    QLabel {
        color: #666;
        font-size: 12px;
        font-weight: 500;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: white;
        color: #FF69B4;
        border-top: 2px solid #FFB7B2;
    }
    
    /* Tables */
    QTableWidget {
        background-color: white;
        gridline-color: #FFB7B2;
        border-radius: 10px;
        border: 1px solid #FFB7B2;
    }
    
    QHeaderView::section {
        background-color: #FFB7B2;
        color: white;
        padding: 8px;
        border: none;
        font-weight: bold;
    }
    
    QTabWidget::pane { 
        border: 2px solid #FFB7B2;
        border-radius: 10px;
        background-color: white;
        top: -2px; 
    }
    
    QTabBar::tab {
        background: #FFDAC1;
        border: 2px solid #FFDAC1;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 8px 12px;
        margin-right: 4px;
        color: #555;
    }
    
    QTabBar::tab:selected {
        background: white;
        border-color: #FFB7B2;
        color: #FF69B4;
        font-weight: bold;
    }
"""

# Status colors (Pastel Versions)
STATUS_COLORS = {
    'disconnected': (255, 154, 162),  # Pastel Red
    'connected': (181, 234, 215),     # Pastel Mint Green
    'sampling': (199, 206, 234),      # Pastel Periwinkle
    'error': (255, 218, 193)          # Pastel Peach
}