import os
from typing import Optional, Tuple, Dict

from ecdsa.curves import SECP256k1
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from ecdsa.util import sigencode_der, sigdecode_der
from hashlib import sha256

from mnemonic import Mnemonic
from bip_utils import (
    Bip39SeedGenerator, 
    Bip32Slip10Secp256k1, 
    Bip44, 
    Bip44Coins, 
    Bip44Changes,
    P2PKHAddr
)

# TODO: Check line 105

class Keys:
    """Class for low-level ECDSA key helpers (secp256k1)"""

    def __init__(self):
        self.private_key = self.generate_private_key()
        self.public_key = self.generate_public_key(self.private_key)

    def generate_private_key(self) -> bytes:
        """Generates fresh random 32-bytes private key
        
        Returns: private key (type(str))
        """
        sk = SigningKey.generate(curve=SECP256k1)

        return sk.to_string()

    def generate_public_key(self, private_key: str) -> bytes:
        """Generates public key from 32-bytes private key
        
        Returns: Uncompressed 64-bytes public key
        """
        sk = SigningKey.from_string(private_key, curve=SECP256k1)
        return sk.get_verifying_key()
    
    def compress_public_key(self, uncompresses_pubkey: bytes) -> bytes:
        """Compress a 64-bytes uncompressed public key to 33 bytes compresses public key
        
        b'\x02', b'\x03' - even and odd prefix for public key
        Returns: Compressed 33 bytes public key (type(bytes))
        """

        if len(uncompresses_pubkey) != 64:
            raise ValueError("Expect 64-bytes uncompressed public key (X || Y)")
        
        x = uncompresses_pubkey[:32]
        y = uncompresses_pubkey[32:]
        prefix = b'\x02' if (int.from_bytes(y, 'big') % 2) == 0 else b'\x03'

        return prefix + x
    
    def sign_message(self, private_key: str, message: bytes) -> bytes:
        """Signs message bytes deterministically
        
        Returns DER-encoded signature
        """

        sk = SigningKey.from_string(private_key, curve=SECP256k1)
        sig = sk.sign_deterministic(
            message, 
            hashfunc=sha256,
            sigencode=sigencode_der
        )

        return sig
    
    def verify_signature(self, public_key: bytes, message: bytes, sig: bytes) -> bool:
        # TODO: This only works for uncompressed public key, make it work for compressed public key
        # TODO: by writing the decompress_public_key function
        """Verify a DER-encoded signature given an uncompressed public key"""

        if len(public_key) != 64:
            raise ValueError("Expected 64-byte uncompressed public key")

        vk = VerifyingKey.from_string(public_key, curve=SECP256k1)
        try:
            return vk.verify(
                sig,
                message,
                hashfunc=sha256,
                sigdecode=sigdecode_der
            )
        except BadSignatureError:
            return False
        
class HDKeys(Keys):
    """
        TESTNET-

        Class for Hierarchical Deterministic (BIP39/BIP32/BIP44) (HD) keys helpers
    
        Usage:
            hd = HDKeys.from_mnemonic("abandon ...", passphrase="")
            seed = hd.seed
            addr = hd.generate_bip44_address(account_idx=0, change=False, address_idx=0)
    """

    def __init__(self, seed: bytes):
        # seed: BIP39 64-bytes seed
        self.seed = seed

    @classmethod
    def from_mnemonic(cls, mnemonic_phrase: str, passphrase: Optional[str]="") -> "HDKeys":
        """ Generates seed from mnemonic phrase, passphrase is optional
        
        Returns: a class instance of HDkeys
        """
        seed = Bip39SeedGenerator(mnemonic_phrase).Generate(passphrase)

        print(f"[x] Generating seed from mnemonic phrase ...")

        return cls(seed)

    def generate_mnemonic(self, strength: int = 256, lang: str='english') -> str:
        """Returns a new BIP39 mnemonic phrases"""

        mnemo = Mnemonic(lang)
        mnemonic_phrase = mnemo.generate(strength=strength)

        print(f"[x] Generating mnemonic phrase for language: {lang} ...")

        return mnemonic_phrase
    
    def generate_seed_from_mnemonic(cls, mnemonic_phrase: str, passphrase: Optional[str]="") -> bytes:
        """Generates seed from mnemonic phrase, passphrase is optional
        
        Returns: seed bytes
        """

        seed = Bip39SeedGenerator(mnemonic_phrase).Generate(passphrase)

        print(f"[x] Generating seed from mnemonic phrase ...")
        print(f"[x] Seed: ", seed.hex())

        return seed
    
    def generate_master_key_and_chain_code(self, seed: bytes) -> Tuple[bytes, bytes]:
        """
        Generate master private key and chain code from seed using SLIP-0010 secp256k1 (BIP32 variant).
        
        Returns:
            (master_private_key_bytes (32), master_chain_code_bytes (32))
        """
        bip32_ctx = Bip32Slip10Secp256k1.FromSeed(seed)
        master_priv = bip32_ctx.PrivateKey().ToRaw().ToBytes()
        chain_code = bip32_ctx.ChainCode().ToBytes()

        return master_priv, chain_code
    
    def derive_bip32_node_from_path(self, seed: bytes, derivation_path: str):
        """
        Derive a BIP32 node from a full derivation path

        Returns: Node context.
        """
        bip32_ctx = Bip32Slip10Secp256k1.FromSeed(seed)
        node = bip32_ctx.DerivePath(derivation_path)

        return node
    
    def derive_address_from_path(self, seed: bytes, derivation_path: str, include_priv: bool=False, testnet=True):
        """
        Derive address info from a full path. Uses Bip44/Bip32 constructs where appropriate.
        
        Returns Address data which include private key bytes only if include_priv=True
        """

        path = derivation_path.strip()
        bip32_ctx = Bip32Slip10Secp256k1.FromSeed(seed)
        node_ctx = bip32_ctx.DerivePath(path)
        pub_key = node_ctx.PublicKey().RawCompressed().ToBytes()

        net_ver = b'\x6f' if testnet else b'\x00'
        address = P2PKHAddr.EncodeKey(pub_key, net_ver=net_ver)

        result = {
            "path": node_ctx,
            "address": address,
            "public_key": pub_key
        }

        if include_priv:
            result["private_key"] = node_ctx.PrivateKey().Raw().ToBytes()

        return result

        
    def generate_bip44_address(self, seed: bytes, account_idx: int, 
                               change: bool, address_idx: int, 
                               testnet: bool=True, include_priv: bool=False) -> dict:
        """Generate a BIP44 address using bip_utils.Bip44 helper.

        Args:
            account_idx: account number (hardened)
            change: 0 for external chain, 1 for change chain
            address_idx: index of address under chain
            testnet: if True generates testnet addresses

        Returns:
            dict with path, address, public_key (compressed bytes), and private_key (raw bytes)
            if include_priv = True
        """

        coin_net = Bip44Coins.BITCOIN_TESTNET if testnet else Bip44Coins.BITCOIN
        bip44_mst_seed = Bip44.FromSeed(seed, coin_net)
        address_ctx = (
            bip44_mst_seed
            .Purpose()
            .Coin()
            .Account(account_idx)
            .Change(Bip44Changes.CHAIN_EXT if not change else Bip44Changes.Chain_EXT)
            .AddressIndex(address_idx)
        )

        print(f"[x] Generating BIP44 account for account index: {account_idx}, change: {change}, address index: {address_idx} ...")

        result = {
            "path": f"m/44'/{1 if testnet else 0}'/{account_idx}'/{0 if not change else 1}/{address_idx}",
            "address": address_ctx.PublicKey().ToAddress(),
            "public_key": address_ctx.PublicKey().RawCompressed().ToBytes(),
        }
        
        if include_priv:
            result["private_key"] = address_ctx.PrivateKey().Raw().ToBytes()

        return result
    