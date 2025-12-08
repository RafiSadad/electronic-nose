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
    QAbstractItemView, QLineEdit
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
        
        # --- TAB 3: Data Library (Fitur Baru) ---
        self.library_tab = QWidget()
        lib_layout = QVBoxLayout()
        
        lib_header = QHBoxLayout()
        lib_label = QLabel("📂 Data Library")
        lib_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lib_header.addWidget(lib_label)
        
        # Tombol Upload Khusus Library
        self.upload_lib_btn = QPushButton("☁️ Upload Selected to EI")
        self.upload_lib_btn.setFixedWidth(180)
        self.upload_lib_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.upload_lib_btn.clicked.connect(self.on_library_upload_click)
        lib_header.addWidget(self.upload_lib_btn)
        
        self.refresh_lib_btn = QPushButton("🔄 Refresh")
        self.refresh_lib_btn.setFixedWidth(100)
        self.refresh_lib_btn.clicked.connect(self.refresh_library)
        lib_header.addWidget(self.refresh_lib_btn)
        
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
        
        # --- ACTION BUTTONS (BOTTOM) ---
        button_layout = QHBoxLayout()
        
        # 1. API Key Input
        api_label = QLabel("EI API Key:")
        api_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        button_layout.addWidget(api_label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Paste Edge Impulse API Key here...")
        self.api_key_input.setEchoMode(QLineEdit.Password) 
        self.api_key_input.setFixedWidth(200)
        self.api_key_input.setToolTip("API Key ini dipakai untuk tombol Upload di bawah & di Library")
        button_layout.addWidget(self.api_key_input)

        # 2. Upload Button (Current Session)
        self.edge_impulse_btn = QPushButton("🚀 Upload Session")
        self.edge_impulse_btn.clicked.connect(self.on_edge_impulse_session)
        button_layout.addWidget(self.edge_impulse_btn)
        
        # 3. Export CSV
        self.export_csv_btn = QPushButton("📥 Export CSV")
        self.export_csv_btn.clicked.connect(self.on_save_data)
        button_layout.addWidget(self.export_csv_btn)
        
        # 4. Clear Plot
        self.clear_btn = QPushButton("🗑️ Clear")
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
        
        # 1. SETUP NETWORK (Untuk Data)
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

        # 2. SETUP SERIAL (Untuk Kontrol)
        # Ini WAJIB ada agar perintah START_SAMPLING terkirim lewat USB
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        if settings['serial_port'] != "No Ports":
            try:
                self.serial_connection = serial.Serial(settings['serial_port'], settings['baud_rate'], timeout=1)
                print(f"✅ Serial Connected: {settings['serial_port']}")
            except Exception as e:
                # Tampilkan pesan error jika COM Port gagal dibuka (misal dipakai Arduino IDE)
                QMessageBox.warning(self, "Serial Error", f"Gagal buka port {settings['serial_port']}!\n\nPastikan Serial Monitor di Arduino IDE sudah DITUTUP.\n\nError: {e}")
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
        # 1. Validasi Input UI
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
        
        # 2. KIRIM COMMAND VIA SERIAL (UTAMA)
        # Ini logic "lama" yang terbukti jalan untuk menggerakkan hardware
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # Kirim string "START_SAMPLING\n" ke Arduino via USB
                self.serial_connection.write(b"START_SAMPLING\n")
                self.statusBar().showMessage("Sampling Started via Serial")
            except Exception as e:
                QMessageBox.critical(self, "Serial Error", f"Failed to send command: {e}")
        else:
            # Jika Serial putus/lupa connect, kasih peringatan
            QMessageBox.warning(self, "Warning", "Serial Port not connected! Hardware mungkin tidak merespon.")
        
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
        
        # KIRIM STOP VIA SERIAL
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
            
            # 2. Buka Plot (Auto Generate PNG + Interactive)
            reply = QMessageBox.question(self, "Visualisasi", "Buka grafik di GNUPLOT?", 
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.open_interactive_plot(filename)
            else:
                self.generate_png(filename)
                self.refresh_library()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {str(e)}")

    def on_edge_impulse_session(self):
        """Upload sesi yang sedang berlangsung/baru selesai"""
        if not self.sampling_times:
            QMessageBox.warning(self, "Warning", "No data to upload!")
            return
            
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "API Key Missing", "Silakan isi API Key di kolom bawah terlebih dahulu!")
            self.api_key_input.setFocus()
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
                self.refresh_library()
                self.statusBar().showMessage("Uploading to Edge Impulse...")
                
                is_uploaded, msg = FileHandler.upload_to_edge_impulse(filename, api_key, sample_info['name'])
                
                if is_uploaded:
                    QMessageBox.information(self, "Success", f"Upload Berhasil!\n{msg}")
                    self.statusBar().showMessage("Upload Success")
                else:
                    QMessageBox.critical(self, "Failed", f"Gagal Upload:\n{msg}")
                    self.statusBar().showMessage("Upload Failed")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    # --- FITUR LIBRARY & PLOTTER ---
    def generate_png(self, csv_filename):
        script_png = "plot_config.plt"
        if not os.path.exists(script_png) and os.path.exists(f"data/{script_png}"):
             script_png = f"data/{script_png}"
        
        png_filename = csv_filename.replace('.csv', '.png')
        try:
            subprocess.run(["gnuplot", "-c", script_png, csv_filename, png_filename], check=False)
        except: pass

    def open_interactive_plot(self, csv_filename):
        self.generate_png(csv_filename) # Pastikan PNG ada
        
        script_interactive = "plot_interactive.plt"
        if not os.path.exists(script_interactive) and os.path.exists(f"data/{script_interactive}"):
             script_interactive = f"data/{script_interactive}"
        
        try:
            subprocess.Popen(["gnuplot", "-p", "-c", script_interactive, csv_filename])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuka Gnuplot Interaktif:\n{str(e)}")
            
        self.refresh_library()

    def refresh_library(self):
        """Membaca folder data/, HANYA CSV yang ditampilkan"""
        self.lib_table.setRowCount(0)
        
        if not os.path.exists("data"):
            return
        
        # HANYA ambil file .csv
        files = glob.glob("data/*.csv")
        files.sort(key=os.path.getmtime, reverse=True)
        
        for file_path in files:
            row = self.lib_table.rowCount()
            self.lib_table.insertRow(row)
            self.lib_table.setRowHeight(row, 100)
            
            filename = os.path.basename(file_path)
            
            # Kolom Preview (Cari PNG pasangannya)
            preview_item = QTableWidgetItem()
            png_path = file_path.replace(".csv", ".png")
            
            if os.path.exists(png_path):
                icon = QIcon(png_path)
                preview_item.setIcon(icon)
                preview_item.setText("")
            else:
                 preview_item.setText("No Preview")
                 preview_item.setTextAlignment(Qt.AlignCenter)
                 
            self.lib_table.setItem(row, 0, preview_item)
            self.lib_table.setItem(row, 1, QTableWidgetItem(filename))
            
            timestamp = os.path.getmtime(file_path)
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            self.lib_table.setItem(row, 2, QTableWidgetItem(date_str))
            
            size_kb = os.path.getsize(file_path) / 1024
            self.lib_table.setItem(row, 3, QTableWidgetItem(f"{size_kb:.1f} KB"))

    def on_library_double_click(self, row, col):
        item = self.lib_table.item(row, 1) # Filename di kolom 1
        if item:
            filename = item.text()
            full_path = os.path.join("data", filename)
            
            # Buka Plot Interaktif (karena sudah pasti CSV)
            self.open_interactive_plot(full_path)

    def on_library_upload_click(self):
        """Upload file CSV yang dipilih di Library (Auto convert to JSON)"""
        # 1. Cek API Key
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "API Key Missing", "Silakan isi API Key di kolom bawah terlebih dahulu!")
            self.api_key_input.setFocus()
            return

        # 2. Cek Seleksi Tabel
        rows = self.lib_table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Warning", "Pilih salah satu file di tabel Library dulu!")
            return
        
        # 3. Ambil Filename dari baris yang dipilih
        row_idx = rows[0].row()
        filename = self.lib_table.item(row_idx, 1).text()
        
        # Path CSV asli
        csv_full_path = os.path.join("data", filename) # Filename di tabel sudah pasti CSV
        
        # Path JSON target
        json_filename = filename.replace('.csv', '.json')
        json_full_path = os.path.join("data", json_filename)
        
        # 4. LOGIKA AUTO-CONVERT
        if not os.path.exists(json_full_path):
            if os.path.exists(csv_full_path):
                self.statusBar().showMessage(f"Converting {filename} to JSON...")
                success = FileHandler.convert_csv_to_json(csv_full_path)
                
                if not success:
                    QMessageBox.warning(self, "Conversion Error", "Gagal mengonversi CSV ke JSON. Cek format CSV.")
                    self.statusBar().showMessage("Conversion Failed")
                    return
                
                # Kita tidak refresh library agar JSON tidak muncul (karena kita hide JSON)
            else:
                QMessageBox.warning(self, "Error", f"File sumber tidak ditemukan:\n{csv_full_path}")
                return

        # 5. Proses Upload
        self.statusBar().showMessage(f"Uploading {json_filename}...")
        
        # Ambil label dari nama file
        label = json_filename.split('_')[0].split('-')[0] 
        
        is_uploaded, msg = FileHandler.upload_to_edge_impulse(json_full_path, api_key, label)
        
        if is_uploaded:
            QMessageBox.information(self, "Success", f"Berhasil Upload ke Edge Impulse!\nFile: {json_filename}\nResponse: {msg}")
            self.statusBar().showMessage("Upload Library Success")
        else:
            QMessageBox.critical(self, "Failed", f"Gagal Upload:\n{msg}")
            self.statusBar().showMessage("Upload Library Failed")

    def on_clear_plot(self):
        if QMessageBox.question(self, "Confirm", "Clear data?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.plot_widget.clear_data()
            self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
            self.sampling_times = []

    def closeEvent(self, event):
        if self.network_worker: self.network_worker.stop()
        if self.serial_connection: self.serial_connection.close()
        event.accept()