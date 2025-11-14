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
    """Connection settings panel"""
    
    connect_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Connection Settings", parent)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # COM Port selection
        layout.addWidget(QLabel("COM Port:"))
        self.com_port = QComboBox()
        self.com_port.addItems(self.get_available_ports())
        self.com_port.setMaximumWidth(100)
        layout.addWidget(self.com_port)
        
        # Baud rate
        layout.addWidget(QLabel("Baud Rate:"))
        self.baud_rate = QComboBox()
        self.baud_rate.addItems(["9600", "115200", "230400"])
        self.baud_rate.setCurrentText("115200")
        self.baud_rate.setMaximumWidth(100)
        layout.addWidget(self.baud_rate)
        
        # Data source
        layout.addWidget(QLabel("Data Source:"))
        self.data_source = QComboBox()
        self.data_source.addItems(["Serial (Arduino)", "Simulation"])
        self.data_source.setMaximumWidth(150)
        layout.addWidget(self.data_source)
        
        # Status indicator
        layout.addWidget(QLabel("Status:"))
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator)
        
        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_clicked.emit)
        layout.addWidget(self.connect_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_available_ports(self) -> list:
        """Get list of available COM ports"""
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            return ports if ports else ["COM3", "COM4", "COM5"]
        except:
            return ["COM3", "COM4", "COM5"]
    
    def get_connection_settings(self) -> dict:
        return {
            'port': self.com_port.currentText(),
            'baudrate': int(self.baud_rate.currentText()),
            'source': self.data_source.currentText()
        }
    
    def set_status(self, status_text: str, color_rgb: tuple):
        self.status_indicator.set_status(status_text, color_rgb)
