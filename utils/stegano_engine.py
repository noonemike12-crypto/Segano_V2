import os
import numpy as np
from PIL import Image
from utils.logger import logger

class SteganoEngine:
    METHODS = ["LSB (Pixel)", "EOF (Append)", "Metadata (Comment)"]

    @staticmethod
    def to_bin(data):
        byte_data = data.encode('utf-8')
        return ''.join(format(b, '08b') for b in byte_data)

    @staticmethod
    def from_bin(bin_data):
        bytes_list = []
        for i in range(0, len(bin_data), 8):
            byte = bin_data[i:i+8]
            bytes_list.append(int(byte, 2))
        return bytes(bytes_list).decode('utf-8', errors='ignore')

    @staticmethod
    def get_image_capacity(image_path, method="LSB (Pixel)"):
        try:
            img = Image.open(image_path)
            width, height = img.size
            
            if method == "LSB (Pixel)":
                total_bits = width * height * 3
                available_bits = total_bits - 8
                return {
                    "total_bits": total_bits,
                    "eng_capacity": available_bits // 8,
                    "thai_capacity": available_bits // 24
                }
            elif method == "EOF (Append)":
                # Theoretically unlimited, but let's say 100MB for safety display
                return {
                    "total_bits": 100 * 1024 * 1024 * 8,
                    "eng_capacity": 100 * 1024 * 1024,
                    "thai_capacity": (100 * 1024 * 1024) // 3
                }
            elif method == "Metadata (Comment)":
                # JPEG/PNG comments are usually limited
                return {
                    "total_bits": 64000 * 8,
                    "eng_capacity": 64000,
                    "thai_capacity": 64000 // 3
                }
        except Exception as e:
            logger.log("error", f"Error calculating capacity: {str(e)}")
            return None

    # --- LSB Technique ---
    @staticmethod
    def hide_lsb(image_path, secret_data, output_path):
        img = Image.open(image_path).convert('RGB')
        data = np.array(img)
        binary_secret = SteganoEngine.to_bin(secret_data) + '00000000'
        flat_data = data.flatten()
        if len(binary_secret) > len(flat_data):
            raise ValueError("ข้อความยาวเกินความจุ LSB!")
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
        binary_data = ""
        for i in range(0, len(bits), 8):
            byte_str = ''.join(map(str, bits[i:i+8]))
            if byte_str == "00000000": break
            binary_data += byte_str
        return SteganoEngine.from_bin(binary_data)

    # --- EOF Technique ---
    @staticmethod
    def hide_eof(image_path, secret_data, output_path):
        import shutil
        shutil.copy(image_path, output_path)
        with open(output_path, "ab") as f:
            # Use a unique delimiter to find the start of secret data
            f.write(b"---SIENG_START---")
            f.write(secret_data.encode('utf-8'))
            f.write(b"---SIENG_END---")
        return output_path

    @staticmethod
    def extract_eof(image_path):
        with open(image_path, "rb") as f:
            content = f.read()
            start_marker = b"---SIENG_START---"
            end_marker = b"---SIENG_END---"
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker)
            if start_idx != -1 and end_idx != -1:
                secret_bytes = content[start_idx + len(start_marker):end_idx]
                return secret_bytes.decode('utf-8')
        raise ValueError("ไม่พบข้อมูลที่ซ่อนแบบ EOF ในไฟล์นี้")

    # --- Metadata Technique ---
    @staticmethod
    def hide_metadata(image_path, secret_data, output_path):
        img = Image.open(image_path)
        from PIL import PngImagePlugin
        meta = PngImagePlugin.PngInfo()
        meta.add_text("Description", secret_data)
        img.save(output_path, "PNG", pnginfo=meta)
        return output_path

    @staticmethod
    def extract_metadata(image_path):
        img = Image.open(image_path)
        if "Description" in img.info:
            return img.info["Description"]
        raise ValueError("ไม่พบข้อมูลที่ซ่อนใน Metadata")
