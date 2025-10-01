# Simple test to check environment variables
import os
from dotenv import load_dotenv

# Explicitly reload the .env file
load_dotenv(override=True)

print("Environment variables from .env file:")
print(f"SENDGRID_API_KEY = {repr(os.getenv('SENDGRID_API_KEY'))}")
print(f"EMAIL_FROM = {repr(os.getenv('EMAIL_FROM'))}")

print("\nAll environment variables containing 'SENDGRID':")
for key, value in os.environ.items():
    if 'SENDGRID' in key.upper():
        print(f"  {key} = {repr(value)}")
        
print("\nAll environment variables containing 'EMAIL':")
for key, value in os.environ.items():
    if 'EMAIL' in key.upper():
        print(f"  {key} = {repr(value)}")