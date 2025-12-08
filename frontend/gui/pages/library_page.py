import os
import glob
import subprocess
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QLineEdit, QMessageBox, QMenu
)
from PySide6.QtGui import QFont, QIcon, QAction
from PySide6.QtCore import Qt, QSize

from utils.file_handler import FileHandler

class LibraryPage(QWidget):
    """
    Halaman 3: Data Library
    Manajemen file CSV: Preview, Plotting, dan Upload ke Edge Impulse.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # --- HEADER & TOOLBAR ---
        toolbar_layout = QHBoxLayout()
        
        title_label = QLabel("📂 Data Library")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        toolbar_layout.addWidget(title_label)
        
        toolbar_layout.addStretch()
        
        # API Key Input
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Edge Impulse API Key...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setFixedWidth(200)
        toolbar_layout.addWidget(self.api_key_input)
        
        # Upload Button
        self.upload_btn = QPushButton("☁️ Upload to EI")
        self.upload_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.upload_btn.setToolTip("Upload file terpilih ke Edge Impulse")
        self.upload_btn.clicked.connect(self.on_upload_click)
        toolbar_layout.addWidget(self.upload_btn)
        
        # Refresh Button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_library)
        toolbar_layout.addWidget(self.refresh_btn)
        
        self.layout.addLayout(toolbar_layout)
        
        # --- TABLE WIDGET ---
        self.lib_table = QTableWidget(0, 4)
        self.lib_table.setHorizontalHeaderLabels(["Preview", "Filename", "Last Modified", "Size"])
        self.lib_table.setIconSize(QSize(160, 90)) # Thumbnail size
        
        # Table Styling
        header = self.lib_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.lib_table.setColumnWidth(0, 180) # Lebar kolom preview
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.lib_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lib_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lib_table.cellDoubleClicked.connect(self.on_double_click)
        
        self.layout.addWidget(self.lib_table)
        
        # Load data awal
        self.refresh_library()

    def refresh_library(self):
        """Scan folder data/ dan update tabel"""
        self.lib_table.setRowCount(0)
        if not os.path.exists("data"):
            os.makedirs("data") # Buat jika belum ada
            return
            
        files = glob.glob("data/*.csv")
        files.sort(key=os.path.getmtime, reverse=True)
        
        for file_path in files:
            row = self.lib_table.rowCount()
            self.lib_table.insertRow(row)
            self.lib_table.setRowHeight(row, 100)
            
            filename = os.path.basename(file_path)
            
            # 1. Preview (Cari PNG)
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
            
            # 2. Filename
            self.lib_table.setItem(row, 1, QTableWidgetItem(filename))
            
            # 3. Last Modified
            timestamp = os.path.getmtime(file_path)
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            self.lib_table.setItem(row, 2, QTableWidgetItem(date_str))
            
            # 4. Size
            size_kb = os.path.getsize(file_path) / 1024
            self.lib_table.setItem(row, 3, QTableWidgetItem(f"{size_kb:.1f} KB"))

    def on_double_click(self, row, col):
        """Buka plot interaktif Gnuplot saat double click"""
        item = self.lib_table.item(row, 1)
        if item:
            filename = item.text()
            full_path = os.path.join("data", filename)
            self.open_interactive_plot(full_path)

    def open_interactive_plot(self, csv_filename):
        # Generate PNG dulu biar preview update
        self.generate_png(csv_filename)
        
        script_interactive = "plot_interactive.plt"
        # Cek lokasi script plt
        if not os.path.exists(script_interactive) and os.path.exists(f"data/{script_interactive}"):
             script_interactive = f"data/{script_interactive}"
        
        try:
            # Panggil Gnuplot eksternal
            subprocess.Popen(["gnuplot", "-p", "-c", script_interactive, csv_filename])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuka Gnuplot:\n{str(e)}")
            
        self.refresh_library() # Refresh biar preview muncul

    def generate_png(self, csv_filename):
        """Helper generate PNG di background"""
        script_png = "plot_config.plt"
        if not os.path.exists(script_png) and os.path.exists(f"data/{script_png}"):
             script_png = f"data/{script_png}"
        
        png_filename = csv_filename.replace('.csv', '.png')
        try:
            subprocess.run(["gnuplot", "-c", script_png, csv_filename, png_filename], check=False)
        except: pass

    def on_upload_click(self):
        """Upload file terpilih ke Edge Impulse"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "API Key Missing", "Isi API Key dulu di kolom atas!")
            self.api_key_input.setFocus()
            return

        rows = self.lib_table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Warning", "Pilih file di tabel dulu!")
            return
        
        row_idx = rows[0].row()
        filename = self.lib_table.item(row_idx, 1).text()
        csv_full_path = os.path.join("data", filename)
        
        # Convert ke JSON (Format EI)
        json_filename = filename.replace('.csv', '.json')
        json_full_path = os.path.join("data", json_filename)
        
        if not os.path.exists(json_full_path):
            if os.path.exists(csv_full_path):
                success = FileHandler.convert_csv_to_json(csv_full_path)
                if not success:
                    QMessageBox.warning(self, "Error", "Gagal convert CSV ke JSON.")
                    return
            else:
                return

        # Proses Upload
        label = json_filename.split('_')[0].split('-')[0] # Ambil label dari nama file
        is_uploaded, msg = FileHandler.upload_to_edge_impulse(json_full_path, api_key, label)
        
        if is_uploaded:
            QMessageBox.information(self, "Success", f"Berhasil Upload!\nFile: {json_filename}\nResponse: {msg}")
        else:
            QMessageBox.critical(self, "Failed", f"Gagal Upload:\n{msg}")