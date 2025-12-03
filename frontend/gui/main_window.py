"""Main application window"""

import serial
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

# Import Modules Sendiri
from gui.widgets import ControlPanel, ConnectionPanel, SensorPlot, GnuplotWidget
from gui.styles import STYLESHEET, STATUS_COLORS
from utils.network_comm import NetworkWorker
from utils.file_handler import FileHandler
from config.constants import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, 
    UPDATE_INTERVAL, SENSOR_NAMES, NUM_SENSORS
)

# Mapping state dari Arduino
STATE_NAMES = {
    0: "IDLE", 1: "PRE-COND", 2: "RAMP_UP", 3: "HOLD",
    4: "PURGE", 5: "RECOVERY", 6: "DONE"
}

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.is_sampling = False
        self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
        self.sampling_times = []
        
        # Workers
        self.network_worker = None
        self.serial_connection = None 
        
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
        info_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
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
        stats_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        tab3_layout.addWidget(stats_label)
        
        self.stats_table = QTableWidget(NUM_SENSORS + 1, 5)
        self.stats_table.setHorizontalHeaderLabels(["Sensor", "Min", "Max", "Mean", "Std Dev"])
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
        self.export_csv_btn.clicked.connect(self.on_save_data)
        button_layout.addWidget(self.export_csv_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Plot")
        self.clear_btn.clicked.connect(self.on_clear_plot)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("background-color: #e8e8e8; color: #333;")
        
        self.update_interval = UPDATE_INTERVAL
        
    def populate_info_table(self):
        info = {
            "Sample Name": "None", "Sample Type": "None",
            "Duration": "Auto (FSM)", "Points Collected": "0", "Elapsed Time": "0 s"
        }
        for row, (key, value) in enumerate(info.items()):
            self.info_table.setItem(row, 0, QTableWidgetItem(key))
            self.info_table.setItem(row, 1, QTableWidgetItem(value))
    
    def populate_stats_table(self):
        for row in range(NUM_SENSORS):
            sensor_name = SENSOR_NAMES[row] if row < len(SENSOR_NAMES) else f"Sensor {row+1}"
            self.stats_table.setItem(row, 0, QTableWidgetItem(sensor_name))
    
    def on_connect(self):
        settings = self.connection_panel.get_connection_settings()
        if self.network_worker:
            self.network_worker.stop()
            self.network_worker.wait()
            self.network_worker = None

        self.statusBar().showMessage(f"Connecting to {settings['host']}...")
        self.connection_panel.set_status("Connecting...", STATUS_COLORS['sampling'])
        self.connection_panel.connect_btn.setEnabled(False)
        
        self.network_worker = NetworkWorker(host=settings['host'], port=settings['port'])
        self.network_worker.data_received.connect(self.on_data_received)
        self.network_worker.connection_status.connect(self.on_connection_status)
        self.network_worker.error_occurred.connect(self.handle_network_error)
        self.network_worker.start()

        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        if settings['serial_port'] != "No Ports":
            try:
                self.serial_connection = serial.Serial(settings['serial_port'], settings['baud_rate'], timeout=1)
                print(f"✅ Serial Connected: {settings['serial_port']}")
            except Exception as e:
                QMessageBox.warning(self, "Serial Error", f"Failed: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No Serial Port selected!")

    def handle_network_error(self, msg: str):
        self.statusBar().showMessage(msg)

    def on_connection_status(self, connected: bool):
        if connected:
            self.connection_panel.set_status("Hybrid Connected", STATUS_COLORS['connected'])
            self.control_panel.enable_start(True)
            self.statusBar().showMessage("Connected: Data (WiFi) + Control (Ready)")
            self.connection_panel.connect_btn.setText("Connected")
            self.connection_panel.connect_btn.setEnabled(False)
        else:
            self.connection_panel.set_status("Disconnected", STATUS_COLORS['disconnected'])
            self.control_panel.enable_start(False)
            self.statusBar().showMessage("Disconnected from Backend")
            self.connection_panel.connect_btn.setText("Connect All")
            self.connection_panel.connect_btn.setEnabled(True)

    def on_start_sampling(self):
        sample_info = self.control_panel.get_sample_info()
        if not sample_info['name']:
            QMessageBox.warning(self, "Warning", "Please enter a sample name!")
            return
        
        self.info_table.setItem(0, 1, QTableWidgetItem(sample_info['name']))
        self.info_table.setItem(1, 1, QTableWidgetItem(sample_info['type']))
        
        self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
        self.sampling_times = []
        self.plot_widget.clear_data()
        
        self.is_sampling = True
        self.start_time = 0
        
        self.control_panel.enable_start(False)
        self.control_panel.enable_stop(True)
        
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b"START_SAMPLING\n")
                self.statusBar().showMessage("Sampling Started via Serial")
            except Exception as e:
                QMessageBox.critical(self, "Serial Error", f"Failed: {e}")
        
        self.connection_panel.set_status("Sampling...", STATUS_COLORS['sampling'])
    
    def on_data_received(self, data: dict):
        try:
            sensor_values = [
                float(data.get('no2', 0.0)), float(data.get('eth', 0.0)), 
                float(data.get('voc', 0.0)), float(data.get('co', 0.0)),
                float(data.get('co_mics', 0.0)), float(data.get('eth_mics', 0.0)),
                float(data.get('voc_mics', 0.0))
            ]
            state_idx = int(data.get('state', 0))
            state_name = STATE_NAMES.get(state_idx, "UNKNOWN")
            level = data.get('level', 0)
            
            self.statusBar().showMessage(f"System State: {state_name} | Level: {level}")
            
            if self.is_sampling:
                if not self.sampling_times:
                    self.start_time = 0.0
                else:
                    self.start_time += self.update_interval / 1000.0
                
                self.plot_widget.add_data_point(self.start_time, sensor_values)
                for i, val in enumerate(sensor_values[:NUM_SENSORS]):
                    self.sampling_data[i].append(val)
                self.sampling_times.append(self.start_time)
                
                self.info_table.setItem(4, 1, QTableWidgetItem(f"{self.start_time:.2f} s"))
                self.info_table.setItem(3, 1, QTableWidgetItem(str(len(self.sampling_times))))
                
                if state_idx == 6: # DONE
                    self.on_stop_sampling()
                    QMessageBox.information(self, "Finished", "Sampling sequence completed!")
        except Exception as e:
            print(f"Error parsing data: {e}")

    def on_stop_sampling(self):
        self.is_sampling = False
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b"STOP_SAMPLING\n")
            except: pass
        
        self.control_panel.enable_start(True)
        self.control_panel.enable_stop(False)
        self.connection_panel.set_status("Hybrid Connected", STATUS_COLORS['connected'])
        self.statusBar().showMessage(f"Stopped. Collected {len(self.sampling_times)} points.")
    
    # --- FITUR 1: SAVE CSV + GNUPLOT ---
    def on_save_data(self):
        if not self.sampling_times:
            QMessageBox.warning(self, "Warning", "No data to save!")
            return
        
        sample_info = self.control_panel.get_sample_info()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{sample_info['name'].replace(' ', '_')}_{timestamp}.csv"
        
        try:
            # Simpan CSV
            FileHandler.save_as_csv(filename, sample_info, self.sampling_data, 
                                  self.sampling_times, SENSOR_NAMES)
            QMessageBox.information(self, "Success", f"Data saved to {filename}")

            # Tanya Gnuplot
            reply = QMessageBox.question(self, "Visualisasi", "Buka grafik di GNUPLOT?", 
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.open_gnuplot(filename)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {str(e)}")

    def open_gnuplot(self, csv_filename):
        png_filename = csv_filename.replace('.csv', '.png')
        script_path = "plot_config.plt"
        try:
            # Generate PNG
            cmd = ["gnuplot", "-c", script_path, csv_filename, png_filename]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Buka Widget Gambar
                viewer = GnuplotWidget(png_filename, self)
                viewer.exec()
            else:
                QMessageBox.warning(self, "Gnuplot Error", f"Gagal generate:\n{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"System Error:\n{str(e)}")

    # --- FITUR 2: EDGE IMPULSE UPLOAD ---
    def on_edge_impulse(self):
        if not self.sampling_times:
            QMessageBox.warning(self, "Warning", "No data to upload!")
            return

        sample_info = self.control_panel.get_sample_info()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{sample_info['name'].replace(' ', '_')}_{timestamp}.json"

        try:
            success = FileHandler.save_edge_impulse_json(
                filename, sample_info['name'], SENSOR_NAMES,
                self.sampling_data, self.update_interval
            )

            if success:
                QMessageBox.information(self, "Ready", f"JSON created at:\n{filename}\n\nBrowser opening...")
                webbrowser.open("https://studio.edgeimpulse.com/studio/select-project?next=/data-acquisition")
            else:
                QMessageBox.warning(self, "Error", "Gagal menyimpan JSON.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def on_clear_plot(self):
        if QMessageBox.question(self, "Confirm", "Clear data?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.plot_widget.clear_data()
            self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
            self.sampling_times = []

    def closeEvent(self, event):
        if self.network_worker: self.network_worker.stop()
        if self.serial_connection: self.serial_connection.close()
        event.accept()