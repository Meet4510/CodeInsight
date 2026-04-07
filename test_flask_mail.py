#!/usr/bin/env python
"""Diagnostic script to test Flask-Mail configuration"""

from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure exactly as in app.py
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@codeinsight.com')
app.config['MAIL_ASCII_ATTACHMENTS'] = True
app.config['MAIL_SUPPRESS_SEND'] = False

print("=" * 60)
print("Testing Flask-Mail Configuration")
print("=" * 60)
print(f"Server: {app.config['MAIL_SERVER']}")
print(f"Port: {app.config['MAIL_PORT']}")
print(f"TLS: {app.config['MAIL_USE_TLS']}")
print(f"Username: {app.config['MAIL_USERNAME']}")
print(f"Password: {'*' * len(app.config['MAIL_PASSWORD'])} (hidden)")
print(f"Default Sender: {app.config['MAIL_DEFAULT_SENDER']}")
print("=" * 60)

# Initialize mail
mail = Mail()
mail.init_app(app)

# Test sending email
with app.app_context():
    try:
        print("\nAttempting to send test email...")
        msg = Message(
            subject='Test Email from Flask-Mail',
            recipients=['meetlathidadiya786@gmail.com'],
            html='<h1>Test Email</h1><p>This is a test email from Flask-Mail.</p>'
        )
        mail.send(msg)
        print("✓ SUCCESS: Email sent successfully!")
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\nFull Traceback:")
        import traceback
        traceback.print_exc()
