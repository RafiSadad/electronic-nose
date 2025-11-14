"""Application entry point"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Main function"""
    
    # Create data folder if not exists
    Path("data").mkdir(exist_ok=True)
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Execute application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
