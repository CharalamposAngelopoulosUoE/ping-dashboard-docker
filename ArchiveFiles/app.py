# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 13:56:18 2025

@author: cangelop
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

EXCEL_FILE = os.getenv("IP_LIST_FILE", "IP_List.xlsx")
RETRY_COUNT = 4
SEND_EMAIL = os.getenv("DISABLE_EMAIL", "False").lower() != "true"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_RECEIVER").split(",")

def ping_host(ip):
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=si
        )
        return result.returncode == 0
    except Exception:
        return False

def send_email_alert(offline_list):
    if not offline_list or not SEND_EMAIL:
        return

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[ALERT] Offline IPs Detected - {now}"

    html = """
    <html><body>
    <h3>The following IPs are offline:</h3>
    <p><a href='http://localhost:5000'>🔗 View Live Dashboard</a></p>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr><th>Building Name</th><th>IP Address</th><th>Status</th><th>Last Checked</th></tr>
    """
    for entry in offline_list:
        html += f"""
        <tr>
            <td>{entry['name']}</td>
            <td>{entry['ip']}</td>
            <td style='color:red;'>Offline</td>
            <td>{entry['timestamp']}</td>
        </tr>
        """
    html += "</table></body></html>"

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
            print("✅ Email alert sent.")
    except Exception as e:
        print("❌ Failed to send email:", e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_ips", methods=["GET"])
def get_ips():
    df = pd.read_excel(EXCEL_FILE)
    return jsonify(df.to_dict(orient="records"))

@app.route("/ping_one", methods=["POST"])
def ping_one():
    data = request.get_json()
    ip = data.get("ip")
    name = data.get("name")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Online"
    try:
        if not ping_host(ip):
            for _ in range(RETRY_COUNT):
                if ping_host(ip):
                    break
            else:
                status = "Offline"
    except Exception as e:
        print(f"❌ Error pinging {ip}: {e}")
        status = "Offline"

    return jsonify({
        "name": name,
        "ip": ip,
        "status": status,
        "timestamp": now
    })

@app.route("/send_email", methods=["POST"])
def trigger_email():
    offline_list = request.get_json()
    send_email_alert(offline_list)
    return jsonify({"status": "Email processed"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


