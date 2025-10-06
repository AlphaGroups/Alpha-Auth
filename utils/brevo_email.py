import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.development")

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "vishalreddy4500@gmail.com")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Alpha Groups Notifications")


def send_email(to_email: str, subject: str, html: str, plain_text: str = None) -> bool:
    """
    Send email using Brevo API
    """
    try:
        print("Sending email via Brevo...")
        print("FROM:", f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>")
        print("TO:", to_email)
        print("SUBJECT:", subject)

        # Check if API key is configured
        if not BREVO_API_KEY:
            print("ERROR: BREVO_API_KEY not configured in environment")
            return False

        # Brevo API endpoint for sending transactional emails
        url = "https://api.brevo.com/v3/smtp/email"

        # Prepare the payload
        payload = {
            "sender": {
                "name": EMAIL_FROM_NAME,
                "email": EMAIL_FROM
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

        # Set headers
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": BREVO_API_KEY
        }

        # Make the API request
        response = requests.post(url, json=payload, headers=headers)

        print("STATUS CODE:", response.status_code)
        if response.text:
            print("RESPONSE BODY:", response.text)
        else:
            print("RESPONSE BODY: No body")

        return response.status_code < 400

    except Exception as e:
        print("Brevo Email Error:", e)
        # Print detailed error if available
        if hasattr(e, "response") and e.response is not None:
            print("Error details:", e.response.text)
        return False


# Run a test if executed directly
if __name__ == "__main__":
    test_email = os.getenv("TEST_EMAIL", "yourpersonal@gmail.com")  # add TEST_EMAIL in .env if you want
    success = send_email(
        to_email=test_email,
        subject="Brevo Test",
        html="<h1>Hello Alpha Groups!</h1><p>This is a test email sent via Brevo.</p>"
    )
    print("Result:", "Sent" if success else "Failed")