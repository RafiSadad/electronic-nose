"""Serial communication utilities"""

from PySide6.QtCore import QThread, pyqtSignal
import serial
import json

class SerialWorker(QThread):
    """Worker thread for serial communication"""
    
    data_received = pyqtSignal(dict)  # Emit received data
    error_occurred = pyqtSignal(str)  # Emit error message
    connection_status = pyqtSignal(bool)  # Emit connection status
    
    def __init__(self, port: str, baudrate: int = 115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_running = False
    
    def run(self):
        """Main thread execution"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            self.is_running = True
            self.connection_status.emit(True)
            
            while self.is_running:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    if line:
                        try:
                            data = json.loads(line)
                            self.data_received.emit(data)
                        except json.JSONDecodeError:
                            pass
        
        except serial.SerialException as e:
            self.error_occurred.emit(f"Serial error: {str(e)}")
            self.connection_status.emit(False)
    
    def stop(self):
        """Stop the serial worker"""
        self.is_running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
    
    def send_command(self, command: str):
        """Send command to serial device"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(f"{command}\n".encode())
