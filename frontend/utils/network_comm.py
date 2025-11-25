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
                # Set blocking mode agar read loop stabil
                self.sock.settimeout(None) 
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
                        self.data_received.emit(data)
                    except json.JSONDecodeError:
                        pass
                        
            except (socket.error, ConnectionRefusedError) as e:
                self.connection_status.emit(False)
                # Retry delay
                time.sleep(3) 
            finally:
                self.cleanup()
    
    def cleanup(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

    def stop(self):
        """Stop the worker"""
        self.is_running = False
        self.cleanup()

    def send_command(self, command: str):
        """Send command to Backend -> Arduino"""
        if self.sock:
            try:
                # Kirim string command dengan newline
                msg = f"{command}\n"
                self.sock.sendall(msg.encode('utf-8'))
                print(f"Sent command: {command}")
            except Exception as e:
                self.error_occurred.emit(f"Failed to send command: {str(e)}")
        else:
            self.error_occurred.emit("Cannot send command: Not connected to Backend!")