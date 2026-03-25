# CodeInsight - Quick Reference Guide

## 📋 File Manifest

### Core Application Files
| File | Purpose | Lines |
|------|---------|-------|
| **app.py** | Main Flask application | 600+ |
| **models.py** | Database operations | 300+ |
| **config.py** | Configuration settings | 50 |
| **requirements.txt** | Python dependencies | 6 packages |

### Database
| File | Purpose |
|------|---------|
| **database.sql** | Complete SQL schema |

### Documentation
| File | Purpose |
|------|---------|
| **README.md** | Complete documentation |
| **SETUP.md** | Detailed installation guide |
| **PROJECT_SUMMARY.md** | Project overview & statistics |
| **QUICK_REFERENCE.md** | This file |

### Frontend Templates (HTML)
| File | Purpose |
|------|---------|
| **login.html** | Login page |
| **register.html** | User registration |
| **dashboard.html** | User dashboard |
| **upload.html** | File upload interface |
| **results.html** | Analysis results display |

### Styling & Assets
| File | Purpose |
|------|---------|
| **static/css/style.css** | Complete styling |

### Setup Scripts
| File | Platform |
|------|----------|
| **setup.bat** | Windows |
| **setup.sh** | Linux/Mac |

### Directories
| Directory | Purpose |
|-----------|---------|
| **/templates** | HTML files |
| **/static/css** | Stylesheets |
| **/static/js** | JavaScript |
| **/uploads** | Uploaded Python files |

---

## 🚀 Quick Start (Copy-Paste)

### Windows
```bash
pip install -r requirements.txt
mysql -u root -p code_reviewer < database.sql
python app.py
# Open: http://localhost:5000
```

### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mysql -u root -p code_reviewer < database.sql
python3 app.py
# Open: http://localhost:5000
```

---

## 🔧 Configuration Changes Needed

### 1. Database Credentials (app.py)
```python
db = Database(
    host='localhost',
    user='root',           # ← Change if needed
    password='',           # ← Add your password
    db='code_reviewer'
)
```

### 2. Secret Key (app.py)
```python
app.secret_key = 'your-secret-key-change-this'  # ← Change this
```

### 3. Flask Port (bottom of app.py)
```python
app.run(debug=True, port=5000)  # ← Change 5000 if needed
```

---

## 📊 Scoring Breakdown

### Overall Score Formula: 0-100

```
STYLE SCORE (max 40)
├─ Base: 40 points
└─ Deduction: 3 points per issue
   └─ Minimum: 0 points

COMPLEXITY SCORE (max 30)
├─ Complexity ≤ 2 → 30 points
├─ Complexity ≤ 4 → 25 points
├─ Complexity ≤ 7 → 20 points
├─ Complexity ≤ 10 → 10 points
└─ Complexity > 10 → 0 points

MAINTAINABILITY SCORE (max 30)
├─ MI ≥ 85 → 30 points
├─ MI ≥ 70 → 25 points
├─ MI ≥ 50 → 20 points
├─ MI ≥ 25 → 10 points
└─ MI < 25 → 0 points

TOTAL = Style + Complexity + Maintainability (0-100)
```

---

## 🔐 Security Checklist

- ✅ Passwords hashed with Werkzeug
- ✅ Session-based authentication
- ✅ User authorization checks
- ✅ File type validation
- ✅ SQL injection protection (parameterized queries)
- ✅ CSRF protection ready (Flask default)
- ✅ Error handling without info leakage
- ✅ Input validation on forms

**TODO for Production:**
- [ ] Change Flask secret key
- [ ] Enable HTTPS
- [ ] Set DEBUG = False
- [ ] Configure CORS if needed
- [ ] Add rate limiting
- [ ] Set up logging
- [ ] Regular backups

---

## 🗄️ Database Structure

```
code_reviewer
├── users
│   ├── id (PK)
│   ├── name
│   ├── email (UNIQUE)
│   ├── password (hashed)
│   ├── created_at
│   └── updated_at
│
├── uploaded_files
│   ├── id (PK)
│   ├── user_id (FK)
│   ├── filename
│   └── upload_date
│
└── analysis_results
    ├── id (PK)
    ├── file_id (FK, UNIQUE)
    ├── score
    ├── complexity
    ├── maintainability
    ├── issues (JSON)
    ├── suggestions (JSON)
    ├── created_at
    └── updated_at
```

---

## 🔄 User Flow

```
START
  │
  ├─→ [Login/Register]
  │   └─→ Authenticate
  │
  ├─→ [Dashboard]
  │   └─→ View Files
  │
  ├─→ [Upload File]
  │   ├─→ Validate File
  │   └─→ Save to Database
  │
  ├─→ [Analyze]
  │   ├─→ Check Syntax (AST)
  │   ├─→ Check Style (Pylint)
  │   ├─→ Calculate Complexity (Radon)
  │   ├─→ Calculate Maintainability (Radon)
  │   ├─→ Calculate Score
  │   └─→ Generate Suggestions
  │
  ├─→ [View Results]
  │   ├─→ Show Score & Metrics
  │   ├─→ Display Chart
  │   ├─→ Show Issues
  │   └─→ Show Suggestions
  │
  └─→ [PDF Report]
      └─→ Download
```

---

## 📝 Testing Samples

### Clean Code (Should score high)
```python
"""Module for mathematical operations."""

def add(x, y):
    """Add two numbers."""
    return x + y

def multiply(x, y):
    """Multiply two numbers."""
    return x * y
```

### Code with Issues
```python
def bad_function( a,b,c ):
x=a+b+c
if x>10:
    if x>20:
        if x>30:
            return x
return 0
```

### Code with Syntax Error
```python
def broken():
    print("Hello"  # Missing closing parenthesis
    return
```

---

## 🐛 Common Issues & Fixes

| Issue | Cause | Solution |
|-------|-------|----------|
| Cannot connect to MySQL | MySQL not running | `mysql.server start` or `sudo service mysql start` |
| Module not found (Flask) | Dependencies not installed | `pip install -r requirements.txt` |
| Port 5000 in use | Another app using port | Change port in app.py or use different port |
| Pylint not found | Not installed | `pip install pylint` |
| Radon not found | Not installed | `pip install radon` |
| File upload fails | File type wrong | Upload .py files only |

---

## 📚 Key Classes & Methods

### CodeAnalyzer
```python
CodeAnalyzer.check_syntax(filepath)        # → List[str]
CodeAnalyzer.check_code_style(filepath)    # → List[str]
CodeAnalyzer.calculate_complexity(filepath) # → float
CodeAnalyzer.calculate_maintainability(filepath) # → float
CodeAnalyzer.analyze(filepath)             # → dict
```

### ScoreCalculator
```python
ScoreCalculator.calculate_score(analysis)   # → dict
ScoreCalculator.get_suggestions(analysis, scores) # → list
```

### Database
```python
Database.register_user(name, email, password)  # → int
Database.get_user_by_email(email)             # → tuple
Database.upload_file(user_id, filename)       # → int
Database.save_analysis_result(...)            # → int
Database.get_analysis_result(file_id)         # → tuple
```

---

## 🌐 API Endpoints

| Method | Route | Auth | Purpose |
|--------|-------|------|---------|
| GET/POST | `/login` | No | User login |
| GET/POST | `/register` | No | User registration |
| GET | `/logout` | Yes | User logout |
| GET | `/dashboard` | Yes | Dashboard |
| GET/POST | `/upload` | Yes | File upload |
| GET | `/analyze/<id>` | Yes | Analyze file |
| GET | `/results/<id>` | Yes | View results |
| GET | `/api/analysis/<id>` | Yes | JSON API |
| GET | `/generate-pdf/<id>` | Yes | PDF report |

---

## 💾 Deployment Steps

### 1. Prepare Server
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip mysql-server
```

### 2. Clone Project
```bash
git clone <repo> /var/www/code_reviewer
cd /var/www/code_reviewer
```

### 3. Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Setup Database
```bash
mysql -u root -p < database.sql
```

### 5. Configure
```bash
# Edit app.py with production settings
nano app.py
```

### 6. Run with Gunicorn
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### 7. Setup Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

---

## 📞 Support Resources

**Official Documentation:**
- Flask: https://flask.palletsprojects.com/
- MySQL: https://dev.mysql.com/doc/
- Python: https://docs.python.org/3/
- Bootstrap: https://getbootstrap.com/docs/5.3/

**Tools Used:**
- Pylint: https://pylint.org/
- Radon: https://radon.readthedocs.io/
- Chart.js: https://www.chartjs.org/

**Communities:**
- Stack Overflow
- GitHub Issues
- Flask Community

---

## ✅ Pre-Submission Checklist

- [ ] All files created
- [ ] Database created and working
- [ ] Application runs without errors
- [ ] User registration works
- [ ] File upload works
- [ ] Analysis runs correctly
- [ ] Results display properly
- [ ] PDF generation works
- [ ] All pages render correctly
- [ ] Responsive design verified
- [ ] Code is commented
- [ ] Documentation is complete
- [ ] Setup verified on clean machine

---

## 📖 VIVA Preparation

### Key Points to Explain
1. Project purpose and scope
2. Technology choices and why
3. Architecture and design
4. Database schema and relationships
5. Authentication and security
6. Code analysis implementation
7. Scoring algorithm
8. User interface design
9. Implementation challenges
10. Future enhancements

### Demo Flow
1. Login with demo account
2. Upload a sample Python file
3. Show analysis results
4. Explain score calculation
5. Generate and download PDF
6. Show database structure
7. Explain code walkthrough

---

## 🎯 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend | ✅ Complete | Flask app with all routes |
| Database | ✅ Complete | 3 tables with proper schema |
| Frontend | ✅ Complete | 5 HTML pages + CSS |
| Authentication | ✅ Complete | Registration & Login |
| File Upload | ✅ Complete | Validation & Storage |
| Code Analysis | ✅ Complete | AST, Pylint, Radon |
| Scoring | ✅ Complete | Weighted algorithm |
| Results | ✅ Complete | Dashboard with charts |
| PDF Reports | ✅ Complete | ReportLab generation |
| Documentation | ✅ Complete | README, SETUP, etc |

---

**Last Updated:** February 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅
