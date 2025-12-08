from PySide6.QtWidgets import QWidget, QVBoxLayout
from gui.widgets import SensorPlot

class DashboardPage(QWidget):
    """
    Halaman 1: Dashboard Grafik Real-time
    Fokus hanya menampilkan visualisasi data sensor.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Widget Grafik dari widgets.py
        self.plot_widget = SensorPlot("Real-Time Sensor Data")
        self.layout.addWidget(self.plot_widget)
        
    def update_plot(self, time: float, sensor_values: list):
        """Dipanggil oleh MainWindow saat ada data masuk dari Rust"""
        self.plot_widget.add_data_point(time, sensor_values)
        
    def clear_plot(self):
        """Reset grafik saat tombol Clear ditekan atau Start baru"""
        self.plot_widget.clear_data()