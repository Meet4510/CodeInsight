# CodeInsight

CodeInsight is a Flask-based code analysis web app for Python and Java files, with user authentication, plan-based access, quality scoring, issue categorization, and PDF export.

## Highlights

- Multi-language upload support: `.py`, `.java`, `.html`, `.css`, `.js`
- Plan-based analysis access:
  - Free: Python
  - Pro: Python, Java
  - Premium: Python, Java, HTML, CSS, JavaScript
- Authentication and user profile support
- Language-aware analysis pipeline
- Results dashboard with:
  - Overall score
  - Style, Complexity, Maintainability sub-scores
  - Suggestions and issue breakdown
- PDF report generation
- Empty-file detection with user-facing warning in results

---

## Tech Stack

### Backend
- Python 3.x
- Flask
- Flask-MySQLdb
- Werkzeug
- Pylint (Python style checks)
- Radon (Python complexity and maintainability)
- ReportLab (PDF export)

### Frontend
- HTML templates (Jinja2)
- Tailwind CSS (CDN)
- Custom UI components and cards

### Database
- MySQL (`code_reviewer`)

---

## Current Scoring Model (0-100)

Overall score is computed as:

- Style Score: 0-50
- Complexity Score: 0-25
- Maintainability Score: 0-25

Total = Style + Complexity + Maintainability

### Complexity Score Buckets (0-25)

- <= 1.5 -> 25
- <= 2.5 -> 23
- <= 4.0 -> 20
- <= 6.0 -> 15
- <= 8.0 -> 10
- <= 10.0 -> 5
- > 10.0 -> 0

### Maintainability Score Buckets (0-25)

- >= 85 -> 25
- >= 75 -> 22
- >= 65 -> 18
- >= 50 -> 12
- >= 35 -> 6
- < 35 -> 0

### Style Score Logic

- Java: based on detected `[ERROR]` / `[WARNING]` counts
- Python: based on parsed Pylint severity classes (`E/F/W/C/R`)

### Critical Guardrails

- Syntax errors force strong score penalties
- Empty files (`code_lines == 0`) return score 0 and show an empty-file message

---

## Analysis Behavior

## Python Analysis

- Syntax: Python AST parsing
- Style: Pylint output parsing
- Complexity: Radon CC
- Maintainability: Radon MI
- Defensive fallback behavior:
  - If Radon fails or returns no output, complexity is treated as high and maintainability as low (not optimistic)

## Java Analysis

- Syntax: custom structural checks (braces/brackets/parentheses + declaration heuristics)
- Style: custom rules including JavaDoc checks, raw type usage, mutable public static fields, hardcoded credentials, parameter count, exception handling patterns, dead code, etc.
- Complexity: custom decision-point + density + nesting based formula
- Maintainability: custom formula with structural penalties and risk-pattern penalties

---

## Project Structure

```text
CodeInsight/
├── app.py
├── models.py
├── database.sql
├── requirements.txt
├── README.md
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── results.html
│   ├── settings.html
│   └── about.html
├── static/
│   ├── css/
│   ├── js/
│   └── avatars/
└── uploads/
```

---

## Setup

## 1) Create virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If execution policy blocks activation:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 2) Install dependencies

```bash
pip install -r requirements.txt
```

## 3) Create database

Option A (recommended):

```bash
mysql -u root -p code_reviewer < database.sql
```

Option B:
- Create database manually and run SQL statements from `database.sql`.

## 4) Configure DB credentials

Update database connection values in `app.py` if your MySQL user/password differ.

## 5) Run app

```bash
python app.py
```

Open:

`http://localhost:5000`

---

## Usage

- Register and log in
- Upload a supported file
- Run analysis
- Review:
  - score cards
  - issue breakdown
  - suggestions
- Export PDF report

---

## Empty File Handling

If an uploaded file has no code lines:

- Overall score is set to 0
- Sub-scores are set to 0
- Results page shows: "Empty File Detected"

This prevents misleading high scores for blank uploads.

---

## Common Troubleshooting

### MySQL connection failure

- Verify MySQL server is running
- Verify username/password/db in `app.py`
- Ensure `code_reviewer` schema exists

### Missing tools (Pylint/Radon)

```bash
pip install -r requirements.txt
```

### Upload path issues

- App auto-creates `uploads/` at startup
- Verify write permissions for project folder

---

## Security Notes

- Passwords are hashed (Werkzeug)
- Change `SECRET_KEY` in production via environment variable
- Use HTTPS in production
- Validate and sanitize all user inputs

---

## License

Academic / project use.
