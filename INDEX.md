# 📚 CodeInsight - Documentation Index

## Quick Links

### 🚀 Getting Started
1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Fast setup and quick answers
2. **[SETUP.md](SETUP.md)** - Detailed installation guide for all platforms
3. **[setup.bat](setup.bat)** - Automated setup for Windows
4. **[setup.sh](setup.sh)** - Automated setup for Linux/Mac

### 📖 Documentation
1. **[README.md](README.md)** - Complete project documentation
2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Full technical overview
3. **[database.sql](database.sql)** - Database schema

### 💻 Source Code
1. **[app.py](app.py)** - Main Flask application (600+ lines)
2. **[models.py](models.py)** - Database models (300+ lines)
3. **[config.py](config.py)** - Configuration file
4. **[requirements.txt](requirements.txt)** - Python dependencies

### 🎨 Frontend
1. **[templates/login.html](templates/login.html)** - Login page
2. **[templates/register.html](templates/register.html)** - Registration page
3. **[templates/dashboard.html](templates/dashboard.html)** - Dashboard
4. **[templates/upload.html](templates/upload.html)** - File upload
5. **[templates/results.html](templates/results.html)** - Analysis results
6. **[static/css/style.css](static/css/style.css)** - Styling

---

## 📋 What You Get

### Complete Files (14 files)
- **2** Python files (app.py, models.py)
- **1** Configuration file (config.py)
- **1** Dependencies list (requirements.txt)
- **1** Database schema (database.sql)
- **5** HTML templates
- **1** CSS stylesheet
- **4** Documentation files
- **2** Setup scripts

### Complete Folders (3 folders)
- **/templates** - HTML pages
- **/static/css** - Stylesheets
- **/uploads** - Uploaded files (auto-created)

---

## 🎯 Feature Checklist

### ✅ Core Features
- [x] User Registration & Login
- [x] Password Hashing & Security
- [x] Session Management
- [x] Python File Upload (.py only)
- [x] Syntax Check (AST)
- [x] Style Check (Pylint)
- [x] Complexity Analysis (Radon)
- [x] Maintainability Calculation (Radon)
- [x] Quality Scoring (0-100)
- [x] Results Dashboard
- [x] Chart Visualization (Chart.js)
- [x] PDF Report Generation
- [x] Responsive UI (Bootstrap 5)

### ✅ Technical Features
- [x] Flask Web Framework
- [x] MySQL Database
- [x] User Authentication
- [x] File Validation
- [x] Code Analysis
- [x] Score Calculation
- [x] Suggestion Generation
- [x] PDF Export
- [x] Clean Architecture
- [x] Error Handling
- [x] Input Validation

---

## 📖 Documentation Guide

### For Quick Setup
Start with: **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**
- Copy-paste commands
- Quick configuration
- Common issues

### For Detailed Setup
Read: **[SETUP.md](SETUP.md)**
- Step-by-step instructions
- Platform-specific guides
- Troubleshooting

### For Understanding Project
Review: **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**
- Architecture overview
- Class structure
- Database design
- Security features
- VIVA talking points

### For Complete Information
Study: **[README.md](README.md)**
- Full feature list
- Installation guide
- Usage instructions
- Sample test cases
- Future enhancements

---

## 🔧 Setup by Platform

### Windows Users
```
1. Read: QUICK_REFERENCE.md
2. Run: setup.bat
3. Edit: app.py (database settings)
4. Start: python app.py
5. Open: http://localhost:5000
```

### Mac/Linux Users
```
1. Read: QUICK_REFERENCE.md
2. Run: bash setup.sh
3. Edit: app.py (database settings)
4. Start: python3 app.py
5. Open: http://localhost:5000
```

---

## 💡 Key Concepts Explained

### Scoring System
See **[PROJECT_SUMMARY.md#scoring-system](PROJECT_SUMMARY.md)** for:
- Style Score (0-40)
- Complexity Score (0-30)
- Maintainability Score (0-30)
- Total Score (0-100)

### Code Analysis
Learn from **[app.py](app.py)** (CodeAnalyzer class):
- Syntax checking with Python AST
- Style checking with Pylint
- Complexity metrics with Radon
- Maintainability calculation

### Database Design
Understand from **[PROJECT_SUMMARY.md#database-design](PROJECT_SUMMARY.md)**:
- users table
- uploaded_files table
- analysis_results table
- Relationships and indexes

### Security Implementation
Review **[PROJECT_SUMMARY.md#security-features](PROJECT_SUMMARY.md)**:
- Password hashing (Werkzeug)
- Session management
- User authorization
- Input validation
- Error handling

---

## 🚀 Running the Application

### Standard Execution
```bash
python app.py
# or on Mac/Linux
python3 app.py
```

### Access the Application
```
http://localhost:5000
```

### Test Login (Create your own account via registration)
```
Email: your-email@example.com
Password: your-password
```

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Files** | 14 |
| **Total Folders** | 3 |
| **Python Code** | 900+ lines |
| **HTML Templates** | 600+ lines |
| **CSS Styling** | 400+ lines |
| **SQL Schema** | 80+ lines |
| **Documentation** | 2000+ lines |
| **Total Size** | ~100KB |

---

## 🎓 Learning Resources

### Inside This Project
- **[app.py](app.py)** - Flask routing, authentication, code analysis
- **[models.py](models.py)** - Database operations and ORM
- **[templates/results.html](templates/results.html)** - Chart.js integration
- **[static/css/style.css](static/css/style.css)** - Bootstrap & custom CSS

### External Resources
- Flask: https://flask.palletsprojects.com/
- MySQL: https://dev.mysql.com/doc/
- Pylint: https://pylint.org/
- Radon: https://radon.readthedocs.io/
- Bootstrap: https://getbootstrap.com/
- Chart.js: https://www.chartjs.org/

---

## ❓ FAQ

**Q: Which Python version?**  
A: Python 3.x recommended. See [SETUP.md](SETUP.md)

**Q: What about the uploads folder?**  
A: Auto-created by app.py. Should be writable for the Flask user.

**Q: How to analyze code I uploaded?**  
A: Click "Analyze" button in dashboard after uploading.

**Q: Can I change the scoring system?**  
A: Yes, modify `ScoreCalculator` class in [app.py](app.py)

**Q: How to get PDF reports?**  
A: After analysis, click "Download PDF" button on results page.

**Q: Is it production-ready?**  
A: Yes, but change secret key and configure properly. See [SETUP.md](SETUP.md)

**Q: Can I use it for other languages?**  
A: Currently .py only. To add support, extend CodeAnalyzer class.

---

## 🔐 Security Notes

### Current Security
✅ Passwords hashed with Werkzeug  
✅ Session-based authentication  
✅ File type validation  
✅ SQL injection protection  
✅ Authorization checks  

### For Production
- [ ] Change Flask secret key in [app.py](app.py)
- [ ] Enable HTTPS
- [ ] Set DEBUG = False
- [ ] Configure proper database backups
- [ ] Add rate limiting
- [ ] Set up logging
- [ ] Regular security audits

See **[SETUP.md](SETUP.md)** for more details.

---

## 📞 Need Help?

1. **Setup Issues?** → Read [SETUP.md](SETUP.md)
2. **Quick Answers?** → Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. **Code Questions?** → Look at comments in [app.py](app.py)
4. **Architecture?** → Study [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
5. **Database?** → Review [database.sql](database.sql)

---

## ✨ What's Included

```
✅ Full working Flask application
✅ Complete database schema
✅ Professional HTML templates
✅ Responsive CSS styling
✅ Code analysis integration
✅ User authentication
✅ PDF report generation
✅ Chart visualization
✅ Setup automation scripts
✅ Comprehensive documentation
✅ Configuration template
✅ Quick reference guide
```

---

## 🎯 Next Steps

1. **Read:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (5 minutes)
2. **Setup:** Run setup script or follow [SETUP.md](SETUP.md) (10 minutes)
3. **Configure:** Update database credentials in [app.py](app.py) (2 minutes)
4. **Run:** Execute `python app.py` (1 minute)
5. **Test:** Open http://localhost:5000 and register (5 minutes)
6. **Learn:** Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) (20 minutes)
7. **Explore:** Test all features and view source code

---

## 📜 File Navigation Cheat Sheet

| I Want To... | Read This File |
|---|---|
| Get started quickly | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| Setup on my computer | [SETUP.md](SETUP.md) |
| Understand the project | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |
| Read full documentation | [README.md](README.md) |
| View the code | [app.py](app.py), [models.py](models.py) |
| Setup database | [database.sql](database.sql) |
| Edit styling | [static/css/style.css](static/css/style.css) |
| Modify HTML | [templates/](templates/) |
| Change settings | [config.py](config.py) |
| Install dependencies | [requirements.txt](requirements.txt) |
| Auto setup (Windows) | [setup.bat](setup.bat) |
| Auto setup (Mac/Linux) | [setup.sh](setup.sh) |

---

**Version:** 1.0.0  
**Created:** February 2026  
**Status:** ✅ Complete & Ready  
**Platform:** Windows, Mac, Linux  
**Python:** 3.x  
**License:** Educational Use

---

**Happy Coding! 🎉**

For questions or issues, refer to the appropriate documentation file above.
