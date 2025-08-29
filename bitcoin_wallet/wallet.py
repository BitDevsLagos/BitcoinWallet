from bitcoinlib.keys import HDKey
from bitcoinlib.mnemonic import Mnemonic


class BitcoinWallet:
    """
    A simple, in-memory Bitcoin wallet generator.

    This class focuses on the core generation logic: creating a wallet
    from a mnemonic phrase and deriving the master keys. It does not store
    any data on the filesystem.
    """

    def __init__(self, mnemonic=None, network='testnet'):
        """
        Initializes the wallet from a mnemonic phrase.

        If no mnemonic is provided, a new 12-word mnemonic is generated.

        Args:
            mnemonic (str, optional): A 12 or 24-word BIP39 mnemonic phrase.
                                      Defaults to None, which triggers generation.
            network (str): The network to use ('bitcoin' or 'testnet').
                           Defaults to 'testnet'.
        """
        if mnemonic:
            self.mnemonic = mnemonic
        else:
            # Generate a new 12-word mnemonic
            self.mnemonic = Mnemonic().generate()

        # Create a master Hierarchical Deterministic (HD) key from the mnemonic
        self.master_key = HDKey.from_passphrase(self.mnemonic, network=network)

    def get_mnemonic(self):
        """
        Returns the wallet's mnemonic phrase.

        Returns:
            str: The mnemonic phrase associated with this wallet instance.
        """
        return self.mnemonic

    def get_master_private_key(self, wif=True):
        """
        Returns the master private key.

        Args:
            wif (bool): If True (default), returns the key in Wallet Import Format.
                        If False, returns the raw private key as a hex string.

        Returns:
            str: The master private key.
        """
        if wif:
            return self.master_key.wif()
        else:
            return self.master_key.private_hex

    def get_master_public_key(self):
        """
        Returns the master public key.

        Returns:
            str: The master public key as a hex-encoded string.
        """
        return self.master_key.public_hex


if __name__ == '__main__':
    print("--- Simple Wallet Generation Example ---")

    # Example 1: Create a wallet with a newly generated mnemonic
    print("\n1. Creating a new wallet...")
    new_wallet = BitcoinWallet(network='testnet')

    mnemonic = new_wallet.get_mnemonic()
    private_key_wif = new_wallet.get_master_private_key()
    public_key_hex = new_wallet.get_master_public_key()

    print(f"   Mnemonic: {mnemonic}")
    print(f"   Master Private Key (WIF): {private_key_wif}")
    print(f"   Master Public Key (Hex): {public_key_hex}")

    # Example 2: Create a wallet from an existing mnemonic
    print("\n2. Loading a wallet from an existing mnemonic...")
    existing_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    existing_wallet = BitcoinWallet(mnemonic=existing_mnemonic, network='testnet')

    loaded_private_key = existing_wallet.get_master_private_key()
    loaded_public_key = existing_wallet.get_master_public_key()

    print(f"   Mnemonic: {existing_wallet.get_mnemonic()}")
    print(f"   Master Private Key (WIF): {loaded_private_key}")
    print(f"   Master Public Key (Hex): {loaded_public_key}")
