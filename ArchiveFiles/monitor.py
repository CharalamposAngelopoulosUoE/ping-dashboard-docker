# monitor.py
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 09:44:22 2025
"""

import argparse
import threading
import webbrowser
import os
import platform

from daily_scan import run_scan
from app import app  # Import your Flask app


def open_browser():
    print("📣 open_browser() triggered")
    url = "http://127.0.0.1:5000"
    if platform.system() == "Windows":
        os.system(f"start {url}")
    else:
        webbrowser.open_new(url)


def main():
    parser = argparse.ArgumentParser(description="Ping Monitor CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- Scan Command ----
    scan_cmd = subparsers.add_parser("scan", help="Run a manual IP scan")
    scan_cmd.add_argument("--file", default="IP_List.xlsx", help="Excel file with IPs")
    scan_cmd.add_argument("--dry-run", action="store_true", help="Run without sending emails")

    # ---- Dashboard Command ----
    dashboard_cmd = subparsers.add_parser("dashboard", help="Launch the web dashboard")

    args = parser.parse_args()

    if args.command == "scan":
        run_scan(args.file, args.dry_run)

    elif args.command == "dashboard":
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            threading.Timer(1.5, open_browser).start()
        app.run(debug=True)


if __name__ == "__main__":
    main()
