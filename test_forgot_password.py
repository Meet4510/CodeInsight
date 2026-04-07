#!/usr/bin/env python
"""Test forgot password email sending exactly like the app does"""

from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Exact same configuration as app.py
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@codeinsight.com')
app.config['MAIL_ASCII_ATTACHMENTS'] = True
app.config['MAIL_SUPPRESS_SEND'] = False

print("=" * 60)
print("Testing Forgot Password Email (Exact App Logic)")
print("=" * 60)
print(f"Server: {app.config['MAIL_SERVER']}")
print(f"Port: {app.config['MAIL_PORT']}")
print(f"TLS: {app.config['MAIL_USE_TLS']}")
print(f"Username: {app.config['MAIL_USERNAME']}")
print(f"Password: {'*' * len(app.config['MAIL_PASSWORD'])} (hidden)")
print(f"Default Sender: {app.config['MAIL_DEFAULT_SENDER']}")
print("=" * 60)

# Check if credentials are configured
if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
    print("❌ Email credentials not configured - would fall back to testing mode")
else:
    print("✅ Email credentials configured")

    # Initialize mail exactly like app.py
    mail = Mail()
    mail.init_app(app)

    # Test sending email exactly like forgot_password route
    with app.app_context():
        try:
            print("\nAttempting to send forgot password email...")
            reset_url = "http://localhost:5000/reset_password/test-token-123"

            msg = Message(
                subject='Password Reset Request - CodeInsight',
                recipients=['lathidadiyameet@gmail.com'],
                html=f"""
                <h2>Password Reset Request</h2>
                <p>Hi Test User,</p>
                <p>We received a request to reset your password. Click the link below to proceed:</p>
                <p><a href="{reset_url}" style="background-color: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, ignore this email.</p>
                <p>Best regards,<br>CodeInsight Team</p>
                """
            )
            mail.send(msg)
            print("✅ SUCCESS: Forgot password email sent successfully!")
        except Exception as e:
            print(f"❌ FAILED: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print("\nFull Traceback:")
            import traceback
            traceback.print_exc()