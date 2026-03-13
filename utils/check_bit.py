import os
from PIL import Image
import numpy as np

def check_bit_lsb(image_path):
    if not image_path or not os.path.exists(image_path): return 0
    img = Image.open(image_path)
    return img.width * img.height * 3

def check_bit_masking_filtering(image_path):
    return check_bit_lsb(image_path) // 2

def check_bit_palette(image_path):
    return 256 * 3

def check_bit_edge_detection(image_path):
    return check_bit_lsb(image_path) // 4

def check_bit_alpha_channel(image_path):
    if not image_path or not os.path.exists(image_path): return 0
    img = Image.open(image_path)
    if img.mode != 'RGBA': return 0
    return img.width * img.height
