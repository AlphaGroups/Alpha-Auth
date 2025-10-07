import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.development")

# Check which email service to use
BREVO_API_KEY = os.getenv("BREVO_API_KEY")


def send_email(to_email: str, subject: str, html: str, plain_text: str = None) -> bool:
    """
    Unified email sending function that uses Brevo API if available, otherwise falls back to SMTP
    """
    print("Unified email sender activated...")
    
    # Import smtp_email module
    import importlib.util
    import os
    
    smtp_email_path = os.path.join(os.path.dirname(__file__), "smtp_email.py")
    smtp_spec = importlib.util.spec_from_file_location("smtp_email", smtp_email_path)
    smtp_module = importlib.util.module_from_spec(smtp_spec)
    smtp_spec.loader.exec_module(smtp_module)

    send_smtp_email = smtp_module.send_smtp_email
    is_smtp_configured = smtp_module.is_smtp_configured

    # Check if Brevo API is configured (uncommented in .env)
    if BREVO_API_KEY:
        # For API approach, we'll use a direct request since no dedicated module exists
        # If we had a brevo_email module, we would import it here
        # For now, we'll fallback to a direct implementation if API is configured
        print("API key detected, attempting Brevo API call...")
        
        import requests
        
        # Prepare email using Brevo API
        email_from = os.getenv("EMAIL_FROM", "noreply@alphagroups.com")
        email_from_name = os.getenv("EMAIL_FROM_NAME", "Alpha Groups Notifications")
        
        url = "https://api.brevo.com/v3/smtp/email"
        
        payload = {
            "sender": {
                "name": email_from_name,
                "email": email_from
            },
            "to": [
                {
                    "email": to_email
                }
            ],
            "subject": subject,
            "htmlContent": html,
            "textContent": plain_text or "View this email in HTML format."
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": BREVO_API_KEY
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            print("Brevo API STATUS CODE:", response.status_code)
            if response.text:
                print("Brevo API RESPONSE:", response.text)
            return response.status_code < 400
        except Exception as e:
            print("Brevo API Error:", e)
            return False
    elif is_smtp_configured():
        print("Using SMTP for email delivery...")
        return send_smtp_email(to_email, subject, html, plain_text)
    else:
        print("ERROR: No email service configured (neither Brevo API nor SMTP)")
        return False


if __name__ == "__main__":
    # Test the unified email function
    test_email = os.getenv("TEST_EMAIL", "test@example.com")
    success = send_email(
        to_email=test_email,
        subject="Unified Email Test",
        html="<h1>Hello Alpha Groups!</h1><p>This is a test email sent via the configured method.</p>",
        plain_text="Hello Alpha Groups!\n\nThis is a test email sent via the configured method."
    )
    print("Unified Result:", "Sent" if success else "Failed")