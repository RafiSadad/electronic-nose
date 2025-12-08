"""Main application window"""

import serial
import subprocess
import webbrowser
import os
import glob
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QInputDialog, QHeaderView,
    QAbstractItemView
)
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap

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
        
        # --- TAB 1: Real-time plot ---
        self.plot_widget = SensorPlot("Real-Time Sensor Data")
        self.tabs.addTab(self.plot_widget, "📊 Real-Time Plot")
        
        # --- TAB 2: Control panel ---
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
        
        # --- TAB 3: Data Library ---
        self.library_tab = QWidget()
        lib_layout = QVBoxLayout()
        
        lib_header = QHBoxLayout()
        lib_label = QLabel("📂 Data Library (Double Click to Open Gnuplot)")
        lib_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lib_header.addWidget(lib_label)
        
        self.refresh_lib_btn = QPushButton("🔄 Refresh Library")
        self.refresh_lib_btn.setFixedWidth(150)
        self.refresh_lib_btn.clicked.connect(self.refresh_library)
        lib_header.addWidget(self.refresh_lib_btn)
        lib_header.addStretch()
        lib_layout.addLayout(lib_header)

        # 4 Kolom: Preview, Filename, Last Modified, Size
        self.lib_table = QTableWidget(0, 4)
        self.lib_table.setHorizontalHeaderLabels(["Preview", "Filename", "Last Modified", "Size"])
        self.lib_table.setIconSize(QSize(160, 90)) # Ukuran Thumbnail
        
        # Konfigurasi Header
        header = self.lib_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)       # Kolom Preview Tetap
        self.lib_table.setColumnWidth(0, 180)                   # Lebar kolom preview
        header.setSectionResizeMode(1, QHeaderView.Stretch)     # Filename lebar
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) 
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.lib_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lib_table.setEditTriggers(QAbstractItemView.NoEditTriggers) 
        self.lib_table.cellDoubleClicked.connect(self.on_library_double_click)
        
        lib_layout.addWidget(self.lib_table)
        self.library_tab.setLayout(lib_layout)
        self.tabs.addTab(self.library_tab, "📚 Data Library")

        # --- TAB 4: Statistics ---
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
        
        # Load library awal
        self.refresh_library()

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
                pass 
        else:
            pass 

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
            except: pass
        
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
            pass

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
    
    # --- FITUR SAVE & UPLOAD ---
    def on_save_data(self):
        if not self.sampling_times:
            QMessageBox.warning(self, "Warning", "No data to save!")
            return
        
        sample_info = self.control_panel.get_sample_info()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{sample_info['name'].replace(' ', '_')}_{timestamp}.csv"
        
        try:
            # 1. Simpan CSV
            FileHandler.save_as_csv(filename, sample_info, self.sampling_data, 
                                  self.sampling_times, SENSOR_NAMES)
            
            QMessageBox.information(self, "Success", f"Data saved to {filename}")
            
            # 2. Buka Plot (Ini akan otomatis generate PNG + Interactive)
            reply = QMessageBox.question(self, "Visualisasi", "Buka grafik di GNUPLOT?", 
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.open_interactive_plot(filename)
            else:
                # Kalau user pilih NO, tetap generate PNG di background untuk Library
                self.generate_png(filename)
                self.refresh_library()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {str(e)}")

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
            
            if not success:
                QMessageBox.warning(self, "Error", "Gagal menyimpan file JSON lokal.")
                return
            
            self.refresh_library() 

            reply = QMessageBox.question(
                self, "Upload Method", 
                "File JSON berhasil dibuat.\nUpload otomatis via API?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                api_key, ok = QInputDialog.getText(self, "Edge Impulse API Key", "Masukkan 'EI Project API Key':")
                if ok and api_key:
                    self.statusBar().showMessage("Uploading...")
                    is_uploaded, msg = FileHandler.upload_to_edge_impulse(filename, api_key, sample_info['name'])
                    if is_uploaded:
                        QMessageBox.information(self, "Success", f"Upload Berhasil!\n{msg}")
                    else:
                        QMessageBox.critical(self, "Failed", f"Gagal Upload:\n{msg}")
            else:
                webbrowser.open("https://studio.edgeimpulse.com/studio/select-project?next=/data-acquisition")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            
    # --- FITUR LIBRARY & PLOTTER ---
    def generate_png(self, csv_filename):
        """
        Menjalankan perintah:
        gnuplot -c plot_config.plt "data/file.csv" "data/file.png"
        """
        script_png = "plot_config.plt"
        # Cek lokasi script
        if not os.path.exists(script_png) and os.path.exists(f"data/{script_png}"):
             script_png = f"data/{script_png}"
        
        png_filename = csv_filename.replace('.csv', '.png')
        try:
            # check=False supaya tidak crash kalau gnuplot error/warning
            subprocess.run(["gnuplot", "-c", script_png, csv_filename, png_filename], check=False)
            print(f"Generated PNG: {png_filename}")
        except Exception as e:
            print(f"Failed to generate PNG: {e}")

    def open_interactive_plot(self, csv_filename):
        """
        1. Generate PNG DULU (Background) -> gnuplot -c plot_config.plt
        2. Baru Buka Interactive Window -> gnuplot -p -c plot_interactive.plt
        """
        
        # --- LANGKAH 1: Generate PNG (Request Anda) ---
        self.generate_png(csv_filename)
        
        # --- LANGKAH 2: Buka Window Interaktif ---
        script_interactive = "plot_interactive.plt"
        if not os.path.exists(script_interactive) and os.path.exists(f"data/{script_interactive}"):
             script_interactive = f"data/{script_interactive}"
        
        try:
            # Gunakan Popen agar window terpisah dan tidak freeze aplikasi utama
            subprocess.Popen(["gnuplot", "-p", "-c", script_interactive, csv_filename])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuka Gnuplot Interaktif:\n{str(e)}")
            
        # Refresh library agar thumbnail PNG yang baru dibuat langsung muncul
        self.refresh_library()

    def refresh_library(self):
        """Membaca folder data/ dan menampilkannya dengan Thumbnail"""
        self.lib_table.setRowCount(0)
        
        if not os.path.exists("data"):
            return
            
        files = glob.glob("data/*.csv") + glob.glob("data/*.json")
        files.sort(key=os.path.getmtime, reverse=True)
        
        for file_path in files:
            row = self.lib_table.rowCount()
            self.lib_table.insertRow(row)
            self.lib_table.setRowHeight(row, 100)
            
            filename = os.path.basename(file_path)
            
            # --- KOLOM 0: PREVIEW ---
            preview_item = QTableWidgetItem()
            png_path = file_path.replace(".csv", ".png").replace(".json", ".png")
            
            if os.path.exists(png_path) and filename.endswith(".csv"):
                icon = QIcon(png_path)
                preview_item.setIcon(icon)
                preview_item.setText("")
            elif filename.endswith(".json"):
                 preview_item.setText("JSON")
                 preview_item.setTextAlignment(Qt.AlignCenter)
            else:
                 preview_item.setText("No Img")
                 preview_item.setTextAlignment(Qt.AlignCenter)
                 
            self.lib_table.setItem(row, 0, preview_item)
            
            # --- KOLOM 1: FILENAME ---
            self.lib_table.setItem(row, 1, QTableWidgetItem(filename))
            
            # --- KOLOM 2: TIME ---
            timestamp = os.path.getmtime(file_path)
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            self.lib_table.setItem(row, 2, QTableWidgetItem(date_str))
            
            # --- KOLOM 3: SIZE ---
            size_kb = os.path.getsize(file_path) / 1024
            self.lib_table.setItem(row, 3, QTableWidgetItem(f"{size_kb:.1f} KB"))

    def on_library_double_click(self, row, col):
        """Saat user double click file di library"""
        item = self.lib_table.item(row, 1) # Ambil filename dari col 1
        if item:
            filename = item.text()
            full_path = os.path.join("data", filename)
            
            if filename.endswith(".csv"):
                # Panggil fungsi yang sudah di-update (Generate PNG + Open Interactive)
                self.open_interactive_plot(full_path)
            else:
                QMessageBox.information(self, "Info", "File JSON tidak bisa diplot.")

    def on_clear_plot(self):
        if QMessageBox.question(self, "Confirm", "Clear data?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.plot_widget.clear_data()
            self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
            self.sampling_times = []

    def closeEvent(self, event):
        if self.network_worker: self.network_worker.stop()
        if self.serial_connection: self.serial_connection.close()
        event.accept()