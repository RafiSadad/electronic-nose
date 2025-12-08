from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal
from gui.widgets import ControlPanel, ConnectionPanel

class ControlPage(QWidget):
    """
    Halaman 2: Control Panel
    Berisi setting koneksi Bridge, tombol Start/Stop/Save/Clear, dan Info Sampling.
    """
    # Signal untuk komunikasi ke MainWindow
    request_connect = Signal()
    request_start = Signal()
    request_stop = Signal()
    request_save = Signal()
    request_clear = Signal() # Signal untuk tombol Clear
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # 1. Connection Panel
        self.conn_panel = ConnectionPanel()
        self.conn_panel.connect_clicked.connect(self.request_connect.emit)
        self.layout.addWidget(self.conn_panel)
        
        # 2. Control Panel (Start/Stop/Save/Clear)
        self.ctrl_panel = ControlPanel()
        self.ctrl_panel.start_clicked.connect(self.request_start.emit)
        self.ctrl_panel.stop_clicked.connect(self.request_stop.emit)
        self.ctrl_panel.save_clicked.connect(self.request_save.emit)
        self.ctrl_panel.clear_clicked.connect(self.request_clear.emit) # Sambungkan tombol clear
        self.layout.addWidget(self.ctrl_panel)
        
        # 3. Info Table
        info_label = QLabel("📈 Sampling Information")
        info_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.layout.addWidget(info_label)
        
        self.info_table = QTableWidget(5, 2)
        self.info_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.info_table.setColumnWidth(0, 150)
        self.info_table.setColumnWidth(1, 300)
        self.populate_info_table()
        self.layout.addWidget(self.info_table)
        
        self.layout.addStretch()

    def populate_info_table(self):
        info = {
            "Sample Name": "None", 
            "Sample Type": "None", 
            "Mode": "Auto (FSM)", 
            "Points": "0", 
            "Time": "0 s"
        }
        for row, (key, value) in enumerate(info.items()):
            self.info_table.setItem(row, 0, QTableWidgetItem(key))
            self.info_table.setItem(row, 1, QTableWidgetItem(value))

    def update_info(self, key_idx, value):
        """Helper untuk update baris tabel tertentu"""
        self.info_table.setItem(key_idx, 1, QTableWidgetItem(str(value)))
        
    def get_connection_settings(self):
        return self.conn_panel.get_connection_settings()
        
    def get_sample_info(self):
        return self.ctrl_panel.get_sample_info()

    def set_status(self, text, color):
        self.conn_panel.set_status(text, color)
        
    def enable_controls(self, is_connected, is_sampling):
        """Mengatur enable/disable tombol secara otomatis"""
        # Connection button
        self.conn_panel.connect_btn.setEnabled(not is_connected)
        self.conn_panel.connect_btn.setText("Connected" if is_connected else "Connect Bridge")
        
        # Start/Stop buttons
        self.ctrl_panel.enable_start(is_connected and not is_sampling)
        self.ctrl_panel.enable_stop(is_connected and is_sampling)