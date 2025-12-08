"""File handling utilities (Fixed: Invalid Signature Error)"""

import csv
import json
import requests
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
            Path("data").mkdir(exist_ok=True)
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Metadata
                writer.writerow(["Electronic Nose Data Export"])
                writer.writerow(["Sample Name", data.get('name', 'Unknown')])
                writer.writerow(["Sample Type", data.get('type', 'Unknown')])
                writer.writerow(["Export Date", datetime.now().isoformat()])
                writer.writerow(["Mode", "Auto FSM"])
                writer.writerow(["Number of Points", len(times)])
                writer.writerow([]) # Empty line
                
                # Headers
                headers = ["Time (s)"] + [name for name in sensor_names]
                writer.writerow(headers)
                
                # Data Rows
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
        """Save data in Edge Impulse Data Acquisition Format (JSON)"""
        try:
            Path("data").mkdir(exist_ok=True)
            
            # Transpose data (Column to Row based)
            values = []
            num_points = 0
            if sensor_data and 0 in sensor_data:
                num_points = len(sensor_data[0])
            
            for i in range(num_points):
                row = []
                for j in range(len(sensor_names)):
                    val = sensor_data[j][i] if (j in sensor_data and i < len(sensor_data[j])) else 0.0
                    row.append(val)
                values.append(row)
            
            # PERBAIKAN DI SINI:
            # Menggunakan "alg": "none" agar server tidak menagih signature panjang
            payload = {
                "protected": {
                    "ver": "v1", 
                    "alg": "none", # <--- UPDATE PENTING (Sebelumnya HS256)
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
            
            if not filename.endswith('.json'):
                filename = filename.replace('.csv', '.json')
                
            with open(filename, 'w') as f:
                json.dump(payload, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving Edge Impulse JSON: {str(e)}")
            return False

    @staticmethod
    def convert_csv_to_json(csv_filename: str) -> bool:
        """
        Membaca file CSV format 'Electronic Nose Data Export' 
        dan mengubahnya menjadi format JSON Edge Impulse.
        """
        try:
            if not os.path.exists(csv_filename):
                return False

            with open(csv_filename, 'r') as f:
                reader = csv.reader(f)
                lines = list(reader)

            # 1. Parsing Metadata
            sample_name = "Unknown"
            start_row_data = 0
            
            for i, line in enumerate(lines[:15]):
                if len(line) >= 2 and line[0] == "Sample Name":
                    sample_name = line[1]
                if len(line) > 0 and line[0].startswith("Time"):
                    start_row_data = i
                    break
            
            if start_row_data == 0 and sample_name == "Unknown":
                print("Format CSV tidak dikenali")
                return False

            header_row = lines[start_row_data]
            sensor_names = header_row[1:] 
            
            # 2. Parsing Data Values
            parsed_sensor_data = {i: [] for i in range(len(sensor_names))}
            times = []
            
            for row in lines[start_row_data + 1:]:
                if len(row) < 2: continue
                try:
                    t = float(row[0])
                    times.append(t)
                    for s_idx in range(len(sensor_names)):
                        val = float(row[s_idx + 1])
                        parsed_sensor_data[s_idx].append(val)
                except ValueError:
                    continue

            if not times:
                return False

            # 3. Hitung Interval (ms)
            interval_ms = 100.0 
            if len(times) > 1:
                diffs = []
                for k in range(min(5, len(times)-1)):
                    diffs.append(times[k+1] - times[k])
                avg_diff_sec = sum(diffs) / len(diffs)
                interval_ms = avg_diff_sec * 1000.0

            # 4. Save as JSON (Panggil fungsi yang sudah diperbaiki)
            json_filename = csv_filename.replace(".csv", ".json")
            return FileHandler.save_edge_impulse_json(
                json_filename, sample_name, sensor_names, parsed_sensor_data, interval_ms
            )

        except Exception as e:
            print(f"Error converting CSV to JSON: {str(e)}")
            return False

    @staticmethod
    def upload_to_edge_impulse(filename: str, api_key: str, label: str = None) -> Tuple[bool, str]:
        """Upload JSON file directly to Edge Impulse Ingestion API."""
        url = "https://ingestion.edgeimpulse.com/api/training/files"
        
        headers = {
            "x-api-key": api_key,
            "x-disallow-duplicates": "1",
        }
        if label: headers["x-label"] = label

        try:
            if not os.path.exists(filename):
                return False, "File JSON tidak ditemukan"

            with open(filename, 'rb') as f:
                files = {'data': (os.path.basename(filename), f, 'application/json')}
                response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                return True, f"Success: {response.text}"
            else:
                return False, f"Failed ({response.status_code}): {response.text}"
                
        except Exception as e:
            return False, f"Connection Error: {str(e)}"