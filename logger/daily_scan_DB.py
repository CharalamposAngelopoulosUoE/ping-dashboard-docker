# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 15:55:49 2025

@author: cangelop
"""
# logger/daily_scan_DB.py
# logger/daily_scan_DB.py

import sys, os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import only daily logging logic
from logger.log_runner_v2 import log_status

if __name__ == "__main__":
    print("[INFO] Daily DB Scan starting...")
    log_status()
    print("[INFO] Daily DB Scan completed.")

