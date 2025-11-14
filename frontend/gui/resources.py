"""Application resources and constants"""

from enum import Enum
from config.constants import SENSOR_NAMES, SAMPLE_TYPES, PLOT_COLORS

class SensorStatus(Enum):
    """Sensor connection status"""
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting..."
    CONNECTED = "Connected"
    ERROR = "Error"

class SamplingState(Enum):
    """Application sampling state"""
    IDLE = "Idle"
    SAMPLING = "Sampling"
    PAUSED = "Paused"
    STOPPED = "Stopped"

class DataSource(Enum):
    """Data source types"""
    SERIAL = "Serial (Arduino)"
    SIMULATION = "Simulation"
    FILE = "File"

def get_sensor_color(sensor_index: int) -> str:
    """Get color for specific sensor"""
    if sensor_index < len(PLOT_COLORS):
        return PLOT_COLORS[sensor_index]
    return PLOT_COLORS[sensor_index % len(PLOT_COLORS)]

def get_sensor_name(sensor_index: int) -> str:
    """Get name for specific sensor"""
    if sensor_index < len(SENSOR_NAMES):
        return SENSOR_NAMES[sensor_index]
    return f"Sensor {sensor_index + 1}"
