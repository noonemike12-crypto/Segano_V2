import os
import numpy as np
import cv2
from PIL import Image
from scipy.signal import convolve2d

def get_image_capacity_lsb(image_path):
    """คำนวณความจุ LSB (bits)"""
    try:
        img = Image.open(image_path).convert('RGB')
        w, h = img.size
        return w * h * 3 - 8 # หักออก 8 bits สำหรับ terminator
    except: return 0

def get_image_capacity_alpha(image_path):
    """คำนวณความจุช่อง Alpha (bits)"""
    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None or img.shape[2] != 4: return 0
        h, w, _ = img.shape
        return h * w - 8
    except: return 0

def get_image_capacity_edge(image_path):
    """คำนวณความจุบริเวณขอบ (bits)"""
    try:
        img = Image.open(image_path).convert('L')
        gray = np.array(img)
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        grad_x = np.abs(convolve2d(gray, sobel_x, mode='same'))
        grad_y = np.abs(convolve2d(gray, sobel_y, mode='same'))
        edges = np.sqrt(grad_x**2 + grad_y**2) > 30
        return np.count_nonzero(edges) - 8
    except: return 0

def get_audio_capacity_lsb(audio_path):
    """คำนวณความจุเสียง (LSB bits)"""
    import wave
    try:
        with wave.open(audio_path, 'rb') as f:
            return f.getnframes() * f.getnchannels() - 8
    except: return 0
