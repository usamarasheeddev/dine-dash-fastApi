import asyncio
from app.utils.email import sendEmail
from app.core.config import settings

async def test_email():
    print(f"Testing email with settings: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    print(f"User: {settings.SMTP_USER}")
    
    options = {
        "email": settings.SMTP_USER,
        "subject": "Test Email from FastAPI",
        "message": "This is a test email to verify SMTP settings.",
        "html": "<h1>Test Email</h1><p>This is a test email to verify SMTP settings.</p>"
    }
    
    try:
        await sendEmail(options)
        print("Success: Email sent successfully!")
    except Exception as e:
        print(f"Failure: {e}")

if __name__ == "__main__":
    asyncio.run(test_email())
