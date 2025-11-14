"""Application constants and configuration"""

# Application Info
APP_NAME = "Electronic Nose Visualizer"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Serial Communication
DEFAULT_BAUD_RATE = 115200
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

# Colors for plotting
PLOT_COLORS = [
    '#FF6B6B',  # Red
    '#4ECDC4',  # Teal
    '#45B7D1',  # Blue
    '#FFA07A'   # Salmon
]

# Status messages
STATUS_DISCONNECTED = "Disconnected"
STATUS_CONNECTED = "Connected"
STATUS_SAMPLING = "Sampling..."
STATUS_ERROR = "Error"

# Sample types
SAMPLE_TYPES = [
    "Kopi Arabika",
    "Kopi Robusta",
    "Teh Hijau",
    "Teh Hitam",
    "Tembakau Kering",
    "Bunga Melati",
    "Jeruk",
    "Lainnya"
]
# Default COM ports for selection