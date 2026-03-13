import base64
import hashlib
from Crypto.Cipher import AES, Blowfish, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from cryptography.fernet import Fernet

class CryptoUtils:
    @staticmethod
    def aes_encrypt(data, key):
        """เข้ารหัส AES-256 (CBC)"""
        key_hash = hashlib.sha256(key.encode()).digest()
        cipher = AES.new(key_hash, AES.MODE_CBC)
        iv = cipher.iv
        padded_data = pad(data.encode(), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted).decode('utf-8')

    @staticmethod
    def aes_decrypt(encrypted_data, key):
        """ถอดรหัส AES-256 (CBC)"""
        try:
            key_hash = hashlib.sha256(key.encode()).digest()
            raw_data = base64.b64decode(encrypted_data)
            iv = raw_data[:16]
            ciphertext = raw_data[16:]
            cipher = AES.new(key_hash, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
            return decrypted.decode('utf-8')
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def rsa_generate_keys():
        """สร้างคู่กุญแจ RSA (2048 bits)"""
        key = RSA.generate(2048)
        private_key = key.export_key().decode('utf-8')
        public_key = key.publickey().export_key().decode('utf-8')
        return private_key, public_key

    @staticmethod
    def rsa_encrypt(message, public_key_str):
        """เข้ารหัสด้วยกุญแจสาธารณะ RSA"""
        key = RSA.import_key(public_key_str)
        cipher = PKCS1_OAEP.new(key)
        encrypted = cipher.encrypt(message.encode())
        return base64.b64encode(encrypted).decode('utf-8')

    @staticmethod
    def rsa_decrypt(encrypted_message, private_key_str):
        """ถอดรหัสด้วยกุญแจส่วนตัว RSA"""
        try:
            key = RSA.import_key(private_key_str)
            cipher = PKCS1_OAEP.new(key)
            decrypted = cipher.decrypt(base64.b64decode(encrypted_message))
            return decrypted.decode('utf-8')
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def blowfish_encrypt(data, key):
        """เข้ารหัส Blowfish"""
        cipher = Blowfish.new(key.encode(), Blowfish.MODE_ECB)
        padded_data = pad(data.encode(), Blowfish.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted).decode('utf-8')

    @staticmethod
    def fernet_generate_key():
        """สร้างกุญแจ Fernet"""
        return Fernet.generate_key().decode()

    @staticmethod
    def fernet_encrypt(message, key):
        """เข้ารหัส Fernet"""
        f = Fernet(key.encode())
        return f.encrypt(message.encode()).decode()
