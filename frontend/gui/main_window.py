import socket
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QListWidget, 
    QStackedWidget, QMessageBox
)
from PySide6.QtGui import QIcon

# Import Config & Utils
from config.constants import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, 
    CMD_PORT, DATA_PORT, UPDATE_INTERVAL, 
    NUM_SENSORS, SENSOR_NAMES, STATUS_COLORS
)
from utils.network_comm import NetworkWorker
from utils.file_handler import FileHandler

# Import Halaman-Halaman Baru
from gui.pages.dashboard_page import DashboardPage
from gui.pages.control_page import ControlPage
from gui.pages.library_page import LibraryPage
from gui.pages.stats_page import StatsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # State Management (Pusat Data)
        self.is_sampling = False
        self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
        self.sampling_times = []
        self.start_time = 0.0
        self.network_worker = None

        # --- UI SETUP ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Navigation (Menu Kiri)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        # Styling Sidebar ala Modern Dashboard
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #2E3440;
                color: white;
                font-size: 14px;
                outline: 0;
                border: none;
                padding-top: 10px;
            }
            QListWidget::item {
                height: 50px;
                padding-left: 15px;
                border-bottom: 1px solid #3B4252;
            }
            QListWidget::item:selected {
                background-color: #88C0D0;
                color: #2E3440;
                font-weight: bold;
                border-left: 5px solid #ECEFF4;
            }
            QListWidget::item:hover {
                background-color: #4C566A;
            }
        """)
        
        menu_items = [
            "📊  Dashboard", 
            "⚙️  Control Panel", 
            "📚  Data Library", 
            "📈  Statistics"
        ]
        self.sidebar.addItems(menu_items)
        self.sidebar.currentRowChanged.connect(self.switch_page)
        main_layout.addWidget(self.sidebar)

        # 2. Main Content Area (Tumpukan Halaman)
        self.pages = QStackedWidget()
        
        # Inisialisasi Halaman
        self.page_dashboard = DashboardPage()
        self.page_control = ControlPage()
        self.page_library = LibraryPage()
        self.page_stats = StatsPage()
        
        # Urutan Index Sesuai Sidebar
        self.pages.addWidget(self.page_dashboard)  # Index 0
        self.pages.addWidget(self.page_control)    # Index 1
        self.pages.addWidget(self.page_library)    # Index 2
        self.pages.addWidget(self.page_stats)      # Index 3
        
        main_layout.addWidget(self.pages)
        
        # --- MENGHUBUNGKAN SIGNAL ANTAR HALAMAN ---
        # Saat tombol ditekan di ControlPage, MainWindow yang merespon
        self.page_control.request_connect.connect(self.on_connect_request)
        self.page_control.request_start.connect(self.on_start_request)
        self.page_control.request_stop.connect(self.on_stop_request)
        self.page_control.request_save.connect(self.on_save_request)
        self.page_control.request_clear.connect(self.on_clear_request)
        
        # Default Page
        self.sidebar.setCurrentRow(0)

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)

    # ================= LOGIC KONEKSI (BRIDGE) =================
    def on_connect_request(self):
        settings = self.page_control.get_connection_settings()
        host = settings['host']
        serial_port = settings['serial_port']

        # Reset Worker jika ada
        if self.network_worker:
            self.network_worker.stop()
            self.network_worker.wait()
            self.network_worker = None

        self.page_control.set_status("Connecting...", STATUS_COLORS['sampling'])
        
        # 1. Start Worker Data Stream (Port 8083)
        self.network_worker = NetworkWorker(host=host, port=DATA_PORT)
        self.network_worker.data_received.connect(self.on_data_received)
        self.network_worker.connection_status.connect(self.on_connection_status)
        self.network_worker.start()

        # 2. Kirim Config ke Rust (Port 8082)
        if serial_port and serial_port != "No Ports":
            if self.send_tcp_command(host, f"CONNECT_SERIAL {serial_port}"):
                print(f"✅ Config sent to Rust: Connect to {serial_port}")
            else:
                QMessageBox.warning(self, "Error", "Gagal kontak Backend Rust (Port 8082)!")
        else:
            QMessageBox.warning(self, "Warning", "Pilih Port dulu!")

    def on_connection_status(self, connected):
        self.page_control.enable_controls(connected, self.is_sampling)
        if connected:
            self.page_control.set_status("System Online", STATUS_COLORS['connected'])
        else:
            self.page_control.set_status("Disconnected", STATUS_COLORS['disconnected'])

    def send_tcp_command(self, host, cmd):
        """Helper kirim command ke Port 8082"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((host, CMD_PORT))
                s.sendall(f"{cmd}\n".encode())
                return True
        except Exception as e:
            print(f"CMD Error: {e}")
            return False

    # ================= LOGIC SAMPLING =================
    def on_start_request(self):
        settings = self.page_control.get_connection_settings()
        
        # Kirim START ke Rust
        if self.send_tcp_command(settings['host'], "START_SAMPLING"):
            # Reset Data Global
            self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
            self.sampling_times = []
            self.start_time = 0.0
            
            # Reset Tampilan Halaman
            self.page_dashboard.clear_plot()
            self.page_stats.clear_stats()
            
            # Update State
            self.is_sampling = True
            self.page_control.enable_controls(True, True)
            self.page_control.set_status("Sampling...", STATUS_COLORS['sampling'])
            
            # Update Info di Control Page
            sample_info = self.page_control.get_sample_info()
            self.page_control.update_info(0, sample_info['name'])
            self.page_control.update_info(1, sample_info['type'])

    def on_stop_request(self):
        settings = self.page_control.get_connection_settings()
        
        # Kirim STOP ke Rust
        self.send_tcp_command(settings['host'], "STOP_SAMPLING")
        
        # Update State
        self.is_sampling = False
        self.page_control.enable_controls(True, False)
        self.page_control.set_status("System Online", STATUS_COLORS['connected'])

    def on_data_received(self, data):
        """Pusat Distribusi Data"""
        try:
            # Parse values
            vals = [
                float(data.get('no2', 0)), float(data.get('eth', 0)),
                float(data.get('voc', 0)), float(data.get('co', 0)),
                float(data.get('co_mics', 0)), float(data.get('eth_mics', 0)),
                float(data.get('voc_mics', 0))
            ]
            state_idx = int(data.get('state', 0))

            if self.is_sampling:
                # Time increment
                if not self.sampling_times: self.start_time = 0
                else: self.start_time += UPDATE_INTERVAL / 1000.0
                
                # Simpan ke Global State
                self.sampling_times.append(self.start_time)
                for i, v in enumerate(vals[:NUM_SENSORS]):
                    self.sampling_data[i].append(v)

                # --- DISTRIBUSI KE HALAMAN ---
                # 1. Dashboard (Update Grafik)
                self.page_dashboard.update_plot(self.start_time, vals)
                
                # 2. Stats (Hitung Statistik)
                self.page_stats.update_statistics(self.sampling_data)
                
                # 3. Control (Update Info Tabel)
                self.page_control.update_info(3, len(self.sampling_times)) # Points
                self.page_control.update_info(4, f"{self.start_time:.2f} s") # Time

                # Auto Stop Check (Jika Arduino bilang DONE)
                if state_idx == 6: 
                    self.on_stop_request()
                    QMessageBox.information(self, "Info", "Sampling Selesai (FSM Done)!")

        except Exception as e:
            print(f"Data Error: {e}")

    # ================= LOGIC SAVE & CLEAR =================
    def on_save_request(self):
        if not self.sampling_times:
            QMessageBox.warning(self, "Warning", "Belum ada data untuk disimpan!")
            return
            
        sample_info = self.page_control.get_sample_info()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{sample_info['name'].replace(' ', '_')}_{timestamp}.csv"
        
        try:
            FileHandler.save_as_csv(
                filename, sample_info, self.sampling_data, 
                self.sampling_times, SENSOR_NAMES
            )
            QMessageBox.information(self, "Success", f"Data berhasil disimpan:\n{filename}")
            
            # Refresh Library agar file baru muncul di sana
            self.page_library.refresh_library()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal simpan: {e}")

    def on_clear_request(self):
        """Menghapus data di memori dan grafik"""
        if self.is_sampling:
            QMessageBox.warning(self, "Warning", "Stop sampling dulu sebelum clear!")
            return

        reply = QMessageBox.question(
            self, "Konfirmasi", 
            "Hapus semua data grafik dan statistik?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 1. Reset Data Global
            self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
            self.sampling_times = []
            self.start_time = 0.0
            
            # 2. Reset Tampilan Halaman
            self.page_dashboard.clear_plot()
            self.page_stats.clear_stats()
            
            # 3. Reset Info di Control Panel
            self.page_control.update_info(3, "0")   # Points
            self.page_control.update_info(4, "0 s") # Time
            
            QMessageBox.information(self, "Info", "Data berhasil dihapus.")

    def closeEvent(self, event):
        """Cleanup saat aplikasi ditutup"""
        if self.network_worker: 
            self.network_worker.stop()
        
        # Disconnect Serial di Backend (Good Practice)
        try:
            settings = self.page_control.get_connection_settings()
            self.send_tcp_command(settings['host'], "DISCONNECT_SERIAL")
        except: pass
        
        event.accept()