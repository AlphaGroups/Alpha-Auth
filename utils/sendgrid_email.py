# utils/sendgrid_email.py

import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("EMAIL_FROM")

def send_email(to_email: str, subject: str, content: str) -> bool:
    try:
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print("✅ SendGrid response:", response.status_code)
        return response.status_code < 400
    except Exception as e:
        print("❌ SendGrid error:", e)
        return False
