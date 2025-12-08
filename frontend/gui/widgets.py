"""Custom widgets for the application (Bridge Mode Compatible 🌸)"""

import serial.tools.list_ports
import pyqtgraph as pg
import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QCheckBox, QGroupBox, 
    QFrame, QDialog, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QPixmap, QIcon

# Import Constants (Pastikan constants.py sudah Anda update sesuai instruksi sebelumnya)
from config.constants import (
    SAMPLE_TYPES, PLOT_COLORS, NUM_SENSORS, SENSOR_NAMES, MAX_PLOT_POINTS,
    DEFAULT_HOST, CMD_PORT, STATUS_COLORS
)

class StatusIndicator(QFrame):
    """Custom status indicator widget (Cute Dot)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_color = QColor(255, 154, 162) # Pastel Red Default
        self.status_text = "Disconnected"
        self.setMinimumWidth(150)
        self.setMinimumHeight(35)
        
    def set_status(self, status_text: str, color_hex: str):
        """Update status with text and color hex code"""
        self.status_text = status_text
        self.status_color = QColor(color_hex)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw cute circle
        painter.setBrush(QBrush(self.status_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 8, 16, 16)
        
        # Draw text
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#555555"))
        painter.drawText(25, 0, 150, 32, Qt.AlignVCenter | Qt.AlignLeft, self.status_text)


class SensorPlot(pg.PlotWidget):
    """Custom PyQtGraph plotting widget (Clean Look)"""
    
    def __init__(self, title: str = "Sensor Data", parent=None):
        super().__init__(parent)
        
        self.plot_title = title
        self.num_sensors = NUM_SENSORS
        self.max_points = MAX_PLOT_POINTS 
        
        # Setup plot style
        self.setTitle(self.plot_title, color='#555555', size='12pt')
        self.setBackground('w')
        self.showGrid(x=True, y=True, alpha=0.2)
        
        # Axis styling
        styles = {'color': '#888', 'font-size': '10pt'}
        self.setLabel('left', 'Sensor Value (Raw)', **styles)
        self.setLabel('bottom', 'Time (seconds)', **styles)
        
        # Data storage
        self.time_data = np.array([])
        self.sensor_data = {i: np.array([]) for i in range(self.num_sensors)}
        self.plot_lines = {}
        
        self.addLegend()
        
        # Create plot lines using Constants Colors
        for i in range(self.num_sensors):
            color = PLOT_COLORS[i % len(PLOT_COLORS)]
            pen = pg.mkPen(color=color, width=3)
            
            # Ambil nama sensor dari constants jika ada
            name = SENSOR_NAMES[i] if i < len(SENSOR_NAMES) else f"Sensor {i+1}"
            
            self.plot_lines[i] = self.plot([], [], pen=pen, name=name)
    
    def add_data_point(self, time: float, sensor_values: list):
        self.time_data = np.append(self.time_data, time)
        
        # Update data per sensor
        for i, value in enumerate(sensor_values[:self.num_sensors]):
            self.sensor_data[i] = np.append(self.sensor_data[i], value)
        
        # Update grafik lines
        for i in range(self.num_sensors):
            self.plot_lines[i].setData(self.time_data, self.sensor_data[i])
    
    def clear_data(self):
        self.time_data = np.array([])
        for i in range(self.num_sensors):
            self.sensor_data[i] = np.array([])
            self.plot_lines[i].setData([], [])


class ControlPanel(QGroupBox):
    """Control panel with flower sampling controls"""
    
    start_clicked = Signal()
    stop_clicked = Signal()
    save_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("🌺 Sampling Control", parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Sample name input
        layout.addWidget(QLabel("Sample Name:"))
        self.sample_input = QLineEdit()
        self.sample_input.setPlaceholderText("e.g. Percobaan 1")
        self.sample_input.setMinimumWidth(150)
        layout.addWidget(self.sample_input)
        
        # Sample type dropdown (BUNGA EDITION)
        layout.addWidget(QLabel("Flower Type:"))
        self.sample_type = QComboBox()
        self.sample_type.addItems(SAMPLE_TYPES)
        self.sample_type.setMinimumWidth(160)
        layout.addWidget(self.sample_type)
        
        # Label Info Mode Otomatis
        mode_label = QLabel("Mode: <b>Auto 30 min (FSM)</b>")
        mode_label.setStyleSheet("color: #FF69B4; background: #FFF0F5; padding: 5px; border-radius: 5px;")
        layout.addWidget(mode_label)
        
        # Buttons
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_clicked.emit)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_clicked.emit)
        layout.addWidget(self.save_btn)
        
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
    """Connection settings panel (Bridge Mode) - Updated"""
    
    connect_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("🔌 Bridge Connection Setup", parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout()
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(15)
        
        # --- Row 1: Backend IP ---
        layout.addWidget(QLabel("📡 Backend IP:"), 0, 0)
        
        self.ip_input = QLineEdit()
        self.ip_input.setText(DEFAULT_HOST)
        self.ip_input.setPlaceholderText("127.0.0.1")
        self.ip_input.setToolTip("IP tempat Backend Rust berjalan")
        self.ip_input.setFixedWidth(180)
        layout.addWidget(self.ip_input, 0, 1)
        
        # --- Row 2: Arduino Port (Bridge) ---
        layout.addWidget(QLabel("🔌 Arduino Port:"), 1, 0)
        
        usb_layout = QHBoxLayout()
        usb_layout.setContentsMargins(0,0,0,0)
        
        self.port_selector = QComboBox()
        self.port_selector.setFixedWidth(130)
        self.port_selector.setToolTip("Port ini akan dibuka oleh Rust, bukan Python")
        self.refresh_ports() # Auto scan
        usb_layout.addWidget(self.port_selector)
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.setToolTip("Refresh Serial Ports")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        usb_layout.addWidget(self.refresh_btn)
        
        usb_layout.addStretch()
        layout.addLayout(usb_layout, 1, 1)
        
        # --- Row 3: Status & Action ---
        bottom_container = QHBoxLayout()
        bottom_container.setContentsMargins(0, 5, 0, 0)
        
        # Status Label
        bottom_container.addWidget(QLabel("Status:"))
        self.status_indicator = StatusIndicator()
        bottom_container.addWidget(self.status_indicator)
        
        bottom_container.addStretch()
        
        # Connect Button
        self.connect_btn = QPushButton("✨ Connect Bridge")
        self.connect_btn.setFixedWidth(140)
        self.connect_btn.setMinimumHeight(35)
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.clicked.connect(self.connect_clicked.emit)
        bottom_container.addWidget(self.connect_btn)
        
        layout.addLayout(bottom_container, 2, 0, 1, 2)
        
        self.setLayout(layout)
    
    def get_available_ports(self) -> list:
        try:
            ports = serial.tools.list_ports.comports()
            # Kembalikan nama device saja (misal: "COM3" atau "/dev/ttyUSB0")
            port_names = [port.device for port in ports]
            return port_names if port_names else ["No Ports"]
        except:
            return ["Error Scanning"]
            
    def refresh_ports(self):
        self.port_selector.clear()
        self.port_selector.addItems(self.get_available_ports())
    
    def get_connection_settings(self) -> dict:
        """Mengembalikan setting untuk main_window"""
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
        
        # Area Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Label untuk gambar
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Load gambar
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("Gagal memuat gambar GNUPLOT")
            
        scroll.setWidget(self.image_label)
        layout.addWidget(scroll)
        
        self.setLayout(layout)