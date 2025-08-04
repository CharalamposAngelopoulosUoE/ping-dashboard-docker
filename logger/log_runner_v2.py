import os
import sqlite3
import pandas as pd
import time
from datetime import datetime
from utils import ping_host
from config import DB_PATH, IP_LIST_FILE

RETRY_COUNT = 4  # Number of ping retries

def safe_insert(cursor, query, params):
    """Insert into DB with retry if database is locked."""
    retries = 5
    while retries > 0:
        try:
            cursor.execute(query, params)
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("[WARN] Database is locked, retrying...")
                time.sleep(2)
                retries -= 1
            else:
                raise
    raise RuntimeError("Failed to write to DB after multiple retries")

def log_status():
    """Ping all IPs from Excel and log results into SQLite database."""
    try:
        # Ensure IP list exists
        if not os.path.exists(IP_LIST_FILE):
            raise FileNotFoundError(f"IP list file missing: {IP_LIST_FILE}")
        
        df = pd.read_excel(IP_LIST_FILE)

        # Connect to DB with timeout
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cursor = conn.cursor()

        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                name TEXT,
                ip TEXT,
                status TEXT
            )
        """)
        conn.commit()

        # Current timestamp
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Ping each IP and log
        for _, row in df.iterrows():
            name, ip = row["Name"], row["IP Address"]

            # Retry ping logic
            status = "Offline"
            for _ in range(RETRY_COUNT):
                if ping_host(ip):
                    status = "Online"
                    break

            safe_insert(
                cursor,
                "INSERT INTO pings (timestamp, name, ip, status) VALUES (?, ?, ?, ?)",
                (now, name, ip, status)
            )

            print(f"Daily Logged {ip} - {status}")

        conn.commit()
        print(f"[OK] Logged scan at {now}")

    except Exception as e:
        print(f"[ERROR] Failed to log status: {e}")

    finally:
        if 'conn' in locals():
            conn.close()

# Run standalone
if __name__ == "__main__":
    log_status()
