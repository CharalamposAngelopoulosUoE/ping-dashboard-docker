# logger/db_setup.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
import os

# Path to database (adjust if needed)
DB_PATH = os.path.join(os.path.dirname(__file__), "ping_dashboard.db")

def create_tables():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Optional: schema version table (future migrations)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_on TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Devices table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip TEXT NOT NULL UNIQUE
        )
        """)

        # Pings table linked to devices
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            name TEXT,
            ip TEXT,
            status TEXT NOT NULL,
            device_id INTEGER,
            FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE
        )
        """)

        # Indexes for performance
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pings_timestamp_ip
        ON pings (timestamp, ip);
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pings_status
        ON pings (status);
        """)

        conn.commit()
        print(f"✅ Database initialized successfully at: {DB_PATH}")

    except sqlite3.Error as e:
        print(f"❌ Error creating database tables: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_tables()
