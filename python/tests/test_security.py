import pytest
import base64
from python.bitcoin_wallet.utils.crypto.security import Security

se = Security()

@pytest.fixture
def sec():
    return Security()

@pytest.fixture
def mnemonic():
    return "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

@pytest.fixture
def password():
    return "strong_password_123"

def test_encrypt_and_decrypt_mnemonic(sec, mnemonic, password):
    """Test that encrypt → decrypt returns the original mnemonic"""
    encrypted = sec.encrypt_mnemonic(mnemonic, password)
    decrypted = sec.decrypt_mnemonic(encrypted, password)

    assert mnemonic == decrypted

def test_encrypted_fields_are_base64(sec, mnemonic, password):
    """Ensure encrypted fields are valid base64 strings"""
    encrypted = sec.encrypt_mnemonic(mnemonic, password)

    # Check base64 decoding work
    assert base64.b64decode(encrypted["kdf_salt"])
    assert base64.b64decode(encrypted["enc_nonce"])
    assert base64.b64decode(encrypted["encrypted_mnemonic"])

def test_decrypt_with_wrong_password(sec, mnemonic, password):
    """Decryption should fail with wrong password"""
    encrypted = sec.encrypt_mnemonic(mnemonic, password)

    with pytest.raises(Exception):
        sec.decrypt_mnemonic(mnemonic, "wrong_password")

def test_different_salts_and_nonce_produce_different_ciphertext(sec, mnemonic, password):
    """Even with the same password & mnemonic, outputs should differ because of random salt & nonce"""
    enc1 = sec.encrypt_mnemonic(mnemonic, password)
    enc2 = sec.encrypt_mnemonic(mnemonic, password)

    assert enc1 != enc2

def test_derive_argon2_and_pbkdf2_keys(sec, password):
    """Check both key derivation functions produce 32-byte keys"""
    salt = b"fixed_salt_123456"
    key1 = sec.derive_argon2_key(password, salt)
    key2 = sec.derive_pbkdf2_key(password, salt)

    assert len(key1) == 32
    assert len(key2) == 32
    assert key1 != key2