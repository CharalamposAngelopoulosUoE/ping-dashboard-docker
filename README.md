# Ping Dashboard v2 (Docker)

A network monitoring dashboard that pings configured IPs, logs status, and provides a Flask dashboard for real-time and historical monitoring. Includes Docker support for easy deployment.

---

## Features
- Periodic IP pings (online/offline)
- SQLite database logging
- Daily scans and weekly summary reports
- Flask dashboard for monitoring
- Dockerized for portable deployment

---

## Run with Docker

### Build Image
```bash
docker build -t ping_dashboard_v2 .
