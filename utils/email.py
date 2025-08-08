# # utils/sendgrid_email.py

# import os
# from dotenv import load_dotenv
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

# load_dotenv()

# SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
# EMAIL_FROM = os.getenv("EMAIL_FROM")

# def send_email(to_email: str, subject: str, content: str) -> bool:
#     try:
#         print("📤 Sending email via SendGrid...")
#         print("FROM:", EMAIL_FROM)
#         print("TO:", to_email)
#         print("SUBJECT:", subject)

#         message = Mail(
#             from_email=EMAIL_FROM,
#             to_emails=to_email,
#             subject=subject,
#             plain_text_content=content,
#         )

#         sg = SendGridAPIClient(SENDGRID_API_KEY)
#         response = sg.send(message)

#         print("✅ STATUS CODE:", response.status_code)
#         print("✅ RESPONSE BODY:", response.body.decode() if response.body else "No body")

#         return response.status_code < 400

#     except Exception as e:
#         print("❌ SendGrid Email Error:", e)
#         return False


# utils/sendgrid_email.py

import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def send_email(to_email: str, subject: str, html: str, plain_text: str = None) -> bool:
    try:
        print("📤 Sending email via SendGrid...")
        print("FROM:", EMAIL_FROM)
        print("TO:", to_email)
        print("SUBJECT:", subject)

        message = Mail(
            from_email=EMAIL_FROM,
            to_emails=to_email,
            subject=subject,
            plain_text_content=plain_text or "View this email in HTML format.",
            html_content=html
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        print("✅ STATUS CODE:", response.status_code)
        print("✅ RESPONSE BODY:", response.body.decode() if response.body else "No body")

        return response.status_code < 400

    except Exception as e:
        print("❌ SendGrid Email Error:", e)
        return False
