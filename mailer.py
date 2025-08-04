# mailer.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from config import EMAIL_USER, EMAIL_PASS, SMTP_SERVER, SMTP_PORT

def send_html_email(to_list, subject, html_body, cc_list=None, attachments=None):
    """Send HTML email with optional CC and attachments."""
    if cc_list is None:
        cc_list = []
    if attachments is None:
        attachments = []

    if not EMAIL_USER or not EMAIL_PASS:
        print("[ERROR] Missing email credentials; cannot send email.")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    for path in attachments:
        if os.path.exists(path):
            with open(path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(path)}"')
                msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"[OK] Email sent to: {', '.join(to_list + cc_list)} | {subject}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False

