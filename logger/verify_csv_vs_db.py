# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 11:17:01 2025

@author: cangelop
"""

import sqlite3
import pandas as pd
import os
from config import DB_PATH  # Ensure this points to logger/ping_dashboard.db

CSV_FILE = os.path.join("data", "your_csv_file.csv")  # update path if needed

# Load CSV
csv_df = pd.read_csv(CSV_FILE)
csv_count = len(csv_df)

# Load DB
conn = sqlite3.connect(DB_PATH)
db_count = conn.execute("SELECT COUNT(*) FROM pings").fetchone()[0]
conn.close()

print(f"CSV rows: {csv_count}")
print(f"DB rows: {db_count}")

if csv_count == db_count:
    print("[OK] DB contains all CSV rows.")
elif db_count > csv_count:
    print(f"[INFO] DB has {db_count - csv_count} more rows (older data included).")
else:
    print(f"[ERROR] DB missing {csv_count - db_count} rows from CSV.")
