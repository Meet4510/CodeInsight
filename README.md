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
  - Style, Complexity, Maintainability, Structure sub-scores
  - Explainable score breakdown (reasoning per metric)
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

CodeInsight uses a continuous, explainable scoring model:

- Style Score: 0-45 (weighted issue density with exponential decay)
- Complexity Score: 0-25 (normalized complexity curve)
- Maintainability Score: 0-25 (MI-based, size-normalized for large modules)
- Structure Score: 0-5 (organization and architecture heuristics)

Total = Style + Complexity + Maintainability + Structure

### Style Scoring (0-45)

- Issues are classified into: `error`, `warning`, `info`, and semantic (`W000x`)
- Weighted issue density is computed per code line
- Score is continuous (no hard buckets), then adjusted for naming/doc/duplicate patterns

### Complexity Scoring (0-25)

- Uses a normalized curve to avoid over-penalizing moderate complexity
- Includes light structural adjustments for deep nesting and very long average function length

### Maintainability Scoring (0-25)

- Starts from Radon MI (`0..100`)
- Applies size normalization so large single-file modules are not unfairly depressed

### Structure Scoring (0-5)

- Rewards presence of functions/classes, manageable nesting, and healthy function-length distribution

### Syntax & Edge Handling

- Syntax penalties apply only when syntax issues exist
- Empty files return 0 with an explicit warning in results

### Explainability

- The scoring API returns a `breakdown` object with human-readable reasoning for:
  - style
  - complexity
  - maintainability
  - structure

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
