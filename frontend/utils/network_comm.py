"""Network communication utilities - JSON STREAM READER"""
import socket
import json
import time
from PySide6.QtCore import QThread, Signal

class NetworkWorker(QThread):
    """
    Worker khusus untuk mendengarkan Data Stream dari Rust (Port 8083).
    Otomatis parsing JSON line-by-line.
    """
    
    data_received = Signal(dict)
    error_occurred = Signal(str)
    connection_status = Signal(bool)
    
    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        self.is_running = False
        self.sock = None
    
    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(5.0) # Timeout connect
                self.sock.connect((self.host, self.port))
                
                # Berhasil Konek
                self.connection_status.emit(True)
                self.sock.settimeout(None) # Blocking mode untuk read
                
                # Stream Reader
                file_obj = self.sock.makefile('r', encoding='utf-8')
                
                while self.is_running:
                    try:
                        line = file_obj.readline()
                        if not line: break # Server putus
                        
                        # Parse JSON dari Rust
                        data = json.loads(line.strip())
                        self.data_received.emit(data)
                        
                    except (json.JSONDecodeError, socket.error):
                        break
                        
            except Exception as e:
                self.connection_status.emit(False)
                # self.error_occurred.emit(f"Connecting to {self.host}:{self.port}...")
                time.sleep(2) # Retry delay
                
            finally:
                self.cleanup()
                self.connection_status.emit(False)
    
    def cleanup(self):
        if self.sock:
            try: self.sock.close()
            except: pass
            self.sock = None

    def stop(self):
        self.is_running = False
        self.cleanup()