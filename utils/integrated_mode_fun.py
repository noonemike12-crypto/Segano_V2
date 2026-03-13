import base64
import os
import uuid
import random
import string
import wave
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PIL import Image
from pydub import AudioSegment

def encrypt_aes_integrated(text, key_str):
    """เข้ารหัส AES สำหรับโหมดรวม"""
    key = key_str.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
    return base64.b64encode(cipher.iv + ct).decode('utf-8')

def decrypt_aes_integrated(encrypted_b64, key_str):
    """ถอดรหัส AES สำหรับโหมดรวม"""
    try:
        key = key_str.encode('utf-8')
        raw = base64.b64decode(encrypted_b64)
        iv = raw[:16]
        ct = raw[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
    except:
        return None

def split_message(msg, parts=2):
    """แบ่งข้อความออกเป็นส่วนๆ"""
    length = len(msg)
    return [msg[i*length//parts : (i+1)*length//parts] for i in range(parts)]

def join_message(parts):
    """รวมข้อความที่ถูกแบ่ง"""
    return "".join(parts)
