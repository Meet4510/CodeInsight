# CodeInsight

A simple web application for analyzing Python code quality. This is an MCA minor project that demonstrates code analysis, scoring, and reporting.

## Features

✅ **User Authentication**
- User registration and login
- Password hashing with Werkzeug
- Session management

✅ **Python File Upload**
- Upload .py files only
- File validation
- Local storage

✅ **Code Analysis**
- Syntax check using AST
- Code style check using Pylint
- Complexity analysis using Radon
- Maintainability calculation

✅ **Quality Scoring**
- Style Score (0-60)
- Complexity Score (0-20)
- Maintainability Score (0-20)
- **Total Score: 0-100**

✅ **Results Dashboard**
- Overall score with progress bar
- Complexity metrics
- Maintainability index
- List of issues found
- Improvement suggestions
- Chart visualization with Chart.js

✅ **PDF Report Generation**
- Download code review reports
- Score summary
- Issues and suggestions

---

## Tech Stack

### Backend
- **Python 3.x**
- **Flask** - Web framework
- **MySQL** - Database
- **AST** - Syntax checking
- **Pylint** - Code style analysis
- **Radon** - Complexity metrics
- **ReportLab** - PDF generation

### Frontend
- **HTML5**
- **CSS3**
- **Bootstrap 5** - UI framework
- **JavaScript** - Interactivity
- **Chart.js** - Data visualization

---

## Project Structure

```
/project
├── app.py              # Main Flask application
├── models.py           # Database models and operations
├── requirements.txt    # Python dependencies
├── database.sql        # Database schema
├── /templates          # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   └── results.html
├── /static
│   ├── /css
│   │   └── style.css
│   └── /js
│       └── (JavaScript files)
└── /uploads           # Uploaded Python files
```

---

## Setup Instructions

### Prerequisites
- Python 3.x installed
- MySQL Server installed and running
- pip (Python package manager)

### Step 1: Clone/Download Project
```bash
cd e:\APP\Project
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Flask 2.3.0
- Flask-MySQLdb 1.0.1
- Werkzeug 2.3.0
- pylint 2.17.0
- radon 6.0.1
- reportlab 4.0.4

### Step 3: Create Database

**Option A: Using MySQL Command Line**

1. Open MySQL Command Line Client or MySQL Workbench
2. Run the following commands:

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS code_reviewer;
USE code_reviewer;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Uploaded Files Table
CREATE TABLE IF NOT EXISTS uploaded_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_upload_date (upload_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Analysis Results Table
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    score INT DEFAULT 0,
    complexity FLOAT DEFAULT 0,
    maintainability FLOAT DEFAULT 0,
    issues LONGTEXT,
    suggestions LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES uploaded_files(id) ON DELETE CASCADE,
    UNIQUE KEY unique_file_analysis (file_id),
    INDEX idx_score (score),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Option B: Using SQL Script**

```bash
mysql -u root -p code_reviewer < database.sql
```

### Step 4: Configure Database Connection

Edit `app.py` and update the database configuration:

```python
db = Database(
    host='localhost',      # MySQL host
    user='root',          # MySQL username
    password='',          # MySQL password (if any)
    db='code_reviewer'    # Database name
)
```

Also update the Flask secret key:

```python
app.secret_key = 'your-secret-key-change-this'
```

### Step 5: Run Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 6: Access Application

1. Open web browser
2. Go to `http://localhost:5000`
3. Register a new account
4. Login with your credentials
5. Upload and analyze Python files

---

## Usage Guide

### Register
1. Click "Register here" on login page
2. Enter name, email, and password
3. Click "Register" button
4. Redirected to login page

### Upload File
1. Go to Dashboard
2. Click "Upload File" button
3. Select a .py file or drag & drop
4. Click "Upload File" button
5. Automatic analysis starts

### View Results
- See overall score (0-100)
- Check complexity metrics
- Review issues found
- Read suggestions
- View chart visualization

### Download Report
- Click "Download PDF" button
- PDF file with all details
- Can be printed or shared

---

## Scoring System

### Style Score (0-60 points)
- Based on number of style issues found
- PEP 8 compliance

### Complexity Score (0-20 points)
```
≤ 2   : 20 points
≤ 4   : 15 points
≤ 8   : 10 points
> 10  : 0 points
```

### Maintainability Score (0-20 points)
```
≥ 85  : 20 points
≥ 70  : 15 points
≥ 50  : 10 points
< 25  : 0 points
```

### Total Score = 0-100

---

## Database Schema

### users table
```
- id (INT, Primary Key)
- name (VARCHAR)
- email (VARCHAR, Unique)
- password (VARCHAR, Hashed)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- plan (VARCHAR)
- bio (Text)
```

### uploaded_files table
```
- id (INT, Primary Key)
- user_id (INT, Foreign Key)
- filename (VARCHAR)
- upload_date (TIMESTAMP)
```

### analysis_results table
```
- id (INT, Primary Key)
- file_id (INT, Foreign Key)
- score (INT)
- complexity (FLOAT)
- maintainability (FLOAT)
- issues (LONGTEXT)
- suggestions (LONGTEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

---

## Important Notes

### Security Considerations
- Passwords are hashed using werkzeug's security functions
- Change the `app.secret_key` before deploying
- Use HTTPS in production
- Validate all user inputs
- Never expose MySQL credentials

### File Upload
- Only .py files are accepted
- Files are stored with timestamp prefix
- Maximum file size depends on Flask configuration
- Uploaded files are analyzed immediately

### Code Analysis
- Uses Python AST module for syntax checking
- Pylint for style analysis
- Radon for complexity metrics
- Analysis results are cached in database

### Limitations
- For demonstration/educational purpose
- Single-threaded analysis
- No advanced AI features
- Simple scoring algorithm
- Dashboard shows recent files only

---

## Troubleshooting

### MySQL Connection Error
```
Error: Access denied for user 'root'@'localhost'
```
Solution: Check MySQL credentials in `app.py`

### Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```
Solution: Run `pip install -r requirements.txt`

### Pylint/Radon Not Found
```
FileNotFoundError: [Errno 2] No such file or directory: 'pylint'
```
Solution: Ensure tools are installed via pip

### Upload Folder Error
```
FileNotFoundError: [Errno 2] No such file or directory: 'uploads'
```
Solution: Application creates folder automatically

---

## Sample Test Cases

### Test 1: Syntax Error
```python
def hello(
    print("Hello")  # Missing closing parenthesis
```

### Test 2: Style Issues
```python
x=1  # No spaces around operator
y = 2
z=x+y
```

### Test 3: High Complexity
```python
def calculate(a, b, c):
    if a > b:
        if a > c:
            return a
        else:
            return c
    else:
        if b > c:
            return b
        else:
            return c
```

### Test 4: Clean Code
```python
"""
A simple calculator module.
"""

def add(a, b):
    """Add two numbers."""
    return a + b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b
```

---

## Future Enhancements

- [ ] Support for multiple programming languages
- [ ] Real-time code analysis (WebSocket)
- [ ] Code metrics history/trends
- [ ] Team collaboration features
- [ ] Integration with GitHub/GitLab
- [ ] Custom scoring rules
- [ ] Email notifications
- [ ] API endpoints
- [ ] Admin panel
- [ ] Advanced visualizations

---

## Author

Created for MCA Minor Project  
February 2026

---

## License

This project is provided as-is for educational purposes.

---

## Support & Contact

For issues or questions:
1. Check the troubleshooting section
2. Review the setup instructions
3. Check Flask/MySQL documentation

---

## Important Files Checklist

- ✅ app.py (Main application)
- ✅ models.py (Database operations)
- ✅ requirements.txt (Dependencies)
- ✅ database.sql (Database schema)
- ✅ templates/login.html
- ✅ templates/register.html
- ✅ templates/dashboard.html
- ✅ templates/upload.html
- ✅ templates/results.html
- ✅ static/css/style.css
- ✅ uploads/ (auto-created)

All files are ready to use!
