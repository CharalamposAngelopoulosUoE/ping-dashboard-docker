import os
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Suppress GUI warnings
import matplotlib.pyplot as plt
from config import DB_PATH, STATIC_REPORT_DIR

def worst_performing_ips(return_df=False):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT name, ip, "
        "SUM(CASE WHEN status='Online' THEN 1 ELSE 0 END) as online_count, "
        "SUM(CASE WHEN status='Offline' THEN 1 ELSE 0 END) as offline_count, "
        "COUNT(*) as total "
        "FROM pings GROUP BY name, ip ORDER BY offline_count DESC LIMIT 20", conn)
    conn.close()
    df['uptime_pct'] = 100 * df['online_count'] / df['total']
    return df if return_df else df.to_dict(orient='records')

def generate_charts():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT date(timestamp) as day, status FROM pings", conn)
    conn.close()
    if df.empty:
        return

    # Daily counts chart
    daily_counts = df.groupby(['day', 'status']).size().unstack(fill_value=0)
    plt.figure(figsize=(6, 4))
    daily_counts.plot(kind='line', ax=plt.gca())
    plt.title("Daily Status Counts")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.savefig(os.path.join(STATIC_REPORT_DIR, "daily_counts.png"))
    plt.close()

    # Pie chart
    plt.figure(figsize=(4, 4))
    status_counts = df['status'].value_counts()
    plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%')
    plt.title("Status Distribution")
    plt.savefig(os.path.join(STATIC_REPORT_DIR, "status_pie.png"))
    plt.close()

    # Top offline chart
    top_offline = df[df['status']=='Offline']['day'].value_counts().head(10)
    plt.figure(figsize=(8, 4))
    top_offline.plot(kind='bar', ax=plt.gca())
    plt.title("Top Offline Days")
    plt.xlabel("Date")
    plt.ylabel("Offline Count")
    plt.savefig(os.path.join(STATIC_REPORT_DIR, "top_offline.png"))
    plt.close()

    # Save timestamp
    with open(os.path.join(STATIC_REPORT_DIR, "last_updated.txt"), "w") as f:
        import datetime
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
