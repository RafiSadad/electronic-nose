"""Application constants and configuration - BRIDGE MODE"""

# Application Info
APP_NAME = "E-Nose Bridge Control | Kelompok 6 SPS"
APP_VERSION = "2.0.0 (Bridge)"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Network Configuration (PENTING untuk Bridge Mode)
DEFAULT_HOST = "127.0.0.1" # Ganti ke IP PC jika akses remote
CMD_PORT = 8082            # Port Perintah (Start/Stop/Connect)
DATA_PORT = 8083           # Port Data Stream

# Data Collection
UPDATE_INTERVAL = 250      # ms (Sesuai refresh rate Arduino)
NUM_SENSORS = 7
MAX_PLOT_POINTS = 20000    # <--- INI YANG HILANG SEBELUMNYA

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
PLOT_COLORS = [
    '#FF9AA2', # Pastel Red
    '#B5EAD7', # Pastel Mint
    '#C7CEEA', # Pastel Periwinkle
    '#FFDAC1', # Pastel Peach
    '#E2F0CB', # Pastel Lime
    '#FFB7B2', # Pastel Salmon
    '#E0BBE4'  # Pastel Lavender
]

# Status Colors
STATUS_COLORS = {
    'connected': "#4CAF50",    # Green
    'disconnected': "#F44336", # Red
    'sampling': "#2196F3"      # Blue
}

# Sample Types
SAMPLE_TYPES = [
    "Bunga Kenanga",
    "Bunga Melati",
    "Bunga Mawar",
    "Bunga Sedap Malam"
]