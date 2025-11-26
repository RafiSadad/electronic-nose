"""Main application window"""

import serial
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

from gui.widgets import ControlPanel, ConnectionPanel, SensorPlot
from gui.styles import STYLESHEET, STATUS_COLORS
from utils.network_comm import NetworkWorker
from config.constants import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, 
    UPDATE_INTERVAL, SENSOR_NAMES, NUM_SENSORS
)

import numpy as np
import csv
from datetime import datetime
from pathlib import Path

# Mapping state dari Arduino (Sesuai Kode Pak Zizu)
STATE_NAMES = {
    0: "IDLE",
    1: "PRE-COND",
    2: "RAMP_UP",
    3: "HOLD",
    4: "PURGE",
    5: "RECOVERY",
    6: "DONE"
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
        
        # Setup tabel statistik sesuai jumlah sensor
        self.stats_table = QTableWidget(NUM_SENSORS + 1, 5) # +1 buffer
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
            for col in range(1, 5):
                self.stats_table.setItem(row, col, QTableWidgetItem("0.00"))
    
    def on_connect(self):
        """Handle connection button click (HYBRID MODE)"""
        settings = self.connection_panel.get_connection_settings()
        
        if self.network_worker:
            self.network_worker.stop()
            self.network_worker.wait()
            self.network_worker = None

        self.statusBar().showMessage(f"Connecting Data to {settings['host']} and Control to {settings['serial_port']}...")
        self.connection_panel.set_status("Connecting...", STATUS_COLORS['sampling'])
        
        self.connection_panel.connect_btn.setEnabled(False)
        self.connection_panel.connect_btn.setText("Connecting...")
        
        self.network_worker = NetworkWorker(host=settings['host'], port=settings['port'])
        self.network_worker.data_received.connect(self.on_data_received)
        self.network_worker.connection_status.connect(self.on_connection_status)
        self.network_worker.error_occurred.connect(self.handle_network_error)
        self.network_worker.start()

        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            
        if settings['serial_port'] != "No Ports":
            try:
                self.serial_connection = serial.Serial(
                    settings['serial_port'], 
                    settings['baud_rate'], 
                    timeout=1
                )
                print(f"✅ Serial Connected: {settings['serial_port']}")
            except Exception as e:
                QMessageBox.warning(self, "Serial Error", f"Failed to connect to Serial Port: {e}")
        else:
            QMessageBox.warning(self, "Warning", "No Serial Port selected. Motor control will not work!")

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
        self.info_table.setItem(2, 1, QTableWidgetItem("Auto (Wait for DONE)"))
        
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
                self.statusBar().showMessage("Sampling Started (Command sent via Serial)")
            except Exception as e:
                QMessageBox.critical(self, "Serial Error", f"Failed to send start command: {e}")
        else:
            self.statusBar().showMessage("Sampling Started (WARNING: Serial not connected!)")
            
        self.connection_panel.set_status("Sampling...", STATUS_COLORS['sampling'])
    
    def on_data_received(self, data: dict):
        """Handle data received from Backend (Signal based)"""
        # Meskipun tidak sedang sampling, kita tetap bisa memonitor status
        # tapi data hanya disimpan jika self.is_sampling = True
        
        try:
            sensor_values = [
                float(data.get('no2', 0.0)),
                float(data.get('eth', 0.0)), 
                float(data.get('voc', 0.0)),
                float(data.get('co', 0.0)),
                float(data.get('co_mics', 0.0)),
                float(data.get('eth_mics', 0.0)),
                float(data.get('voc_mics', 0.0))
            ]
            
            state_idx = int(data.get('state', 0))
            state_name = STATE_NAMES.get(state_idx, "UNKNOWN")
            level = data.get('level', 0)
            
            # Update status bar dengan fase Zizu
            self.statusBar().showMessage(f"System State: {state_name} | Level: {level}")
            
            if self.is_sampling:
                self.process_new_data(sensor_values)
                
                # --- LOGIKA BARU: Stop Otomatis jika DONE (State 6) ---
                if state_idx == 6: # DONE
                    self.on_stop_sampling()
                    QMessageBox.information(self, "Finished", "Sampling sequence completed (All Levels Done)!")
                    
        except Exception as e:
            print(f"Error parsing data: {e}")

    def process_new_data(self, sensor_values: list):
        if not self.sampling_times:
            self.start_time = 0.0
        else:
            self.start_time += self.update_interval / 1000.0
            
        self.plot_widget.add_data_point(self.start_time, sensor_values)
        
        # Simpan data
        for i, val in enumerate(sensor_values[:NUM_SENSORS]):
            self.sampling_data[i].append(val)
        self.sampling_times.append(self.start_time)
        
        self.info_table.setItem(4, 1, QTableWidgetItem(f"{self.start_time:.2f} s"))
        self.info_table.setItem(3, 1, QTableWidgetItem(str(len(self.sampling_times))))
        self.update_statistics()
        
        # --- PERUBAHAN: TIDAK ADA LAGI STOP BERDASARKAN WAKTU ---
        # Stop hanya dipicu oleh state_idx == 6 di on_data_received

    def on_stop_sampling(self):
        self.is_sampling = False
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b"STOP_SAMPLING\n")
            except Exception as e:
                print(f"Serial stop error: {e}")
        
        self.control_panel.enable_start(True)
        self.control_panel.enable_stop(False)
        self.connection_panel.set_status("Hybrid Connected", STATUS_COLORS['connected'])
        self.statusBar().showMessage(f"Sampling stopped. Collected {len(self.sampling_times)} data points.")
    
    def update_statistics(self):
        """Update statistics table"""
        for sensor_id in range(NUM_SENSORS):
            if self.sampling_data[sensor_id]:
                data = np.array(self.sampling_data[sensor_id])
                self.stats_table.setItem(sensor_id, 1, QTableWidgetItem(f"{data.min():.2f}"))
                self.stats_table.setItem(sensor_id, 2, QTableWidgetItem(f"{data.max():.2f}"))
                self.stats_table.setItem(sensor_id, 3, QTableWidgetItem(f"{data.mean():.2f}"))
                self.stats_table.setItem(sensor_id, 4, QTableWidgetItem(f"{data.std():.2f}"))
    
    def on_save_data(self):
        if not self.sampling_times:
            QMessageBox.warning(self, "Warning", "No data to save!")
            return
        
        sample_info = self.control_panel.get_sample_info()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{sample_info['name'].replace(' ', '_')}_{timestamp}.csv"
        
        try:
            Path("data").mkdir(exist_ok=True)
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Electronic Nose Data Export"])
                writer.writerow(["Sample Name", sample_info['name']])
                writer.writerow(["Sample Type", sample_info['type']])
                writer.writerow(["Export Date", datetime.now().isoformat()])
                writer.writerow(["Mode", "Auto FSM (Zizu)"])
                writer.writerow(["Number of Points", len(self.sampling_times)])
                writer.writerow([])
                headers = ["Time (s)"] + [SENSOR_NAMES[i] for i in range(NUM_SENSORS)]
                writer.writerow(headers)
                for t_idx, t in enumerate(self.sampling_times):
                    row = [f"{t:.3f}"]
                    for s_idx in range(NUM_SENSORS):
                        if t_idx < len(self.sampling_data[s_idx]):
                            row.append(f"{self.sampling_data[s_idx][t_idx]:.2f}")
                        else:
                            row.append("0")
                    writer.writerow(row)
            QMessageBox.information(self, "Success", f"Data saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
    
    def on_clear_plot(self):
        reply = QMessageBox.question(self, "Confirm", "Clear all data and plot?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.plot_widget.clear_data()
            self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
            self.sampling_times = []
            self.statusBar().showMessage("Plot cleared")
    
    def on_edge_impulse(self):
        import webbrowser
        webbrowser.open("https://studio.edgeimpulse.com/")
        QMessageBox.information(self, "Info", "Edge Impulse opened in your default browser.")
    
    def on_export_csv(self):
        self.on_save_data()
    
    def closeEvent(self, event):
        if self.is_sampling:
            reply = QMessageBox.question(self, "Confirm", "Sampling in progress. Exit anyway?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        if self.network_worker:
            self.network_worker.stop()
            self.network_worker.wait()
        if self.serial_connection:
            self.serial_connection.close()
        event.accept()