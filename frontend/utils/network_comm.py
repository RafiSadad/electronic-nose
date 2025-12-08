"""
Network communication utilities - COMMAND SENDER & DATA RECEIVER
"""
import socket
import json
import time
from PySide6.QtCore import QThread, Signal

# --- BAGIAN 1: PENGIRIM PERINTAH (PYTHON -> RUST) ---
class BridgeCommander:
    """
    Kelas khusus untuk mengirim perintah kontrol ke Backend Rust (Port 8082).
    Menggantikan fungsi serial langsung di Python.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8082):
        self.host = host
        self.port = port

    def _send(self, command_str: str) -> bool:
        """Helper internal untuk kirim string via TCP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0) # Timeout 2 detik agar UI tidak hang
                s.connect((self.host, self.port))
                s.sendall(f"{command_str}\n".encode('utf-8'))
                return True
        except Exception as e:
            print(f"❌ Bridge Error ({command_str}): {e}")
            return False

    def connect_serial(self, port_name: str) -> bool:
        """Minta Rust untuk Connect ke Serial Port"""
        return self._send(f"CONNECT_SERIAL {port_name}")

    def disconnect_serial(self) -> bool:
        """Minta Rust untuk putus koneksi Serial"""
        return self._send("DISCONNECT_SERIAL")

    def start_sampling(self) -> bool:
        """Minta Rust mulai Sampling (FSM Start)"""
        return self._send("START_SAMPLING")

    def stop_sampling(self) -> bool:
        """Minta Rust stop Sampling"""
        return self._send("STOP_SAMPLING")


# --- BAGIAN 2: PENERIMA DATA (RUST -> PYTHON) ---
class NetworkWorker(QThread):
    """
    Worker thread background untuk mendengarkan Data Stream dari Rust (Port 8083).
    """
    
    data_received = Signal(dict)
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
                self.sock.settimeout(5.0) 
                self.sock.connect((self.host, self.port))
                
                # Berhasil Konek
                self.connection_status.emit(True)
                self.sock.settimeout(None) # Blocking mode untuk read stream
                
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
                        
            except Exception:
                self.connection_status.emit(False)
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