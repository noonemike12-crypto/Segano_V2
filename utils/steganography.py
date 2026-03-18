import numpy as np
import cv2
from PIL import Image
import struct
import zlib
from scipy.signal import convolve2d

def string_to_binary(message):
    """แปลงข้อความเป็นเลขฐานสอง (UTF-8)"""
    return ''.join(format(byte, '08b') for byte in message.encode('utf-8'))

def binary_to_string(binary):
    """แปลงเลขฐานสองกลับเป็นข้อความ (UTF-8)"""
    try:
        # ลบ padding 0 ที่อาจติดมาตอนท้าย
        if len(binary) % 8 != 0:
            binary = binary[:-(len(binary) % 8)]
        
        bytes_list = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
        return bytes_list.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error decoding binary: {e}")
        return "เกิดข้อผิดพลาดในการถอดรหัสข้อมูล"

# --- Image Steganography Logic ---

def hide_lsb_image(image_path, message, output_path):
    """ซ่อนข้อมูลแบบ LSB ในภาพ RGB"""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    
    # เพิ่มตัวปิดท้าย (null terminator) เพื่อให้รู้จุดสิ้นสุด
    binary_message = string_to_binary(message) + '00000000'
    required_bits = len(binary_message)
    
    flat_arr = arr.flatten()
    if required_bits > len(flat_arr):
        raise ValueError("ข้อความยาวเกินความจุของภาพ")
        
    for i in range(required_bits):
        flat_arr[i] = (flat_arr[i] & 254) | int(binary_message[i])
        
    res_arr = flat_arr.reshape(arr.shape)
    Image.fromarray(res_arr).save(output_path, format='PNG')
    return True

def extract_lsb_image(image_path):
    """ดึงข้อมูลแบบ LSB จากภาพ"""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    flat_arr = arr.flatten()
    
    binary_message = ""
    found = False
    for val in flat_arr:
        binary_message += str(val & 1)
        if len(binary_message) >= 8 and binary_message[-8:] == '00000000':
            found = True
            break
            
    if not found:
        return "ไม่พบข้อมูลที่ซ่อนอยู่"
    return binary_to_string(binary_message[:-8])

def hide_alpha_channel(image_path, message, output_path):
    """ซ่อนข้อมูลในช่อง Alpha (ความโปร่งใส)"""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None or img.shape[2] != 4:
        raise ValueError("ภาพต้องเป็น PNG ที่มีช่อง Alpha")
        
    binary_message = string_to_binary(message) + '00000000'
    h, w, _ = img.shape
    if len(binary_message) > h * w:
        raise ValueError("ข้อความยาวเกินความจุของช่อง Alpha")
        
    idx = 0
    for i in range(h):
        for j in range(w):
            if idx < len(binary_message):
                img[i, j, 3] = (img[i, j, 3] & 254) | int(binary_message[idx])
                idx += 1
            else: break
        if idx >= len(binary_message): break
        
    cv2.imwrite(output_path, img)
    return True

def extract_alpha_channel(image_path):
    """ดึงข้อมูลจากช่อง Alpha"""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None or img.shape[2] != 4:
        return "ไม่พบช่อง Alpha ในภาพนี้"
        
    binary_message = ""
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            binary_message += str(img[i, j, 3] & 1)
            if len(binary_message) >= 8 and binary_message[-8:] == '00000000':
                return binary_to_string(binary_message[:-8])
    return "ไม่พบข้อมูลที่ซ่อนอยู่"

def hide_edge_detection(image_path, message, output_path):
    """ซ่อนข้อมูลในบริเวณขอบของภาพ (Edge Detection)"""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    gray = np.array(img.convert('L'))
    
    # Sobel Edge Detection
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    grad_x = np.abs(convolve2d(gray, sobel_x, mode='same'))
    grad_y = np.abs(convolve2d(gray, sobel_y, mode='same'))
    edges = np.sqrt(grad_x**2 + grad_y**2) > 30
    
    edge_indices = np.argwhere(edges)
    binary_message = string_to_binary(message) + '00000000'
    
    if len(binary_message) > len(edge_indices):
        raise ValueError("ข้อความยาวเกินจำนวนพิกเซลขอบที่พบ")
        
    for idx, (r, c) in enumerate(edge_indices[:len(binary_message)]):
        arr[r, c, 0] = (arr[r, c, 0] & 254) | int(binary_message[idx])
        
    Image.fromarray(arr).save(output_path, format='PNG')
    return True

def extract_edge_detection(image_path):
    """ดึงข้อมูลจากบริเวณขอบของภาพ"""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    gray = np.array(img.convert('L'))
    
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    grad_x = np.abs(convolve2d(gray, sobel_x, mode='same'))
    grad_y = np.abs(convolve2d(gray, sobel_y, mode='same'))
    edges = np.sqrt(grad_x**2 + grad_y**2) > 30
    
    edge_indices = np.argwhere(edges)
    binary_message = ""
    for r, c in edge_indices:
        binary_message += str(arr[r, c, 0] & 1)
        if len(binary_message) >= 8 and binary_message[-8:] == '00000000':
            return binary_to_string(binary_message[:-8])
    return "ไม่พบข้อมูลที่ซ่อนอยู่"

# --- Video Steganography Logic ---

def hide_dct_image(image_path, message, output_path):
    """ซ่อนข้อมูลในความถี่ของภาพ (DCT) - Simplified version"""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None: raise ValueError("ไม่สามารถโหลดภาพได้")
    
    # แปลงเป็น YCrCb เพื่อซ่อนในช่อง Y (Luminance)
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(img_yuv)
    
    # ทำงานกับบล็อก 8x8
    h, w = y.shape
    binary_message = string_to_binary(message) + '00000000'
    
    if len(binary_message) > (h // 8) * (w // 8):
        raise ValueError("ข้อความยาวเกินความจุของ DCT (1 บิตต่อบล็อก 8x8)")
        
    y_float = np.float32(y)
    idx = 0
    for i in range(0, h - 8, 8):
        for j in range(0, w - 8, 8):
            if idx < len(binary_message):
                block = y_float[i:i+8, j:j+8]
                dct_block = cv2.dct(block)
                
                # ซ่อนในค่าสัมประสิทธิ์ความถี่ต่ำ (Mid-band) เพื่อความทนทาน
                # ตำแหน่ง (4,4) เป็นตัวอย่าง
                val = dct_block[4, 4]
                if int(binary_message[idx]) == 1:
                    if val <= 0: dct_block[4, 4] = 1.0
                else:
                    if val > 0: dct_block[4, 4] = -1.0
                
                y_float[i:i+8, j:j+8] = cv2.idct(dct_block)
                idx += 1
            else: break
        if idx >= len(binary_message): break
        
    y_final = np.uint8(np.clip(y_float, 0, 255))
    img_final = cv2.merge([y_final, cr, cb])
    img_final = cv2.cvtColor(img_final, cv2.COLOR_YCrCb2BGR)
    cv2.imwrite(output_path, img_final)
    return True

def extract_dct_image(image_path):
    """ดึงข้อมูลจากความถี่ DCT"""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None: return "ไม่สามารถโหลดภาพได้"
    
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, _, _ = cv2.split(img_yuv)
    h, w = y.shape
    y_float = np.float32(y)
    
    binary_message = ""
    for i in range(0, h - 8, 8):
        for j in range(0, w - 8, 8):
            block = y_float[i:i+8, j:j+8]
            dct_block = cv2.dct(block)
            
            if dct_block[4, 4] > 0: binary_message += "1"
            else: binary_message += "0"
            
            if len(binary_message) >= 8 and binary_message[-8:] == '00000000':
                return binary_to_string(binary_message[:-8])
                
    return "ไม่พบข้อมูลที่ซ่อนอยู่"

def hide_lsb_video(video_path, message, output_path):
    """ซ่อนข้อมูลแบบ LSB ในเฟรมแรกของวิดีโอ (Simple implementation)"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("ไม่สามารถเปิดไฟล์วิดีโอได้")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'FFV1') # ใช้ Lossless codec เพื่อรักษาข้อมูล LSB
    
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    binary_message = string_to_binary(message) + '00000000'
    ret, frame = cap.read()
    
    if ret:
        flat_frame = frame.flatten()
        if len(binary_message) > len(flat_frame):
            cap.release()
            out.release()
            raise ValueError("ข้อความยาวเกินความจุของเฟรมวิดีโอ")
            
        for i in range(len(binary_message)):
            flat_frame[i] = (flat_frame[i] & 254) | int(binary_message[i])
            
        frame = flat_frame.reshape(frame.shape)
        out.write(frame)
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            out.write(frame)
            
    cap.release()
    out.release()
    return True

def extract_lsb_video(video_path):
    """ดึงข้อมูลจากเฟรมแรกของวิดีโอ"""
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return "ไม่สามารถอ่านวิดีโอได้"
        
    flat_frame = frame.flatten()
    binary_message = ""
    found = False
    for val in flat_frame:
        binary_message += str(val & 1)
        if len(binary_message) >= 8 and binary_message[-8:] == '00000000':
            found = True
            break
            
    if not found:
        return "ไม่พบข้อมูลที่ซ่อนอยู่"
    return binary_to_string(binary_message[:-8])
