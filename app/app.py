# app/app.py
# -*- coding: utf-8 -*-
"""
Ping Monitoring CLI Tool
- Manual scan
- Launch Flask dashboard
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, send_from_directory, url_for, request, jsonify
from logger.db_tools import worst_performing_ips, generate_charts
from config import STATIC_REPORT_DIR, IP_LIST_FILE
from utils import ping_host
import pandas as pd
import datetime

# Initialize Flask
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)

# ---------------------- SUMMARY DASHBOARD (Existing) ----------------------
@app.route("/reports")
def reports():
    generate_charts()
    worst_df = worst_performing_ips(return_df=True)
    worst_ips_table = worst_df.to_html(classes="table table-striped", index=False)

    # Read last updated timestamp
    timestamp_path = os.path.join(STATIC_REPORT_DIR, "last_updated.txt")
    last_updated = "Unknown"
    if os.path.exists(timestamp_path):
        with open(timestamp_path) as f:
            last_updated = f.read()

    return render_template(
        "reports.html",
        worst_ips_table=worst_ips_table,
        chart_daily=url_for('static', filename='reports/daily_counts.png'),
        chart_pie=url_for('static', filename='reports/status_pie.png'),
        chart_top=url_for('static', filename='reports/top_offline.png'),
        last_updated=last_updated
    )



# ---------------------- API ENDPOINTS FOR LIVE DASHBOARD ----------------------
@app.route("/get_ips")
def get_ips():
    """Return IP list from Excel file configured in IP_LIST_FILE."""
    df = pd.read_excel(IP_LIST_FILE)
    ips = df.to_dict(orient="records")
    return jsonify(ips)

@app.route("/ping_one", methods=["POST"])
def ping_one():
    """Ping single IP and return status with retries."""
    from logger.log_runner_v2 import RETRY_COUNT  # use same retry count as log_runner

    data = request.json
    name = data.get("name")
    ip = data.get("ip")

    # First ping
    if ping_host(ip):
        status = "Online"
    else:
        # Retry up to RETRY_COUNT - 1
        for _ in range(RETRY_COUNT - 1):
            if ping_host(ip):
                status = "Online"
                break
        else:
            status = "Offline"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"name": name, "ip": ip, "status": status, "timestamp": timestamp})


@app.route("/send_email", methods=["POST"])
def send_email():
    """Stub for sending email alerts from live dashboard (implement if needed)."""
    # You can integrate with mailer.py if you want alerts sent when offline detected
    return jsonify({"message": "Email notification triggered"})

# ---------------------- STATIC FILE SERVING ----------------------
@app.route('/reports/<path:filename>')
def report_files(filename):
    return send_from_directory(STATIC_REPORT_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
