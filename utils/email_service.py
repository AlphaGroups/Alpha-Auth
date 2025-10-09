# import os
# import smtplib
# import socket
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from dotenv import load_dotenv
# from typing import Optional

# # Load environment variables based on environment
# if os.getenv("APP_ENV") == "production":
#     # In production, environment variables are set by Render directly
#     # So we don't need to load from .env file
#     pass
# else:
#     # For development, load from .env.development
#     load_dotenv(".env.development")

# # SMTP Configuration from environment
# EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
# EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
# EMAIL_USER = os.getenv("EMAIL_USER", "")
# EMAIL_PASS = os.getenv("EMAIL_PASS", "")
# EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@alphagroups.com")
# EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Alpha Groups Notifications")


# def send_email(to_email: str, subject: str, html: str, plain_text: str = None) -> bool:
#     """
#     Send email using SMTP configuration
#     """
#     # Retry mechanism - try up to 3 times
#     for attempt in range(3):
#         try:
#             print(f"Sending email via SMTP... (attempt {attempt + 1})")
#             print("FROM:", f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>")
#             print("TO:", to_email)
#             print("SUBJECT:", subject)

#             # Check if required SMTP settings are configured
#             if not EMAIL_USER or not EMAIL_PASS:
#                 print("ERROR: EMAIL_USER or EMAIL_PASS not configured in environment")
#                 return False

#             # Create message
#             msg = MIMEMultipart('alternative')
#             msg['Subject'] = subject
#             msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
#             msg['To'] = to_email

#             # Create both plain text and HTML versions
#             if plain_text:
#                 text_part = MIMEText(plain_text, 'plain')
#                 msg.attach(text_part)
            
#             html_part = MIMEText(html, 'html')
#             msg.attach(html_part)

#             # Connect to server and send email
#             server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30)  # Add timeout
#             server.set_debuglevel(0)  # Set to 1 to see SMTP communication
#             try:
#                 server.starttls()  # Enable encryption
#                 server.login(EMAIL_USER, EMAIL_PASS)
#                 server.send_message(msg)
#             except smtplib.SMTPAuthenticationError:
#                 print("SMTP Error: Authentication failed. Check your EMAIL_USER and EMAIL_PASS")
#                 return False
#             except smtplib.SMTPRecipientsRefused:
#                 print("SMTP Error: Recipients were refused by the server")
#                 return False
#             except smtplib.SMTPServerDisconnected:
#                 print("SMTP Error: Server unexpectedly disconnected")
#                 if attempt < 2:  # If not the last attempt, continue to next iteration
#                     print("Retrying...")
#                     continue
#                 return False
#             except socket.timeout:
#                 print(f"SMTP Error: Connection to {EMAIL_HOST}:{EMAIL_PORT} timed out")
#                 if attempt < 2:  # If not the last attempt, continue to next iteration
#                     print("Retrying...")
#                     continue
#                 return False
#             except ConnectionRefusedError:
#                 print(f"SMTP Error: Connection was refused by {EMAIL_HOST}:{EMAIL_PORT}")
#                 if attempt < 2:  # If not the last attempt, continue to next iteration
#                     print("Retrying...")
#                     continue
#                 return False
#             except Exception as e:
#                 print(f"SMTP Error during email sending: {str(e)}")
#                 if attempt < 2:  # If not the last attempt, continue to next iteration
#                     print("Retrying...")
#                     continue
#                 return False
#             finally:
#                 try:
#                     server.quit()
#                 except:
#                     pass  # Ignore errors during quit

#             print("Email sent successfully via SMTP")
#             return True

#         except Exception as e:
#             print("SMTP Email Error:", str(e))
#             if attempt < 2:  # If not the last attempt, continue to next iteration
#                 print("Retrying...")
#                 continue
#             return False
        
#         # If email sent successfully, break from the loop
#         break

#     return False  # Return False if all attempts failed


# def is_smtp_configured() -> bool:
#     """
#     Check if SMTP is properly configured
#     """
#     return bool(EMAIL_USER and EMAIL_PASS)


# if __name__ == "__main__":
#     # Test SMTP email functionality
#     test_email = os.getenv("TEST_EMAIL", "test@example.com")
#     success = send_email(
#         to_email=test_email,
#         subject="SMTP Test",
#         html="<h1>Hello Alpha Groups!</h1><p>This is a test email sent via SMTP.</p>",
#         plain_text="Hello Alpha Groups!\n\nThis is a test email sent via SMTP."
#     )
#     print("SMTP Result:", "Sent" if success else "Failed")
# utils/email_service.py
import os
import time
import socket
import smtplib
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Optional: requests for Brevo API
try:
    import requests  # type: ignore
except ImportError:
    requests = None  # type: ignore

# load .env for local/dev
if os.getenv("APP_ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv(".env.development")

# Common config
FROM_EMAIL = os.getenv("EMAIL_FROM", "noreply@alphagroups.com")
FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Alpha Groups Notifications")
USE_SMTP = os.getenv("USE_SMTP", "false").lower() in ("1", "true", "yes")
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "10"))
SEND_RETRIES = int(os.getenv("EMAIL_RETRIES", "3"))
RETRY_BACKOFF = float(os.getenv("EMAIL_RETRY_BACKOFF", "2"))

# SMTP config (used only if USE_SMTP is true)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")

# Brevo (Sendinblue) API config
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_URL = "https://api.brevo.com/v3/smtp/email"

def _send_via_brevo(to_email: str, subject: str, html: Optional[str], text: Optional[str]) -> bool:
    if not BREVO_API_KEY:
        print("Brevo API key not configured; skipping Brevo send.")
        return False
    if requests is None:
        print("requests library not available. Add 'requests' to requirements.txt")
        return False

    payload = {
        "sender": {"email": FROM_EMAIL, "name": FROM_NAME},
        "to": [{"email": to_email}],
        "subject": subject,
    }
    if html:
        payload["htmlContent"] = html
    if text:
        payload["textContent"] = text

    headers = {
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    for attempt in range(1, SEND_RETRIES + 1):
        try:
            resp = requests.post(BREVO_URL, headers=headers, json=payload, timeout=EMAIL_TIMEOUT)
            if 200 <= resp.status_code < 300:
                print(f"Brevo: Email sent to {to_email}")
                return True
            else:
                print(f"Brevo API error (attempt {attempt}): {resp.status_code} {resp.text}")
        except requests.exceptions.RequestException as e:
            print(f"Brevo request exception (attempt {attempt}): {e}")

        # backoff
        time.sleep(RETRY_BACKOFF * attempt)

    print(f"Brevo: Failed to send to {to_email} after {SEND_RETRIES} attempts")
    return False

def _send_via_smtp(to_email: str, subject: str, html: Optional[str], text: Optional[str]) -> bool:
    if not (EMAIL_USER and EMAIL_PASS):
        print("SMTP credentials not configured; unable to send via SMTP.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    if text:
        msg.attach(MIMEText(text, "plain"))
    if html:
        msg.attach(MIMEText(html, "html"))

    for attempt in range(1, SEND_RETRIES + 1):
        try:
            print(f"SMTP: connecting to {EMAIL_HOST}:{EMAIL_PORT} (attempt {attempt})")
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=EMAIL_TIMEOUT) as server:
                server.ehlo()
                # Common pattern: use STARTTLS on port 587
                try:
                    server.starttls()
                    server.ehlo()
                except Exception:
                    # starttls may fail for some ports/hosts; continue to login attempt
                    pass
                server.login(EMAIL_USER, EMAIL_PASS)
                server.send_message(msg)
            print(f"SMTP: Email sent to {to_email}")
            return True
        except (smtplib.SMTPAuthenticationError) as e:
            print("SMTP auth error:", e)
            return False
        except (socket.timeout, smtplib.SMTPServerDisconnected, ConnectionRefusedError) as e:
            print(f"SMTP connection error (attempt {attempt}): {e}")
        except Exception as e:
            print(f"SMTP send error (attempt {attempt}): {e}")

        time.sleep(RETRY_BACKOFF * attempt)

    print(f"SMTP: Failed to send to {to_email} after {SEND_RETRIES} attempts")
    return False

def send_email(to_email: str, subject: str, html: str, plain_text: str = None) -> bool:
    """
    Main send function: try Brevo API first (preferred), then SMTP if USE_SMTP is true.
    Returns True on success, False on failure.
    """
    # 1) Try Brevo API (works on Render free)
    try:
        success = _send_via_brevo(to_email, subject, html, plain_text)
        if success:
            return True
    except Exception as e:
        print("Brevo send raised exception:", e)

    # 2) If Brevo failed, fallback to SMTP only if explicitly enabled
    if USE_SMTP:
        print("Falling back to SMTP because USE_SMTP is true.")
        try:
            return _send_via_smtp(to_email, subject, html, plain_text)
        except Exception as e:
            print("Fallback SMTP raised exception:", e)
            return False

    # 3) If we reach here, nothing succeeded
    print("Email not sent: Brevo failed and SMTP fallback disabled.")
    return False

def is_smtp_configured() -> bool:
    """
    Check if SMTP is properly configured
    """
    return bool(EMAIL_USER and EMAIL_PASS)


if __name__ == "__main__":
    # Test email functionality
    test_email = os.getenv("TEST_EMAIL", "test@example.com")
    success = send_email(
        to_email=test_email,
        subject="Email Test",
        html="<h1>Hello Alpha Groups!</h1><p>This is a test email.</p>",
        plain_text="Hello Alpha Groups!\n\nThis is a test email."
    )
    print("Email Result:", "Sent" if success else "Failed")