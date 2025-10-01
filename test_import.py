import os

# Don't call load_dotenv() here to avoid loading the .env file
# Just check what's in the os.environ at the start
print("System environment variables (before load_dotenv):")
print(f"SENDGRID_API_KEY in os.environ: {'SENDGRID_API_KEY' in os.environ}")
if 'SENDGRID_API_KEY' in os.environ:
    print(f"SENDGRID_API_KEY = {repr(os.environ['SENDGRID_API_KEY'])}")
else:
    print("SENDGRID_API_KEY is not in system environment variables")

print(f"EMAIL_FROM in os.environ: {'EMAIL_FROM' in os.environ}")
if 'EMAIL_FROM' in os.environ:
    print(f"EMAIL_FROM = {repr(os.environ['EMAIL_FROM'])}")
else:
    print("EMAIL_FROM is not in system environment variables")
    
# Now let's see what happens when we explicitly import and use sendgrid_email
print("\nNow importing sendgrid_email module...")
from utils.sendgrid_email import SENDGRID_API_KEY, EMAIL_FROM

print(f"After import - SENDGRID_API_KEY = {repr(SENDGRID_API_KEY)}")
print(f"After import - EMAIL_FROM = {repr(EMAIL_FROM)}")