import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class CryptoEngine:
    @staticmethod
    def aes_encrypt(text, key_str):
        key = key_str.encode('utf-8').ljust(32, b'0')[:32]
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
        return base64.b64encode(cipher.iv + ct_bytes).decode('utf-8')

    @staticmethod
    def aes_decrypt(encrypted_b64, key_str):
        try:
            data = base64.b64decode(encrypted_b64)
            iv = data[:16]
            ct = data[16:]
            key = key_str.encode('utf-8').ljust(32, b'0')[:32]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
        except Exception as e:
            return f"Error: {str(e)}"
