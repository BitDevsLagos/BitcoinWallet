from python.bitcoin_wallet.utils.db.db_op import get_db_cursor
from python.bitcoin_wallet.utils.db.schema_init import init_db

# Initialize and create the database with the complete table
# TODO: Maybe change it to a better one

# init_db()

# TODO: Change the data types of the parameters

class WalletDB:
    """Sqlite object to handle wallet operations"""

    def __init__(self):
        pass

    def create_wallet(self, name: str, encrypted_mnemonic: bytes, kdf: str, kdf_salt: bytes, kdf_params: str, enc_nonce: bytes, version: int):
        with get_db_cursor() as cur:
            cur.execute(
                """INSERT INTO wallets (name, encrypted_mnemonic, kdf, kdf_salt, kdf_params, enc_nonce, version) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, encrypted_mnemonic, kdf, kdf_salt, kdf_params, enc_nonce, version)
            )
            return cur.lastrowid

    def delete_wallet(self, wallet_id: int):
        with get_db_cursor() as cur:
            cur.execute(
                "DELETE FROM wallets WHERE id = ?",
                (wallet_id,)
            )

    def get_wallet(self, wallet_id: int):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT * FROM wallets WHERE id = ?",
                (wallet_id,)
            )
            return cur.fetchone()

class AddressDB:
    """Sqlite object to handle address operations"""

    def __init__(self):
        pass

    def create_address(self, wallet_id: int, address: str, address_type: str, 
                       index_num: int, derivation_path: str, is_used: bool=False, 
                       is_change: bool=False):
        with get_db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO addresses (wallet_id, address, address_type, index_num, derivation_path, is_change, is_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (wallet_id, address, address_type, index_num, derivation_path, is_change, is_used)
            )
            return cur.lastrowid

    def delete_address(self, address):
        with get_db_cursor() as cur:
            cur.execute(
                "DELETE FROM addresses WHERE address = ?",
                (address,)
            )

    def all_addresses(self, wallet_id: str):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT * FROM addresses WHERE wallet_id = ?",
                (wallet_id,)
            )
            return cur.fetchall()

class TransactionDB:
    """Stores all wallet transaction activity"""
    
    def __init__(self):
        ...

    def add_transaction(self, wallet_id: int, txid: str, raw_tx: bytes, status: str="pending"):
        with get_db_cursor() as cur:
            cur.execute(
                """INSERT OR IGNORE INTO transactions (wallet_id, txid, raw_tx, status) VALUES(?, ?, ?, ?)""",
                (wallet_id, txid, raw_tx, status,)
            )
            return cur.lastrowid

    def all_transactions(self, wallet_id: int):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT * FROM transactions WHERE wallet_id = ?",
                (wallet_id,)
            )
            return cur.fetchall()
        