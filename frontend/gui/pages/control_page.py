from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal
from gui.widgets import ControlPanel, ConnectionPanel

class ControlPage(QWidget):
    # Signals
    request_connect = Signal()
    request_start = Signal()
    request_stop = Signal()
    request_save = Signal()
    request_clear = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # 1. Connection Panel
        self.conn_panel = ConnectionPanel()
        self.conn_panel.connect_clicked.connect(self.request_connect.emit)
        self.layout.addWidget(self.conn_panel)
        
        # 2. Control Panel
        self.ctrl_panel = ControlPanel()
        self.ctrl_panel.start_clicked.connect(self.request_start.emit)
        self.ctrl_panel.stop_clicked.connect(self.request_stop.emit)
        self.ctrl_panel.save_clicked.connect(self.request_save.emit)
        self.ctrl_panel.clear_clicked.connect(self.request_clear.emit)
        self.layout.addWidget(self.ctrl_panel)
        
        # 3. Info Table
        self.layout.addWidget(QLabel("📈 Sampling Stats"))
        self.info_table = QTableWidget(5, 2)
        self.info_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.info_table.horizontalHeader().setStretchLastSection(True)
        self.populate_initial()
        self.layout.addWidget(self.info_table)
        
        self.layout.addStretch()

    def populate_initial(self):
        defaults = {"Name": "-", "Type": "-", "Mode": "Auto", "Points": "0", "Time": "0s"}
        for r, (k, v) in enumerate(defaults.items()):
            self.info_table.setItem(r, 0, QTableWidgetItem(k))
            self.info_table.setItem(r, 1, QTableWidgetItem(v))

    def update_info(self, row, val):
        self.info_table.setItem(row, 1, QTableWidgetItem(str(val)))
        
    def get_connection_settings(self):
        return self.conn_panel.get_connection_settings()
        
    def get_sample_info(self):
        return self.ctrl_panel.get_sample_info()

    def set_status(self, text, color):
        self.conn_panel.set_status(text, color)
        
    def enable_controls(self, connected, sampling):
        self.conn_panel.connect_btn.setEnabled(not connected)
        self.ctrl_panel.enable_start(connected and not sampling)
        self.ctrl_panel.enable_stop(connected and sampling)