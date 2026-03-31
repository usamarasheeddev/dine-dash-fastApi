import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

async def sendEmail(options):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_name = os.getenv("FROM_NAME", "Mart POS")
    from_email = os.getenv("FROM_EMAIL", smtp_user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = options.get("subject")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = options.get("email")

    if options.get("message"):
        msg.attach(MIMEText(options.get("message"), "plain"))
    if options.get("html"):
        msg.attach(MIMEText(options.get("html"), "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_port == 587:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            print(f"Message sent to {options.get('email')}")
            return True
    except Exception as e:
        print(f"Error sending email: {e}")
        raise Exception("Email sending failed")
