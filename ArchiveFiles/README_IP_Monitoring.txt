# 🔍 IP Monitoring Dashboard

A Python-based monitoring tool to track the online/offline status of IP addresses across buildings. Includes automated daily scans, email alerts, logging, and weekly analytics in PDF format.

---

## 📦 Features

- ✅ Scheduled IP scans (ping) with retry logic
- 📧 Email alerts for offline devices — grouped by building
- 📊 Weekly analytics report with:
  - Uptime % per device
  - Flapping IP detection
  - Downtime distribution by hour/day
  - PDF summary with charts & tables
- 🧾 Historical logs stored in CSV format
- 🌐 Local Flask dashboard (for internal viewing)
- ⚙️ Uses `.env` for secure config

---

## 🗂️ Project Structure

Ping_Dashboard/
├── app.py                  # Flask dashboard
├── daily_scan.py           # Manual scan tool
├── .env                    # Credentials & config
├── IP_List.xlsx            # Main input (IP and building names)
│
├── logger/
│   ├── log_runner.py       # Scheduled scanner (for logging)
│   ├── weekly_report.py    # Weekly report & PDF generator
│   └── logs/               # All CSV logs + PDF reports
│
└── tests/                  # Unit tests (coming soon)

---

## 🚀 Setup Instructions

### 1. ✅ Install Dependencies

pip install pandas python-dotenv colorama fpdf matplotlib openpyxl

### 2. 📁 Configure `.env`

Create a `.env` file with:
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password
EMAIL_RECEIVER=receiver1@example.com,receiver2@example.com
DISABLE_EMAIL=False
IP_LIST_FILE=IP_List.xlsx

### 3. 📋 Excel Input Format (`IP_List.xlsx`)

| Name               | IP Address     |
|--------------------|----------------|
| Usher 4th Floor    | 192.168.1.10   |
| Building XYZ       | 10.0.0.5       |

---

## 🕒 Automating with Task Scheduler (Windows)

### **Daily Logging**
- Run `log_runner.py` 3x per day
- Logs to `/logger/logs/week_YYYY_WW.csv`

### **Weekly Report**
- Run `weekly_report.py` every Sunday
- Sends email + attaches PDF with summary & charts

### Scheduler Setup:
1. Use `python.exe` as the executable
2. Script path in "Add arguments"
3. Set "Start in" directory properly
4. Enable "Run whether user is logged in or not"

---

## 🧪 Testing (WIP)

Coming soon:
pytest tests/

Will include:
- Ping mocking
- Excel parsing
- Email formatting logic

---

## 📌 Notes

- Designed for **internal use only** — pinging requires local university network
- Web dashboard (`app.py`) is accessible via `http://localhost:5000`
- Not intended for external cloud deployment (due to IP restrictions)

---

## 💡 Future Ideas

- Export summary to Excel
- Live chart on dashboard
- Docker-based internal deployment
- Role-based web view (e.g., energy team vs IT)

---

## 🧑‍💻 Author

Dr Charalampos Angelopoulos  
