"""Application constants and configuration - BRIDGE MODE"""

# Application Info
APP_NAME = "E-Nose Bridge Control | Kelompok 6 SPS"
APP_VERSION = "2.0.0 (Bridge)"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Network Configuration (PENTING!)
DEFAULT_HOST = "127.0.0.1" # Ganti ke IP PC jika diakses dari luar
CMD_PORT = 8082            # Port untuk Kirim Perintah (Start/Stop/Connect)
DATA_PORT = 8083           # Port untuk Terima Data Sensor

# Data Collection
UPDATE_INTERVAL = 250      # ms (Sesuai Arduino 4Hz)
NUM_SENSORS = 7

# Sensor Names (Sesuai main.ino)
SENSOR_NAMES = [
    "GM-NO2 (Nitrogen Dioxide)",
    "GM-C2H5OH (Ethanol)",
    "GM-VOC (Volatile Org)",
    "GM-CO (Carbon Monoxide)",
    "MiCS-CO (Approximation)",
    "MiCS-Ethanol (Approximation)",
    "MiCS-VOC (Approximation)"
]

# Plot Colors
PLOT_COLORS = ['#FF9AA2', '#B5EAD7', '#C7CEEA', '#FFDAC1', '#E2F0CB', '#FFB7B2', '#E0BBE4']

# Status Colors
STATUS_COLORS = {
    'connected': "#4CAF50",    # Green
    'disconnected': "#F44336", # Red
    'sampling': "#2196F3"      # Blue
}

SAMPLE_TYPES = ["Bunga Kenanga", "Bunga Melati", "Bunga Mawar", "Bunga Sedap Malam"]