import pytest
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
