import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_smtp_connection():
    """Test SMTP configuration and connection"""
    print("Testing SMTP Configuration...")
    
    # Check environment variables
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USER = os.getenv("EMAIL_USER", "")
    EMAIL_PASS = os.getenv("EMAIL_PASS", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@alphagroups.com")
    
    print(f"SMTP Host: {EMAIL_HOST}")
    print(f"SMTP Port: {EMAIL_PORT}")
    print(f"SMTP User: {EMAIL_USER}")
    print(f"Email From: {EMAIL_FROM}")
    
    # Check if credentials are provided
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ Error: EMAIL_USER or EMAIL_PASS not configured in environment")
        print("   Make sure you have set EMAIL_USER and EMAIL_PASS in your environment")
        return False
    
    import smtplib
    
    try:
        print(f"Attempting connection to {EMAIL_HOST}:{EMAIL_PORT}...")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()  # Enable encryption
        server.login(EMAIL_USER, EMAIL_PASS)
        print("[SUCCESS] SMTP connection successful!")
        server.quit()
        return True
    except Exception as e:
        print(f"[ERROR] SMTP connection failed: {str(e)}")
        return False

def test_email_sending():
    """Test sending an email using the configured service"""
    print("\nTesting Email Sending...")
    
    # Import and test the email service
    try:
        from utils.email_service import send_email
        
        test_email = os.getenv("TEST_EMAIL", "test@example.com")
        
        success = send_email(
            to_email=test_email,
            subject="SMTP Test from Alpha Groups",
            html="<h1>Test Email</h1><p>This is a test email sent via SMTP.</p>",
            plain_text="Test Email\n\nThis is a test email sent via SMTP."
        )
        
        if success:
            print("[SUCCESS] Email sent successfully!")
            return True
        else:
            print("[ERROR] Failed to send email")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error testing email sending: {str(e)}")
        return False

if __name__ == "__main__":
    print("SMTP Configuration Test for Alpha-Auth")
    print("=" * 40)
    
    smtp_success = test_smtp_connection()
    email_success = test_email_sending()
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"SMTP Connection: {'[PASSED]' if smtp_success else '[FAILED]'}")
    print(f"Email Sending: {'[PASSED]' if email_success else '[FAILED]'}")
    
    if smtp_success and email_success:
        print("\n[SUCCESS] All tests passed! SMTP is working correctly.")
    else:
        print("\n[WARNING] Some tests failed. Please check your SMTP configuration.")