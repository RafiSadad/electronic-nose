"""File handling utilities"""

import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class FileHandler:
    """Handle file operations"""
    
    @staticmethod
    def save_as_csv(filename: str, data: Dict, sensor_data: Dict[int, List[float]], 
                   times: List[float]) -> bool:
        """Save data as CSV"""
        try:
            Path("data").mkdir(exist_ok=True)
            
            with open(f"data/{filename}.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Metadata
                writer.writerow(["Electronic Nose Data Export"])
                writer.writerow(["Sample Name", data.get('name', 'Unknown')])
                writer.writerow(["Sample Type", data.get('type', 'Unknown')])
                writer.writerow(["Export Date", datetime.now().isoformat()])
                writer.writerow([])
                
                # Data
                headers = ["Time (s)"] + [f"Sensor {i+1}" for i in range(len(sensor_data))]
                writer.writerow(headers)
                
                for t_idx, t in enumerate(times):
                    row = [f"{t:.3f}"]
                    for s_idx in range(len(sensor_data)):
                        if t_idx < len(sensor_data[s_idx]):
                            row.append(f"{sensor_data[s_idx][t_idx]:.2f}")
                    writer.writerow(row)
            
            return True
        except Exception as e:
            print(f"Error saving CSV: {str(e)}")
            return False
    
    @staticmethod
    def save_as_json(filename: str, data: Dict, sensor_data: Dict[int, List[float]], 
                    times: List[float]) -> bool:
        """Save data as JSON"""
        try:
            Path("data").mkdir(exist_ok=True)
            
            export_data = {
                "metadata": {
                    "name": data.get('name', 'Unknown'),
                    "type": data.get('type', 'Unknown'),
                    "export_date": datetime.now().isoformat(),
                    "num_points": len(times),
                    "num_sensors": len(sensor_data)
                },
                "times": times,
                "sensors": {
                    f"sensor_{i}": sensor_data[i] 
                    for i in range(len(sensor_data))
                }
            }
            
            with open(f"data/{filename}.json", 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving JSON: {str(e)}")
            return False
    
    @staticmethod
    def load_csv(filename: str) -> tuple:
        """Load data from CSV"""
        try:
            times = []
            sensor_data = {0: [], 1: [], 2: [], 3: []}
            
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                # Skip metadata
                next(reader)  # "Electronic Nose Data Export"
                next(reader)  # Sample Name
                next(reader)  # Sample Type
                next(reader)  # Export Date
                next(reader)  # Empty line
                
                next(reader)  # Headers
                
                for row in reader:
                    if row:
                        times.append(float(row))
                        for i in range(1, min(5, len(row))):
                            sensor_data[i-1].append(float(row[i]))
            
            return times, sensor_data
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            return [], {}
