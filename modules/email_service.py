"""
email_service.py
----------------
Outbound email via SMTP (TLS on port 587).

Reads credentials from environment variables loaded by modules/config.py:
    EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD

Public API
----------
    send_email(to, subject, body, html=False)  → bool
    send_lead_notification(lead_data)          → bool   (internal alert)
    send_lead_confirmation(lead_email, name)   → bool   (thank-you to lead)
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from modules.config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Core sender
# ─────────────────────────────────────────────────────────────────────────────

def send_email(to: str, subject: str, body: str, html: bool = False) -> bool:
    """
    Send a single email via SMTP with STARTTLS.

    Args:
        to:      Recipient email address.
        subject: Email subject line.
        body:    Plain-text or HTML body content.
        html:    If True the body is sent as text/html; otherwise text/plain.

    Returns:
        True on success, False if any error occurs (error is logged).
    """
    if not all([EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD]):
        logger.warning(
            "Email credentials not configured — skipping send to %s", to
        )
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_USER
        msg["To"] = to
        msg["Subject"] = subject

        mime_type = "html" if html else "plain"
        msg.attach(MIMEText(body, mime_type, "utf-8"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, to, msg.as_string())

        logger.info("Email sent to %s — subject: %s", to, subject)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check EMAIL_USER / EMAIL_PASSWORD.")
    except smtplib.SMTPException as exc:
        logger.error("SMTP error sending to %s: %s", to, exc)
    except OSError as exc:
        logger.error("Network error sending email: %s", exc)

    return False


# ─────────────────────────────────────────────────────────────────────────────
# Internal team notification
# ─────────────────────────────────────────────────────────────────────────────

def send_lead_notification(lead_data: dict) -> bool:
    """
    Send an HTML alert to the business mailbox when a new lead is captured.

    Args:
        lead_data: Dict with keys: name, email, phone, interest, message, score.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    name     = lead_data.get("name",     "N/A")
    email    = lead_data.get("email",    "N/A")
    phone    = lead_data.get("phone",    "N/A")
    interest = lead_data.get("interest", "N/A")
    message  = lead_data.get("message",  "—")
    score    = lead_data.get("score",    0)
    category = lead_data.get("category", "Unknown")

    subject = f"🔔 New Lead: {name} — {category} (Score: {score}/100)"

    body = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
      <h2 style="color:#4F46E5;">New Lead Captured</h2>
      <table style="border-collapse:collapse; width:100%; max-width:600px;">
        <tr><td style="padding:8px;background:#f3f4f6;font-weight:bold;">Name</td>
            <td style="padding:8px;">{name}</td></tr>
        <tr><td style="padding:8px;background:#f3f4f6;font-weight:bold;">Email</td>
            <td style="padding:8px;">{email}</td></tr>
        <tr><td style="padding:8px;background:#f3f4f6;font-weight:bold;">Phone</td>
            <td style="padding:8px;">{phone}</td></tr>
        <tr><td style="padding:8px;background:#f3f4f6;font-weight:bold;">Interested In</td>
            <td style="padding:8px;">{interest}</td></tr>
        <tr><td style="padding:8px;background:#f3f4f6;font-weight:bold;">Lead Score</td>
            <td style="padding:8px;"><strong>{score}/100</strong> — {category}</td></tr>
        <tr><td style="padding:8px;background:#f3f4f6;font-weight:bold;">Message</td>
            <td style="padding:8px;">{message}</td></tr>
      </table>
      <p style="color:#6b7280;font-size:12px;margin-top:16px;">
        Sent automatically by Codenixia AI Assistant
      </p>
    </body></html>
    """

    return send_email(to=EMAIL_USER, subject=subject, body=body, html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Lead confirmation / thank-you
# ─────────────────────────────────────────────────────────────────────────────

def send_lead_confirmation(lead_email: str, lead_name: str) -> bool:
    """
    Send a personalised thank-you email to the lead.

    Args:
        lead_email: The lead's email address.
        lead_name:  The lead's first (or full) name.

    Returns:
        True if sent successfully, False otherwise.
    """
    first_name = lead_name.split()[0] if lead_name else "there"
    subject = "Thanks for reaching out to Codenixia! 🚀"

    body = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333; max-width:600px;">
      <h2 style="color:#4F46E5;">Hey {first_name}, we got your message! 👋</h2>
      <p>
        Thank you for your interest in <strong>Codenixia</strong>.
        We've received your enquiry and a member of our team will be in touch
        within <strong>24–48 hours</strong>.
      </p>
      <p>In the meantime, feel free to explore our resources or connect with us:</p>
      <ul>
        <li>🌐 Website: <a href="https://codenixia.com">codenixia.com</a></li>
        <li>📧 Email: <a href="mailto:{EMAIL_USER}">{EMAIL_USER}</a></li>
      </ul>
      <p>Looking forward to working with you!</p>
      <p style="margin-top:24px;">
        Warm regards,<br/>
        <strong>The Codenixia Team</strong>
      </p>
      <p style="color:#9ca3af;font-size:11px;margin-top:32px;">
        You received this email because you submitted a form on Codenixia AI Assistant.
      </p>
    </body></html>
    """

    return send_email(to=lead_email, subject=subject, body=body, html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Daily lead summary report
# ─────────────────────────────────────────────────────────────────────────────

def send_daily_report(leads_df) -> bool:
    """
    Generate and send a summary email of leads captured today to the admin.

    Args:
        leads_df: Pandas DataFrame containing all current leads.

    Returns:
        True if sent successfully, False otherwise.
    """
    import datetime

    if leads_df.empty:
        subject = "📊 Codenixia Daily Lead Report — No leads today"
        body = """
        <html><body style="font-family: Arial, sans-serif; color: #333;">
          <h2 style="color:#4F46E5;">Daily Lead Summary</h2>
          <p>No new leads were captured today.</p>
        </body></html>
        """
        return send_email(to=EMAIL_USER, subject=subject, body=body, html=True)

    # Filter for today's leads (UTC date matching database timestamps)
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    today_leads = leads_df[leads_df["timestamp"].astype(str).str.startswith(today_str)]

    count_today = len(today_leads)
    count_total = len(leads_df)

    subject = f"📊 Codenixia Daily Lead Report: {count_today} New Leads Today"

    # Generate leads rows for HTML
    rows_html = ""
    leads_to_show = today_leads if not today_leads.empty else leads_df.head(10)
    for _, row in leads_to_show.iterrows():
        rows_html += f"""
        <tr>
            <td style="padding:8px; border: 1px solid #ddd;">{row.get('name', 'N/A')}</td>
            <td style="padding:8px; border: 1px solid #ddd;">{row.get('email', 'N/A')}</td>
            <td style="padding:8px; border: 1px solid #ddd;">{row.get('interest', 'N/A')}</td>
            <td style="padding:8px; border: 1px solid #ddd;">{row.get('score', 0)}</td>
            <td style="padding:8px; border: 1px solid #ddd;">{row.get('category', 'Unknown')}</td>
        </tr>
        """

    title_leads = "New Leads Today" if not today_leads.empty else "Recent Leads (Up to 10)"

    body = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
      <h2 style="color:#4F46E5;">Daily Lead Summary Report</h2>
      <p>Here is your daily summary of leads captured for Codenixia:</p>
      
      <table style="border-collapse:collapse; width:100%; max-width:600px; margin-bottom: 20px;">
        <tr style="background:#f3f4f6;">
            <th style="padding:8px; border: 1px solid #ddd; text-align:left; width:50%;">Metric</th>
            <th style="padding:8px; border: 1px solid #ddd; text-align:left; width:50%;">Value</th>
        </tr>
        <tr>
            <td style="padding:8px; border: 1px solid #ddd;">New Leads Today</td>
            <td style="padding:8px; border: 1px solid #ddd;"><strong>{count_today}</strong></td>
        </tr>
        <tr>
            <td style="padding:8px; border: 1px solid #ddd;">Total Cumulative Leads</td>
            <td style="padding:8px; border: 1px solid #ddd;"><strong>{count_total}</strong></td>
        </tr>
      </table>

      <h3 style="color:#4F46E5; margin-top:24px;">{title_leads}</h3>
      <table style="border-collapse:collapse; width:100%; max-width:800px; margin-top:8px;">
        <tr style="background:#f3f4f6;">
            <th style="padding:8px; border: 1px solid #ddd; text-align:left;">Name</th>
            <th style="padding:8px; border: 1px solid #ddd; text-align:left;">Email</th>
            <th style="padding:8px; border: 1px solid #ddd; text-align:left;">Interest</th>
            <th style="padding:8px; border: 1px solid #ddd; text-align:left;">Score</th>
            <th style="padding:8px; border: 1px solid #ddd; text-align:left;">Category</th>
        </tr>
        {rows_html}
      </table>

      <p style="color:#6b7280;font-size:12px;margin-top:32px;">
        Sent automatically by Codenixia AI Assistant Dashboard.
      </p>
    </body></html>
    """
    return send_email(to=EMAIL_USER, subject=subject, body=body, html=True)
