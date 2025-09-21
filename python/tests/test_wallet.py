import pytest
from pyzbar.pyzbar import decode
from PIL import Image
from bitcoin_wallet.wallet import BitcoinWallet


class TestBitcoinWallet:
    """
    Unit tests for the BitcoinWallet class.
    """

    def test_create_new_wallet(self):
        """
        Test that a new wallet is created with a 12-word mnemonic
        when none is provided, and that keys are generated.
        """
        wallet = BitcoinWallet()
        mnemonic = wallet.get_mnemonic()
        assert isinstance(mnemonic, str)
        assert len(mnemonic.split(' ')) == 12

        priv_key = wallet.get_master_private_key()
        pub_key = wallet.get_master_public_key()
        assert isinstance(priv_key, str)
        assert len(priv_key) > 0
        assert isinstance(pub_key, str)
        assert len(pub_key) > 0

    def test_create_from_existing_mnemonic(self):
        """
        Test creating a wallet from a known mnemonic phrase.
        """
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        wallet = BitcoinWallet(mnemonic=mnemonic)
        assert wallet.get_mnemonic() == mnemonic

    def test_deterministic_key_generation(self):
        """
        Test that the same mnemonic phrase always results in the same
        private and public keys.
        """
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        wallet1 = BitcoinWallet(mnemonic=mnemonic)
        wallet2 = BitcoinWallet(mnemonic=mnemonic)

        assert wallet1.get_master_private_key() == wallet2.get_master_private_key()
        assert wallet1.get_master_public_key() == wallet2.get_master_public_key()

    def test_different_mnemonics_produce_different_wallets(self):
        """
        Test that two wallets created without specified mnemonics have
        different keys, as they should have different mnemonics.
        """
        wallet1 = BitcoinWallet()
        wallet2 = BitcoinWallet()

        # It's astronomically unlikely, but check just in case of a bad random source
        assert wallet1.get_mnemonic() != wallet2.get_mnemonic()
        assert wallet1.get_master_private_key() != wallet2.get_master_private_key()

    def test_bech32_address_format(self):
        """
        Test that get_bech32_address returns a valid testnet Bech32 address (starts with 'tb1').
        """
        wallet = BitcoinWallet(network='bitcoin')
        addr = wallet.get_address()
        assert isinstance(addr, str)
        assert addr.startswith('bc1')
        assert len(addr) > 10  # Bech32 addresses are longer

    def test_qr_address_generation(self):
        """
        Test that generate_qr_code creates a QR code file for the wallet address.

        Also verifies that the QR code encodes the correct address.
        """
        wallet = BitcoinWallet()
        addr = wallet.get_address()
        qr_path = wallet.generate_qr_code(filename='test_qr.png')
        assert qr_path == 'test_qr.png'

        # Decode the QR code to verify it encodes the correct address
        decoded = decode(Image.open(qr_path))[0].data.decode()
        assert decoded == addr

        # Check that the file was created
        import os
        assert os.path.isfile(qr_path)

        # Clean up the test QR code file
        os.remove(qr_path)

    def test_get_balance(self):
        """
        Test that get_balance returns an integer >= 0 for a valid address.

        Note: This is an integration test and requires internet access.
        The balance for a new wallet is expected to be 0.
        """
        wallet = BitcoinWallet(network='testnet')
        balance = wallet.get_balance()
        assert isinstance(balance, int)
        assert balance >= 0

        