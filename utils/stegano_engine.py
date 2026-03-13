import os
import numpy as np
from PIL import Image
from utils.logger import logger

class SteganoEngine:
    @staticmethod
    def hide_lsb(image_path, secret_data, output_path):
        logger.log("debug", f"Starting LSB hide on {image_path}")
        try:
            img = Image.open(image_path).convert('RGB')
            data = np.array(img)
            
            binary_secret = ''.join(format(ord(i), '08b') for i in secret_data) + '00000000'
            flat_data = data.flatten()
            
            if len(binary_secret) > len(flat_data):
                logger.log("error", f"Data size ({len(binary_secret)}) exceeds capacity ({len(flat_data)})")
                raise ValueError("Data too large for this image.")
                
            bits = np.array([int(b) for b in binary_secret], dtype=np.uint8)
            flat_data[:len(bits)] = (flat_data[:len(bits)] & 254) | bits
            
            res_data = flat_data.reshape(data.shape)
            Image.fromarray(res_data).save(output_path, "PNG")
            logger.log("info", f"LSB hide complete. Output: {output_path}")
            return f"Hidden in {os.path.basename(output_path)}"
        except Exception as e:
            logger.log("error", f"Exception in hide_lsb: {str(e)}")
            raise e

    @staticmethod
    def extract_lsb(image_path):
        logger.log("debug", f"Starting LSB extraction from {image_path}")
        try:
            img = Image.open(image_path).convert('RGB')
            data = np.array(img).flatten()
            
            bits = data & 1
            bytes_data = []
            for i in range(0, len(bits), 8):
                byte = bits[i:i+8]
                if len(byte) < 8: break
                char_code = int(''.join(map(str, byte)), 2)
                if char_code == 0: break 
                bytes_data.append(chr(char_code))
                
            result = ''.join(bytes_data)
            logger.log("info", f"LSB extraction successful. Length: {len(result)}")
            return result
        except Exception as e:
            logger.log("error", f"Exception in extract_lsb: {str(e)}")
            raise e
