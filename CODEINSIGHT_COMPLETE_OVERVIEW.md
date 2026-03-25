# CodeInsight - Complete Project Overview

## Project Summary

**CodeInsight** is a web-based Python code quality analyzer that evaluates code submissions and provides comprehensive feedback. It's built as an MCA Minor Project and demonstrates full-stack web development with automated code analysis integration.

**Key Stats:**
- Python 3.x backend (Flask)
- MySQL database integration
- Real-time code analysis with multiple tools
- Automated scoring system (0-100 scale)
- PDF report generation
- User authentication and session management

---

## Core Features

### 1. **User Authentication System**
- **Registration**: New users can create accounts with email validation
- **Login**: Secure login with password hashing using Werkzeug
- **Session Management**: Persistent user sessions with Flask
- **Password Security**: Passwords hashed with SHA-256
- **User Profile**: Each user has a dashboard showing their submissions

### 2. **File Upload & Validation**
- Accepts `.py` files only
- File validation before processing
- Timestamp-based file naming system (format: `YYYYMMDD_HHMMSS_filename.py`)
- Local storage in `/uploads` directory
- Database tracking of all uploads with user association

### 3. **Multi-Level Code Analysis**

#### A. Syntax Validation (AST Module)
- Uses Python's Abstract Syntax Tree (AST)
- Detects syntax errors before other analysis
- Provides line numbers and error descriptions
- Prevents processing of invalid Python files

#### B. Style Analysis (Pylint)
- PEP 8 compliance checking
- Detects style violations like:
  - Naming convention errors
  - Unused imports and variables
  - Undefined variables
  - Missing docstrings
  - Import organization
  - Line length violations
  - Bad indentation
- Configurable issue detection
- Returns up to 50 issues per analysis

#### C. Complexity Analysis (Radon)
- Calculates cyclomatic complexity
- Measures average complexity per function
- Identifies overly complex functions
- Complexity ratings:
  - A (1-5): Simple, easy to understand
  - B (6-10): Slightly complex
  - C (11-20): Complex
  - D (21-40): Very complex
  - E (>40): Extremely complex

#### D. Maintainability Index (Radon)
- Evaluates code readability
- Checks documentation levels
- Calculates overall maintainability score
- Range: 0-100
- Categories: A (high), B (medium), C (low)

### 4. **Automated Scoring System**

The scoring system is divided into three components:

```
Total Score = Style Score + Complexity Score + Maintainability Score
Total Range: 0-100

Style Score (0-40 points):
  - Starts at 40 points
  - -3 points for each style issue found
  - Minimum: 0 points

Complexity Score (0-30 points):
  - Complexity ≤ 2: 30 points (excellent)
  - Complexity 2-5: 25 points (good)
  - Complexity 5-10: 20 points (fair)
  - Complexity 10-20: 15 points (concerning)
  - Complexity > 20: 5 points (problematic)

Maintainability Score (0-30 points):
  - MI ≥ 85: 30 points (highly maintainable)
  - MI 75-85: 25 points (maintainable)
  - MI 65-75: 20 points (somewhat maintainable)
  - MI 55-65: 15 points (low maintainability)
  - MI < 55: 5 points (very poor maintainability)
```

### 5. **Results Dashboard**
- Real-time display of analysis results
- Visual score representation with progress bar
- Broken down scores (style, complexity, maintainability)
- Detailed issue listing with descriptions
- Improvement suggestions based on analysis
- Chart visualization using Chart.js
- Pie charts showing score distribution

### 6. **PDF Report Generation**
- Downloadable analysis reports
- Summary of scores and metrics
- Complete issue listing
- Improvement recommendations
- Professional formatting using ReportLab
- Generated on-demand for each submission

---

## Technical Architecture

### Backend Stack
```
Language: Python 3.x
Framework: Flask 3.0.0
Database: MySQL 5.7+
ORM/Database Driver: MySQLdb (Flask-MySQLdb 1.0.1)
Security: Werkzeug 3.0.0 (password hashing)
Code Analysis Tools:
  - pylint 3.0.0 (style checking)
  - radon 6.0.1 (complexity & maintainability)
Report Generation: reportlab 4.0.4
```

### Frontend Stack
```
Structure: HTML5
Styling: CSS3 + Bootstrap 5
UI Framework: Bootstrap 5 (responsive design)
Charts: Chart.js (data visualization)
Interactivity: Vanilla JavaScript
```

### Database System
- **Database**: MySQL (code_reviewer)
- **Tables**: 
  - `users` - User accounts and credentials
  - `submissions` - Uploaded files and analysis results
  - `analysis_results` - Detailed analysis data

---

## Project Structure

```
CodeInsight/
├── app.py                          # Main Flask application (800+ lines)
│                                   # - Route handlers
│                                   # - CodeAnalyzer class
│                                   # - PDF generation logic
│
├── models.py                       # Database models and operations
│                                   # - Database class
│                                   # - User operations
│                                   # - Submission operations
│
├── config.py                       # Configuration settings
│                                   # - Database credentials
│                                   # - Environment variables
│
├── database.sql                    # MySQL schema and initial setup
│                                   # - CREATE TABLE statements
│                                   # - Indexes
│
├── requirements.txt                # Python dependencies list
├── setup.bat                       # Windows automated setup script
├── setup.sh                        # Linux/Mac automated setup script
│
├── /templates                      # HTML template files
│   ├── login.html                  # Login page with form
│   ├── register.html               # Registration page with form
│   ├── dashboard.html              # Main user dashboard
│   ├── upload.html                 # File upload form
│   ├── results.html                # Analysis results display
│   └── about.html                  # About/help page
│
├── /static                         # Static assets
│   ├── /css
│   │   └── style.css               # Main stylesheet (700+ lines)
│   │                               # - Custom styling
│   │                               # - Responsive design
│   │                               # - Chart styling
│   └── /js
│       └── (Chart.js integration)
│
├── /uploads                        # User-uploaded Python files (auto-created)
│                                   # - Stored with timestamp naming
│                                   # - Organized by upload date
│
└── Documentation Files:
    ├── README.md                   # Full user documentation
    ├── SETUP.md                    # Detailed setup instructions
    ├── PROJECT_SUMMARY.md          # Project overview
    ├── QUICK_REFERENCE.md          # Quick command reference
    ├── STRUCTURE.md                # File structure details
    └── INDEX.md                    # Project index
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Submissions Table
```sql
CREATE TABLE submissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX (user_id),
    INDEX (uploaded_at)
);
```

### Analysis Results Table
```sql
CREATE TABLE analysis_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    submission_id INT NOT NULL,
    style_score INT,
    complexity_score INT,
    maintainability_score INT,
    total_score INT,
    style_issues JSON,
    complexity_value FLOAT,
    maintainability_index FLOAT,
    metrics JSON,
    suggestions JSON,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    INDEX (submission_id),
    UNIQUE KEY (submission_id)
);
```

---

## Application Flow

### User Registration & Login
```
User Registration:
  1. User fills registration form
  2. Email validation (uniqueness check)
  3. Password hashing with Werkzeug
  4. User stored in database
  5. Redirect to login page

User Login:
  1. User submits email and password
  2. Database lookup by email
  3. Password verification
  4. Session creation
  5. Redirect to dashboard
```

### Code Analysis Pipeline
```
File Upload:
  1. User selects .py file
  2. File validation (extension check)
  3. File saved with timestamp naming
  4. Submission recorded in database

Code Analysis (automated):
  1. Syntax Check (AST)
     → If syntax error: Stop and report
     → If valid: Continue
  
  2. Style Analysis (Pylint)
     → Run pylint with custom rules
     → Extract all issues
     → Calculate style score (40 max)
  
  3. Complexity Analysis (Radon)
     → Calculate cyclomatic complexity
     → Extract average complexity
     → Map to complexity score (30 max)
  
  4. Maintainability Analysis (Radon)
     → Calculate maintainability index
     → Map to maintainability score (30 max)
  
  5. Calculate Total Score
     → Sum all three scores
     → Generate improvement suggestions
  
  6. Store Results
     → Save scores to database
     → Save detailed metrics
     → Save issues and suggestions

Results Display:
  1. Load analysis from database
  2. Render results page with charts
  3. Display all metrics and suggestions
  4. Offer PDF download
```

---

## Key Routes (Endpoints)

```
GET /                          → Dashboard (logged-in users)
GET /about                     → About page
GET /login                     → Login form
POST /login                    → Process login
GET /register                  → Registration form
POST /register                 → Create new user
GET /logout                    → Destroy session

GET /dashboard                 → User dashboard (login required)
GET /upload                    → Upload form (login required)
POST /upload                   → Process file upload (login required)
GET /results/<submission_id>   → View analysis results (login required)
GET /download_pdf/<result_id>  → Download PDF report (login required)

API Routes:
POST /api/analyze              → Trigger analysis (internal)
GET /api/submissions           → Get user submissions (internal)
```

---

## Code Analysis Engine Details

### CodeAnalyzer Class Methods

```python
CodeAnalyzer.check_syntax(filepath)
  - Parses file using AST
  - Returns: List of syntax errors (if any)
  - Returns: Empty list if valid
  - Format: "Syntax Error: {message} (Line {number})"

CodeAnalyzer.check_code_style(filepath)
  - Runs pylint with specific rule set
  - Detects: naming, imports, variables, docstrings, etc.
  - Returns: List of issues (up to 50)
  - Format: Standard pylint message format
  - Timeout: 20 seconds

CodeAnalyzer.calculate_complexity(filepath)
  - Runs radon cc (cyclomatic complexity)
  - Calculates average complexity
  - Returns: Float value (1.0 - 100.0+)
  - Timeout: 10 seconds

CodeAnalyzer.calculate_maintainability(filepath)
  - Runs radon mi (maintainability index)
  - Returns: Float value (0-100)
  - Timeout: 10 seconds

CodeAnalyzer.get_code_metrics(filepath)
  - Parses code with AST
  - Counts: lines, functions, classes, etc.
  - Returns: Dictionary with metrics

CodeAnalyzer.generate_suggestions(scores, issues)
  - Analyzes low scores
  - Generates improvement recommendations
  - Returns: List of suggestion strings
```

### Scoring Algorithm

```python
def calculate_scores(style_issues, complexity, maintainability):
    # Style Score (0-40)
    style_score = max(0, 40 - (len(style_issues) * 3))
    
    # Complexity Score (0-30)
    if complexity <= 2:
        complexity_score = 30
    elif complexity <= 5:
        complexity_score = 25
    elif complexity <= 10:
        complexity_score = 20
    elif complexity <= 20:
        complexity_score = 15
    else:
        complexity_score = 5
    
    # Maintainability Score (0-30)
    if maintainability >= 85:
        maintainability_score = 30
    elif maintainability >= 75:
        maintainability_score = 25
    elif maintainability >= 65:
        maintainability_score = 20
    elif maintainability >= 55:
        maintainability_score = 15
    else:
        maintainability_score = 5
    
    total_score = style_score + complexity_score + maintainability_score
    return total_score, style_score, complexity_score, maintainability_score
```

---

## Dependencies & Versions

```
Flask==3.0.0                   # Web framework
Flask-MySQLdb==1.0.1          # MySQL integration
Werkzeug==3.0.0               # Security utilities
pylint==3.0.0                 # Code style analysis
radon==6.0.1                  # Complexity metrics
reportlab==4.0.4              # PDF generation
MySQLdb==1.2.5                # MySQL database driver
```

---

## Security Features

1. **Password Hashing**: Werkzeug generate_password_hash (PBKDF2-SHA256)
2. **Session Management**: Flask session with secret key
3. **File Validation**: Only .py files accepted
4. **File Isolation**: Files stored per-user with timestamps
5. **SQL Injection Prevention**: Parameterized queries with MySQLdb
6. **Authentication Decorator**: `@login_required` for protected routes
7. **CSRF Protection**: Flask's built-in session security

---

## Configuration

### Database Setup (config.py)
```
host='localhost'
user='root'
password='root'
database='code_reviewer'
```

### Flask Configuration
```
SECRET_KEY: Environment variable or default key
UPLOAD_FOLDER: 'uploads' directory
MAX_CONTENT_LENGTH: File size limit (if configured)
ALLOWED_EXTENSIONS: {'.py'}
```

---

## Error Handling

The application handles:
- **Database Connection Errors**: Graceful degradation with warnings
- **File Upload Errors**: Validation and user feedback
- **Analysis Tool Failures**: Timeout handling (20s for pylint, 10s for radon)
- **Syntax Errors**: Caught and reported to user
- **Session Errors**: Redirect to login if session expired
- **Invalid File Access**: Redirect with error message

---

## Performance Considerations

- **Asynchronous Analysis**: Analysis runs synchronously but with timeouts
- **File Size**: No explicit limit (can be configured)
- **Database Indexing**: Indexes on user_id, submission_id, timestamps
- **Cache**: No caching implemented (could be optimized)
- **Timeout Management**:
  - Pylint: 20 seconds
  - Radon: 10 seconds

---

## Deployment Ready

✅ Modular code structure  
✅ Separate config file for credentials  
✅ Environment variable support  
✅ Automated setup scripts (Windows & Linux)  
✅ Database schema provided  
✅ Error logging and warnings  
✅ Static assets properly organized  
✅ No hardcoded secrets (mostly)  

---

## Use Cases

1. **CS Students**: Get code quality feedback on assignments
2. **Code Reviews**: Automated first-pass analysis
3. **Learning Tool**: Understand code quality metrics
4. **Portfolio**: Demonstrate understanding of best practices
5. **Team Projects**: Enforce code quality standards
6. **Interviews**: Show code analysis capabilities

---

## Future Enhancement Opportunities

- Support for multiple languages (JavaScript, Java, etc.)
- Real-time collaborative analysis
- Historical trends and progress tracking
- Team/project management features
- Integration with GitHub/GitLab
- Advanced visualization dashboards
- Email notifications
- API for external integrations
- Performance optimization with caching
- Batch analysis capabilities

---

## Quick Start Summary

1. **Install**: `pip install -r requirements.txt`
2. **Database**: `mysql -u root -p < database.sql`
3. **Configure**: Update database credentials in config.py
4. **Run**: `python app.py`
5. **Access**: `http://localhost:5000`

---

## Testing Files in /uploads

The project includes sample files for testing:
- `clean_example.py` - Well-written code (high score expected)
- `bad_code_test.py` - Poor code quality (low score expected)
- `demogood.py` - Good code example
- `demobad*.py` - Multiple bad code examples for testing

---

## File Statistics

- **app.py**: ~800 lines (main application)
- **style.css**: ~700 lines (comprehensive styling)
- **models.py**: ~200 lines (database operations)
- **Total Dependencies**: 6 major packages
- **HTML Templates**: 6 files
- **Database Tables**: 3 tables

---

## Documentation Files Available

- `README.md` - User guide and features
- `SETUP.md` - Installation and setup instructions
- `PROJECT_SUMMARY.md` - Project overview
- `QUICK_REFERENCE.md` - Command quick reference
- `STRUCTURE.md` - File structure details
- `INDEX.md` - Project index
- This file: CODEINSIGHT_COMPLETE_OVERVIEW.md

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Status**: Production Ready  
**License**: Open Source (MCA Project)

---

## Contact & Support

For questions about CodeInsight, refer to:
- README.md for feature documentation
- SETUP.md for installation help
- QUICK_REFERENCE.md for common commands
- This overview for technical architecture details
