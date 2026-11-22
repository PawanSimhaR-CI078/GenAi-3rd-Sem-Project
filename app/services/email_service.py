import smtplib
from email.message import EmailMessage
from flask import current_app


def send_contact_email(subject, message, sender_name=None):
    cfg = current_app.config
    if not cfg.get("MAIL_SERVER") or not cfg.get("ADMIN_EMAIL"):
        return False, "Mail not configured"
    msg = EmailMessage()
    msg["Subject"] = (subject or "Contact").replace("\n", " ").replace("\r", " ")
    msg["From"] = cfg.get("MAIL_DEFAULT_SENDER") or cfg.get("MAIL_USERNAME")
    msg["To"] = cfg["ADMIN_EMAIL"]
    body = f"From: {sender_name or 'user'}\n\n{message}"
    msg.set_content(body)
    try:
        with smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=15) as s:
            s.starttls()
            if cfg.get("MAIL_USERNAME"):
                s.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
            s.send_message(msg)
        return True, "Sent"
    except Exception as e:
        return False, str(e)