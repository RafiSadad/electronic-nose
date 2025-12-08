import sys
import os
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

# Konfigurasi High DPI (Agar tidak buram di layar resolusi tinggi)
if hasattr(sys, 'frozen'):
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
else:
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

def main():
    """Entry point aplikasi"""
    app = QApplication(sys.argv)
    
    # Set Metadata Aplikasi
    app.setApplicationName("E-Nose Bridge Control")
    app.setOrganizationName("Kelompok 6 SPS")
    
    # Styling Global (Opsional, jika ingin font default)
    font = app.font()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    # Load Main Window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()