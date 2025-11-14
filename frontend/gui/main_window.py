"""Main application window"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QStatusBar
)
# CHANGE THIS LINE:
from PySide6.QtCore import Qt, QTimer, QThread, Signal
# from PySide6.QtCore import Qt, QTimer, QThread, pyqtSignal  # ← DELETE THIS

from PySide6.QtGui import QIcon, QFont

from gui.widgets import ControlPanel, ConnectionPanel, SensorPlot, StatusIndicator
from gui.styles import STYLESHEET, STATUS_COLORS
from utils.serial_comm import SerialWorker
from utils.data_processor import DataProcessor
from utils.file_handler import FileHandler
from config.constants import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, 
    UPDATE_INTERVAL, SENSOR_NAMES
)

import numpy as np
import csv
from datetime import datetime
from pathlib import Path


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.is_sampling = False
        self.sampling_data = {i: [] for i in range(4)}
        self.sampling_times = []
        self.serial_worker = None
        self.serial_thread = None
        
        # Setup UI
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(STYLESHEET)
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Connection panel
        self.connection_panel = ConnectionPanel()
        self.connection_panel.connect_clicked.connect(self.on_connect)
        main_layout.addWidget(self.connection_panel)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Tab 1: Real-time plot
        self.plot_widget = SensorPlot("Real-Time Sensor Data")
        self.tabs.addTab(self.plot_widget, "📊 Real-Time Plot")
        
        # Tab 2: Control panel and data info
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        
        self.control_panel = ControlPanel()
        self.control_panel.start_clicked.connect(self.on_start_sampling)
        self.control_panel.stop_clicked.connect(self.on_stop_sampling)
        self.control_panel.save_clicked.connect(self.on_save_data)
        tab2_layout.addWidget(self.control_panel)
        
        # Data info table
        info_group_layout = QVBoxLayout()
        info_label = QLabel("📈 Sampling Information")
        info_label_font = QFont()
        info_label_font.setBold(True)
        info_label_font.setPointSize(11)
        info_label.setFont(info_label_font)
        info_group_layout.addWidget(info_label)
        
        self.info_table = QTableWidget(5, 2)
        self.info_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.info_table.setColumnWidth(0, 150)
        self.info_table.setColumnWidth(1, 300)
        self.populate_info_table()
        info_group_layout.addWidget(self.info_table)
        
        tab2_layout.addLayout(info_group_layout)
        tab2_layout.addStretch()
        tab2.setLayout(tab2_layout)
        self.tabs.addTab(tab2, "⚙️ Control Panel")
        
        # Tab 3: Data statistics
        tab3 = QWidget()
        tab3_layout = QVBoxLayout()
        
        stats_label = QLabel("📊 Data Statistics")
        stats_label.setFont(info_label_font)
        tab3_layout.addWidget(stats_label)
        
        self.stats_table = QTableWidget(5, 5)
        self.stats_table.setHorizontalHeaderLabels([
            "Sensor", "Min", "Max", "Mean", "Std Dev"
        ])
        for i in range(5):
            self.stats_table.setColumnWidth(i, 150)
        self.populate_stats_table()
        tab3_layout.addWidget(self.stats_table)
        
        tab3_layout.addStretch()
        tab3.setLayout(tab3_layout)
        self.tabs.addTab(tab3, "📈 Statistics")
        
        main_layout.addWidget(self.tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.edge_impulse_btn = QPushButton("🚀 Upload to Edge Impulse")
        self.edge_impulse_btn.clicked.connect(self.on_edge_impulse)
        button_layout.addWidget(self.edge_impulse_btn)
        
        self.export_csv_btn = QPushButton("📥 Export as CSV")
        self.export_csv_btn.clicked.connect(self.on_export_csv)
        button_layout.addWidget(self.export_csv_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Plot")
        self.clear_btn.clicked.connect(self.on_clear_plot)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("background-color: #e8e8e8; color: #333;")
        
        # Update timer for sampling
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.on_update_plot)
        
        self.start_time = None
        self.update_interval = UPDATE_INTERVAL
        
    def populate_info_table(self):
        """Populate information table"""
        info = {
            "Sample Name": "None",
            "Sample Type": "None",
            "Duration": "0 s",
            "Points Collected": "0",
            "Elapsed Time": "0 s"
        }
        
        for row, (key, value) in enumerate(info.items()):
            self.info_table.setItem(row, 0, QTableWidgetItem(key))
            self.info_table.setItem(row, 1, QTableWidgetItem(value))
    
    def populate_stats_table(self):
        """Populate statistics table"""
        headers = ["Min", "Max", "Mean", "Std Dev"]
        
        for row in range(4):
            sensor_name = SENSOR_NAMES[row] if row < len(SENSOR_NAMES) else f"Sensor {row+1}"
            self.stats_table.setItem(row, 0, QTableWidgetItem(sensor_name))
            
            for col in range(1, 5):
                self.stats_table.setItem(row, col, QTableWidgetItem("0.00"))
    
    def on_connect(self):
        """Handle connection button click"""
        settings = self.connection_panel.get_connection_settings()
        
        if settings['source'] == "Simulation":
            self.statusBar().showMessage("Using Simulation mode")
            self.connection_panel.set_status("Simulation Mode", 
                                            STATUS_COLORS['connected'])
            self.control_panel.enable_start(True)
        else:
            # Try to connect to Arduino
            self.statusBar().showMessage("Attempting to connect...")
            # TODO: Implement actual serial connection
            self.connection_panel.set_status("Connected", 
                                            STATUS_COLORS['connected'])
            self.control_panel.enable_start(True)
    
    def on_start_sampling(self):
        """Start sampling process"""
        sample_info = self.control_panel.get_sample_info()
        
        if not sample_info['name']:
            QMessageBox.warning(self, "Warning", "Please enter a sample name!")
            return
        
        # Update info table
        self.info_table.setItem(0, 1, QTableWidgetItem(sample_info['name']))
        self.info_table.setItem(1, 1, QTableWidgetItem(sample_info['type']))
        self.info_table.setItem(2, 1, QTableWidgetItem(f"{sample_info['duration']} s"))
        
        # Clear previous data
        self.sampling_data = {i: [] for i in range(4)}
        self.sampling_times = []
        self.plot_widget.clear_data()
        
        self.is_sampling = True
        self.start_time = 0
        
        # Enable/disable buttons
        self.control_panel.enable_start(False)
        self.control_panel.enable_stop(True)
        
        # Start update timer
        self.update_timer.start(self.update_interval)
        
        self.connection_panel.set_status("Sampling...", 
                                        STATUS_COLORS['sampling'])
        self.statusBar().showMessage("Sampling in progress...")
    
    def on_update_plot(self):
        """Update plot with new simulated data"""
        if not self.is_sampling:
            return
        
        self.start_time += self.update_interval / 1000.0
        
        # Simulate sensor data
        sensor_values = [
            np.random.normal(250, 30),
            np.random.normal(300, 35),
            np.random.normal(200, 25),
            np.random.normal(280, 32)
        ]
        
        # Add to data storage
        self.plot_widget.add_data_point(self.start_time, sensor_values)
        for i, val in enumerate(sensor_values):
            self.sampling_data[i].append(val)
        self.sampling_times.append(self.start_time)
        
        # Update info
        self.info_table.setItem(4, 1, QTableWidgetItem(f"{self.start_time:.2f} s"))
        self.info_table.setItem(3, 1, QTableWidgetItem(str(len(self.sampling_times))))
        
        # Update stats
        self.update_statistics()
        
        # Check if sampling duration reached
        sample_info = self.control_panel.get_sample_info()
        if self.start_time >= sample_info['duration']:
            self.on_stop_sampling()
    
    def on_stop_sampling(self):
        """Stop sampling process"""
        self.is_sampling = False
        self.update_timer.stop()
        
        # Enable/disable buttons
        self.control_panel.enable_start(True)
        self.control_panel.enable_stop(False)
        
        self.connection_panel.set_status("Connected", 
                                        STATUS_COLORS['connected'])
        self.statusBar().showMessage(f"Sampling stopped. Collected {len(self.sampling_times)} data points.")
    
    def update_statistics(self):
        """Update statistics table"""
        for sensor_id in range(4):
            if self.sampling_data[sensor_id]:
                data = np.array(self.sampling_data[sensor_id])
                
                self.stats_table.setItem(sensor_id, 1, 
                    QTableWidgetItem(f"{data.min():.2f}"))
                self.stats_table.setItem(sensor_id, 2, 
                    QTableWidgetItem(f"{data.max():.2f}"))
                self.stats_table.setItem(sensor_id, 3, 
                    QTableWidgetItem(f"{data.mean():.2f}"))
                self.stats_table.setItem(sensor_id, 4, 
                    QTableWidgetItem(f"{data.std():.2f}"))
    
    def on_save_data(self):
        """Save sampling data to CSV"""
        if not self.sampling_times:
            QMessageBox.warning(self, "Warning", "No data to save!")
            return
        
        sample_info = self.control_panel.get_sample_info()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename
        filename = f"data/{sample_info['name'].replace(' ', '_')}_{timestamp}.csv"
        
        try:
            Path("data").mkdir(exist_ok=True)
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header with metadata
                writer.writerow(["Electronic Nose Data Export"])
                writer.writerow(["Sample Name", sample_info['name']])
                writer.writerow(["Sample Type", sample_info['type']])
                writer.writerow(["Export Date", datetime.now().isoformat()])
                writer.writerow(["Number of Points", len(self.sampling_times)])
                writer.writerow([])
                
                # Write data header
                headers = ["Time (s)"] + [f"Sensor {i+1}" for i in range(4)]
                writer.writerow(headers)
                
                # Write data
                for t_idx, t in enumerate(self.sampling_times):
                    row = [f"{t:.3f}"]
                    for s_idx in range(4):
                        if t_idx < len(self.sampling_data[s_idx]):
                            row.append(f"{self.sampling_data[s_idx][t_idx]:.2f}")
                        else:
                            row.append("0")
                    writer.writerow(row)
            
            QMessageBox.information(self, "Success", f"Data saved to {filename}")
            self.statusBar().showMessage(f"Data saved: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
    
    def on_clear_plot(self):
        """Clear plot and data"""
        reply = QMessageBox.question(self, "Confirm", 
            "Clear all data and plot?", 
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.plot_widget.clear_data()
            self.sampling_data = {i: [] for i in range(4)}
            self.sampling_times = []
            self.statusBar().showMessage("Plot cleared")
    
    def on_edge_impulse(self):
        """Open Edge Impulse in browser"""
        import webbrowser
        webbrowser.open("https://studio.edgeimpulse.com/")
        QMessageBox.information(self, "Info", 
            "Edge Impulse opened in your default browser.\n\n" +
            "Upload your CSV files to train your model.")
    
    def on_export_csv(self):
        """Export data as CSV (same as save)"""
        self.on_save_data()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_sampling:
            reply = QMessageBox.question(self, "Confirm", 
                "Sampling in progress. Exit anyway?", 
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        if self.serial_thread:
            self.serial_thread.quit()
            self.serial_thread.wait()
        
        event.accept()
