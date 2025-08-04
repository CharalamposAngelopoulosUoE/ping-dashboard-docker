# logger/migrate_csv_to_db.py
"""
Migrate all historical weekly CSV logs into SQLite database
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
import sqlite3
import pandas as pd
from config import DB_PATH

CSV_PATH = r"C:\Users\cangelop\Desktop\Python\Ping_Dashboard_v2\logger\logs\week_21_07_2025.csv"

def migrate_csv_to_db():
    # Ensure database folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Initialize database schema if not exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

    print(f"[OK] Database initialized at: {DB_PATH}")

    # Load CSV
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] CSV file not found: {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)

    # Normalize timestamp format
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', dayfirst=True)
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Insert rows
    rows_imported = 0
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO pings (timestamp, name, ip, status)
            VALUES (?, ?, ?, ?)
        """, (row['timestamp'], row['name'], row['ip'], row['status']))
        rows_imported += 1

    conn.commit()
    conn.close()

    print(f"[OK] Imported {rows_imported} rows from {os.path.basename(CSV_PATH)}")

if __name__ == "__main__":
    migrate_csv_to_db()
