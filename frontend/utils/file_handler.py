"""File handling utilities (Updated for Edge Impulse JSON & API)"""

import csv
import json
import requests  # Pastikan library ini ada (pip install requests)
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class FileHandler:
    """Handle file operations"""
    
    @staticmethod
    def save_as_csv(filename: str, data: Dict, sensor_data: Dict[int, List[float]], 
                   times: List[float], sensor_names: List[str]) -> bool:
        """Save data as CSV (Standard Format)"""
        try:
            # Buat folder 'data' jika belum ada
            Path("data").mkdir(exist_ok=True)
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Metadata (Header Informasi)
                writer.writerow(["Electronic Nose Data Export"])
                writer.writerow(["Sample Name", data.get('name', 'Unknown')])
                writer.writerow(["Sample Type", data.get('type', 'Unknown')])
                writer.writerow(["Export Date", datetime.now().isoformat()])
                writer.writerow([])
                
                # Nama Kolom (Waktu + Nama Sensor)
                headers = ["Time (s)"] + [name for name in sensor_names]
                writer.writerow(headers)
                
                # Isi Data Baris per Baris
                for t_idx, t in enumerate(times):
                    row = [f"{t:.3f}"]
                    for s_idx in range(len(sensor_data)):
                        if t_idx < len(sensor_data[s_idx]):
                            row.append(f"{sensor_data[s_idx][t_idx]:.2f}")
                        else:
                            row.append("0")
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"Error saving CSV: {str(e)}")
            return False

    @staticmethod
    def save_edge_impulse_json(filename: str, sample_name: str, sensor_names: List[str], 
                             sensor_data: Dict[int, List[float]], interval_ms: float) -> bool:
        """
        Save data in Edge Impulse Data Acquisition Format (JSON).
        Standard: https://docs.edgeimpulse.com/reference/data-acquisition-format
        """
        try:
            Path("data").mkdir(exist_ok=True)
            
            # 1. Transpose data (Ubah dari kolom ke baris agar sesuai format Edge Impulse)
            values = []
            num_points = len(sensor_data[0]) if sensor_data else 0
            
            for i in range(num_points):
                row = []
                for j in range(len(sensor_names)):
                    val = sensor_data[j][i] if i < len(sensor_data[j]) else 0.0
                    row.append(val)
                values.append(row)
            
            # 2. Buat Struktur JSON Edge Impulse
            payload = {
                "protected": {
                    "ver": "v1",
                    "alg": "HS256",
                    "iat": int(datetime.now().timestamp())
                },
                "signature": "0", 
                "payload": {
                    "device_name": "ENose-UnoR4",
                    "device_type": "ELECTRONIC_NOSE",
                    "interval_ms": interval_ms,
                    "sensors": [{"name": name, "units": "V"} for name in sensor_names],
                    "values": values
                }
            }
            
            # 3. Simpan File (.json)
            # Pastikan nama file berakhiran .json
            if not filename.endswith('.json'):
                json_filename = filename.replace(".csv", ".json")
            else:
                json_filename = filename
                
            with open(json_filename, 'w') as f:
                json.dump(payload, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving Edge Impulse JSON: {str(e)}")
            return False

    @staticmethod
    def upload_to_edge_impulse(filename: str, api_key: str, label: str = None) -> Tuple[bool, str]:
        """
        Upload JSON file directly to Edge Impulse Ingestion API.
        Endpoint: https://ingestion.edgeimpulse.com/api/training/files
        """
        url = "https://ingestion.edgeimpulse.com/api/training/files"
        
        headers = {
            "x-api-key": api_key,
            "x-disallow-duplicates": "1",
        }
        
        # Jika label diberikan, tambahkan ke header agar otomatis ter-label
        if label:
            headers["x-label"] = label

        try:
            # Cek apakah file ada
            if not os.path.exists(filename):
                return False, "File JSON tidak ditemukan"

            # Kirim request POST ke Edge Impulse
            with open(filename, 'rb') as f:
                # Mengirim file sebagai multipart/form-data
                files = {'data': (os.path.basename(filename), f, 'application/json')}
                response = requests.post(url, headers=headers, files=files)
            
            # Cek respon dari server
            if response.status_code == 200:
                return True, f"Success: {response.text}"
            else:
                return False, f"Failed ({response.status_code}): {response.text}"
                
        except Exception as e:
            return False, f"Connection Error: {str(e)}"