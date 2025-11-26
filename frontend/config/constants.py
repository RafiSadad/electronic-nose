"""Application constants and configuration"""

# Application Info
APP_NAME = "Electronic Nose Visualizer | Kelompok 6 SPS (Multichannel + MiCS)"
APP_VERSION = "1.2.0" # Updated version
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Serial Communication
DEFAULT_BAUD_RATE = 9600
SERIAL_TIMEOUT = 1
SERIAL_BUFFER_SIZE = 1024

# Data Collection
# UPDATE: Dinaikkan ke 20.000 untuk support durasi >30 menit tanpa hilang
MAX_PLOT_POINTS = 20000 

# UPDATE: Diubah ke 250ms agar sinkron dengan Arduino (4Hz)
# Ini penting agar sumbu waktu di grafik akurat (Real-Time)
UPDATE_INTERVAL = 250  

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

# Cute Pastel Colors for plotting 🌸
PLOT_COLORS = [
    '#FF9AA2',  # Pastel Red
    '#B5EAD7',  # Pastel Mint
    '#C7CEEA',  # Pastel Periwinkle
    '#FFDAC1',  # Pastel Peach
    '#E2F0CB',  # Pastel Lime
    '#FFB7B2',  # Pastel Salmon
    '#E0BBE4'   # Pastel Lavender
]

# Status messages
STATUS_DISCONNECTED = "Disconnected"
STATUS_CONNECTED = "Connected"
STATUS_SAMPLING = "Sampling..."
STATUS_ERROR = "Error"

# Sample types (Flower Theme 🌺)
SAMPLE_TYPES = [
    "Bunga Kenanga",
    "Bunga Melati",
    "Bunga Mawar",
    "Bunga Sedap Malam"
]