# monitor/monitor.py
# -*- coding: utf-8 -*-
"""
Ping Monitoring CLI Tool
- Manual scan
- Launch Flask dashboard
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import threading
import webbrowser
import platform
from logger.log_runner_v2 import log_status as run_scan
from app.app import app

def open_browser(live=False):
    """Opens the selected dashboard in default browser."""
    print("[INFO] Opening dashboard in browser...")
    url = "http://127.0.0.1:5000/live" if live else "http://127.0.0.1:5000/reports"
    if platform.system() == "Windows":
        os.system(f"start {url}")
    else:
        webbrowser.open_new(url)

def main():
    parser = argparse.ArgumentParser(description="Ping Monitor CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-command: scan (manual DB log)
    scan_cmd = subparsers.add_parser("scan", help="Run a manual IP scan")
    scan_cmd.add_argument(
        "--file",
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "IP_List.xlsx"),
        help="Excel file with IPs"
    )
    scan_cmd.add_argument("--dry-run", action="store_true", help="Run without sending emails")

    # Sub-command: dashboard
    dash_cmd = subparsers.add_parser("dashboard", help="Launch dashboard")
    dash_cmd.add_argument("--live", action="store_true", help="Open real-time live dashboard")

    args = parser.parse_args()

    if args.command == "scan":
        run_scan()  # file param not needed, log_runner_v2 reads config
    elif args.command == "dashboard":
        # Open browser slightly after Flask starts
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            threading.Timer(1.5, lambda: open_browser(args.live)).start()
        app.run(debug=True, use_reloader=True)

if __name__ == "__main__":
    main()

