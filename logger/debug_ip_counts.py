# -*- coding: utf-8 -*-
"""
Created on Thu Jul 31 11:15:35 2025

@author: cangelop
"""

import sys, os
# Add project root (one level up from logger folder) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import DB_PATH
import sqlite3
import pandas as pd


# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)

# Query: total runs per IP and first/last seen
query = """
SELECT name, ip,
       COUNT(*) AS total_runs,
       MIN(date(timestamp)) AS first_seen,
       MAX(date(timestamp)) AS last_seen
FROM pings
GROUP BY name, ip
ORDER BY total_runs ASC;
"""

df = pd.read_sql_query(query, conn)
conn.close()

# Show summary
print("=== ALL IP COUNTS (sorted by lowest first) ===")
print(df)

# Filter for low-count IPs (<10 runs)
low_count_df = df[df['total_runs'] < 10]

print("\n=== LOW COUNT IPs (<10 runs) ===")
print(low_count_df)

# Save results to CSV
output_path = os.path.join(os.path.dirname(DB_PATH), "low_count_ips.csv")
df.to_csv(output_path, index=False)
print(f"\nFull counts saved to: {output_path}")
