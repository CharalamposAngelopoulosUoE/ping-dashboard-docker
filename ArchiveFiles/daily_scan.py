# daily_scan.py

import pandas as pd
import subprocess
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for Windows terminal compatibility
init()
load_dotenv()

# Routing Setup
GROUP_A_EMAIL = "c.angelopoulos@ed.ac.uk"
GROUP_B_EMAIL = "ceangelopoulos@gmail.com"
ALWAYS_RECEIVE = "ceangelopoulos@gmail.com"

# Define building sets
GROUP_A_BUILDINGS = {
    "Usher Grd Floor", "Usher 4th Floor Electrical", "Usher 4th Floor Mechanical",
    'Sub-Station  "A"   KB ( Energy Centre)', "Geology", "Ashworth", "John Murray",
    'Sub-Station "B" KB - Sanderson', "Solar Farm", "0668 - William Rankine",
    "2702 - QMRI - East (Non Ess)", 'Sub-Station "D" KB - JCMB',
    "2702 - QMRI - East (ESS)", "2702 - QMRI - Drum (Non ESS)",
    "2702 - QMRI - Drum (ESS)", "2702 - QMRI - West (Non ESS)",
    "2702 - QMRI - West (ESS)", "2702 - QMRI - Central (Non ESS)",
    "2702 - QMRI - Central (ESS)", "2702 - QMRI - Primary LV (West/Central) TX1",
    "2702 - QMRI - Primary LV (West/Central)", "2702 - QMRI - Primary LV (East/Drum)",
    "Joseph Black", "Ashworth 2", "Nucleus Building - 4th Floor Plantroom",
    "Sanderson", "Fleeming Jenkin", "Structures Lab", "John Muir", "Main Library PV"
}

# Environment fallbacks
DEFAULT_EXCEL = os.getenv("IP_LIST_FILE", "IP_List.xlsx")
DEFAULT_DISABLE_EMAIL = os.getenv("DISABLE_EMAIL", "False").lower() == "true"
DEFAULT_EMAIL_USER = os.getenv("EMAIL_USER")
DEFAULT_EMAIL_PASS = os.getenv("EMAIL_PASS")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
RETRY_COUNT = 4


def ping_host(ip):
    """Ping an IP once and return True if online."""
    try:
        result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False


def send_email_alert(offline_list, total_count, dry_run, now):
    """
    Send formatted email alerts to Group A and B based on offline IPs.
    Always CCs one address with the full list.
    """
    if not offline_list or dry_run:
        print("📭 Email sending skipped (dry run or no offline IPs).")
        return

    grouped = {GROUP_A_EMAIL: [], GROUP_B_EMAIL: []}
    full_copy = []

    for entry in offline_list:
        full_copy.append(entry)
        building = entry["name"].strip().lower()
        group_a_lower = [b.lower() for b in GROUP_A_BUILDINGS]
        if building in group_a_lower:
            grouped[GROUP_A_EMAIL].append(entry)
        else:
            grouped[GROUP_B_EMAIL].append(entry)

    def build_html(offline_data):
        html = f"""
        <html><body>
        <h3>Offline IPs Detected - {now}</h3>
        <p><i>(Dashboard is available only on Angelo's laptop for internal use)</i></p>
        <p><b>Total Devices Scanned:</b> {total_count}<br>
        <b>Total Offline:</b> {len(offline_data)}</p>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>Building Name</th><th>IP Address</th><th>Status</th><th>Last Checked</th></tr>
        """
        for entry in offline_data:
            html += f"<tr><td>{entry['name']}</td><td>{entry['ip']}</td><td style='color:red;'>Offline</td><td>{entry['timestamp']}</td></tr>"
        html += "</table></body></html>"
        return html

    # Send to each group
    for recipient, entries in grouped.items():
        if entries:
            msg = MIMEMultipart("alternative")
            msg["From"] = DEFAULT_EMAIL_USER
            msg["To"] = recipient
            msg["Cc"] = ALWAYS_RECEIVE
            msg["Subject"] = f"[ALERT] {len(entries)} Offline IPs - {now}"
            msg.attach(MIMEText(build_html(entries), "html"))

            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(DEFAULT_EMAIL_USER, DEFAULT_EMAIL_PASS)
                    server.sendmail(DEFAULT_EMAIL_USER, [recipient, ALWAYS_RECEIVE], msg.as_string())
                    print(f"✅ Email sent to {recipient} (+cc {ALWAYS_RECEIVE})")
            except Exception as e:
                print(f"❌ Failed to send email to {recipient}: {e}")

    # Always send full list to ALWAYS_RECEIVE
    if full_copy:
        msg = MIMEMultipart("alternative")
        msg["From"] = DEFAULT_EMAIL_USER
        msg["To"] = ALWAYS_RECEIVE
        msg["Subject"] = f"[TEST COPY] All Offline IPs - {now}"
        msg.attach(MIMEText(build_html(full_copy), "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(DEFAULT_EMAIL_USER, DEFAULT_EMAIL_PASS)
                server.sendmail(DEFAULT_EMAIL_USER, [ALWAYS_RECEIVE], msg.as_string())
                print(f"✅ Full copy sent to {ALWAYS_RECEIVE}")
        except Exception as e:
            print(f"❌ Failed to send full copy: {e}")


def run_scan(file_path=DEFAULT_EXCEL, dry_run=DEFAULT_DISABLE_EMAIL):
    """
    Runs the IP scan from an Excel file, shows terminal output with online/offline status,
    and optionally sends email alerts.
    """
    print(f"📡 Running scan using file: {file_path}")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ Failed to load Excel file '{file_path}': {e}")
        return

    offline_list = []
    scan_results = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_count = len(df)

    for _, row in df.iterrows():
        try:
            name = row["Name"]
            ip = row["IP Address"]

            is_online = ping_host(ip)
            for _ in range(RETRY_COUNT - 1):
                if is_online:
                    break
                is_online = ping_host(ip)

            if not is_online:
                print(f"{Fore.RED}🔴 {ip} is offline{Style.RESET_ALL}")
                offline_list.append({"name": name, "ip": ip, "timestamp": now})
                scan_results.append({"name": name, "ip": ip, "status": "Offline", "timestamp": now})
            else:
                print(f"{Fore.GREEN}🟢 {ip} is online{Style.RESET_ALL}")
                scan_results.append({"name": name, "ip": ip, "status": "Online", "timestamp": now})

        except Exception as e:
            print(f"⚠️ Error processing row: {e}")

    # Save results to file
    pd.DataFrame(scan_results).to_csv("latest_scan_results.csv", index=False)

    # Summary
    print("\n📊 Summary:")
    print(f"  Total scanned: {total_count}")
    print(f"  Offline: {len(offline_list)}")
    print(f"  Online: {total_count - len(offline_list)}")

    # Send alerts
    send_email_alert(offline_list, total_count, dry_run, now)


# CLI entry
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run a manual IP scan")
    parser.add_argument("--file", default=DEFAULT_EXCEL, help="Path to Excel file with IPs")
    parser.add_argument("--dry-run", action="store_true", help="Skip email sending")
    args = parser.parse_args()
    run_scan(args.file, args.dry_run)
