import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from typing import Optional

# Load environment variables based on environment
if os.getenv("APP_ENV") == "production":
    # In production, environment variables are set by Render directly
    # So we don't need to load from .env file
    pass
else:
    # For development, load from .env.development
    load_dotenv(".env.development")

# SMTP Configuration from environment
SMTP_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("EMAIL_PORT", "587"))
SMTP_USER = os.getenv("EMAIL_USER", "")
SMTP_PASSWORD = os.getenv("EMAIL_PASS", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@alphagroups.com")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Alpha Groups Notifications")


def send_smtp_email(to_email: str, subject: str, html: str, plain_text: str = None) -> bool:
    """
    Send email using SMTP configuration
    """
    try:
        print("Sending email via SMTP...")
        print("FROM:", f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>")
        print("TO:", to_email)
        print("SUBJECT:", subject)

        # Check if required SMTP settings are configured
        if not SMTP_USER or not SMTP_PASSWORD:
            print("ERROR: SMTP_USER or SMTP_PASSWORD not configured in environment")
            return False

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
        msg['To'] = to_email

        # Create both plain text and HTML versions
        if plain_text:
            text_part = MIMEText(plain_text, 'plain')
            msg.attach(text_part)
        
        html_part = MIMEText(html, 'html')
        msg.attach(html_part)

        # Connect to server and send email
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.set_debuglevel(0)  # Set to 1 to see SMTP communication
        try:
            server.starttls()  # Enable encryption
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        except smtplib.SMTPAuthenticationError:
            print("SMTP Error: Authentication failed. Check your EMAIL_USER and EMAIL_PASS")
            return False
        except smtplib.SMTPRecipientsRefused:
            print("SMTP Error: Recipients were refused by the server")
            return False
        except smtplib.SMTPServerDisconnected:
            print("SMTP Error: Server unexpectedly disconnected")
            return False
        except Exception as e:
            print(f"SMTP Error during email sending: {str(e)}")
            return False
        finally:
            try:
                server.quit()
            except:
                pass  # Ignore errors during quit

        print("Email sent successfully via SMTP")
        return True

    except Exception as e:
        print("SMTP Email Error:", str(e))
        return False


def is_smtp_configured() -> bool:
    """
    Check if SMTP is properly configured
    """
    return bool(SMTP_USER and SMTP_PASSWORD)


if __name__ == "__main__":
    # Test SMTP email functionality
    test_email = os.getenv("TEST_EMAIL", "test@example.com")
    success = send_smtp_email(
        to_email=test_email,
        subject="SMTP Test",
        html="<h1>Hello Alpha Groups!</h1><p>This is a test email sent via SMTP.</p>",
        plain_text="Hello Alpha Groups!\n\nThis is a test email sent via SMTP."
    )
    print("SMTP Result:", "Sent" if success else "Failed")