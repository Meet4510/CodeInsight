# Forgot Password Feature Setup Guide

The CodeInsight application now includes a complete forgot password functionality. This guide will help you set it up.

## Features

✅ **Secure Password Reset Flow**
- Users can request a password reset via email
- Secure tokens with 1-hour expiration
- Email notification with reset link
- Password validation (minimum 8 characters)

## Prerequisites

1. Flask-Mail and python-dotenv packages (included in requirements.txt)
2. An email account (Gmail, Outlook, SendGrid, etc.)
3. MySQL database (reset token columns will be created automatically)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email Settings

#### Option A: Using Gmail (Recommended)

1. Go to your [Google Account Security Settings](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already enabled
3. Visit [App Passwords](https://myaccount.google.com/apppasswords)
4. Select "Mail" and "Windows Computer" (or your device)
5. Google will generate a 16-character password

#### Option B: Using Outlook/Office 365

Create an app-specific password in your Microsoft account security settings.

#### Option C: Using SendGrid (Free tier available)

1. Create a free account at [SendGrid](https://sendgrid.com)
2. Generate an API key
3. Use `apikey` as MAIL_USERNAME and your API key as MAIL_PASSWORD

### 3. Create .env File

Create a `.env` file in the project root directory (use `.env.example` as a template):

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your email credentials:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=noreply@codeinsight.com
```

### 4. Update Database (Automatic)

The database schema will be updated automatically when you run the app. The following columns will be added to the `users` table:
- `reset_token` - Stores the password reset token
- `reset_token_expires` - Stores the token expiration time

### 5. Run the Application

```bash
python app.py
```

## How Users Use the Feature

### 1. Visit Forgot Password Page
- Click "Forgot?" link on the login page
- Or visit `/forgot_password`

### 2. Enter Email Address
- User enters their email address
- A security message appears: "If an account exists with that email, a reset link will be sent"
- (This message appears regardless of whether the email exists - security best practice)

### 3. Check Email
- User receives an email with a password reset link
- Link is valid for **1 hour**
- Link follows this format: `/reset_password/<secure-token>`

### 4. Reset Password
- User clicks the link in the email
- User enters a new password (minimum 8 characters)
- User confirms the password
- Password is updated and token is cleared from database

### 5. Login with New Password
- User can now login with their new password

## Email Template

The password reset email includes:
- User's name
- A prominent reset button
- Expiration time (1 hour)
- Security note: "Ignore this email if you didn't request it"

## Troubleshooting

### Email Not Sending

**Problem**: Emails are not being sent
**Solution**: 
1. Check that MAIL_USERNAME and MAIL_PASSWORD are correct in `.env`
2. For Gmail, ensure you're using an [App Password](https://myaccount.google.com/apppasswords), not your regular password
3. Check that MAIL_SERVER and MAIL_PORT are correct for your email provider
4. Check application logs for error messages

### Token Expired

**Problem**: User gets "Invalid or expired reset link"
**Solution**: Token is valid for 1 hour by default. User must request a new reset link.

### Database Columns Not Created

**Problem**: Getting database errors related to reset_token columns
**Solution**: Run this Python script:
```python
from models import Database
db = Database('localhost', 'root', 'root', 'code_reviewer')
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute('ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) DEFAULT NULL;')
cursor.execute('ALTER TABLE users ADD COLUMN reset_token_expires DATETIME DEFAULT NULL;')
cursor.execute('CREATE INDEX idx_reset_token ON users(reset_token);')

conn.commit()
cursor.close()
conn.close()
```

## Security Features

✅ **Token Security**
- Uses Python's `secrets` module for cryptographically secure tokens
- URL-safe tokens with 32 bytes of entropy
- Tokens stored hashed in database (not plain text)
- Tokens expire after 1 hour

✅ **Password Security**
- Passwords are never sent via email
- Only reset link is sent
- Passwords are hashed with Werkzeug's security functions
- Minimum 8-character requirement enforced

✅ **User Privacy**
- Email validation doesn't reveal if an email exists (prevents user enumeration)
- Only account owner can reset their password

## API Routes

### POST /forgot_password
Request body (form data):
```
email=user@example.com
```

Response: Forgot password form with success/error message

### GET /reset_password/<token>
Display password reset form

### POST /reset_password/<token>
Request body (form data):
```
password=new_password
confirm_password=new_password
```

Response: Success message with redirect to login

## Database Schema

The `users` table includes:
```sql
ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) DEFAULT NULL;
ALTER TABLE users ADD COLUMN reset_token_expires DATETIME DEFAULT NULL;
CREATE INDEX idx_reset_token ON users(reset_token);
```

## Testing

To test the feature locally without sending real emails, you can:

1. Set Flask to debug mode in `config.py`
2. Check printed output in console for debug messages
3. Or use a test email service like [Mailtrap](https://mailtrap.io)

## Production Deployment

When deploying to production:

1. ✅ Use environment variables for all credentials
2. ✅ Set `DEBUG = False` in `config.py`
3. ✅ Use TLS/SSL for email transmission
4. ✅ Ensure `.env` file is in `.gitignore` and never committed to version control
5. ✅ Use a reputable email service (SendGrid, AWS SES, etc.)
6. ✅ Monitor email delivery rates and bounces

## Future Enhancements

Potential improvements to the forgot password feature:
- SMS-based password reset
- Two-factor authentication
- Account recovery via security questions
- Password reset history/audit logging
- Custom email templates
- Configurable token expiration time

## Support

For issues or questions, please refer to the main README.md or create an issue in the repository.
