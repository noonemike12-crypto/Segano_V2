import os
import numpy as np
from PIL import Image

class SteganoEngine:
    @staticmethod
    def to_bin(data):
        if isinstance(data, str):
            return ''.join(format(ord(i), '08b') for i in data)
        return ''.join(format(i, '08b') for i in data)

    @staticmethod
    def hide_lsb(image_path, secret_data, output_path):
        img = Image.open(image_path).convert('RGB')
        data = np.array(img)
        
        binary_secret = SteganoEngine.to_bin(secret_data) + '00000000'
        flat_data = data.flatten()
        
        if len(binary_secret) > len(flat_data):
            raise ValueError("Data too large for this image.")
            
        # Vectorized LSB modification for efficiency
        bits = np.array([int(b) for b in binary_secret], dtype=np.uint8)
        flat_data[:len(bits)] = (flat_data[:len(bits)] & 254) | bits
        
        res_data = flat_data.reshape(data.shape)
        Image.fromarray(res_data).save(output_path, "PNG")
        return output_path

    @staticmethod
    def extract_lsb(image_path):
        img = Image.open(image_path).convert('RGB')
        data = np.array(img).flatten()
        
        bits = data & 1
        # Group bits into bytes
        bytes_data = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) < 8: break
            char_code = int(''.join(map(str, byte)), 2)
            if char_code == 0: break # Null terminator
            bytes_data.append(chr(char_code))
            
        return ''.join(bytes_data)
