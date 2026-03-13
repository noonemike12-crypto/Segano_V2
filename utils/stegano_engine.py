import os
import numpy as np
import cv2
from PIL import Image
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, COMM
from mutagen.mp4 import MP4
from pypdf import PdfReader, PdfWriter
from utils.logger import logger
from utils.crypto_engine import CryptoEngine

class SteganoEngine:
    METHODS = [
        "LSB (Least Significant Bit)", 
        "EOF (File Append/Join)", 
        "Metadata (Tag/Comment)", 
        "Alpha Channel (PNG/BMP)",
        "Edge Detection (Advanced)",
        "Masking (XOR Pattern)",
        "Palette (Index Shift)"
    ]

    @staticmethod
    def to_bin(data):
        if isinstance(data, str):
            byte_data = data.encode('utf-8')
        else:
            byte_data = data
        return ''.join(format(b, '08b') for b in byte_data)

    @staticmethod
    def from_bin(bin_data):
        bytes_list = []
        for i in range(0, len(bin_data), 8):
            byte = bin_data[i:i+8]
            bytes_list.append(int(byte, 2))
        return bytes(bytes_list)

    @staticmethod
    def get_capacity(file_path, method):
        if not os.path.exists(file_path): return 0
        ext = os.path.splitext(file_path)[1].lower()
        
        if method == "LSB (Least Significant Bit)":
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                img = Image.open(file_path)
                return (img.width * img.height * 3) // 8
            elif ext == ".wav":
                import wave
                with wave.open(file_path, 'rb') as f:
                    return (f.getnframes() * f.getnchannels() * f.getsampwidth()) // 8
        elif method == "EOF (File Append/Join)":
            return 500 * 1024 * 1024 # 500MB limit for safety
        elif method == "Alpha Channel (PNG/BMP)":
            if ext in [".png", ".bmp"]:
                img = Image.open(file_path).convert("RGBA")
                return (img.width * img.height) // 8
        elif method == "Edge Detection (Advanced)":
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                img = cv2.imread(file_path)
                edges = cv2.Canny(img, 100, 200)
                return np.sum(edges > 0) // 8
        elif method == "Masking (XOR Pattern)":
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                img = Image.open(file_path)
                return (img.width * img.height * 3) // 8
        elif method == "Palette (Index Shift)":
            if ext in [".png", ".bmp"]:
                img = Image.open(file_path)
                if img.mode == 'P':
                    return 256 * 3 // 8
                return (img.width * img.height) // 8
        return 1024 * 1024 # Default 1MB

    # --- 1. LSB Technique ---
    @staticmethod
    def hide_lsb(carrier_path, data_bytes, output_path):
        ext = os.path.splitext(carrier_path)[1].lower()
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            return SteganoEngine.hide_image_lsb(carrier_path, data_bytes, output_path)
        elif ext == ".wav":
            return SteganoEngine.hide_audio_lsb(carrier_path, data_bytes, output_path)
        raise ValueError("LSB supports Image and WAV only")

    @staticmethod
    def hide_image_lsb(image_path, data_bytes, output_path):
        img = Image.open(image_path).convert('RGB')
        arr = np.array(img)
        data_len = len(data_bytes)
        header = format(data_len, '032b')
        binary_data = header + ''.join(format(b, '08b') for b in data_bytes)
        
        flat = arr.flatten()
        if len(binary_data) > len(flat):
            raise ValueError(f"Data size ({len(binary_data)} bits) exceeds capacity ({len(flat)} bits)")
            
        bits = np.array([int(b) for b in binary_data], dtype=np.uint8)
        flat[:len(bits)] = (flat[:len(bits)] & 254) | bits
        
        res = flat.reshape(arr.shape)
        Image.fromarray(res).save(output_path, "PNG")
        return output_path

    # --- 2. EOF (File Append) - Scope 1.1.2 ---
    @staticmethod
    def hide_eof(carrier_path, secret_data, output_path):
        import shutil
        shutil.copy(carrier_path, output_path)
        
        # If secret_data is a path (File-in-File)
        if isinstance(secret_data, str) and os.path.exists(secret_data):
            with open(secret_data, "rb") as f_secret:
                data_bytes = f_secret.read()
            # Add file info header
            header = f"FILE|{os.path.basename(secret_data)}|{len(data_bytes)}|".encode()
        else:
            # It's raw bytes or text
            data_bytes = secret_data if isinstance(secret_data, bytes) else secret_data.encode()
            header = f"TEXT|{len(data_bytes)}|".encode()

        marker_start = b"---SIENG_BEGIN---"
        marker_end = b"---SIENG_END---"
        
        with open(output_path, "ab") as f:
            f.write(marker_start + header + data_bytes + marker_end)
        return output_path

    @staticmethod
    def extract_eof(file_path):
        marker_start = b"---SIENG_BEGIN---"
        marker_end = b"---SIENG_END---"
        with open(file_path, "rb") as f:
            content = f.read()
            s = content.find(marker_start)
            e = content.find(marker_end)
            if s != -1 and e != -1:
                raw = content[s + len(marker_start):e]
                parts = raw.split(b"|", 3)
                if parts[0] == b"FILE":
                    filename = parts[1].decode()
                    data = parts[3]
                    return {"type": "file", "filename": filename, "data": data}
                else:
                    data = parts[2]
                    return {"type": "text", "data": data}
        raise ValueError("No hidden EOF data found")

    # --- 3. Alpha Channel ---
    @staticmethod
    def hide_alpha(image_path, data_bytes, output_path):
        img = Image.open(image_path).convert("RGBA")
        arr = np.array(img)
        
        data_len = len(data_bytes)
        header = format(data_len, '032b')
        binary_data = header + ''.join(format(b, '08b') for b in data_bytes)
        
        alpha = arr[:, :, 3].flatten()
        if len(binary_data) > len(alpha):
            raise ValueError("Data too large for Alpha Channel")
            
        bits = np.array([int(b) for b in binary_data], dtype=np.uint8)
        alpha[:len(bits)] = (alpha[:len(bits)] & 254) | bits
        
        arr[:, :, 3] = alpha.reshape(arr.shape[0], arr.shape[1])
        Image.fromarray(arr).save(output_path, "PNG")
        return output_path

    @staticmethod
    def extract_alpha(image_path):
        img = Image.open(image_path).convert("RGBA")
        arr = np.array(img)
        alpha = arr[:, :, 3].flatten()
        bits = alpha & 1
        header_bits = bits[:32]
        data_len = int(''.join(map(str, header_bits)), 2)
        data_bits = bits[32:32 + (data_len * 8)]
        return SteganoEngine.from_bin(''.join(map(str, data_bits)))

    # --- 4. Edge Detection Stegano ---
    @staticmethod
    def hide_edge(image_path, data_bytes, output_path):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_indices = np.where(edges > 0)
        
        data_len = len(data_bytes)
        header = format(data_len, '032b')
        binary_data = header + ''.join(format(b, '08b') for b in data_bytes)
        
        if len(binary_data) > len(edge_indices[0]):
            raise ValueError("Data too large for Edge Detection method")
            
        for i in range(len(binary_data)):
            r, c = edge_indices[0][i], edge_indices[1][i]
            img[r, c, 0] = (img[r, c, 0] & 254) | int(binary_data[i])
            
        cv2.imwrite(output_path, img)
        return output_path

    @staticmethod
    def extract_edge(image_path):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_indices = np.where(edges > 0)
        
        bits = []
        for i in range(32): # Header
            r, c = edge_indices[0][i], edge_indices[1][i]
            bits.append(img[r, c, 0] & 1)
            
        data_len = int(''.join(map(str, bits)), 2)
        data_bits = []
        for i in range(32, 32 + (data_len * 8)):
            r, c = edge_indices[0][i], edge_indices[1][i]
            data_bits.append(img[r, c, 0] & 1)
            
        return SteganoEngine.from_bin(''.join(map(str, data_bits)))

    # --- 5. Metadata ---
    @staticmethod
    def hide_metadata(file_path, secret_text, output_path):
        import shutil
        shutil.copy(file_path, output_path)
        # If secret_text is bytes, decode it
        if isinstance(secret_text, bytes):
            try: secret_text = secret_text.decode('utf-8')
            except: secret_text = str(secret_text)
            
        audio = MutagenFile(output_path)
        if audio is None: raise ValueError("Unsupported format")
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".mp3":
            if audio.tags is None: audio.add_tags()
            audio.tags.add(COMM(encoding=3, lang='eng', desc='sieng', text=secret_text))
        elif ext in [".mp4", ".m4a", ".mov"]:
            audio["\xa9cmt"] = secret_text
        else:
            audio["comment"] = secret_text
        audio.save()
        return output_path

    # --- 6. Masking ---
    @staticmethod
    def hide_masking(carrier_path, data_bytes, output_path):
        img = Image.open(carrier_path).convert('RGB')
        arr = np.array(img)
        data_len = len(data_bytes)
        header = format(data_len, '032b')
        binary_data = header + ''.join(format(b, '08b') for b in data_bytes)
        
        flat = arr.flatten()
        if len(binary_data) > len(flat):
            raise ValueError("Data too large for masking")
            
        for i, bit in enumerate(binary_data):
            pattern = (i * 13) % 2
            val = flat[i]
            if bit == '1':
                flat[i] = val | 1 if pattern == 0 else val & ~1
            else:
                flat[i] = val & ~1 if pattern == 0 else val | 1
                
        res = flat.reshape(arr.shape)
        Image.fromarray(res).save(output_path, "PNG")
        return output_path

    @staticmethod
    def extract_masking(stego_path):
        img = Image.open(stego_path).convert('RGB')
        arr = np.array(img)
        flat = arr.flatten()
        
        bits = []
        for i in range(32):
            pattern = (i * 13) % 2
            bit = '1' if (flat[i] & 1) != pattern else '0'
            bits.append(bit)
            
        data_len = int(''.join(bits), 2)
        data_bits = []
        for i in range(32, 32 + (data_len * 8)):
            pattern = (i * 13) % 2
            bit = '1' if (flat[i] & 1) != pattern else '0'
            data_bits.append(bit)
            
        return SteganoEngine.from_bin(''.join(data_bits))

    # --- 7. Palette ---
    @staticmethod
    def hide_palette(carrier_path, data_bytes, output_path):
        img = Image.open(carrier_path)
        if img.mode != 'P':
            img = img.convert('P', palette=Image.ADAPTIVE)
            
        palette = img.getpalette()
        data_len = len(data_bytes)
        header = format(data_len, '032b')
        binary_data = header + ''.join(format(b, '08b') for b in data_bytes)
        
        if len(binary_data) > len(palette):
            raise ValueError("Data too large for palette")
            
        for i, bit in enumerate(binary_data):
            if bit == '1':
                palette[i] |= 1
            else:
                palette[i] &= ~1
                
        img.putpalette(palette)
        img.save(output_path)
        return output_path

    @staticmethod
    def extract_palette(stego_path):
        img = Image.open(stego_path)
        if img.mode != 'P':
            raise ValueError("Not a palette-indexed image")
            
        palette = img.getpalette()
        bits = []
        for i in range(32):
            bits.append(str(palette[i] & 1))
            
        data_len = int(''.join(bits), 2)
        data_bits = []
        for i in range(32, 32 + (data_len * 8)):
            data_bits.append(str(palette[i] & 1))
            
        return SteganoEngine.from_bin(''.join(data_bits))

    @staticmethod
    def extract_metadata(file_path):
        audio = MutagenFile(file_path)
        if audio is None: raise ValueError("Unsupported format")
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".mp3":
            for tag in audio.tags.values():
                if isinstance(tag, COMM) and tag.desc == 'sieng':
                    return tag.text[0]
        elif ext in [".mp4", ".m4a", ".mov"]:
            return audio.get("\xa9cmt", [None])[0]
        return audio.get("comment", [None])[0]
