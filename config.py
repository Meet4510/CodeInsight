#!/usr/bin/env python3
"""
Configuration file for CodeInsight
Change these settings before deploying to production
"""

import os

# Flask Configuration
DEBUG = True  # Set to False in production
TESTING = False

# Secret key for session management
SECRET_KEY = 'change-this-to-a-random-string-in-production'

# Upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'py'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Database Configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'root'  # MySQL password 
DB_NAME = 'code_reviewer'

# Code Analysis Settings
ANALYSIS_TIMEOUT = 10  # seconds
MAX_ISSUES_DISPLAY = 10

# Scoring Configuration
STYLE_WEIGHT = 40
COMPLEXITY_WEIGHT = 30
MAINTAINABILITY_WEIGHT = 30

# Complexity Thresholds
COMPLEXITY_THRESHOLDS = {
    2: 30,
    4: 25,
    7: 20,
    10: 10,
}

# Maintainability Thresholds
MAINTAINABILITY_THRESHOLDS = {
    85: 30,
    70: 25,
    50: 20,
    25: 10,
}

# PDF Settings
PDF_PAGE_SIZE = 'letter'
PDF_FONT_SIZE = 10

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'app.log'

# Session settings
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
SESSION_TYPE = 'filesystem'

print("Configuration loaded successfully!")
