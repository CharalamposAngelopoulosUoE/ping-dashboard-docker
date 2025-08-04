# logger/send_daily_email.py

import os, sys, sqlite3, pandas as pd, datetime

# Ensure project root in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force daily environment
os.environ["ENV_FILE"] = ".env.daily"

from config import EMAIL_RECEIVER, DB_PATH
from mailer import send_html_email

# --- Fetch today's data ---
def fetch_today_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            """
            SELECT ip, name, status, MAX(timestamp) as last_seen
            FROM pings
            WHERE DATE(timestamp) = DATE('now', 'localtime')
            GROUP BY ip
            """, conn
        )
        conn.close()
        return df
    except Exception as e:
        print(f"[ERROR] Fetching daily data failed: {e}")
        return pd.DataFrame()

df = fetch_today_data()

# Count unique gateways
offline_df = df[df["status"] == "Offline"]
offline_count = len(offline_df)
online_count = len(df) - offline_count
scan_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Classification (same as weekly)
def classify(uptime):
    if uptime >= 85: return "Stable"
    elif uptime >= 75: return "Unstable"
    else: return "Critical"

# Add Status column (Flapping detection not needed for daily snapshot)
offline_df = offline_df.copy()
offline_df["Status"] = "Critical"  # Offline = Critical

# Build HTML table with color coding
def color_row(row):
    status = row["Status"]
    if status == "Stable":
        return 'style="background-color: #90EE90;"'   # Green
    elif status == "Unstable":
        return 'style="background-color: #FFA500;"'   # Orange
    elif status == "Critical":
        return 'style="background-color: #FF6347;"'   # Red
    elif status == "Flapping":
        return 'style="background-color: #87CEEB;"'   # Blue
    return ""

if not offline_df.empty:
    rows_html = ""
    for _, row in offline_df.iterrows():
        rows_html += f"<tr {color_row(row)}><td>{row['name']}</td><td>{row['ip']}</td><td>{row['Status']}</td></tr>"
    table_html = f"""
    <table border="1" cellpadding="4" cellspacing="0">
      <tr><th>Building</th><th>IP Address</th><th>Status</th></tr>
      {rows_html}
    </table>
    """
else:
    table_html = "<p>No offline gateways detected in this scan.</p>"

# Legend
legend_html = "<p><i>Legend: Green=Stable, Orange=Unstable, Red=Critical, Blue=Flapping</i></p>"

# Email body
html_body = f"""
<html><body>
<p>Dear all,</p>
<p>The scan at <b>{scan_time}</b> showed:</p>
<ul>
  <li><b>{offline_count} Offline</b> gateways</li>
  <li><b>{online_count} Online</b> gateways</li>
</ul>
<p>Offline gateways:</p>
{table_html}
{legend_html}
<p>Note: The live dashboard is for internal use and accessible only on the monitoring machine.</p>
<p>Best regards,<br>Dr. Charalampos Angelopoulos</p>
</body></html>
"""

# Send email
sent = send_html_email(
    to_list=EMAIL_RECEIVER,
    subject=f"Daily Scan Report – {scan_time}",
    html_body=html_body
)

if sent:
    print(f"[OK] Daily completion email sent to: {', '.join(EMAIL_RECEIVER)}")
else:
    print("[ERROR] Failed to send daily completion email.")
