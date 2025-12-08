import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QFont
from config.constants import NUM_SENSORS, SENSOR_NAMES

class StatsPage(QWidget):
    """
    Halaman 4: Statistics
    Menampilkan statistik real-time (Min, Max, Mean, Std Dev) dari data sensor.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # Header
        title = QLabel("📊 Data Statistics")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.layout.addWidget(title)
        
        # Table
        self.stats_table = QTableWidget(NUM_SENSORS, 5)
        self.stats_table.setHorizontalHeaderLabels(["Sensor", "Min", "Max", "Mean", "Std Dev"])
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.setAlternatingRowColors(True)
        
        # Styling Table
        header = self.stats_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch) # Sensor Name wider
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
            
        self.populate_rows()
        self.layout.addWidget(self.stats_table)

    def populate_rows(self):
        """Isi nama sensor awal"""
        for row in range(NUM_SENSORS):
            # Ambil nama sensor
            name = SENSOR_NAMES[row] if row < len(SENSOR_NAMES) else f"Sensor {row+1}"
            self.stats_table.setItem(row, 0, QTableWidgetItem(name))
            
            # Init values with 0
            for col in range(1, 5):
                self.stats_table.setItem(row, col, QTableWidgetItem("0.00"))

    def update_statistics(self, sampling_data: dict):
        """
        Hitung statistik dari data yang terkumpul dan update tabel.
        sampling_data: dict {0: [val1, val2...], 1: [...]}
        """
        # Cek apakah ada data di sensor pertama, jika kosong skip
        if not sampling_data or not sampling_data[0]:
            return

        for sensor_idx, values in sampling_data.items():
            if not values:
                continue
            
            # Convert ke numpy array biar cepat hitungnya
            arr = np.array(values)
            
            v_min = np.min(arr)
            v_max = np.max(arr)
            v_mean = np.mean(arr)
            v_std = np.std(arr)
            
            # Update Table (Kolom 1=Min, 2=Max, 3=Mean, 4=Std)
            self.stats_table.setItem(sensor_idx, 1, QTableWidgetItem(f"{v_min:.2f}"))
            self.stats_table.setItem(sensor_idx, 2, QTableWidgetItem(f"{v_max:.2f}"))
            self.stats_table.setItem(sensor_idx, 3, QTableWidgetItem(f"{v_mean:.2f}"))
            self.stats_table.setItem(sensor_idx, 4, QTableWidgetItem(f"{v_std:.2f}"))
            
    def clear_stats(self):
        """Reset nilai ke 0"""
        for row in range(NUM_SENSORS):
            for col in range(1, 5):
                self.stats_table.setItem(row, col, QTableWidgetItem("0.00"))