# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 10:07:52 2025

@author: cangelop
"""

import sqlite3
import os

# Path to your database
DB_PATH = os.path.join("logger", "ping_dashboard.db")
# Total logs
conn = sqlite3.connect("logger/ping_dashboard.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM pings")
print("Total logs:", cursor.fetchone()[0])


def show_last_10_offline():
    """Display the last 10 offline events from the database."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, name, ip
        FROM pings
        WHERE status = 'Offline'
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    rows = cursor.fetchall()

    print("\n=== Last 10 Offline Entries ===")
    if not rows:
        print("No offline entries found.")
    else:
        for ts, name, ip in rows:
            print(f"{ts} | {name} | {ip}")

    conn.close()

if __name__ == "__main__":
    show_last_10_offline()
