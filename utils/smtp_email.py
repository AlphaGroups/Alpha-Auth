import os
import smtplib
import socket
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
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@alphagroups.com")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Alpha Groups Notifications")


def send_email(to_email: str, subject: str, html: str, plain_text: str = None) -> bool:
    """
    Send email using SMTP configuration
    """
    # Retry mechanism - try up to 3 times
    for attempt in range(3):
        try:
            print(f"Sending email via SMTP... (attempt {attempt + 1})")
            print("FROM:", f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>")
            print("TO:", to_email)
            print("SUBJECT:", subject)

            # Check if required SMTP settings are configured
            if not EMAIL_USER or not EMAIL_PASS:
                print("ERROR: EMAIL_USER or EMAIL_PASS not configured in environment")
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
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30)  # Add timeout
            server.set_debuglevel(0)  # Set to 1 to see SMTP communication
            try:
                server.starttls()  # Enable encryption
                server.login(EMAIL_USER, EMAIL_PASS)
                server.send_message(msg)
            except smtplib.SMTPAuthenticationError:
                print("SMTP Error: Authentication failed. Check your EMAIL_USER and EMAIL_PASS")
                return False
            except smtplib.SMTPRecipientsRefused:
                print("SMTP Error: Recipients were refused by the server")
                return False
            except smtplib.SMTPServerDisconnected:
                print("SMTP Error: Server unexpectedly disconnected")
                if attempt < 2:  # If not the last attempt, continue to next iteration
                    print("Retrying...")
                    continue
                return False
            except socket.timeout:
                print(f"SMTP Error: Connection to {EMAIL_HOST}:{EMAIL_PORT} timed out")
                if attempt < 2:  # If not the last attempt, continue to next iteration
                    print("Retrying...")
                    continue
                return False
            except ConnectionRefusedError:
                print(f"SMTP Error: Connection was refused by {EMAIL_HOST}:{EMAIL_PORT}")
                if attempt < 2:  # If not the last attempt, continue to next iteration
                    print("Retrying...")
                    continue
                return False
            except Exception as e:
                print(f"SMTP Error during email sending: {str(e)}")
                if attempt < 2:  # If not the last attempt, continue to next iteration
                    print("Retrying...")
                    continue
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
            if attempt < 2:  # If not the last attempt, continue to next iteration
                print("Retrying...")
                continue
            return False
        
        # If email sent successfully, break from the loop
        break

    return False  # Return False if all attempts failed


def is_smtp_configured() -> bool:
    """
    Check if SMTP is properly configured
    """
    return bool(EMAIL_USER and EMAIL_PASS)


if __name__ == "__main__":
    # Test SMTP email functionality
    test_email = os.getenv("TEST_EMAIL", "test@example.com")
    success = send_email(
        to_email=test_email,
        subject="SMTP Test",
        html="<h1>Hello Alpha Groups!</h1><p>This is a test email sent via SMTP.</p>",
        plain_text="Hello Alpha Groups!\n\nThis is a test email sent via SMTP."
    )
    print("SMTP Result:", "Sent" if success else "Failed")