"""Custom widgets for the application (Bridge Mode Compatible 🌸)"""

import serial.tools.list_ports
import pyqtgraph as pg
import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QGroupBox, 
    QFrame, QDialog, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QPixmap, QIcon

# Import Constants
from config.constants import (
    SAMPLE_TYPES, PLOT_COLORS, NUM_SENSORS, SENSOR_NAMES, MAX_PLOT_POINTS,
    DEFAULT_HOST, CMD_PORT, STATUS_COLORS
)

class StatusDot(QWidget):
    """Hanya menggambar titik status berwarna"""
    def __init__(self, color=QColor("#F44336"), parent=None):
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
    """Indikator status dengan Layout Rapi (Titik + Teks)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(0)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)
        
        self.dot = StatusDot()
        layout.addWidget(self.dot)
        
        self.label = QLabel("Disconnected")
        self.label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.label.setStyleSheet("color: #555555; border: none;")
        layout.addWidget(self.label)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def set_status(self, text: str, color_hex: str):
        self.label.setText(text)
        self.dot.set_color(QColor(color_hex))

class SensorPlot(pg.PlotWidget):
    """Custom PyQtGraph plotting widget"""
    
    def __init__(self, title: str = "Sensor Data", parent=None):
        super().__init__(parent)
        
        self.plot_title = title
        self.num_sensors = NUM_SENSORS
        self.max_points = MAX_PLOT_POINTS 
        
        self.setTitle(self.plot_title, color='#555555', size='12pt')
        self.setBackground('w')
        self.showGrid(x=True, y=True, alpha=0.2)
        
        styles = {'color': '#888', 'font-size': '10pt'}
        self.setLabel('left', 'Sensor Value (Raw)', **styles)
        self.setLabel('bottom', 'Time (seconds)', **styles)
        
        self.time_data = np.array([])
        self.sensor_data = {i: np.array([]) for i in range(self.num_sensors)}
        self.plot_lines = {}
        
        self.addLegend()
        
        for i in range(self.num_sensors):
            color = PLOT_COLORS[i % len(PLOT_COLORS)]
            pen = pg.mkPen(color=color, width=3)
            name = SENSOR_NAMES[i] if i < len(SENSOR_NAMES) else f"Sensor {i+1}"
            self.plot_lines[i] = self.plot([], [], pen=pen, name=name)
    
    def add_data_point(self, time: float, sensor_values: list):
        self.time_data = np.append(self.time_data, time)
        for i, value in enumerate(sensor_values[:self.num_sensors]):
            self.sensor_data[i] = np.append(self.sensor_data[i], value)
        
        for i in range(self.num_sensors):
            self.plot_lines[i].setData(self.time_data, self.sensor_data[i])
    
    def clear_data(self):
        self.time_data = np.array([])
        for i in range(self.num_sensors):
            self.sensor_data[i] = np.array([])
            self.plot_lines[i].setData([], [])

class ControlPanel(QGroupBox):
    """Control panel with Start, Stop, Save, and Clear buttons"""
    
    start_clicked = Signal()
    stop_clicked = Signal()
    save_clicked = Signal()
    clear_clicked = Signal()  # <--- Signal Baru
    
    def __init__(self, parent=None):
        super().__init__("🌺 Sampling Control", parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(10)
        
        # Sample Name
        lbl_name = QLabel("Sample Name:")
        lbl_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lbl_name)
        
        self.sample_input = QLineEdit()
        self.sample_input.setPlaceholderText("e.g. Percobaan 1")
        self.sample_input.setMinimumWidth(150)
        self.sample_input.setFixedHeight(30)
        layout.addWidget(self.sample_input)
        
        # Flower Type
        lbl_type = QLabel("Flower Type:")
        lbl_type.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lbl_type)
        
        self.sample_type = QComboBox()
        self.sample_type.addItems(SAMPLE_TYPES)
        self.sample_type.setMinimumWidth(160)
        self.sample_type.setFixedHeight(30)
        layout.addWidget(self.sample_type)
        
        # Info Mode
        layout.addSpacing(10)
        mode_label = QLabel("Mode: <b>Auto (FSM)</b>")
        mode_label.setStyleSheet("color: #FF69B4; background: #FFF0F5; padding: 5px 10px; border-radius: 5px;")
        mode_label.setFixedHeight(30)
        layout.addWidget(mode_label)
        layout.addSpacing(10)
        
        # Buttons
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setMinimumHeight(30)
        self.start_btn.clicked.connect(self.start_clicked.emit)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setMinimumHeight(30)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setMinimumHeight(30)
        self.save_btn.clicked.connect(self.save_clicked.emit)
        layout.addWidget(self.save_btn)

        # --- TOMBOL CLEAR (BARU) ---
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setMinimumHeight(30)
        self.clear_btn.clicked.connect(self.clear_clicked.emit)
        layout.addWidget(self.clear_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def enable_start(self, enabled: bool = True):
        self.start_btn.setEnabled(enabled)
    
    def enable_stop(self, enabled: bool = True):
        self.stop_btn.setEnabled(enabled)
    
    def get_sample_info(self) -> dict:
        return {
            'name': self.sample_input.text() or "Unnamed Sample",
            'type': self.sample_type.currentText(),
            'mode': "Auto (FSM)" 
        }

class ConnectionPanel(QGroupBox):
    """Connection settings panel"""
    
    connect_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("🔌 Bridge Connection Setup", parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout()
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(15)
        
        lbl_ip = QLabel("📡 Backend IP:")
        lbl_ip.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lbl_ip, 0, 0)
        
        self.ip_input = QLineEdit()
        self.ip_input.setText(DEFAULT_HOST)
        self.ip_input.setPlaceholderText("127.0.0.1")
        self.ip_input.setFixedWidth(200)
        self.ip_input.setFixedHeight(30)
        layout.addWidget(self.ip_input, 0, 1)
        
        lbl_port = QLabel("🔌 Arduino Port:")
        lbl_port.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lbl_port, 1, 0)
        
        usb_layout = QHBoxLayout()
        usb_layout.setContentsMargins(0,0,0,0)
        
        self.port_selector = QComboBox()
        self.port_selector.setFixedWidth(150)
        self.port_selector.setFixedHeight(30)
        self.refresh_ports() 
        usb_layout.addWidget(self.port_selector)
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        usb_layout.addWidget(self.refresh_btn)
        
        usb_layout.addStretch()
        layout.addLayout(usb_layout, 1, 1)
        
        bottom_container = QHBoxLayout()
        bottom_container.setContentsMargins(0, 10, 0, 0)
        
        lbl_status = QLabel("Status:")
        lbl_status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bottom_container.addWidget(lbl_status)
        
        self.status_indicator = StatusIndicator()
        bottom_container.addWidget(self.status_indicator)
        
        bottom_container.addStretch()
        
        self.connect_btn = QPushButton("✨ Connect Bridge")
        self.connect_btn.setFixedWidth(160)
        self.connect_btn.setMinimumHeight(35)
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.clicked.connect(self.connect_clicked.emit)
        bottom_container.addWidget(self.connect_btn)
        
        layout.addLayout(bottom_container, 2, 0, 1, 2)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        
        self.setLayout(layout)
    
    def get_available_ports(self) -> list:
        try:
            ports = serial.tools.list_ports.comports()
            port_names = [port.device for port in ports]
            return port_names if port_names else ["No Ports"]
        except:
            return ["Error Scanning"]
            
    def refresh_ports(self):
        self.port_selector.clear()
        self.port_selector.addItems(self.get_available_ports())
    
    def get_connection_settings(self) -> dict:
        return {
            'host': self.ip_input.text().strip(),
            'port': CMD_PORT, 
            'serial_port': self.port_selector.currentText(),
            'baud_rate': 9600 
        }
    
    def set_status(self, status_text: str, color_hex: str):
        self.status_indicator.set_status(status_text, color_hex)

class GnuplotWidget(QDialog):
    """Widget pop-up untuk menampilkan hasil render GNUPLOT"""
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualisasi GNUPLOT")
        self.resize(1100, 700)
        
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("Gagal memuat gambar GNUPLOT")
            
        scroll.setWidget(self.image_label)
        layout.addWidget(scroll)
        self.setLayout(layout)