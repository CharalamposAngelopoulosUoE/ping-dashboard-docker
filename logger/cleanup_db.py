# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 11:28:15 2025

@author: cangelop
"""
# Add project root to path
import os, sys, sqlite3, pandas as pd, datetime

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#import sqlite3
from config import DB_PATH

def cleanup_duplicates():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create a temporary table with duplicates resolved (Offline prioritized)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pings_clean AS
    SELECT * FROM pings WHERE 1=0
    """)

    # Clear previous clean table
    cur.execute("DELETE FROM pings_clean")

    # Insert deduplicated data
    cur.execute("""
    INSERT INTO pings_clean (timestamp, name, ip, status)
    SELECT timestamp, name, ip, MAX(status)  -- 'Offline' > 'Online'
    FROM (
        SELECT timestamp, name, ip,
               CASE status
                   WHEN 'Offline' THEN 2
                   WHEN 'Online' THEN 1
               END AS status_priority,
               status
        FROM pings
    )
    GROUP BY timestamp, ip
    """)

    # Replace old table with cleaned one
    cur.execute("DROP TABLE pings")
    cur.execute("ALTER TABLE pings_clean RENAME TO pings")

    conn.commit()
    conn.close()
    print("[OK] Duplicates removed and Offline prioritized.")

if __name__ == "__main__":
    cleanup_duplicates()
