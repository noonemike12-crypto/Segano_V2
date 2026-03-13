import os
import hashlib
import gnupg
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import utils as asym_utils

class CryptoEngine:
    def __init__(self, gpg_home="gpg_home"):
        if not os.path.exists(gpg_home):
            os.makedirs(gpg_home)
        self.gpg = gnupg.GPG(gnupghome=gpg_home)

    @staticmethod
    def derive_key(passphrase: str, salt: bytes = b'sieng_salt_123'):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(passphrase.encode())

    @staticmethod
    def aes_encrypt(data: bytes, passphrase: str) -> bytes:
        key = CryptoEngine.derive_key(passphrase)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext

    @staticmethod
    def aes_decrypt(encrypted_data: bytes, passphrase: str) -> bytes:
        key = CryptoEngine.derive_key(passphrase)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data

    @staticmethod
    def get_checksum(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    # --- PGP (Asymmetric) - Scope 1.1.3 ---
    def generate_pgp_key(self, name, email, passphrase, expiry='0'):
        input_data = self.gpg.gen_key_input(
            name_real=name,
            name_email=email,
            passphrase=passphrase,
            key_type="RSA",
            key_length=2048,
            expire_date=expiry
        )
        key = self.gpg.gen_key(input_data)
        return key

    def encrypt_pgp(self, data, recipient_email):
        encrypted = self.gpg.encrypt(data, recipient_email, always_trust=True)
        if not encrypted.ok:
            raise ValueError(f"PGP Encryption failed: {encrypted.stderr}")
        return str(encrypted)

    def decrypt_pgp(self, encrypted_data, passphrase):
        decrypted = self.gpg.decrypt(encrypted_data, passphrase=passphrase)
        if not decrypted.ok:
            raise ValueError(f"PGP Decryption failed: {decrypted.stderr}")
        return decrypted.data

    # --- ECC (Asymmetric) ---
    @staticmethod
    def generate_ecc_keys():
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        public_key = private_key.public_key()
        
        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return priv_pem, pub_pem

    @staticmethod
    def sign_data(data: bytes, priv_pem: bytes) -> bytes:
        private_key = serialization.load_pem_private_key(priv_pem, password=None, backend=default_backend())
        signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
        return signature

    @staticmethod
    def verify_signature(data: bytes, signature: bytes, pub_pem: bytes) -> bool:
        public_key = serialization.load_pem_public_key(pub_pem, backend=default_backend())
        try:
            public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
            return True
        except:
            return False
