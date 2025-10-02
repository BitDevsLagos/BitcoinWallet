import pytest
from ecdsa import BadSignatureError
from python.bitcoin_wallet.utils.crypto.keys import Keys, HDKeys


@pytest.fixture
def keys():
    return Keys()

@pytest.fixture
def message():
    return b"this is a test message"

@pytest.fixture
def mnemonic():
    return "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"


def test_generate_private_and_public_key(keys):
    """Private key and public key are generated and are not None"""
    assert keys.private_key is not None
    assert keys.public_key is not None

def test_sign_and_verify_message(keys, message):
    """Signing and verifying works with the same key pair"""
    sig = keys.sign_message(keys.private_key, message)
    assert keys.verify_signature(keys.public_key.to_string(), message, sig)

def test_verify_with_wrong_signature(keys, message):
    """Verification should fail with a wrong signature"""
    sig = keys.sign_message(keys.private_key, message)
    wrong_sig = sig[:-1] + (b"\x00" if sig[-1:] != b"\x00" else b"\x01")

    assert not keys.verify_signature(keys.public_key.to_string(), message, wrong_sig)

def test_verify_with_wrong_message(keys, message):
    """Verification should fail when message is tampered"""
    sig = keys.sign_message(keys.private_key, message)
    tampered = message + b"tampered"

    assert not keys.verify_signature(keys.public_key.to_string(), tampered, sig)


def test_generate_mnemonic_and_seed():
    """Mnemonic and derived seed should not be empty"""
    hd = HDKeys(b"dummy_seed")
    mnemonic = hd.generate_mnemonic()
    seed = hd.generate_seed_from_mnemonic(mnemonic)

    assert isinstance(mnemonic, str)
    assert len(mnemonic.split(" ")) in [12, 15, 18, 21, 24]  # valid word count
    assert isinstance(seed, bytes)
    assert len(seed) > 0

def test_generate_bip44_address(mnemonic):
    """BIP44 address generation should return valid dict"""
    hd = HDKeys(b"dummy_seed")
    seed = hd.generate_seed_from_mnemonic(mnemonic)

    addr = hd.generate_bip44_address(seed, account_idx=0, change=False, address_idx=0, include_priv=True)

    assert "address" in addr
    assert "public_key" in addr
    assert "private_key" in addr
    assert "path" in addr
    assert addr["path"].startswith("m/44'")

def test_get_address_from_path(mnemonic):
    """Getting an address from derivation path should work"""
    hd = HDKeys(b"dummy_seed")
    seed = hd.generate_seed_from_mnemonic(mnemonic)

    addr1 = hd.derive_address_from_path(seed, "m/44'/0'/0'/0/0", include_priv=True)
    addr2 = hd.derive_address_from_path(seed, "m/44'/0'/0'/0/0", include_priv=True)

    # Determinism check: same path and seed give same result
    assert addr1["address"] == addr2["address"]
    assert addr1["public_key"] == addr2["public_key"]
    assert addr1["private_key"] == addr2["private_key"]

def test_different_paths_generate_different_addresses(mnemonic):
    """Different derivation paths should generate different addresses"""
    hd = HDKeys(b"dummy_seed")
    seed = hd.generate_seed_from_mnemonic(mnemonic)

    addr1 = hd.derive_address_from_path(seed, "m/44'/0'/0'/0/0", include_priv=True)
    addr2 = hd.derive_address_from_path(seed, "m/44'/0'/0'/0/1", include_priv=True)

    assert addr1["address"] != addr2["address"]
