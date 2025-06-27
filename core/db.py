import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Devices (
            mac_address TEXT PRIMARY KEY,
            device_name TEXT,
            first_seen DATETIME,
            last_seen DATETIME,
            frequency_count INTEGER,
            rssi INTEGER,
            manufacturer TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def purge_old_entries(days: int = 30) -> None:
    cutoff = datetime.now() - timedelta(days=days)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Devices WHERE last_seen < ?", (cutoff,))
    conn.commit()
    conn.close()
