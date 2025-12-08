"""Custom widgets for the application (Floral Theme Compatible 🌸)"""

import serial.tools.list_ports # AMAN: Hanya untuk listing, bukan koneksi
import pyqtgraph as pg
import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QGroupBox, 
    QFrame, QDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QPixmap

from config.constants import (
    SAMPLE_TYPES, PLOT_COLORS, NUM_SENSORS, SENSOR_NAMES, MAX_PLOT_POINTS,
    DEFAULT_HOST, CMD_PORT, STATUS_COLORS
)

class StatusDot(QWidget):
    """Titik status berwarna"""
    def __init__(self, color=QColor("#BDBDBD"), parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(20, 20)
    
    def set_color(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 16, 16)

class StatusIndicator(QFrame):
    """Indikator status (Titik + Teks)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.dot = StatusDot()
        layout.addWidget(self.dot)
        
        self.label = QLabel("Disconnected")
        self.label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(self.label)
        layout.addStretch()
        
    def set_status(self, text: str, color_hex: str):
        self.label.setText(text)
        self.dot.set_color(QColor(color_hex))

class SensorPlot(pg.PlotWidget):
    """Widget Grafik"""
    def __init__(self, title: str = "Sensor Data", parent=None):
        super().__init__(parent)
        self.setTitle(title, color='#5D4037', size='12pt')
        self.setBackground('w') # Background putih agar clean
        self.showGrid(x=True, y=True, alpha=0.3)
        
        # Style Axis
        styles = {'color': '#5D4037', 'font-size': '10pt'}
        self.setLabel('left', 'Value (V)', **styles)
        self.setLabel('bottom', 'Time (s)', **styles)
        
        self.num_sensors = NUM_SENSORS
        self.plot_lines = {}
        self.addLegend()
        
        for i in range(self.num_sensors):
            color = PLOT_COLORS[i % len(PLOT_COLORS)]
            pen = pg.mkPen(color=color, width=3)
            name = SENSOR_NAMES[i]
            self.plot_lines[i] = self.plot([], [], pen=pen, name=name)
    
    def update_plot(self, time_val, sensor_vals):
        # Implementasi update sederhana (bisa dioptimasi dengan deque)
        # Di sini kita asumsikan MainWindow mengatur data buffer
        pass 
        # (MainWindow memanggil setData langsung ke plot_lines biasanya, 
        # tapi di struktur sebelumnya MainWindow mengelola data arrays.
        # Fungsi ini placeholder jika ingin logic plot ada di sini)

    def add_data_point(self, time_arr, data_dict):
        for i in range(self.num_sensors):
            self.plot_lines[i].setData(time_arr, data_dict[i])
    
    def clear_data(self):
        for i in range(self.num_sensors):
            self.plot_lines[i].setData([], [])

class ControlPanel(QGroupBox):
    """Panel Tombol (Start, Stop, Save, Clear)"""
    start_clicked = Signal()
    stop_clicked = Signal()
    save_clicked = Signal()
    clear_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("🌺 Controls", parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Inputs
        layout.addWidget(QLabel("Name:"))
        self.sample_input = QLineEdit()
        self.sample_input.setPlaceholderText("Nama Sampel...")
        layout.addWidget(self.sample_input)
        
        layout.addWidget(QLabel("Type:"))
        self.sample_type = QComboBox()
        self.sample_type.addItems(SAMPLE_TYPES)
        layout.addWidget(self.sample_type)
        
        # Buttons
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.clicked.connect(self.start_clicked.emit)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_clicked.emit)
        layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_clicked.emit)
        layout.addWidget(self.clear_btn)
        
        self.setLayout(layout)
    
    def enable_start(self, enabled=True): self.start_btn.setEnabled(enabled)
    def enable_stop(self, enabled=True): self.stop_btn.setEnabled(enabled)
    
    def get_sample_info(self):
        return {
            'name': self.sample_input.text() or "Unnamed",
            'type': self.sample_type.currentText(),
            'mode': "Auto FSM"
        }

class ConnectionPanel(QGroupBox):
    """Panel Koneksi Bridge"""
    connect_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("🔌 Connection", parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # IP Input
        layout.addWidget(QLabel("Backend IP:"), 0, 0)
        self.ip_input = QLineEdit(DEFAULT_HOST)
        layout.addWidget(self.ip_input, 0, 1)
        
        # Port Selector (COM)
        layout.addWidget(QLabel("Arduino Port:"), 1, 0)
        h_lay = QHBoxLayout()
        self.port_selector = QComboBox()
        self.refresh_ports()
        h_lay.addWidget(self.port_selector)
        
        ref_btn = QPushButton("↻")
        ref_btn.setFixedWidth(30)
        ref_btn.clicked.connect(self.refresh_ports)
        h_lay.addWidget(ref_btn)
        layout.addLayout(h_lay, 1, 1)
        
        # Status & Connect Button
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator, 2, 0)
        
        self.connect_btn = QPushButton("✨ Connect Bridge")
        self.connect_btn.clicked.connect(self.connect_clicked.emit)
        layout.addWidget(self.connect_btn, 2, 1)
        
        self.setLayout(layout)
        
    def refresh_ports(self):
        self.port_selector.clear()
        # AMAN: Hanya LISTING ports, tidak OPEN
        try:
            ports = serial.tools.list_ports.comports()
            names = [p.device for p in ports]
            self.port_selector.addItems(names if names else ["No Ports"])
        except:
            self.port_selector.addItem("Error Scanning")

    def get_connection_settings(self):
        return {
            'host': self.ip_input.text(),
            'serial_port': self.port_selector.currentText()
        }
    
    def set_status(self, text, color):
        self.status_indicator.set_status(text, color)

class GnuplotWidget(QDialog):
    """Popup Gambar Gnuplot"""
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualisasi GNUPLOT")
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        
        lbl = QLabel()
        pix = QPixmap(image_path)
        if not pix.isNull():
            lbl.setPixmap(pix.scaled(780, 580, Qt.KeepAspectRatio))
        else:
            lbl.setText("Gagal load gambar")
        
        scroll = QScrollArea()
        scroll.setWidget(lbl)
        layout.addWidget(scroll)