# Hardcoded config for dashboard-only version (no .env)

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Hardcoded database path
DB_PATH = os.path.join(BASE_DIR, "logger", "ping_dashboard.db")

# Hardcoded static reports path
STATIC_REPORT_DIR = os.path.join(BASE_DIR, "app", "static", "reports")
os.makedirs(STATIC_REPORT_DIR, exist_ok=True)

# Hardcoded IP list path
IP_LIST_FILE = os.path.join(BASE_DIR, "data", "IP_List.xlsx")
