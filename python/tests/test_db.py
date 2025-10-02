import sqlite3
import pytest

from python.bitcoin_wallet.utils.db.schema_init import init_db
from python.bitcoin_wallet.database.models import WalletDB, AddressDB, TransactionDB
from python.bitcoin_wallet.utils.db.db_op import DB_NAME

init_db()

# ---------------- FIXTURE SETUP ----------------
@pytest.fixture(scope="function", autouse=True)
def temp_db(monkeypatch):
    """
    Use an in-memory SQLite database for testing.
    Monkeypatch get_db_cursor to always use this temporary DB.
    """
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    init_db(conn) 

    def get_cursor():
        return conn.cursor()

    # Monkeypatch get_db_cursor in all modules
    monkeypatch.setattr("python.bitcoin_wallet.utils.db.db_op.get_db_cursor", lambda: conn.cursor())

    yield conn
    conn.close()


# ---------------- WALLETDB TESTS ----------------
def test_create_and_delete_wallet(temp_db):
    wallet_db = WalletDB()
    wallet_id = wallet_db.create_wallet(
        "TestWallet",
        b"encrypted_mnemonic",
        "argon2id",
        b"salt",
        '{"time_cost":2,"memory_cost":65536,"parallelism":4,"hash_len":32}',
        b"nonce",
        1
    )

    assert isinstance(wallet_id, int)

    # Verify inserted
    row = wallet_db.get_wallet(wallet_id)
    assert row is not None

    # Delete wallet
    wallet_db.delete_wallet(wallet_id)
    row = wallet_db.get_wallet(wallet_id)
    assert row is None


# ---------------- ADDRESSDB TESTS ----------------
def test_create_and_list_addresses(temp_db):
    wallet_db = WalletDB()
    wallet_id = wallet_db.create_wallet(
        "AddrWallet",
        b"enc",
        "argon2id",
        b"salt",
        "{}",
        b"nonce",
        1
    )

    addr_db = AddressDB()
    addr_id = addr_db.create_address(
        wallet_id,
        "tb1qtestaddress123",
        "p2wpkh",
        0,
        "m/44'/0'/0'/0/0",
        is_used=False,
        is_change=False
    )

    assert isinstance(addr_id, int)

    # Verify in list
    addrs = addr_db.all_addresses(wallet_id)
    assert len(addrs) == 1
    assert addrs[0][2] == "tb1qtestaddress123"


def test_delete_address(temp_db):
    wallet_db = WalletDB()
    wallet_id = wallet_db.create_wallet(
        "AddrWallet2",
        b"enc",
        "argon2id",
        b"salt",
        "{}",
        b"nonce",
        1
    )

    addr_db = AddressDB()
    addr_id = addr_db.create_address(
        wallet_id,
        "tb1qdelete123",
        "p2wpkh",
        1,
        "m/44'/0'/0'/0/1"
    )

    # Delete
    addr_db.delete_address("tb1qdelete123")
    addrs = addr_db.all_addresses(wallet_id)
    assert len(addrs) == 0


# ---------------- TRANSACTIONDB TESTS ----------------
def test_add_and_list_transaction(temp_db):
    wallet_db = WalletDB()
    wallet_id = wallet_db.create_wallet(
        "TxWallet",
        b"enc",
        "argon2id",
        b"salt",
        "{}",
        b"nonce",
        1
    )

    tx_db = TransactionDB()
    txid = "abcd1234"
    raw_tx = b"rawbytes"
    tx_id = tx_db.add_transaction(wallet_id, txid, raw_tx, "pending")

    assert isinstance(tx_id, int)
    print(tx_id)

    # Verify retrieval
    txs = tx_db.all_transactions(wallet_id)
    assert len(txs) == 1
    assert txs[0][2] == txid 
