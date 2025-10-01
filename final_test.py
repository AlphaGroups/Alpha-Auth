#!/usr/bin/env python3
"""
Final test to check if the email functionality works in mock mode
"""
import os
import sys

# Remove the problematic environment variables from the current process
if 'SENDGRID_API_KEY' in os.environ:
    del os.environ['SENDGRID_API_KEY']

# Now check what we have
print("Environment after cleaning:")
print(f"SENDGRID_API_KEY in os.environ: {'SENDGRID_API_KEY' in os.environ}")
if 'SENDGRID_API_KEY' in os.environ:
    print(f"SENDGRID_API_KEY = {repr(os.environ['SENDGRID_API_KEY'])}")
else:
    print("SENDGRID_API_KEY has been removed from environment")

# Now import and test
from utils.sendgrid_email import send_email

print("\nTesting email in mock mode...")
result = send_email(
    to_email="test@example.com",
    subject="Test Subject",
    html="<p>Test email content</p>"
)

print(f"Email result: {result}")
if result:
    print("SUCCESS: Email functionality is working in mock mode!")
else:
    print("ERROR: Email functionality failed")