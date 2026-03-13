import os
import numpy as np
from PIL import Image
import cv2

def string_to_binary(message):
    return ''.join(format(byte, '08b') for byte in message.encode('utf-8'))

def binary_to_string(binary):
    try:
        bytes_list = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
        return bytes_list.decode('utf-8')
    except:
        return None

def hide_message_lsb_from_steganography(image_path, message, output_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    binary_message = string_to_binary(message) + '00000000'
    idx = 0
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            for k in range(3):
                if idx < len(binary_message):
                    arr[i, j, k] = (arr[i, j, k] & 254) | int(binary_message[idx])
                    idx += 1
    Image.fromarray(arr).save(output_path)

def retrieve_message_lsb_from_steganography(image_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    binary_message = ""
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            for k in range(3):
                binary_message += str(arr[i, j, k] & 1)
                if len(binary_message) % 8 == 0 and binary_message.endswith('00000000'):
                    return binary_to_string(binary_message[:-8])
    return None

# Placeholder for other steganography methods
def hide_message_masking_filtering_from_steganography(image_path, message, output_path):
    hide_message_lsb_from_steganography(image_path, message, output_path)

def retrieve_message_masking_filtering_from_steganography(image_path):
    return retrieve_message_lsb_from_steganography(image_path)

def hide_message_palette_based_from_steganography(image_path, message, output_path):
    hide_message_lsb_from_steganography(image_path, message, output_path)

def retrieve_message_palette_based_from_steganography(image_path):
    return retrieve_message_lsb_from_steganography(image_path)

def hide_message_edge_detection(image_path, message, output_path):
    hide_message_lsb_from_steganography(image_path, message, output_path)

def retrieve_message_edge_detection(image_path):
    return retrieve_message_lsb_from_steganography(image_path)

def hide_message_alpha_channel(image_path, message, output_path):
    img = Image.open(image_path).convert('RGBA')
    arr = np.array(img)
    binary_message = string_to_binary(message) + '00000000'
    idx = 0
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if idx < len(binary_message):
                arr[i, j, 3] = (arr[i, j, 3] & 254) | int(binary_message[idx])
                idx += 1
    Image.fromarray(arr).save(output_path)

def retrieve_message_alpha_channel(image_path):
    img = Image.open(image_path).convert('RGBA')
    arr = np.array(img)
    binary_message = ""
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            binary_message += str(arr[i, j, 3] & 1)
            if len(binary_message) % 8 == 0 and binary_message.endswith('00000000'):
                return binary_to_string(binary_message[:-8])
    return None
