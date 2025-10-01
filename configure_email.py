#!/usr/bin/env python3
"""
Script to fix and configure email settings for Alpha-Auth application
Supports both development and production environment files
"""
import os
from pathlib import Path

def update_env_file(env_file="development"):
    """
    Updates the specified environment file with proper configuration
    """
    if env_file == "development":
        env_path = Path(".env.development")
    elif env_file == "production":
        env_path = Path(".env.production")
    else:
        env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"ERROR: {env_path} file not found!")
        return False
        
    # Read the current environment file
    with open(env_path, 'r') as f:
        content = f.read()
    
    if env_file == "development":
        # For development, ensure the API key is commented out
        if "SENDGRID_API_KEY=your_actual_sendgrid_api_key_here" in content:
            updated_content = content.replace(
                "SENDGRID_API_KEY=your_actual_sendgrid_api_key_here",
                "# SENDGRID_API_KEY=your_actual_sendgrid_api_key_here  # Uncomment and set this in production"
            )
        elif "SENDGRID_API_KEY=" in content and not content.split("SENDGRID_API_KEY=")[1].strip().startswith('#'):
            # If API key exists but isn't commented, comment it out
            updated_content = content.replace(
                "SENDGRID_API_KEY=",
                "# SENDGRID_API_KEY=  # Uncomment and set this in production"
            )
        else:
            updated_content = content  # No changes needed
        
        # Update email from for development
        if "EMAIL_FROM=noreply@yourdomain.com" in updated_content:
            updated_content = updated_content.replace(
                "EMAIL_FROM=noreply@yourdomain.com",
                "EMAIL_FROM=dev-test@yourdomain.com  # Set this to your verified sender in production"
            )
    else:  # production
        # For production, ensure the API key is ready to be set
        if "# SENDGRID_API_KEY=your_actual_sendgrid_api_key_here" in content:
            updated_content = content.replace(
                "# SENDGRID_API_KEY=your_actual_sendgrid_api_key_here  # Uncomment and set this in production",
                "SENDGRID_API_KEY=your_actual_sendgrid_api_key_here"
            )
        else:
            updated_content = content  # No changes needed
    
    # Write the updated content back to the file
    with open(env_path, 'w') as f:
        f.write(updated_content)
    
    if env_file == "development":
        print("SUCCESS: .env.development file updated for development mode")
        print("   - SendGrid API key commented out (mock mode)")
        print("   - Email from address set for development")
    else:
        print("SUCCESS: .env.production file updated for production mode")
        print("   - SendGrid API key ready for setting")
        print("   - Email from address configured for production")
    
    return True

def show_email_status():
    """
    Shows current email configuration status
    """
    from dotenv import load_dotenv
    import os
    
    # Try to load from .env first, then .env.development
    if Path('.env').exists():
        load_dotenv(dotenv_path='.env')
        source = ".env"
    elif Path('.env.development').exists():
        load_dotenv(dotenv_path='.env.development')
        source = ".env.development"
    else:
        load_dotenv()  # fallback
        source = "environment"
    
    print(f"\n=== Current Email Configuration (from {source}) ===")
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    email_from = os.getenv("EMAIL_FROM")
    
    print(f"SENDGRID_API_KEY: {'SET' if sendgrid_key and sendgrid_key != 'your_actual_sendgrid_api_key_here' else 'NOT SET (mock mode)'}")
    print(f"EMAIL_FROM: {email_from if email_from else 'NOT SET'}")
    
    if not sendgrid_key or sendgrid_key.startswith('#') or sendgrid_key == 'your_actual_sendgrid_api_key_here':
        print("\nIn development mode, emails will be logged instead of sent.")
    else:
        print("\nIn production mode, emails will be sent via SendGrid API.")

def copy_env_file(source, destination):
    """
    Copy environment file from source to destination
    """
    source_path = Path(source)
    dest_path = Path(destination)
    
    if not source_path.exists():
        print(f"ERROR: Source file {source_path} does not exist!")
        return False
    
    # Read source file
    with open(source_path, 'r') as f:
        content = f.read()
    
    # Write to destination
    with open(dest_path, 'w') as f:
        f.write(content)
    
    print(f"SUCCESS: Copied {source} to {destination}")
    return True

def main():
    print("Configuring email settings for Alpha-Auth...")
    print("=" * 60)
    print("Available options:")
    print("1. Setup development environment (.env.development -> .env)")
    print("2. Setup production environment (.env.production -> .env)")
    print("3. Update development environment file only")
    print("4. Update production environment file only")
    print("=" * 60)
    
    choice = input("Select option (1-4, default is 1): ").strip()
    
    if choice == "1" or choice == "":
        # Setup development environment
        if Path('.env.development').exists():
            copy_env_file('.env.development', '.env')
            print("\nDevelopment environment copied to .env")
        else:
            print("ERROR: .env.development file not found!")
            return
    elif choice == "2":
        # Setup production environment
        if Path('.env.production').exists():
            copy_env_file('.env.production', '.env')
            print("\nProduction environment copied to .env")
        else:
            print("ERROR: .env.production file not found!")
            return
    elif choice == "3":
        # Update development environment only
        update_env_file("development")
    elif choice == "4":
        # Update production environment only
        update_env_file("production")
    else:
        print("Invalid choice. Using default (option 1: Setup development environment)")
        if Path('.env.development').exists():
            copy_env_file('.env.development', '.env')
            print("\nDevelopment environment copied to .env")
    
    print("\nConfiguration updated successfully!")
    print("\nNote: In development mode, emails will be logged instead of actually sent.")
    print("To send real emails, use production settings with valid SENDGRID_API_KEY")
    
    # Show the current status
    show_email_status()
    
    print("\n" + "=" * 60)
    print("Configuration complete!")

if __name__ == "__main__":
    main()