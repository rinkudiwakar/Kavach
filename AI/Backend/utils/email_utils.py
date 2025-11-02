# backend/utils/email_utils.py
import smtplib
from email.mime.text import MIMEText
from configs.settings import settings

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
        s.starttls()
        s.login(settings.SMTP_USER, settings.SMTP_PASS)
        s.send_message(msg)

def notify_admin_subject_body(subject: str, body: str):
    send_email(settings.ADMIN_EMAIL, subject, body)

def notify_user_email(email: str, subject: str, body: str):
    send_email(email, subject, body)

# Higher-level helpers
def alert_intrusion(profile_name: str, details: str):
    subject = f"🚨 Intrusion Alert — {profile_name}"
    body = f"Intrusion detected for {profile_name}.\n\nDetails:\n{details}"
    notify_admin_subject_body(subject, body)

def alert_intent_mismatch(profile_name: str, details: str):
    subject = f"⚠️ Intent mismatch — {profile_name}"
    body = f"User voice matched but intent did not match expected command.\n\nDetails:\n{details}"
    notify_admin_subject_body(subject, body)

def alert_user_failed_attempt(user_email: str, message: str):
    subject = "Security Alert — Failed Unlock Attempt"
    notify_user_email(user_email, subject, message)
