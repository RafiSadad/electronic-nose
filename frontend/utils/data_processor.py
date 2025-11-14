"""Data processing utilities"""

import numpy as np
from typing import List

class DataProcessor:
    """Process and filter sensor data"""
    
    @staticmethod
    def moving_average(data: List[float], window_size: int = 5) -> List[float]:
        """Apply moving average filter"""
        if len(data) < window_size:
            return data
        
        data_array = np.array(data)
        filtered = np.convolve(data_array, 
                              np.ones(window_size) / window_size, 
                              mode='valid')
        
        # Pad beginning
        padding = [data] * (len(data) - len(filtered))
        return list(padding + filtered.tolist())
    
    @staticmethod
    def normalize(data: List[float]) -> List[float]:
        """Normalize data to 0-1 range"""
        data_array = np.array(data)
        min_val = data_array.min()
        max_val = data_array.max()
        
        if max_val == min_val:
            return list(np.ones_like(data_array) * 0.5)
        
        normalized = (data_array - min_val) / (max_val - min_val)
        return list(normalized)
    
    @staticmethod
    def z_score_normalize(data: List[float]) -> List[float]:
        """Z-score normalization"""
        data_array = np.array(data)
        mean = data_array.mean()
        std = data_array.std()
        
        if std == 0:
            return list(np.zeros_like(data_array))
        
        z_scored = (data_array - mean) / std
        return list(z_scored)
    
    @staticmethod
    def get_statistics(data: List[float]) -> dict:
        """Get statistics from data"""
        if not data:
            return {}
        
        data_array = np.array(data)
        return {
            'min': float(data_array.min()),
            'max': float(data_array.max()),
            'mean': float(data_array.mean()),
            'median': float(np.median(data_array)),
            'std': float(data_array.std()),
            'variance': float(data_array.var()),
        }
