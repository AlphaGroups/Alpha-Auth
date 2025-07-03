# # utils/email.py
# from email.message import EmailMessage
# import aiosmtplib
# import os

# SMTP_HOST = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
# SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
# SMTP_USER = os.getenv("SMTP_USER")
# SMTP_PASS = os.getenv("SMTP_PASS")


# async def send_email(subject: str, recipient: str, body: str):
#     message = EmailMessage()
#     message["From"] = SMTP_USER
#     message["To"] = recipient
#     message["Subject"] = subject
#     message.set_content(body)

#     try:
#         await aiosmtplib.send(
#             message,
#             hostname=SMTP_HOST,
#             port=SMTP_PORT,
#             username=SMTP_USER,
#             password=SMTP_PASS,
#             start_tls=True
#         )
#         return True
#     except Exception as e:
#         print("Email send failed:", e)
#         return False




# utils/sendgrid_email.py

import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def send_email(to_email: str, subject: str, content: str) -> bool:
    try:
        print("📤 Sending email via SendGrid...")
        print("FROM:", EMAIL_FROM)
        print("TO:", to_email)
        print("SUBJECT:", subject)

        message = Mail(
            from_email=EMAIL_FROM,
            to_emails=to_email,
            subject=subject,
            plain_text_content=content,
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        print("✅ STATUS CODE:", response.status_code)
        print("✅ RESPONSE BODY:", response.body.decode() if response.body else "No body")

        return response.status_code < 400

    except Exception as e:
        print("❌ SendGrid Email Error:", e)
        return False
