# -*- coding: utf-8 -*-
"""
Created on Thu Jul 31 09:23:04 2025

@author: cangelop
"""

import sqlite3
import pandas as pd
import os

# Path to your ping_dashboard.db file
DB_PATH = r"C:\Users\cangelop\Desktop\Python\Ping_Dashboard_v2\logger\ping_dashboard.db"

def export_pings_table():
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)

    # Check available tables
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    print("Tables found:", tables['name'].tolist())

    # Ensure 'pings' table exists
    if 'pings' not in tables['name'].values:
        print("'pings' table not found in this database.")
        conn.close()
        return

    # Export entire pings table
    df = pd.read_sql_query("SELECT * FROM pings", conn)
    conn.close()

    # Save as CSV in same folder as DB
    export_path = os.path.join(os.path.dirname(DB_PATH), "pings_full_export.csv")
    df.to_csv(export_path, index=False)

    print(f"Exported {len(df)} rows to {export_path}")

if __name__ == "__main__":
    export_pings_table()

