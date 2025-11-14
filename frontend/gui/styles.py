"""Application styling and themes"""

STYLESHEET = """
    QMainWindow {
        background-color: #f5f5f5;
    }
    
    QWidget {
        background-color: #f5f5f5;
        color: #333333;
    }
    
    QGroupBox {
        color: #333333;
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }
    
    QPushButton {
        background-color: #0084ff;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 11px;
    }
    
    QPushButton:hover {
        background-color: #0073e6;
    }
    
    QPushButton:pressed {
        background-color: #0059b3;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    
    QPushButton#startButton {
        background-color: #27ae60;
    }
    
    QPushButton#startButton:hover {
        background-color: #229954;
    }
    
    QPushButton#stopButton {
        background-color: #e74c3c;
    }
    
    QPushButton#stopButton:hover {
        background-color: #c0392b;
    }
    
    QLineEdit {
        border: 1px solid #bbb;
        border-radius: 4px;
        padding: 6px;
        background-color: white;
        font-size: 11px;
    }
    
    QLineEdit:focus {
        border: 2px solid #0084ff;
    }
    
    QComboBox {
        border: 1px solid #bbb;
        border-radius: 4px;
        padding: 6px;
        background-color: white;
        font-size: 11px;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QLabel {
        color: #333333;
        font-size: 11px;
    }
    
    QLabel#statusLabel {
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 3px;
        background-color: #ffcccc;
        color: #990000;
    }
    
    QLabel#statusConnected {
        background-color: #ccffcc;
        color: #009900;
    }
    
    QLabel#statusSampling {
        background-color: #ccffffcc;
        color: #0099cc;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    
    QSpinBox, QDoubleSpinBox {
        border: 1px solid #bbb;
        border-radius: 4px;
        padding: 4px;
        background-color: white;
    }
    
    QCheckBox {
        spacing: 5px;
    }
    
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
    
    QStatusBar {
        background-color: #e8e8e8;
        color: #333333;
        border-top: 1px solid #ccc;
    }
    
    QMessageBox QLabel {
        color: #333333;
    }
    
    QHeaderView::section {
        background-color: #0084ff;
        color: white;
        padding: 5px;
        border: none;
    }
    
    QTableWidget {
        gridline-color: #ddd;
        background-color: white;
    }
    
    QTableWidget::item {
        padding: 4px;
    }
    
    QTableWidget::item:selected {
        background-color: #0084ff;
        color: white;
    }
"""

# Status colors (RGB tuples)
STATUS_COLORS = {
    'disconnected': (255, 102, 102),  # Red
    'connected': (102, 255, 102),     # Green
    'sampling': (102, 178, 255),      # Blue
    'error': (255, 153, 51)           # Orange
}
