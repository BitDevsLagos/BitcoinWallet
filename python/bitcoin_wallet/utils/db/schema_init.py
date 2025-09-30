import sqlite3
from python.bitcoin_wallet.utils.db.db_op import DB_NAME

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    encrypted_mnemonic BLOB NOT NULL,
    kdf TEXT NOT NULL,
    kdf_salt BLOB NOT NULL,
    kdf_params TEXT NOT NULL,
    enc_nonce BLOB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    address TEXT NOT NULL UNIQUE,
    address_type TEXT CHECK(address_type IN ('p2pkh','p2sh','p2wpkh','p2tr')),
    index_num INTEGER,
    derivation_path TEXT NOT NULL,
    is_change BOOLEAN DEFAULT 0,
    is_used BOOLEAN DEFAULT 0,
    FOREIGN KEY(wallet_id) REFERENCES wallets(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    txid TEXT NOT NULL UNIQUE,
    raw_tx BLOB,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(wallet_id) REFERENCES wallets(id)
);

CREATE TABLE IF NOT EXISTS utxos (
    txid TEXT NOT NULL,
    vout INTEGER NOT NULL,
    wallet_id INTEGER NOT NULL,
    address TEXT NOT NULL,
    amount_sat INTEGER NOT NULL,
    script_pubkey BLOB NOT NULL,
    spent BOOLEAN DEFAULT 0,
    PRIMARY KEY (txid, vout),
    FOREIGN KEY(wallet_id) REFERENCES wallets(id)
);
"""

def init_db(con=sqlite3.connect(DB_NAME)):
    cur = con.cursor()
    cur.executescript(SCHEMA_SQL)
    con.commit()
    con.close()
    print(f"[DB] Initialized database schema in {DB_NAME}")