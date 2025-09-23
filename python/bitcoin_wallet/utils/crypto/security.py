import os
import json
import base64
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class Security:
    """
        Class for handling encrypting and decrypting of mnemonics phrases and seed
    """

    def __init__(self):
        pass

    def derive_argon2_key(self, password: str, salt: bytes, 
                          time_cost: int=2,
                          memory_cost: int=2**16, 
                          parallelism: int=4, 
                          hash_len: int=32) -> bytes:
        """Derives a key from a password using Argon2id"""

        return hash_secret_raw(
            secret=password.encode("utf-8"),
            salt=salt,
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            type=Type.ID
        )
    
    def derive_pbkdf2_key(self, password: str, salt: bytes, iterations: int=300_000, length: int=32) -> bytes:
        """Derives a key from a password using PBKDF2"""

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )

        return kdf.derive(password.encode("utf-8"))
    
    def encrypt_mnemonic(self, mnemonic_phrase: str, password: str) -> dict:
        """
            Encrypts Mnemonic phrase using AES-GCM
        
            Argon2: Generate a key from the password,
            AES-GCM: Encrypts the mnemonic phrase using the key from Argon2

            Result: kdf, salt, enc_nonce, and parameters
        """

        salt = os.urandom(16)
        key = self.derive_argon2_key(password, salt)
        aesgcm = AESGCM(key)
        enc_nonce = os.urandom(12)
        encrypted_mnemonic = aesgcm.encrypt(
                enc_nonce, 
                mnemonic_phrase.encode("utf-8"), 
                None
            )

        return {
            "kdf": "argon2id",
            "kdf_salt": base64.b64encode(salt).decode(),
            "kdf_params": json.dumps({
                "time_cost": 2,
                "memory_cost": 2**16,
                "parallelism": 4,
                "hash_len": 32
            }),
            "enc_nonce": base64.b64encode(enc_nonce).decode(),
            "encrypted_mnemonic": base64.b64encode(encrypted_mnemonic).decode(),
            "version": 1
        }
    
    def decrypt_mnemonic(self, encrypted_blob: dict, password: str) -> str:
        """
            Decrypts Mnemonic phrase using AES-GCM
            
            Returns: decrypted Mnemonic
        """

        assert encrypted_blob["kdf"] == "argon2id", "Unsupported KDF"
        salt = base64.b64decode(encrypted_blob["kdf_salt"])
        kdf_params = json.loads(encrypted_blob["kdf_params"])
        enc_nonce = base64.b64decode(encrypted_blob["enc_nonce"])
        encrypted_mnemonic = base64.b64decode(encrypted_blob["encrypted_mnemonic"])

        key = self.derive_argon2_key(
            password,
            salt,
            time_cost=kdf_params["time_cost"],
            memory_cost=kdf_params["memory_cost"],
            parallelism=kdf_params["parallelism"],
            hash_len=kdf_params["hash_len"]
        )

        aesgcm = AESGCM(key)
        decrypted_mnemonic = aesgcm.decrypt(enc_nonce, encrypted_mnemonic, None)
        
        return decrypted_mnemonic.decode("utf-8")