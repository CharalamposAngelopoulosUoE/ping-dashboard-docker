Ping Dashboard v2 - README
===========================

Overview
--------
Ping Dashboard v2 is a network monitoring solution that:
- Periodically pings configured IPs and logs their online/offline status.
- Stores all data in a SQLite database (logger/ping_dashboard.db).
- Generates daily scan logs and weekly summary reports (PDF + email).
- Provides a Flask dashboard for real-time and historical monitoring.

Installation
------------
1. Install Python 3.13
2. Install dependencies:
   pip install pandas matplotlib fpdf flask colorama
3. Clone or extract this repository

Configuration
-------------
Edit config.py to set:
- DB_PATH: SQLite database location
- EMAIL_USER, EMAIL_PASS, EMAIL_RECEIVER: for weekly reports
- STATIC_REPORT_DIR: for chart storage

Usage
-----
1. Initial DB Rebuild (from legacy CSV)
   Run scripts/rebuild_db_from_csv.bat

2. Daily Scans (automated)
   - Script: scripts/daily_scan.bat
   - Logs results to database and logs/daily_scan.log

3. Weekly Reports (automated email)
   - Script: scripts/weekly_report_DB.bat
   - Generates PDF summary and emails it

4. Dashboard (manual)
   Run: python monitor/monitor.py dashboard
   Opens at: http://127.0.0.1:5000/

Task Scheduler Setup
--------------------
Daily Scan (3x per day: 10:00, 13:00, 16:00)
- Program: scripts/daily_scan.bat
- Start in: C:\Users\cangelop\Desktop\Python\Ping_Dashboard_v2

Weekly Report (every Monday 08:00)
- Program: scripts/weekly_report_DB.bat
- Start in: C:\Users\cangelop\Desktop\Python\Ping_Dashboard_v2

Data Storage
------------
- DB: logger/ping_dashboard.db
- Table: pings(timestamp TEXT, name TEXT, ip TEXT, status TEXT)
- CSV (legacy): logger/logs/ (only used for rebuilds)

Maintenance
-----------
- Check DB count: python logger/check_db_count.py
- Rebuild from CSV: scripts/rebuild_db_from_csv.bat
- Run weekly report manually: python logger/weekly_report_v2.py

Notes
-----
- Dashboard is internal (localhost only)
- Weekly emails summarize uptime, flapping, offline counts
- Daily scans must be scheduled for accurate weekly reports
