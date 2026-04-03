import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import asyncio

def _send_email_sync(smtp_host, smtp_port, smtp_user, smtp_pass, msg, email_to):
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_port == 587:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            print(f"Message sent to {email_to}")
            return True
    except Exception as e:
        print(f"Error sending email: {e}")
        raise Exception("Email sending failed")

async def sendEmail(options):
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASS
    from_name = settings.FROM_NAME
    from_email = settings.FROM_EMAIL or smtp_user

    msg = MIMEMultipart("alternative")
    msg["Subject"] = options.get("subject")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = options.get("email")

    if options.get("message"):
        msg.attach(MIMEText(options.get("message"), "plain"))
    if options.get("html"):
        msg.attach(MIMEText(options.get("html"), "html"))

    # smtplib is synchronous and blocks the asyncio event loop.
    # We must run it in a threadpool so it doesn't hang the FastAPI server.
    return await asyncio.to_thread(
        _send_email_sync, 
        smtp_host, 
        smtp_port, 
        smtp_user, 
        smtp_pass, 
        msg, 
        options.get("email")
    )
