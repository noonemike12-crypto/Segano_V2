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

def encrypt_aes(text, key_str=None):
    if not key_str:
        key_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    key = key_str.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
    encrypted_b64 = base64.b64encode(cipher.iv + ct).decode()
    return key_str, encrypted_b64

def split_msg(msg, parts=2):
    length = len(msg)
    return [msg[i*length//parts : (i+1)*length//parts] for i in range(parts)]
