# # utils/sendgrid_email.py

# import os
# from dotenv import load_dotenv
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

# load_dotenv()

# SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
# SENDER_EMAIL = os.getenv("EMAIL_FROM")

# def send_email(to_email: str, subject: str, content: str) -> bool:
#     try:
#         message = Mail(
#             from_email=SENDER_EMAIL,
#             to_emails=to_email,
#             subject=subject,
#             plain_text_content=content
#         )
#         sg = SendGridAPIClient(SENDGRID_API_KEY)
#         response = sg.send(message)
#         print("✅ SendGrid response:", response.status_code)
#         return response.status_code < 400
#     except Exception as e:
#         print("❌ SendGrid error:", e)
#         return False


import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def send_email(to_email: str, subject: str, html: str, plain_text: str = None) -> bool:
    """
    Send email using SendGrid in production, with fallback to console in development
    """
    if not EMAIL_FROM:
        logger.error("EMAIL_FROM not configured")
        return False
    
    if not SENDGRID_API_KEY:
        # Development/Testing mode - log instead of sending
        logger.info(f"📧 MOCK EMAIL (no API key) - TO: {to_email}, SUBJECT: {subject}")
        logger.info(f"   HTML content preview: {html[:100]}...")
        return True  # Return success in development mode
    
    # Production mode - actually send email
    try:
        message = Mail(
            from_email=EMAIL_FROM,
            to_emails=to_email,
            subject=subject,
            plain_text_content=plain_text or "Please view this email in HTML format.",
            html_content=html
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code < 400:
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"❌ Failed to send email. Status: {response.status_code}")
            logger.error(f"Response: {response.body}")
            return False

    except Exception as e:
        logger.error(f"❌ SendGrid error: {str(e)}")
        return False
