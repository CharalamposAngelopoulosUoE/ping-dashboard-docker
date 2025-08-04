# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 11:35:10 2025

@author: cangelop
"""
import sys, os, pandas as pd, sqlite3

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DB_PATH

# Path to CSV file (update or pass as argument)
csv_path = r"C:\Users\cangelop\Desktop\Python\Ping_Dashboard_v2\logger\logs\week_21_07_2025.csv"

# Load CSV
csv_df = pd.read_csv(csv_path)
csv_count = len(csv_df)

# Normalize CSV timestamp
csv_df['timestamp'] = pd.to_datetime(csv_df['timestamp'], errors='coerce', dayfirst=True)
csv_df['timestamp'] = csv_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# DB connection
conn = sqlite3.connect(DB_PATH)

# Total rows in DB
db_total = conn.execute("SELECT COUNT(*) FROM pings").fetchone()[0]

# Rows filtered by project start date
db_filtered = conn.execute("""
    SELECT COUNT(*) FROM pings
    WHERE date(timestamp) >= '2025-07-21'
""").fetchone()[0]

conn.close()

print(f"CSV rows: {csv_count}")
print(f"DB total rows: {db_total}")
print(f"DB rows (from 2025-07-21): {db_filtered}")
