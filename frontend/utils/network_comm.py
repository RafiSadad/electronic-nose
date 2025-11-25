"""Network communication utilities (Replaces Serial)"""

from PySide6.QtCore import QThread, Signal
import socket
import json
import time

class NetworkWorker(QThread):
    """Worker thread for Network communication with Rust Backend"""
    
    data_received = Signal(dict)
    error_occurred = Signal(str)
    connection_status = Signal(bool)
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8082):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = None
        self.is_running = False
    
    def run(self):
        """Main thread execution"""
        self.is_running = True
        
        while self.is_running:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(5.0)
                self.sock.connect((self.host, self.port))
                
                self.connection_status.emit(True)
                self.error_occurred.emit(f"Connected to Backend {self.host}:{self.port}")
                
                # Buffer untuk stream
                file_obj = self.sock.makefile('r', encoding='utf-8')
                
                while self.is_running:
                    line = file_obj.readline()
                    if not line:
                        break # Connection lost
                        
                    try:
                        data = json.loads(line.strip())
                        # Mapping data backend ke format GUI jika perlu
                        # Backend mengirim field snake_case, pastikan GUI handle itu
                        self.data_received.emit(data)
                    except json.JSONDecodeError:
                        pass
                        
            except (socket.error, ConnectionRefusedError) as e:
                self.connection_status.emit(False)
                self.error_occurred.emit(f"Connection failed: {str(e)}. Retrying in 3s...")
                time.sleep(3) # Retry delay
            finally:
                if self.sock:
                    self.sock.close()
                    
    def stop(self):
        """Stop the worker"""
        self.is_running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.sock.close()

    # Perintah kirim balik ke backend (jika perlu kontrol Arduino via Backend)
    def send_command(self, command: str):
        # Implementasi kirim command ke Rust (jika Rust support 2-way comm)
        pass