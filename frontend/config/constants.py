"""Application constants and configuration"""

# Application Info
APP_NAME = "Electronic Nose Visualizer | Kelompok 6 SPS (Sample Bunga)"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Serial Communication
DEFAULT_BAUD_RATE = 9600
SERIAL_TIMEOUT = 1
SERIAL_BUFFER_SIZE = 1024

# Data Collection
MAX_PLOT_POINTS = 500
UPDATE_INTERVAL = 100  # milliseconds
NUM_SENSORS = 4

# Sensor Names
SENSOR_NAMES = [
    "Sensor 1 (MQ-4)",
    "Sensor 2 (MQ-135)",
    "Sensor 3 (MQ-6)",
    "Sensor 4 (MQ-7)"
]

# Cute Pastel Colors for plotting 🌸
PLOT_COLORS = [
    '#FF9AA2',  # Pastel Red/Pink
    '#B5EAD7',  # Pastel Mint
    '#C7CEEA',  # Pastel Periwinkle
    '#FFDAC1'   # Pastel Peach
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