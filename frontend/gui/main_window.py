import json
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QListWidget, 
    QStackedWidget, QMessageBox
)
from PySide6.QtCore import Slot

# Import Config & Utils
from config.constants import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, 
    DATA_PORT, CMD_PORT, UPDATE_INTERVAL, 
    NUM_SENSORS, SENSOR_NAMES, STATUS_COLORS
)
from utils.network_comm import NetworkWorker, BridgeCommander
from utils.file_handler import FileHandler
# Import Styles
from gui.styles import STYLESHEET

# Import Halaman
from gui.pages.dashboard_page import DashboardPage
from gui.pages.control_page import ControlPage
from gui.pages.library_page import LibraryPage
from gui.pages.stats_page import StatsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Terapkan Tema Floral/Cute
        self.setStyleSheet(STYLESHEET)
        
        # State Management
        self.is_sampling = False
        self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
        self.sampling_times = []
        self.start_time = 0.0
        
        # Network Modules
        self.network_worker = None
        self.commander = BridgeCommander(port=CMD_PORT) # Inisialisasi Commander

        # --- UI SETUP ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Navigation
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        # Sidebar Style (Override sedikit agar pas dengan tema Floral)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #FFF0F5;
                color: #5D4037;
                font-size: 14px;
                border-right: 2px solid #F8BBD0;
                padding-top: 10px;
            }
            QListWidget::item {
                height: 50px;
                padding-left: 15px;
                border-bottom: 1px solid #FFC1E3;
            }
            QListWidget::item:selected {
                background-color: #F48FB1;
                color: #FFFFFF;
                font-weight: bold;
                border-left: 5px solid #E91E63;
            }
            QListWidget::item:hover {
                background-color: #FFC1E3;
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

        # 2. Main Content Area
        self.pages = QStackedWidget()
        
        self.page_dashboard = DashboardPage()
        self.page_control = ControlPage()
        self.page_library = LibraryPage()
        self.page_stats = StatsPage()
        
        self.pages.addWidget(self.page_dashboard)
        self.pages.addWidget(self.page_control)
        self.pages.addWidget(self.page_library)
        self.pages.addWidget(self.page_stats)
        
        main_layout.addWidget(self.pages)
        
        # Connect Signals from Control Page
        self.page_control.request_connect.connect(self.on_connect_request)
        self.page_control.request_start.connect(self.on_start_request)
        self.page_control.request_stop.connect(self.on_stop_request)
        self.page_control.request_save.connect(self.on_save_request)
        self.page_control.request_clear.connect(self.on_clear_request)
        
        self.sidebar.setCurrentRow(0)

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)

    # ================= LOGIC KONEKSI (BRIDGE) =================
    @Slot()
    def on_connect_request(self):
        """Handle tombol Connect/Disconnect"""
        settings = self.page_control.get_connection_settings()
        host = settings['host']
        port_name = settings['serial_port']
        
        # Update IP Commander
        self.commander.host = host

        # Cek apakah kita mau Connect atau Disconnect?
        # Kita cek text tombol di Control Page
        # (Cara lebih robust: simpan state di variable, tapi ini shortcut UI)
        current_btn_text = self.page_control.conn_panel.connect_btn.text()
        
        if "Disconnect" in current_btn_text:
            # ---> REQ DISCONNECT
            if self.commander.disconnect_serial():
                self.page_control.set_status("Disconnecting...", STATUS_COLORS['disconnected'])
                # Stop worker data
                if self.network_worker:
                    self.network_worker.stop()
            
            # Reset UI segera (Optimistic update)
            self.page_control.conn_panel.connect_btn.setText("✨ Connect Bridge")
            self.page_control.conn_panel.port_selector.setEnabled(True)
            self.page_control.set_status("Disconnected", STATUS_COLORS['disconnected'])

        else:
            # ---> REQ CONNECT
            if port_name == "No Ports":
                QMessageBox.warning(self, "Warning", "Tidak ada Port Serial yang dipilih!")
                return

            self.page_control.set_status("Connecting...", STATUS_COLORS['sampling'])
            
            # 1. Kirim Perintah ke Rust
            if self.commander.connect_serial(port_name):
                # 2. Nyalakan Worker Penerima Data
                if self.network_worker: 
                    self.network_worker.stop()
                    
                self.network_worker = NetworkWorker(host=host, port=DATA_PORT)
                self.network_worker.data_received.connect(self.on_data_received)
                self.network_worker.connection_status.connect(self.on_connection_status)
                self.network_worker.start()
                
                print(f"✅ Request Sent: Connect to {port_name}")
            else:
                QMessageBox.critical(self, "Error", "Gagal menghubungi Backend Rust (Port 8082).\nPastikan 'cargo run' sudah jalan!")
                self.page_control.set_status("Bridge Error", STATUS_COLORS['disconnected'])

    def on_connection_status(self, connected):
        """Callback saat socket data (8083) terhubung/putus"""
        self.page_control.enable_controls(connected, self.is_sampling)
        
        if connected:
            self.page_control.set_status("Bridge Connected", STATUS_COLORS['connected'])
            self.page_control.conn_panel.connect_btn.setText("🛑 Disconnect")
            self.page_control.conn_panel.port_selector.setEnabled(False)
        else:
            # Jika putus tiba-tiba
            self.page_control.set_status("Disconnected", STATUS_COLORS['disconnected'])
            self.page_control.conn_panel.connect_btn.setText("✨ Connect Bridge")
            self.page_control.conn_panel.port_selector.setEnabled(True)

    # ================= LOGIC SAMPLING =================
    @Slot()
    def on_start_request(self):
        # Kirim START ke Rust
        if self.commander.start_sampling():
            # Reset Data
            self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
            self.sampling_times = []
            self.start_time = 0.0
            
            # Clear UI
            self.page_dashboard.clear_plot()
            self.page_stats.clear_stats()
            
            # Update UI State
            self.is_sampling = True
            self.page_control.enable_controls(True, True)
            self.page_control.set_status("Sampling...", STATUS_COLORS['sampling'])
            
            # Update Info
            info = self.page_control.get_sample_info()
            self.page_control.update_info(0, info['name'])
            self.page_control.update_info(1, info['type'])

    @Slot()
    def on_stop_request(self):
        # Kirim STOP ke Rust
        self.commander.stop_sampling()
        
        # Update UI State
        self.is_sampling = False
        self.page_control.enable_controls(True, False)
        self.page_control.set_status("Bridge Connected", STATUS_COLORS['connected'])

    def on_data_received(self, data):
        """Menerima Data JSON dari Rust"""
        try:
            # Parse Data
            vals = [
                float(data.get('no2', 0)), float(data.get('eth', 0)),
                float(data.get('voc', 0)), float(data.get('co', 0)),
                float(data.get('co_mics', 0)), float(data.get('eth_mics', 0)),
                float(data.get('voc_mics', 0))
            ]
            state_idx = int(data.get('state', 0))

            if self.is_sampling:
                # Timer
                if not self.sampling_times: self.start_time = 0
                else: self.start_time += UPDATE_INTERVAL / 1000.0
                
                # Simpan Data
                self.sampling_times.append(self.start_time)
                for i, v in enumerate(vals[:NUM_SENSORS]):
                    self.sampling_data[i].append(v)

                # Update Halaman
                self.page_dashboard.update_plot(self.start_time, vals)
                self.page_stats.update_statistics(self.sampling_data)
                
                # Update Info Panel
                self.page_control.update_info(3, len(self.sampling_times))
                self.page_control.update_info(4, f"{self.start_time:.2f} s")

                # Auto Stop Check (Jika FSM Rust bilang DONE / state 6)
                if state_idx == 6: 
                    self.on_stop_request()
                    QMessageBox.information(self, "Selesai", "Proses Sampling Selesai!")

        except Exception as e:
            print(f"Data Error: {e}")

    # ================= LOGIC SAVE & CLEAR =================
    @Slot()
    def on_save_request(self):
        if not self.sampling_times:
            QMessageBox.warning(self, "Empty", "Belum ada data untuk disimpan!")
            return
            
        info = self.page_control.get_sample_info()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{info['name'].replace(' ', '_')}_{timestamp}.csv"
        
        try:
            FileHandler.save_as_csv(
                filename, info, self.sampling_data, 
                self.sampling_times, SENSOR_NAMES
            )
            QMessageBox.information(self, "Success", f"Data tersimpan di:\n{filename}")
            self.page_library.refresh_library()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal simpan: {e}")

    @Slot()
    def on_clear_request(self):
        if self.is_sampling:
            QMessageBox.warning(self, "Hold on", "Stop sampling dulu sebelum clear!")
            return

        if QMessageBox.question(self, "Reset", "Hapus semua grafik?") == QMessageBox.Yes:
            self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
            self.sampling_times = []
            self.start_time = 0.0
            
            self.page_dashboard.clear_plot()
            self.page_stats.clear_stats()
            self.page_control.update_info(3, "0")
            self.page_control.update_info(4, "0 s")

    def closeEvent(self, event):
        if self.network_worker: 
            self.network_worker.stop()
        try:
            self.commander.disconnect_serial()
        except: pass
        event.accept()