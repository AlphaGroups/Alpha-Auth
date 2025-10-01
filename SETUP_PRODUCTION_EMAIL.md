# Setting Up Production Email with SendGrid API

When you're ready to send actual emails in your Alpha-Auth application, follow these steps:

## Step 1: Sign Up for SendGrid
1. Go to https://sendgrid.com/
2. Click "Sign Up" and create an account
3. Complete email verification

## Step 2: Create an API Key
1. Log into your SendGrid dashboard
2. Navigate to Settings > API Keys
3. Click "Create API Key"
4. Give your API key a name (e.g., "Alpha-Auth Production")
5. Select "Restricted Access"
6. Under "Mail Send", select "Permissions: Full Access" 
7. Click "Create & View"
8. **Important**: Copy the API key immediately - you won't be able to see it again!

## Step 3: Verify Your Sender Identity
1. In your SendGrid dashboard, go to Settings > Sender Authentication
2. Choose "Single Sender Verification"
3. Click "Create New Sender"
4. Enter the email address you want to send from (e.g., noreply@yourdomain.com)
5. Follow the verification process

## Step 4: Configure Your Environment Files
For production deployment, you have two options:

### Option 1: Copy .env.production (Recommended for Production)
1. Copy the `.env.production` file to `.env`:
   ```bash
   cp .env.production .env
   ```
2. Open the new `.env` file and update these values:
   - Set `SENDGRID_API_KEY=your_copied_sendgrid_api_key_here`
   - Set `EMAIL_FROM=your_verified_sender@example.com`
   - Set `DATABASE_URL` with your production database credentials
   - Set `ADMIN_EMAIL`, `ADMIN_PASS` with secure production values
   - Ensure `DEBUG=false`

### Option 2: Manual .env Update
1. Open your `.env` file in the Alpha-Auth project root
2. Update the `SENDGRID_API_KEY`:
   ```bash
   SENDGRID_API_KEY=your_copied_sendgrid_api_key_here
   ```
3. Make sure your `EMAIL_FROM` matches your verified sender:
   ```bash
   EMAIL_FROM=your_verified_sender@example.com
   ```

## Step 5: Test Your Configuration
1. Restart your application to load the new environment variables
2. Trigger an email action (like password reset)
3. Monitor your SendGrid dashboard for successful delivery

## Important Security Notes
- Never commit your actual API key to version control
- Store API keys only in environment variables
- Regularly rotate your API keys (recommended every 6 months)
- Monitor your SendGrid usage and dashboard for any suspicious activity

## Troubleshooting Production Setup
- If emails aren't sending, check your SendGrid dashboard for errors
- Verify that your sending domain is authenticated in SendGrid
- Make sure you're not sending to spam trap addresses during testing
- Review SendGrid's documentation on avoiding spam filters

Your application is currently configured in development mode and will log emails instead of sending them. Follow these steps when you're ready to enable production email functionality.