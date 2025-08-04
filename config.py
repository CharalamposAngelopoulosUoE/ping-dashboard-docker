# config.py
import os
from dotenv import load_dotenv

# Detect if running inside Docker (Linux) or Windows
if os.name == "nt":
    # Windows: use your local path
    BASE_DIR = r"C:\Users\cangelop\Desktop\Python\Ping_Dashboard_v2"
else:
    # Docker/Linux: use /app (workdir in Dockerfile)
    BASE_DIR = "/app"

# Load environment file (default .env.daily if ENV_FILE not set)
ENV_FILE = os.getenv("ENV_FILE", ".env.daily")
ENV_PATH = os.path.join(BASE_DIR, "env", ENV_FILE)

if not load_dotenv(dotenv_path=ENV_PATH):
    raise RuntimeError(f"Failed to load environment variables from {ENV_PATH}")

# Database path
DB_PATH = os.path.join(BASE_DIR, "logger", "ping_dashboard.db")

# Static reports path
STATIC_REPORT_DIR = os.path.join(BASE_DIR, "app", "static", "reports")
os.makedirs(STATIC_REPORT_DIR, exist_ok=True)

# IP list file
ip_env = os.getenv("IP_LIST_FILE")
if ip_env:
    # If env var is relative, join with BASE_DIR
    IP_LIST_FILE = ip_env if os.path.isabs(ip_env) else os.path.join(BASE_DIR, ip_env)
else:
    IP_LIST_FILE = os.path.join(BASE_DIR, "data", "IP_List.xlsx")

# Email settings
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = [email.strip() for email in os.getenv("EMAIL_RECEIVER", "").split(",") if email.strip()]
DISABLE_EMAIL = os.getenv("DISABLE_EMAIL", "False").lower() == "true"

# SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

