# CodeInsight Complete Project Documentation

## 1. Project Overview

CodeInsight is a Flask-based web application that performs automated source code quality analysis and reporting.

Current implementation focus:
- Authentication and profile-enabled user workflow
- Plan-based language access control
- Python and Java analysis pipeline
- Dashboard-based issue and score presentation
- PDF report generation
- Admin panel for audits and user management
- Forgot-password flow with token-based reset

## 2. Primary Objectives

- Automate code review tasks that are usually manual
- Provide understandable quality scoring and suggestions
- Centralize upload, analysis, visualization, and reporting in one platform
- Support role-based access (user/admin) and plan-based language access

## 3. Technology Stack

Frontend:
- HTML templates (Jinja2)
- CSS (custom stylesheet in static/css/style.css)
- JavaScript (static/js/script.js)

Backend:
- Python 3.x
- Flask 3.0.0
- Flask-Mail 0.9.1
- Werkzeug 3.0.0
- python-dotenv 1.0.0

Database:
- MySQL
- Flask-MySQLdb 1.0.1 / MySQLdb driver

Analysis and Reporting Tools:
- AST (Python syntax parsing)
- Pylint (Python style checks)
- Radon (Python complexity and maintainability)
- Custom Java analysis rules (syntax/style/metrics)
- Optional javalang parser import support
- ReportLab (PDF generation)

## 4. Repository Structure (Current)

Root files and folders:
- .env
- app.py
- models.py
- config.py
- database.sql
- requirements.txt
- README.md
- SETUP.md
- QUICK_REFERENCE.md
- PROJECT_SUMMARY.md
- INDEX.md
- STRUCTURE.md
- CODEINSIGHT_COMPLETE_OVERVIEW.md
- SYSTEM_ARCHITECTURE.md
- FORGOT_PASSWORD_SETUP.md
- analysis_algorithms_summary.txt
- setup.bat
- setup.sh
- fix_java_issues.py
- update_analyzer.py
- test_flask_mail.py
- test_forgot_password.py
- test_pylint_style.py
- templates/
- static/
- uploads/

Templates:
- templates/login.html
- templates/register.html
- templates/dashboard.html
- templates/upload.html
- templates/results.html
- templates/about.html
- templates/settings.html
- templates/forgot_password.html
- templates/reset_password.html
- templates/admin/admin_dashboard.html
- templates/admin/admin_audits.html
- templates/admin/admin_user_management.html

Static assets:
- static/css/style.css
- static/js/script.js
- static/avatars/

## 5. Functional Modules

### 5.1 Authentication and Session Management
- User registration with validation
- Login with password hash verification
- Session-backed access control with login_required decorator
- Logout session clear
- Account status checks (active/blocked)

### 5.2 Password Recovery
- Forgot password route generates secure token
- Token is stored in DB with expiration window
- Reset password route validates token and updates password hash
- Email sending via Flask-Mail
- Testing fallback mode supported when email credentials are unavailable

### 5.3 Upload and Access Control
- File extension validation via ALLOWED_EXTENSIONS
- Plan-based language access control:
  - free: python
  - pro: python, java
  - premium: python, java, html, css, javascript
- Unique stored filename generation using secure token hex
- Upload metadata persistence in uploaded_files table

### 5.4 Analysis Engine

Language detection:
- Extension-driven mapping (py/java/js/css/html)

Python path:
- Syntax: ast parsing
- Style: pylint output parsing
- Complexity: radon cyclomatic complexity
- Maintainability: radon MI
- Semantic quality checks (custom W000x style flags)

Java path:
- Syntax: custom structural checks (braces/parentheses/brackets + declaration heuristics)
- Style: custom Java conventions checks (including JavaDoc-related checks and risk patterns)
- Complexity: custom formula from decision points, density, nesting
- Maintainability: custom score based on metrics and risk penalties
- Optional javalang integration if library is available

Edge handling:
- Empty file detection returns explicit warning and zero-scored output
- Defensive fallback behavior for analysis tool failures

### 5.5 Scoring and Suggestions
- ScoreCalculator computes explainable, continuous scores
- Current scoring breakdown in code:
  - Style: 0 to 45
  - Complexity: 0 to 25
  - Maintainability: 0 to 25
  - Structure: 0 to 5
  - Total: 0 to 100
- Syntax issues apply soft penalties instead of hard fail-only scoring
- Technical debt estimate derived from severity profile
- Suggestions generated from language-aware heuristics and thresholds

### 5.6 Results and Reporting
- results route renders score, metrics, categorized issues, and suggestions
- api route provides JSON analysis payload
- generate-pdf route builds report with ReportLab
- Admin report route generates admin summary PDF

### 5.7 Admin Operations
- Dedicated admin dashboard
- Recent audits view
- User management view with filters
- Block/unblock non-admin accounts
- Admin summary report export

## 5.8 Admin Information (Detailed)

Admin role model:
- Admin access is controlled by users.role value = admin.
- Admin routes are protected by login_required and role checks.
- Non-admin users are redirected to user dashboard when trying to access admin pages.

Admin pages:
- /admin_dashboard
  - Displays platform summary KPIs.
  - Shows compact recent audit activity.
  - Exposes trend data for signups, subscriptions, and analyses.
- /admin_audits
  - Shows extended recent audit table.
  - Includes filename, engine label, status, relative time, and score text.
- /admin_user_management
  - Lists users with controls for operational moderation.
  - Supports filtering by search text, plan, role, and account status.

Admin analytics and metrics:
- Total users
- Active subscriptions (non-free)
- Analyses executed today
- Weekly user growth trend
- Weekly subscription trend
- Weekly analysis trend

Admin controls:
- Block user account:
  - Route: POST /admin_users/<int:target_user_id>/block
  - Sets account_status to blocked.
  - Blocked users are denied login.
- Unblock user account:
  - Route: POST /admin_users/<int:target_user_id>/unblock
  - Sets account_status to active.
- Safety rules:
  - Admin cannot block self.
  - Admin actions do not target other admin users through management flow.

Admin reporting:
- Route: GET /admin_report
- Generates downloadable PDF summary containing:
  - System KPIs
  - Recent audits table
  - Timestamped generation details

Admin workflow:
1. Login as admin account.
2. Open admin dashboard for high-level system status.
3. Review audits in detail on admin_audits page.
4. Manage accounts and moderation actions from admin_user_management.
5. Export admin PDF report for review and record keeping.

## 6. HTTP Route Catalog

Public and auth routes:
- GET /
- GET/POST /register
- GET/POST /login
- GET /logout
- GET /test_email
- GET/POST /forgot_password
- GET/POST /reset_password/<token>

User routes:
- GET /dashboard
- GET/POST /upload
- GET /analyze/<int:file_id>
- POST /delete/<int:file_id>
- GET /results/<int:file_id>
- GET /api/analysis/<int:file_id>
- GET /generate-pdf/<int:file_id>
- GET /view_code/<int:file_id>
- GET /about
- GET/POST /settings
- GET /about.html

Admin routes:
- GET /admin_dashboard
- GET /admin_audits
- GET /admin_user_management
- POST /admin_users/<int:target_user_id>/block
- POST /admin_users/<int:target_user_id>/unblock
- GET /admin_report

## 7. Database Documentation

Database name:
- code_reviewer

Tables:

users:
- id (PK)
- name
- email (UNIQUE)
- password (hashed)
- plan
- role
- account_status
- bio
- avatar
- reset_token
- reset_token_expires
- created_at
- updated_at

uploaded_files:
- id (PK)
- user_id (FK -> users.id, cascade delete)
- filename
- stored_filename
- upload_date

analysis_results:
- id (PK)
- file_id (FK -> uploaded_files.id, unique, cascade delete)
- score
- complexity
- maintainability
- issues
- suggestions
- created_at
- updated_at

Schema behaviors:
- On startup, model layer ensures presence of account_status and stored_filename columns
- Analysis result rows are upserted using ON DUPLICATE KEY UPDATE

## 8. End-to-End Processing Flow

1. User logs in and accesses upload page.
2. File is validated by extension and checked against user plan language policy.
3. File is stored with secure generated filename in uploads directory.
4. Upload metadata is stored in uploaded_files table.
5. Analysis route resolves the stored file and runs CodeAnalyzer pipeline.
6. ScoreCalculator computes total score plus sub-scores and explanations.
7. Issues are categorized and suggestions are generated.
8. Result is saved to analysis_results.
9. User sees results dashboard and optionally exports PDF.

## 9. Security Controls

- Password hashing via Werkzeug
- Session-based route protection
- Ownership checks for file operations
- Account status enforcement (blocked users restricted)
- Parameterized SQL queries via DB driver cursor parameter binding
- Tokenized password reset with expiry
- Input validation on registration, login, upload, and password reset

## 10. Testing and Utility Scripts

test_flask_mail.py:
- Verifies Flask-Mail configuration and email dispatch behavior

test_forgot_password.py:
- Simulates forgot-password email sending path used in application

test_pylint_style.py:
- Utility to inspect style issue output from analyzer

Support scripts:
- fix_java_issues.py
- update_analyzer.py

## 11. Setup and Run

1. Create and activate virtual environment.
2. Install dependencies from requirements.txt.
3. Create MySQL database and run database.sql.
4. Configure environment variables in .env as needed.
5. Start app with python app.py.
6. Open browser at local Flask URL.

Setup references:
- setup.bat for Windows
- setup.sh for Linux/Mac
- SETUP.md and QUICK_REFERENCE.md for guided setup

## 12. Configuration and Environment Variables

Common environment variables:
- SECRET_KEY
- MAIL_SERVER
- MAIL_PORT
- MAIL_USE_TLS
- MAIL_USERNAME
- MAIL_PASSWORD
- MAIL_DEFAULT_SENDER

Operational configuration also exists in config.py.

## 13. Known Documentation Drift Notes

Some legacy documentation files describe older scoring bands and older scope statements.
Current source-of-truth behavior should be treated as:
- app.py for analysis/scoring/routes
- models.py for DB operations
- database.sql for schema definitions
- requirements.txt for dependency versions

## 14. Limitations and Future Enhancements

Current limitations:
- Most detailed analyzer logic is focused on Python and Java
- Some docs still reference older versions/features
- Production hardening tasks are not fully automated

Potential enhancements:
- Expand deep analysis support for html/css/javascript
- Add comprehensive automated test suite with CI
- Add rate limiting and stricter production security defaults
- Improve observability (structured logging and monitoring)
- Add scalable async analysis queue for large workloads

## 15. Quick Navigation Map

Core backend:
- app.py
- models.py
- config.py

Database:
- database.sql

Frontend templates:
- templates/
- templates/admin/

Static assets:
- static/css/style.css
- static/js/script.js

Project docs:
- README.md
- SETUP.md
- PROJECT_SUMMARY.md
- QUICK_REFERENCE.md
- INDEX.md
- STRUCTURE.md
- SYSTEM_ARCHITECTURE.md