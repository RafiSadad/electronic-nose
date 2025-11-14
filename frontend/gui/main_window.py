from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLineEdit, 
                               QLabel, QComboBox)
from PySide6.QtCore import QTimer
import pyqtgraph as pg
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Electronic Nose - Data Visualization")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Control panel
        control_layout = self.create_control_panel()
        main_layout.addLayout(control_layout)
        
        # Graph widget
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.setLabel('left', 'Sensor Value')
        self.graph_widget.setLabel('bottom', 'Time (s)')
        self.graph_widget.showGrid(x=True, y=True)
        main_layout.addWidget(self.graph_widget)
        
        # Data arrays
        self.time_data = []
        self.sensor_data = []
        self.max_points = 500
        
        # Plot line
        pen = pg.mkPen(color='b', width=2)
        self.plot_line = self.graph_widget.plot([], [], pen=pen)
        
        # Timer for real-time update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        
    def create_control_panel(self):
        layout = QHBoxLayout()
        
        # Sample name input
        layout.addWidget(QLabel("Nama Sampel:"))
        self.sample_input = QLineEdit()
        self.sample_input.setPlaceholderText("Contoh: Kopi Arabika")
        layout.addWidget(self.sample_input)
        
        # COM port selection
        layout.addWidget(QLabel("COM Port:"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(["COM3", "COM4", "COM5"])
        layout.addWidget(self.port_combo)
        
        # Control buttons
        self.start_btn = QPushButton("Start Sampling")
        self.start_btn.clicked.connect(self.start_sampling)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_sampling)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton("Save Data")
        self.save_btn.clicked.connect(self.save_data)
        layout.addWidget(self.save_btn)
        
        self.edge_btn = QPushButton("Edge Impulse")
        self.edge_btn.clicked.connect(self.open_edge_impulse)
        layout.addWidget(self.edge_btn)
        
        layout.addStretch()
        
        return layout
    
    def start_sampling(self):
        print("Sampling started...")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.timer.start(100)  # Update every 100ms
        
    def stop_sampling(self):
        print("Sampling stopped.")
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def update_plot(self):
        # Simulate sensor data (replace with real serial data later)
        import time
        if len(self.time_data) == 0:
            t = 0
        else:
            t = self.time_data[-1] + 0.1
            
        value = np.random.uniform(100, 500)  # Simulated sensor value
        
        self.time_data.append(t)
        self.sensor_data.append(value)
        
        # Keep only last max_points
        if len(self.time_data) > self.max_points:
            self.time_data.pop(0)
            self.sensor_data.pop(0)
        
        # Update plot
        self.plot_line.setData(self.time_data, self.sensor_data)
        
    def save_data(self):
        import csv
        from datetime import datetime
        
        sample_name = self.sample_input.text() or "unknown"
        filename = f"data/{sample_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time', 'Sensor_Value'])
            for t, v in zip(self.time_data, self.sensor_data):
                writer.writerow([t, v])
        
        print(f"Data saved to {filename}")
        
    def open_edge_impulse(self):
        import webbrowser
        webbrowser.open("https://studio.edgeimpulse.com/")
