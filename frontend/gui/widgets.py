"""Custom widgets for the application"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QGroupBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

import pyqtgraph as pg
import numpy as np

class StatusIndicator(QFrame):
    """Custom status indicator widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_color = QColor(255, 102, 102)
        self.status_text = "Disconnected"
        
    def set_status(self, status_text: str, color_rgb: tuple):
        """Update status with text and color"""
        self.status_text = status_text
        self.status_color = QColor(*color_rgb)
        self.update()
        
    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QBrush
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle
        painter.setBrush(QBrush(self.status_color))
        painter.drawEllipse(5, 5, 20, 20)
        
        # Draw text
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(30, 8, 200, 20, Qt.AlignVCenter, self.status_text)


class SensorPlot(pg.PlotWidget):
    """Custom PyQtGraph plotting widget for sensor data"""
    
    def __init__(self, title: str = "Sensor Data", parent=None):
        super().__init__(parent)
        
        self.plot_title = title
        self.num_sensors = 4
        self.max_points = 500
        
        # Setup plot
        self.setLabel('left', 'Sensor Value (Raw)')
        self.setLabel('bottom', 'Time (seconds)')
        self.setTitle(self.plot_title)
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setBackground('w')
        
        # Data storage
        self.time_data = np.array([])
        self.sensor_data = {i: np.array([]) for i in range(self.num_sensors)}
        self.plot_lines = {}
        
        # Create plot lines
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        for i in range(self.num_sensors):
            pen = pg.mkPen(color=colors[i], width=2)
            self.plot_lines[i] = self.plot([], [], pen=pen, name=f"Sensor {i+1}")
    
    def add_data_point(self, time: float, sensor_values: list):
        """Add new data point(s) to plot"""
        self.time_data = np.append(self.time_data, time)
        
        for i, value in enumerate(sensor_values[:self.num_sensors]):
            self.sensor_data[i] = np.append(self.sensor_data[i], value)
        
        # Keep only last max_points
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            for i in range(self.num_sensors):
                self.sensor_data[i] = self.sensor_data[i][-self.max_points:]
        
        # Update plots
        for i in range(self.num_sensors):
            self.plot_lines[i].setData(self.time_data, self.sensor_data[i])
    
    def clear_data(self):
        """Clear all plot data"""
        self.time_data = np.array([])
        for i in range(self.num_sensors):
            self.sensor_data[i] = np.array([])
            self.plot_lines[i].setData([], [])


class ControlPanel(QGroupBox):
    """Control panel with sampling controls"""
    
    start_clicked = Signal()
    stop_clicked = Signal()
    save_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Sampling Control", parent)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Sample name input
        layout.addWidget(QLabel("Sample Name:"))
        self.sample_input = QLineEdit()
        self.sample_input.setPlaceholderText("e.g., Coffee Arabica")
        self.sample_input.setMaximumWidth(200)
        layout.addWidget(self.sample_input)
        
        # Sample type dropdown
        layout.addWidget(QLabel("Sample Type:"))
        self.sample_type = QComboBox()
        self.sample_type.addItems([
            "Kopi Arabika", "Kopi Robusta", "Teh Hijau", "Teh Hitam",
            "Tembakau Kering", "Bunga Melati", "Jeruk", "Lainnya"
        ])
        self.sample_type.setMaximumWidth(150)
        layout.addWidget(self.sample_type)
        
        # Duration input
        layout.addWidget(QLabel("Duration (s):"))
        self.duration_input = QSpinBox()
        self.duration_input.setValue(30)
        self.duration_input.setMinimum(1)
        self.duration_input.setMaximum(600)
        self.duration_input.setMaximumWidth(80)
        layout.addWidget(self.duration_input)
        
        # Buttons
        self.start_btn = QPushButton("▶ Start Sampling")
        self.start_btn.setObjectName("startButton")
        self.start_btn.clicked.connect(self.start_clicked.emit)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton("💾 Save Data")
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
            'name': self.sample_input.text() or "Sample",
            'type': self.sample_type.currentText(),
            'duration': self.duration_input.value()
        }


class ConnectionPanel(QGroupBox):
    """Connection settings panel with Hybrid Mode (Serial + Network)"""
    
    connect_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Connection Settings (Hybrid)", parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # --- BAGIAN 1: NETWORK (Untuk Data Stream) ---
        layout.addWidget(QLabel("Data (WiFi):"))
        self.ip_input = QLineEdit()
        self.ip_input.setText("127.0.0.1") # IP Backend Rust
        self.ip_input.setMaximumWidth(100)
        self.ip_input.setPlaceholderText("Backend IP")
        layout.addWidget(self.ip_input)
        
        # Line Vertical Separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # --- BAGIAN 2: SERIAL (Untuk Control Motor) ---
        layout.addWidget(QLabel("Control (USB):"))
        self.port_selector = QComboBox()
        self.port_selector.addItems(self.get_available_ports())
        self.port_selector.setMaximumWidth(100)
        layout.addWidget(self.port_selector)
        
        # Tombol Refresh Port
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedWidth(30)
        self.refresh_btn.setToolTip("Refresh COM Ports")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)
        
        # --- BAGIAN 3: CONNECT BUTTON ---
        layout.addStretch()
        layout.addWidget(QLabel("Status:"))
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator)
        
        self.connect_btn = QPushButton("Connect All")
        self.connect_btn.clicked.connect(self.connect_clicked.emit)
        layout.addWidget(self.connect_btn)
        
        self.setLayout(layout)
    
    def get_available_ports(self) -> list:
        """Mencari COM port yang aktif"""
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            return ports if ports else ["No Ports"]
        except:
            return ["Error"]

    def refresh_ports(self):
        """Update isi dropdown port"""
        self.port_selector.clear()
        self.port_selector.addItems(self.get_available_ports())
    
    def get_connection_settings(self) -> dict:
        return {
            'host': self.ip_input.text(),
            'port': 8082, # Port default backend
            'serial_port': self.port_selector.currentText(),
            'baud_rate': 9600 # Sesuai main.ino
        }
    
    def set_status(self, status_text: str, color_rgb: tuple):
        self.status_indicator.set_status(status_text, color_rgb)