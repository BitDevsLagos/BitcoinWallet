import requests
from bitcoinlib.keys import HDKey
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.transactions import Transaction
import qrcode


class BitcoinWallet:
    """
    A simple, in-memory Bitcoin wallet generator.

    This class focuses on the core generation logic: creating a wallet
    from a mnemonic phrase and deriving the master keys. It does not store
    any data on the filesystem.
    """

    def __init__(self, mnemonic=None, network='bitcoin'):
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

    def get_address(self):
        """
        Returns the a bitcoin address9Defaults to bech32 format.

        Returns:
            str: The bech32 address (starts with "bc1" for mainnet and "tb1" for testnet).
        """
        return self.master_key.address()
    
    def generate_qr_code(self, filename=None):
        """
        Generate a PNG QR code for the bech32 address.

        Args:
            file_name (str, optional): Filename (with .png) to save the QR code.
                                    Defaults to '<address>.png' in cwd.
        Returns:
            str: Path to the saved QR code image.
        """
        address = self.get_address()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(address)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        if not filename:
            filename = f"{address}.png"
        img.save(filename)
        return filename
    
    def get_balance(self):
        """
        Fetch the confirmed balance (in satoshis) for the wallet's address using Blockstream API.

        Returns:
            int: The confirmed balance in satoshis.
        Raises:
            Exception: If the API call fails.
        """
        address = self.get_address()
        if self.master_key.network.name == 'testnet':
            api_url = f"https://blockstream.info/testnet/api/address/{address}"
        else:
            api_url = f"https://blockstream.info/api/address/{address}"

        try:
            resp = requests.get(api_url)
            resp.raise_for_status()
            data = resp.json()
            # 'chain_stats' contains confirmed transactions
            return data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
        except Exception as e:
            raise Exception(f"Failed to fetch balance: {e}")

    def send_bitcoin(self, to_address, amount_sats, fee_rate=1.0, network=None):
        """
        Build, sign, and broadcast a Bitcoin transaction.

        Args:
            to_address (str): Recipient's Bitcoin address.
            amount_sats (int): Amount to send in satoshis.
            fee_rate (float): Fee rate in sat/vbyte (default: 1.0).
            network (str, optional): 'bitcoin' or 'testnet'. Uses wallet's network if not specified.

        Returns:
            str: Transaction ID if broadcast is successful.

        Raises:
            Exception: If transaction fails.
        """
        # 1. Fetch UTXOs for this address
        # For HD wallets, you might need an API to fetch all UXTOs for derived addresses.
        # Also validate the returned address format (library/address validator) before using it in URLs.
        address = self.get_address()

        # Safer to normalize the string and detect testnet via substring
        net = network or self.master_key.network.name
        if net == 'testnet':
            utxo_url = f"https://blockstream.info/testnet/api/address/{address}/utxo"
            push_url = "https://blockstream.info/testnet/api/tx"
        else:
            utxo_url = f"https://blockstream.info/api/address/{address}/utxo"
            push_url = "https://blockstream.info/api/tx"

        utxos = requests.get(utxo_url).json()
        if not utxos:
            raise Exception("No UTXOs available to spend.")

        # 2. Select UTXOs to cover amount + fee (simple greedy selection)
        selected = []
        total = 0
        for utxo in utxos:
            selected.append(utxo)
            total += utxo['value']
            if total >= amount_sats:
                break
        if total < amount_sats:
            raise Exception("Insufficient funds.")

        # 3. Build transaction
        tx = Transaction(network=net)
        for utxo in selected:
            tx.add_input(prev_txid=utxo['txid'], output_n=utxo['vout'], value=utxo['value'], address=address)
        tx.add_output(address=to_address, value=amount_sats)

        # 4. Estimate fee and add change output if needed
        tx_size = tx.size()
        fee = int(fee_rate * tx_size)
        change = total - amount_sats - fee
        if change > 0:
            tx.add_output(address=address, value=change)

        # 5. Sign transaction
        tx.sign(self.master_key)

        # 6. Broadcast transaction
        rawtx = tx.raw_hex()
        resp = requests.post(push_url, data=rawtx)
        if resp.status_code != 200:
            raise Exception(f"Broadcast failed: {resp.text}")
        return resp.text  # txid

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

    # Example 3: Generate Bech32 address from a new mnemonic
    print("\n3. Generating a Bech32 wallet address from a new mnemonic...")
    bech32_address_new = new_wallet.get_address()
    print(f"    Address: {bech32_address_new}")

    # Example 4: Generate Bech32 address from an existing mnemonic
    print("\n4. Generating a Bech32 wallet address from an existing mnemonic...")
    bech32_address_existing = existing_wallet.get_address()
    print(f"    Address: {bech32_address_existing}")

    # Example 5: Generate QR code for the address
    print("\n5. Generating a QR code for the Bech32 address...")
    qr_path = existing_wallet.generate_qr_code()
    print(f"    QR code saved to: {qr_path}")

    # Example 6: Fetch balance for the address
    print("\n6. Fetching the confirmed balance for the address...")
    try:
        balance = existing_wallet.get_balance()
        print(f"    Confirmed Balance for {bech32_address_existing}: {balance} satoshis")
    except Exception as e:
        print(f"    Error fetching balance: {e}")

    # Example 7: Sending Bitcoin (commented out to prevent accidental spending)
    print("\n7. Sending Bitcoin to another address...")
    try:
        recipient_address = "tb1qh4eju9vpchznqv043mdrk7t2s32freruty77qk"
        amount_to_send = 100  # in satoshis
        txid = existing_wallet.send_bitcoin(to_address=recipient_address, amount_sats=amount_to_send, fee_rate=1.0)
        print(f"    Transaction sent! TXID: {txid}")
    except Exception as e:
        print(f"    Error sending transaction: {e}")
