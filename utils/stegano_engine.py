import os
import numpy as np
from PIL import Image
from utils.logger import logger

class SteganoEngine:
    @staticmethod
    def to_bin(data):
        """Convert data to binary string using UTF-8 encoding."""
        if isinstance(data, str):
            # Encode string to bytes first to handle Thai/Unicode correctly
            byte_data = data.encode('utf-8')
            return ''.join(format(b, '08b') for b in byte_data)
        return ''.join(format(i, '08b') for i in data)

    @staticmethod
    def from_bin(bin_data):
        """Convert binary string back to UTF-8 string."""
        bytes_list = []
        for i in range(0, len(bin_data), 8):
            byte = bin_data[i:i+8]
            bytes_list.append(int(byte, 2))
        return bytes(bytes_list).decode('utf-8', errors='ignore')

    @staticmethod
    def get_image_capacity(image_path):
        """Calculate capacity in bits, Thai chars, and English chars."""
        try:
            img = Image.open(image_path)
            width, height = img.size
            # Assuming 1 bit per color channel (RGB)
            total_bits = width * height * 3
            # Reserve bits for null terminator (8 bits)
            available_bits = total_bits - 8
            
            eng_chars = available_bits // 8
            # Thai characters in UTF-8 typically take 3 bytes (24 bits)
            thai_chars = available_bits // 24
            
            return {
                "total_bits": total_bits,
                "eng_capacity": eng_chars,
                "thai_capacity": thai_chars
            }
        except Exception as e:
            logger.log("error", f"Error calculating capacity: {str(e)}")
            return None

    @staticmethod
    def hide_lsb(image_path, secret_data, output_path):
        logger.log("debug", f"Starting LSB hide (UTF-8) on {image_path}")
        try:
            img = Image.open(image_path).convert('RGB')
            data = np.array(img)
            
            # Convert secret data to binary using UTF-8
            binary_secret = SteganoEngine.to_bin(secret_data) + '00000000'
            flat_data = data.flatten()
            
            if len(binary_secret) > len(flat_data):
                logger.log("error", "Data size exceeds image capacity")
                raise ValueError("ข้อความยาวเกินความจุของรูปภาพ!")
                
            bits = np.array([int(b) for b in binary_secret], dtype=np.uint8)
            flat_data[:len(bits)] = (flat_data[:len(bits)] & 254) | bits
            
            res_data = flat_data.reshape(data.shape)
            Image.fromarray(res_data).save(output_path, "PNG")
            logger.log("info", f"LSB hide complete. Output: {output_path}")
            return output_path
        except Exception as e:
            logger.log("error", f"Exception in hide_lsb: {str(e)}")
            raise e

    @staticmethod
    def extract_lsb(image_path):
        logger.log("debug", f"Starting LSB extraction (UTF-8) from {image_path}")
        try:
            img = Image.open(image_path).convert('RGB')
            data = np.array(img).flatten()
            
            bits = data & 1
            # Extract bits until null terminator
            binary_data = ""
            for i in range(0, len(bits), 8):
                byte = bits[i:i+8]
                byte_str = ''.join(map(str, byte))
                if byte_str == "00000000": break
                binary_data += byte_str
            
            # Convert binary back to UTF-8 string
            result = SteganoEngine.from_bin(binary_data)
            logger.log("info", "LSB extraction successful.")
            return result
        except Exception as e:
            logger.log("error", f"Exception in extract_lsb: {str(e)}")
            raise e
