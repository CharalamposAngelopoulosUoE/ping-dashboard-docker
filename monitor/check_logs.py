# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 10:05:47 2025

@author: cangelop
"""

import sqlite3

conn = sqlite3.connect("logger/ping_dashboard.db")
cursor = conn.cursor()

# Total logs
cursor.execute("SELECT COUNT(*) FROM pings")
print("Total logs:", cursor.fetchone()[0])

# Last 5 entries
cursor.execute("SELECT timestamp, name, ip, status FROM pings ORDER BY timestamp DESC LIMIT 5")
rows = cursor.fetchall()
for r in rows:
    print(r)

conn.close()
