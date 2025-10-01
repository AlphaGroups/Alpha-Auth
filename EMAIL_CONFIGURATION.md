# Email Configuration Guide for Alpha-Auth

## Overview

Alpha-Auth uses SendGrid API for email functionality. The application has separate configuration files for different environments:

- **Development Mode** (`.env.development`): Emails are logged instead of being sent (no API key required)
- **Production Mode** (`.env.production`): Emails are sent via SendGrid API (requires valid API key)

## Environment Files

### 1. Development Environment - `.env.development`

For development, the application uses `.env.development` which has:

- `SENDGRID_API_KEY` commented out (mock mode)
- `EMAIL_FROM` set to a development address
- Debug mode enabled

```
# SendGrid Email Configuration - Development
# SENDGRID_API_KEY=your_actual_sendgrid_api_key_here  # Uncomment for production only
EMAIL_FROM=dev-test@yourdomain.com
DEBUG=true
```

### 2. Production Environment - `.env.production`

For production, the application uses `.env.production` which has:

- `SENDGRID_API_KEY` set with your actual API key
- `EMAIL_FROM` set to your verified sender
- Debug mode disabled

```
# SendGrid Email Configuration - Production
SENDGRID_API_KEY=your_actual_sendgrid_api_key_here
EMAIL_FROM=noreply@yourdomain.com
DEBUG=false
```

## How to Configure Email Settings

### 1. Development Setup (No API Key Required)

For local development:

1. Copy the `.env.development` file to `.env`:
   ```bash
   cp .env.development .env
   ```

2. The `SENDGRID_API_KEY` is already commented out, so emails will be mocked and logged instead of sent

### 2. Production Setup (Requires SendGrid API Key)

To deploy in production:

1. **Obtain a SendGrid API Key**:
   - Sign up for a SendGrid account at https://sendgrid.com/
   - Navigate to Settings > API Keys in your SendGrid dashboard
   - Create a new API key with "Mail Send" permissions

2. **Set up your production environment**:
   - Copy the `.env.production` file to `.env`:
     ```bash
     cp .env.production .env
     ```
   - Set `SENDGRID_API_KEY` to your actual API key
   - Set `EMAIL_FROM` to a verified sender address in SendGrid

3. **Verify Your Sender Identity**:
   - In the SendGrid dashboard, verify the domain or email address you'll be sending from
   - This is required to prevent emails from going to spam

### 3. Testing Email Functionality

To test email functionality:

1. **Development Mode**:
   - Check that `SENDGRID_API_KEY` is commented out in your `.env` file
   - Check logs for "📧 MOCK EMAIL" messages when email operations occur

2. **Production Mode**:
   - Set a valid `SENDGRID_API_KEY` in your `.env` file
   - Set a verified `EMAIL_FROM` address
   - Check SendGrid dashboard for email delivery statistics

### 4. Forgot Password Email Example

The application sends password reset emails through the `/auth/forgot-password` endpoint. When this endpoint is called:

1. The system looks up the user by email
2. Generates a password reset token
3. Renders the `forgot_password_notification.html` template
4. Sends the email via SendGrid (production) or logs it (development)

## Troubleshooting

### Common Issues:

1. **Email not being sent in production**:
   - Verify that `SENDGRID_API_KEY` is set and valid in your `.env` file
   - Ensure `EMAIL_FROM` is a verified sender in SendGrid
   - Check SendGrid dashboard for errors

2. **Email being marked as spam**:
   - Verify your sending domain in SendGrid
   - Configure SPF and DKIM records
   - Ensure you're only sending to recipients who have opted in

3. **"Invalid or expired token" errors**:
   - Check that token generation and validation code is working properly
   - Verify token expiration settings in your environment

## Security Notes

- Never commit actual API keys to version control
- Use separate environment files for different environments
- Regularly rotate API keys for security
- Monitor your SendGrid dashboard for unusual email activity