"""
Email Sender — auto-queue outreach emails for every close package.

Supports SendGrid (preferred) and SMTP fallback.
Alberto never writes emails. This module sends them.

Env vars (SendGrid — preferred):
  SENDGRID_API_KEY     — get at sendgrid.com, free tier = 100/day

Env vars (SMTP fallback):
  EMAIL_FROM           — sender address (e.g. alberto@yourdomain.com)
  EMAIL_PASSWORD       — SMTP password or app password
  EMAIL_SMTP_HOST      — e.g. smtp.gmail.com
  EMAIL_SMTP_PORT      — e.g. 587
"""

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


def has_email_configured() -> bool:
    return bool(os.getenv("SENDGRID_API_KEY") or (
        os.getenv("EMAIL_FROM") and os.getenv("EMAIL_PASSWORD") and os.getenv("EMAIL_SMTP_HOST")
    ))


def send_outreach_email(
    to_email:    str,
    subject:     str,
    body:        str,
    from_name:   str = "Alberto Soriano",
    reply_to:    str = "",
) -> bool:
    """
    Send outreach email via SendGrid (preferred) or SMTP.
    Returns True if sent, False if failed or not configured.
    """
    if not to_email or "@" not in to_email:
        print("  [email] Invalid or missing recipient address — skipping")
        return False

    sg_key = os.getenv("SENDGRID_API_KEY", "")
    if sg_key:
        return _send_via_sendgrid(to_email, subject, body, from_name, reply_to, sg_key)

    return _send_via_smtp(to_email, subject, body, from_name)


def _send_via_sendgrid(
    to_email: str,
    subject:  str,
    body:     str,
    from_name: str,
    reply_to: str,
    api_key:  str,
) -> bool:
    try:
        import urllib.request, urllib.error, json
        from_email = os.getenv("EMAIL_FROM", "")
        if not from_email:
            print("  [email] EMAIL_FROM not set — add it to .env for correct sender address")
            from_email = "noreply@wholesaleai.app"
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email, "name": from_name},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        }
        if reply_to:
            payload["reply_to"] = {"email": reply_to}

        req = urllib.request.Request(
            "https://api.sendgrid.com/v3/mail/send",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=15)
        if resp.status in (200, 202):
            print(f"  [email] ✓ Sent via SendGrid → {to_email}")
            return True
        print(f"  [email] SendGrid returned {resp.status}")
        return False
    except Exception as e:
        print(f"  [email] SendGrid error: {str(e)[:80]}")
        return False


def _send_via_smtp(
    to_email:  str,
    subject:   str,
    body:      str,
    from_name: str,
) -> bool:
    from_addr = os.getenv("EMAIL_FROM", "")
    password  = os.getenv("EMAIL_PASSWORD", "")
    host      = os.getenv("EMAIL_SMTP_HOST", "")
    port      = int(os.getenv("EMAIL_SMTP_PORT", "587"))

    if not (from_addr and password and host):
        print("  [email] SMTP not configured — skipping")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{from_name} <{from_addr}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(body, "plain"))

        ctx = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.login(from_addr, password)
            server.sendmail(from_addr, to_email, msg.as_string())

        print(f"  [email] ✓ Sent via SMTP → {to_email}")
        return True
    except Exception as e:
        print(f"  [email] SMTP error: {str(e)[:80]}")
        return False


def queue_deal_outreach(
    seller_email:   str,
    property_address: str,
    email_subject:  str,
    email_body:     str,
    investor_name:  str = "Alberto Soriano",
    investor_email: str = "",
) -> bool:
    """
    Send deal outreach email to a seller.
    Called automatically from the close package builder.
    """
    if not seller_email:
        print("  [email] No seller email available — skipping auto-send")
        return False

    sent = send_outreach_email(
        to_email   = seller_email,
        subject    = email_subject,
        body       = email_body,
        from_name  = investor_name,
        reply_to   = investor_email,
    )
    return sent


def email_status() -> dict:
    sg = bool(os.getenv("SENDGRID_API_KEY"))
    smtp = bool(os.getenv("EMAIL_FROM") and os.getenv("EMAIL_PASSWORD") and os.getenv("EMAIL_SMTP_HOST"))
    return {
        "configured": sg or smtp,
        "provider":   "SendGrid" if sg else ("SMTP" if smtp else "none"),
    }
