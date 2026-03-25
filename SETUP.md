# CodeInsight - Installation Guide

## Quick Start (5 Minutes)

### For Windows Users

#### 1. Install Python
- Download from https://www.python.org/downloads/
- **Important:** Check "Add Python to PATH" during installation
- Verify: Open Command Prompt and run `python --version`

#### 2. Install MySQL
- Download from https://dev.mysql.com/downloads/mysql/
- Run installer and complete setup
- Remember root password
- Verify: Open Command Prompt and run `mysql --version`

#### 3. Setup Project
```bash
# Navigate to project folder
cd e:\APP\Project

# Install dependencies
pip install -r requirements.txt

# Create database (do this in MySQL Command Line)
mysql -u root -p < database.sql
```

#### 4. Configure & Run
```bash
# Edit app.py and update database credentials:
# - Change 'root' to your MySQL username
# - Add your MySQL password if exists

# Run Flask application
python app.py

# Open browser: http://localhost:5000
```

---

## For Mac/Linux Users

#### 1. Install Python & MySQL
```bash
# macOS (using Homebrew)
brew install python3 mysql

# Ubuntu/Debian
sudo apt-get install python3 python3-pip mysql-server
```

#### 2. Setup Project
```bash
# Navigate to project
cd ~/Projects/code_reviewer

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. Create Database
```bash
# Start MySQL
mysql -u root -p

# In MySQL console:
CREATE DATABASE code_reviewer;
USE code_reviewer;

# Copy and paste all SQL from database.sql file
# ... (paste SQL content)
```

#### 4. Run Application
```bash
python3 app.py
# Visit http://localhost:5000
```

---

## Database Setup (Detailed)

### Step 1: Start MySQL Server

**Windows:**
```
Services → MySQL Server → Start
```

**Mac:**
```bash
mysql.server start
```

**Linux:**
```bash
sudo service mysql start
```

### Step 2: Connect to MySQL
```bash
mysql -u root -p
# Enter password when prompted
```

### Step 3: Run Setup Script
```sql
-- Copy-paste from database.sql file
-- Or execute:
mysql -u root -p < database.sql
```

### Step 4: Verify Setup
```sql
USE code_reviewer;
SHOW TABLES;
-- Should show: users, uploaded_files, analysis_results
```

---

## Common Issues & Solutions

### Issue 1: MySQL Connection Failed
```
Error: Access denied for user 'root'@'localhost'
```

**Solution:**
1. Check MySQL is running
2. Verify username/password in app.py
3. Ensure 'code_reviewer' database exists

```bash
# List all databases
mysql -u root -p -e "SHOW DATABASES;"
```

### Issue 2: Pylint/Radon Not Working
```
FileNotFoundError: [Errno 2] No such file or directory: 'pylint'
```

**Solution:**
```bash
# Reinstall packages
pip uninstall pilint radon
pip install pylint radon
```

### Issue 3: Port 5000 Already in Use
```
Address already in use
```

**Solution:**
```bash
# Use different port
# In app.py, change:
app.run(debug=True, port=5001)
```

### Issue 4: Module Import Errors
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Ensure virtual environment is activated (if using one)
# Reinstall all requirements
pip install --upgrade -r requirements.txt
```

---

## Configuration File Example

Create `config.py`:

```python
import os

class Config:
    """Base configuration"""
    SECRET_KEY = 'your-secret-key-here'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
class DatabaseConfig:
    """Database configuration"""
    HOST = 'localhost'
    USER = 'root'
    PASSWORD = ''  # Add your password
    DATABASE = 'code_reviewer'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
```

Then update `app.py`:
```python
from config import DevelopmentConfig

app.config.from_object(DevelopmentConfig)
```

---

## Testing the Application

### Test 1: User Registration
1. Go to http://localhost:5000
2. Click "Register here"
3. Enter details:
   - Name: Test User
   - Email: test@example.com
   - Password: Test@123
4. Click "Register"
5. Login with credentials

### Test 2: File Upload & Analysis
1. Create a test Python file:

```python
def hello(name):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    hello("World")
```

2. Save as `test.py`
3. Go to Dashboard
4. Click "Upload File"
5. Select `test.py`
6. View analysis results

### Test 3: Error Handling
Try uploading:
- Non-Python file (should error)
- File with syntax errors (should be detected)
- Large file (should handle gracefully)

---

## Performance Tips

1. **Database Optimization:**
   - Indexes are created automatically
   - Backup database regularly

2. **File Handling:**
   - Clean uploads folder periodically
   - Set max file size limit

3. **Code Analysis:**
   - Add timeout for analysis
   - Cache results

---

## Deployment Checklist

Before deploying to production:

- [ ] Change Flask secret key
- [ ] Set DEBUG = False
- [ ] Secure database credentials
- [ ] Use HTTPS only
- [ ] Set up proper logging
- [ ] Configure CORS if needed
- [ ] Regular database backups
- [ ] Monitor uptime
- [ ] Update dependencies regularly
- [ ] Security headers configured

---

## Getting Help

**Resources:**
- Flask Documentation: https://flask.palletsprojects.com/
- MySQL Documentation: https://dev.mysql.com/doc/
- Pylint: https://pylint.org/
- Radon: https://radon.readthedocs.io/

**Online Communities:**
- Stack Overflow
- Python Discord
- Flask GitHub Issues

---

## Next Steps

After successful installation:

1. ✅ Register a test account
2. ✅ Upload a Python file
3. ✅ View analysis results
4. ✅ Download PDF report
5. ✅ Test with different code samples
6. ✅ Customize styling/features
7. ✅ Deploy to production

---

Good luck with your MCA project! 🚀
