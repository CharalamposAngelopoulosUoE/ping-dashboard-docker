import sys, os, sqlite3, datetime, time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import logging

# --- Force weekly env ---
os.environ["ENV_FILE"] = ".env.weekly"
print("[INFO] Using environment file: .env.weekly")

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import EMAIL_RECEIVER, DB_PATH
from mailer import send_html_email

# ----- Logging Setup -----
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "weekly_report.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("===== Weekly IP Summary Report Started =====")

# ----- Date Range (Weekly) -----
today = datetime.date.today()
week_start = today - datetime.timedelta(days=7)
week_end = today

start_str = week_start.strftime("%Y-%m-%d")
end_str = week_end.strftime("%Y-%m-%d")

# ----- Safe Query with Retry -----
def safe_query(query):
    retries = 5
    while retries > 0:
        try:
            with sqlite3.connect(DB_PATH, timeout=30) as conn:
                return pd.read_sql_query(query, conn, parse_dates=["timestamp"])
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("[WARN] Database is locked, retrying...")
                time.sleep(2)
                retries -= 1
            else:
                raise
    raise RuntimeError("Failed to read from DB after multiple retries")

# ----- Fetch Weekly Data -----
def fetch_week_data():
    try:
        query = f"""
        SELECT timestamp, name, ip, status
        FROM pings
        WHERE date(timestamp) BETWEEN '{start_str}' AND '{end_str}'
        """
        df = safe_query(query)
        return df
    except Exception as e:
        logging.error(f"Fetching weekly data failed: {e}")
        return pd.DataFrame()

df = fetch_week_data()
if df.empty:
    logging.warning(f"No data found for week {start_str} to {end_str}")
    print(f"No data found for week {start_str} to {end_str}")
    sys.exit(1)
else:
    logging.info(f"Fetched {len(df)} records from {start_str} to {end_str}")

# --- Deduplicate: same IP + timestamp + status = keep one
before_dedup = len(df)
df = df.drop_duplicates(subset=["timestamp", "ip", "status"], keep="first")
removed = before_dedup - len(df)
logging.info(f"Deduplication removed {removed} duplicate rows (kept {len(df)} records).")

# Prepare summary
df["date"] = df["timestamp"].dt.date
summary = df.groupby(["name", "ip", "status"]).size().unstack(fill_value=0).reset_index()

# Ensure Online/Offline columns exist
if "Online" not in summary.columns:
    summary["Online"] = 0
if "Offline" not in summary.columns:
    summary["Offline"] = 0

summary["total"] = summary["Online"] + summary["Offline"]
summary["uptime [%]"] = (100 * summary["Online"] / summary["total"]).round(1)

# --- Per-Day Flapping Detection ---
def detect_flapping_per_day(df):
    """Detect flapping per IP if any single day meets strict conditions."""
    df['date'] = df['timestamp'].dt.date
    daily_changes = df.groupby(['ip', 'date'])['status'].apply(lambda x: x.ne(x.shift()).sum())
    daily_counts = df.groupby(['ip', 'date'])['status'].size()
    daily_offlines = df.groupby(['ip', 'date'])['status'].apply(lambda x: (x == "Offline").sum())

    daily_flap_rate = daily_changes / daily_counts

    # New stricter logic: BOTH conditions + offline >= 2
    daily_flapping = ((daily_flap_rate >= 0.3) & (daily_changes >= 4) & (daily_offlines >= 2))

    # Skip if uptime >95% (mostly stable)
    flapping_ips = daily_flapping.groupby('ip').any()

    flapping_days = daily_flapping[daily_flapping].groupby('ip').apply(
        lambda x: list(x.index.get_level_values('date').unique())
    )

    return flapping_ips, flapping_days


flapping_ips, flapping_days = detect_flapping_per_day(df)

def classify(row):
    if flapping_ips.get(row["ip"], False):
        return "Flapping"
    uptime = row["uptime [%]"]
    if uptime >= 85:
        return "Stable"
    elif uptime >= 75:
        return "Unstable"
    else:
        return "Critical"

summary["Status"] = summary.apply(classify, axis=1)
summary["Status"] = summary["Status"].str.strip().str.title()

# ----- Top 10 Offline Devices -----
summary_sorted = summary.sort_values(by=["Offline", "uptime [%]"], ascending=[False, True]).head(10)

# ----- Chart: Online vs Offline -----
chart_path = os.path.join(LOG_DIR, f"summary_chart_{week_start}.png")
plt.figure(figsize=(5, 5))

total_ips = summary["ip"].nunique()
offline_count = (summary["Status"] == "Critical").sum()
online_count = total_ips - offline_count
sizes = [online_count, offline_count]

def autopct_percent(pct):
    return f"{pct:.1f}%"

wedges, texts, autotexts = plt.pie(
    sizes,
    autopct=autopct_percent,
    startangle=140
)

# Percent inside
for autotext in autotexts:
    autotext.set_color("white")
    autotext.set_fontsize(12)
    autotext.set_weight("bold")

# Absolute counts outside
for i, wedge in enumerate(wedges):
    angle = (wedge.theta2 + wedge.theta1) / 2
    x = 1.3 * np.cos(np.deg2rad(angle))
    y = 1.3 * np.sin(np.deg2rad(angle))
    plt.text(x, y, f"{sizes[i]}", ha='center', va='center', fontsize=10, fontweight='bold')

plt.title("Overall Online vs Offline")
plt.savefig(chart_path, bbox_inches="tight")
plt.close()

logging.info(f"Pie chart created: {online_count} online, {offline_count} offline, total {total_ips}")

# ----- PDF Generation -----
pdf_name = f"IP_Dashboard_Weekly_Report_{week_start.strftime('%d_%m_%Y')}_to_{week_end.strftime('%d_%m_%Y')}.pdf"
pdf_path = os.path.join(LOG_DIR, pdf_name)

pdf = FPDF()
pdf.add_page()

pdf.set_font("Arial", "B", 12)
pdf.cell(200, 10, f"Weekly IP Monitoring Summary ({start_str} to {end_str})", ln=True, align="C")
pdf.ln(5)

pdf.multi_cell(0, 8,
    "Definitions:\n"
    "- Stable: >= 85% uptime\n"
    "- Unstable: 75% - 84.9% uptime\n"
    "- Critical: < 75% uptime\n"
    "- Flapping: >= 4 state changes OR >= 30% transitions in a single day"
)

pdf.ln(2)
pdf.image(chart_path, x=60, w=90)
pdf.ln(5)

# Headers configuration
headers = [
    "Building",
    "IP Address",
    "Online Count (%)",
    "Offline Count",
    "Total Count",
    "Status"
]
col_widths = [63, 25, 23, 20, 20, 25]

def draw_headers(pdf, headers, col_widths):
    pdf.set_font("Arial", "B", 7.5)
    for header, width in zip(headers, col_widths):
        pdf.cell(width, 8, header, border=1, align="C")
    pdf.ln(8)

def status_color(status):
    status = status.strip().title()
    if status == "Stable": return (144, 238, 144)
    if status == "Unstable": return (255, 165, 0)
    if status == "Critical": return (255, 99, 71)
    if status == "Flapping": return (135, 206, 235)
    return (255, 255, 255)

# Top 10 table
pdf.set_font("Arial", "B", 9)
pdf.cell(0, 8, "Top 10 Devices with Most Offline Activity", ln=True)
draw_headers(pdf, headers, col_widths)

pdf.set_font("Arial", "", 7)
for _, row in summary_sorted.iterrows():
    r, g, b = status_color(row["Status"])
    pdf.set_fill_color(r, g, b)
    pdf.cell(63, 8, str(row["name"]), border=1, fill=True)
    pdf.cell(25, 8, str(row["ip"]), border=1, fill=True)
    pdf.cell(23, 8, f"{row['Online']} ({row['uptime [%]']}%)", border=1, align="C", fill=True)
    pdf.cell(20, 8, str(row["Offline"]), border=1, align="C", fill=True)
    pdf.cell(20, 8, str(row["total"]), border=1, align="C", fill=True)
    pdf.cell(25, 8, str(row["Status"]), border=1, align="C", fill=True)
    pdf.ln(8)

    # Add flapping days if applicable
    if row["Status"] == "Flapping" and row["ip"] in flapping_days.index:
        days_str = ", ".join([d.strftime("%d-%m") for d in flapping_days[row["ip"]]])
        pdf.set_font("Arial", "I", 6)
        pdf.cell(0, 6, f"Flapping days: {days_str}", ln=True)
        pdf.set_font("Arial", "", 7)

# Full summary table
pdf.add_page()
pdf.set_font("Arial", "B", 9)
pdf.cell(0, 8, "Full Device Summary", ln=True)
draw_headers(pdf, headers, col_widths)

pdf.set_font("Arial", "", 7)
for _, row in summary.iterrows():
    r, g, b = status_color(row["Status"])
    pdf.set_fill_color(r, g, b)
    pdf.cell(63, 8, str(row["name"]), border=1, fill=True)
    pdf.cell(25, 8, str(row["ip"]), border=1, fill=True)
    pdf.cell(23, 8, f"{row['Online']} ({row['uptime [%]']}%)", border=1, align="C", fill=True)
    pdf.cell(20, 8, str(row["Offline"]), border=1, align="C", fill=True)
    pdf.cell(20, 8, str(row["total"]), border=1, align="C", fill=True)
    pdf.cell(25, 8, str(row["Status"]), border=1, align="C", fill=True)
    pdf.ln(8)

    # Add flapping days if applicable
    if row["Status"] == "Flapping" and row["ip"] in flapping_days.index:
        days_str = ", ".join([d.strftime("%d-%m") for d in flapping_days[row["ip"]]])
        pdf.set_font("Arial", "I", 6)
        pdf.cell(0, 6, f"Flapping days: {days_str}", ln=True)
        pdf.set_font("Arial", "", 7)

pdf.output(pdf_path)

# ----- HTML Email Body -----
def color_html(status):
    status = status.strip().title()
    if status == "Stable": return 'style="background-color:#90EE90;"'
    if status == "Unstable": return 'style="background-color:#FFA500;"'
    if status == "Critical": return 'style="background-color:#FF6347;"'
    if status == "Flapping": return 'style="background-color:#87CEEB;"'
    return ""

rows_html = ""
for _, row in summary_sorted.iterrows():
    rows_html += (
        f"<tr {color_html(row['Status'])}>"
        f"<td>{row['name']}</td>"
        f"<td>{row['ip']}</td>"
        f"<td>{row['Online']} ({row['uptime [%]']}%)</td>"
        f"<td>{row['Offline']}</td>"
        f"<td>{row['total']}</td>"
        f"<td>{row['Status']}</td></tr>"
    )

table_html = """
<table border="1" cellpadding="4" cellspacing="0">
<tr>
  <th>Building</th>
  <th>IP Address</th>
  <th>Online Count (%)</th>
  <th>Offline Count</th>
  <th>Total Count</th>
  <th>Status</th>
</tr>
""" + rows_html + """
</table>
<p><i>Legend: Green=Stable, Orange=Unstable, Red=Critical, Blue=Flapping</i></p>
<p><i>Flapping: ≥ 4 state changes OR ≥ 30% transitions in a single day (with ≥ 1 offline event)</i></p>
"""

html_body = f"""
<html><body>
<p>Dear all,</p>
<p>Please find attached the weekly IP monitoring summary report for the period: {start_str} to {end_str}.</p>
<p>The report includes:</p>
<ul>
  <li>Uptime and reliability classification</li>
  <li>Flapping (frequent online/offline) behavior with daily detail</li>
  <li>All offline events and critical status notes</li>
</ul>
<p>Top 10 devices with most offline activity:</p>
{table_html}
<p>Note: The live dashboard is for internal use and accessible only on the monitoring machine.</p>
<p>Best regards,<br>Dr. Charalampos Angelopoulos</p>
</body></html>
"""

# ----- Send Email -----
sent = send_html_email(
    to_list=EMAIL_RECEIVER,
    subject=f"Weekly IP Summary ({start_str} - {end_str})",
    html_body=html_body,
    attachments=[pdf_path]
)

if sent:
    logging.info(f"Weekly summary emailed successfully: {pdf_path}")
    print(f"[OK] Weekly summary emailed successfully: {pdf_path}")
    sys.exit(0)
else:
    logging.error("Failed to send weekly email")
    print("[ERROR] Failed to send weekly email")
    sys.exit(1)
