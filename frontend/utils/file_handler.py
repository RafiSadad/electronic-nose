"""File handling utilities (Updated for Edge Impulse JSON)"""

import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

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
                writer.writerow([])
                
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
        """
        Save data in Edge Impulse Data Acquisition Format (JSON).
        Standard: https://docs.edgeimpulse.com/reference/data-acquisition-format
        """
        try:
            Path("data").mkdir(exist_ok=True)
            
            # 1. Transpose data
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
            json_filename = filename.replace(".csv", ".json")
            with open(json_filename, 'w') as f:
                json.dump(payload, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving Edge Impulse JSON: {str(e)}")
            return False