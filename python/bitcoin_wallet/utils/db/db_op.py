import sqlite3
from contextlib import contextmanager

DB_NAME = "wallet.db"

@contextmanager
def get_db_cursor():
    "Yield DB cursor for database operation"
    
    con = sqlite3.connect(DB_NAME)

    try:
        cur = con.cursor()
        yield cur
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()