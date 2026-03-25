from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import Database
import os
import json
import ast
from datetime import datetime
from functools import wraps
import subprocess
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '0b1443b6ace6b17afde0079911ec829595fae544471a0cb248cde4f3666aa94c')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'py','java','js','css','html'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration
try:
    db = Database(
        host='localhost',
        user='root',
        password='root', 
        db='code_reviewer'
    )
    # Test connection
    test_conn = db.get_connection()
    if test_conn:
        test_conn.close()
        print("✓ Database connection successful")
    else:
        print("⚠ Warning: Could not connect to database")
        print("  Please ensure MySQL is running and 'code_reviewer' database exists")
        print("  Run: mysql -u root -p < database.sql")
except Exception as e:
    print(f"⚠ Warning: Database initialization error: {e}")
    print("  The application will start but database features may not work")
    db = None

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Allowed file check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#checks the language of the file based on the extension
def get_language(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    
    mapping = {
        'py': 'python',
        'java': 'java',
        'html': 'html',
        'css': 'css',
        'js': 'javascript'
    }
    
    return mapping.get(ext, 'unknown')

# Check if the user's plan allows analyzing the given language
def is_allowed(plan, language):
    if plan == 'free':
        return language == 'python'
    
    elif plan == 'pro':
        return language in ['python', 'java']
    
    elif plan == 'premium':
        return language in ['python', 'java', 'html', 'css', 'javascript']
    
    return False


# Code Analysis Module
class CodeAnalyzer:
    """Analyze Python code for syntax, style, and complexity"""
    
    @staticmethod
    def check_syntax(filepath):
        """Check for syntax errors using AST"""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            return issues
        except SyntaxError as e:
            issues.append(f"Syntax Error: {e.msg} (Line {e.lineno})")
            return issues
        except Exception as e:
            issues.append(f"Error: {str(e)}")
            return issues
    
    @staticmethod
    def check_code_style(filepath):
        """Check code style using pylint with stricter rules"""
        issues = []
        try:
            result = subprocess.run(
                ['pylint', filepath, '--disable=all', '--enable=syntax-error,basic,unused-import,unused-variable,undefined-variable,missing-docstring,invalid-name,line-too-long,too-many-lines,too-many-branches,too-many-statements,too-many-locals,too-few-public-methods,bad-indentation,superfluous-parens,missing-final-newline,trailing-whitespace,trailing-newlines,wrong-import-position,ungrouped-imports,broad-except,consider-using-with,unnecessary-pass,duplicate-code'],
                capture_output=True,
                text=True,
                timeout=20
            )
            
            # Pylint prints issues to stdout/stderr; combine both.
            output = (result.stdout or "") + "\n" + (result.stderr or "")
            lines = output.split('\n')

            # Match standard pylint message format: file:line:col: CODE: message
            issue_pattern = re.compile(r"^[^:]+:\d+:\d+:\s+[A-Z]\d+:")
            for line in lines:
                if issue_pattern.match(line.strip()) and "useless-option-value" not in line:
                    cleaned = line.strip()
                    issues.append(cleaned)

            # If pylint output contains lines beyond the rating/headers, keep them
            if not issues:
                for line in output.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    # Skip noise lines that do not represent issues
                    if line.startswith('*************') or line.startswith('Your code has been rated') or line.startswith('----------------------------------------------------------------------'):
                        continue
                    # Skip plain separators like '-----' or '====='
                    if re.fullmatch(r"^[\-\s=\*]+$", line):
                        continue
                    issues.append(line)

            # Filter out any remaining lines that are still just noise
            issues = [i for i in issues if i and not re.fullmatch(r"^[\-\s=\*]+$", i)]

            return issues[:50]  # Limit to 50 issues for strict analysis
        except Exception as e:
            return [f"Pylint check failed: {str(e)}"]
    
    @staticmethod
    def calculate_complexity(filepath):
        """Calculate cyclomatic complexity using Radon"""
        try:
            result = subprocess.run(
                ['radon', 'cc', filepath, '-a'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout
            
            # Extract complexity value
            if 'Average' in output:
                match = re.search(r'Average complexity: ([\d.]+)', output)
                if match:
                    complexity = float(match.group(1))
                else:
                    complexity = 1.0
            else:
                complexity = 1.0
            
            return complexity
        except Exception as e:
            return 1.0
    
    @staticmethod
    def calculate_maintainability(filepath):
        """Calculate maintainability index using Radon"""
        try:
            result = subprocess.run(
                ['radon', 'mi', filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout
            
            # Extract maintainability index or grade
            match = re.search(r'([\d.]+)\s+-', output)
            if match:
                mi = float(match.group(1))
            else:
                # Check for letter grade
                match_letter = re.search(r'-\s+([A-F])', output)
                if match_letter:
                    grade = match_letter.group(1)
                    # Convert letter to approximate number
                    grade_map = {'A': 100, 'B': 90, 'C': 80, 'D': 70, 'E': 60, 'F': 50}
                    mi = grade_map.get(grade, 50.0)
                else:
                    mi = 50.0
            
            return mi
        except Exception as e:
            return 50.0
    
    @staticmethod
    def get_code_metrics(filepath):
        """Get basic code metrics"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            lines = code.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Count functions and classes
            tree = ast.parse(code)
            functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            return {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'functions': functions,
                'classes': classes
            }
        except Exception as e:
            return {'total_lines': 0, 'code_lines': 0, 'functions': 0, 'classes': 0}
    
    @staticmethod
    def analyze(filepath):
        """Complete code analysis with enhanced metrics"""
        analysis = {
            'syntax_issues': CodeAnalyzer.check_syntax(filepath),
            'style_issues': CodeAnalyzer.check_code_style(filepath),
            'complexity': CodeAnalyzer.calculate_complexity(filepath),
            'maintainability': CodeAnalyzer.calculate_maintainability(filepath),
            'metrics': CodeAnalyzer.get_code_metrics(filepath)
        }
        return analysis

# Scoring Module
def categorize_issues(issues):
    """Group pylint issues into categories for easier reading."""
    categories = {
        'Formatting': [],
        'Naming': [],
        'Documentation': [],
        'Logic': [],
        'Other': []
    }

    for issue in issues:
        key = issue.lower()
        if any(tag in key for tag in ['bad-indentation', 'trailing-whitespace', 'missing-final-newline', 'line-too-long', 'superfluous-parens', 'wrong-import-position', 'ungrouped-imports']):
            categories['Formatting'].append(issue)
        elif 'invalid-name' in key:
            categories['Naming'].append(issue)
        elif any(tag in key for tag in ['missing-module-docstring', 'missing-function-docstring', 'missing-class-docstring']):
            categories['Documentation'].append(issue)
        elif any(tag in key for tag in ['unused-import', 'unused-variable', 'undefined-variable', 'broad-except', 'too-many-branches', 'too-many-statements', 'too-many-locals', 'unused-argument', 'redefined-outer-name']):
            categories['Logic'].append(issue)
        else:
            categories['Other'].append(issue)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


class ScoreCalculator:
    """Calculate code quality score"""
    
    @staticmethod
    def calculate_score(analysis):
        """Calculate overall score (0-100) with stricter criteria"""
        
        metrics = analysis.get('metrics', {})
        
        # Style Score (0-60) using explicit buckets - highest weight
        style_issues_count = len(analysis['style_issues'])
        if style_issues_count == 0:
            style_score = 60
        elif 1 <= style_issues_count <= 3:
            style_score = 45
        elif 4 <= style_issues_count <= 6:
            style_score = 30
        else:
            style_score = 15
        
        # Complexity Score (0-20) using explicit buckets - lower weight
        complexity = analysis['complexity']
        if complexity <= 2:
            complexity_score = 20
        elif complexity <= 4:
            complexity_score = 17
        elif complexity <= 7:
            complexity_score = 13
        elif complexity <= 10:
            complexity_score = 7
        else:
            complexity_score = 0
        
        # Maintainability Score (0-20) using explicit buckets - lower weight
        mi = analysis['maintainability']
        if mi >= 85:
            maintainability_score = 20
        elif mi >= 70:
            maintainability_score = 17
        elif mi >= 50:
            maintainability_score = 13
        elif mi >= 25:
            maintainability_score = 7
        else:
            maintainability_score = 0
        
        # Total score is the sum of the three weighted metrics
        total_score = style_score + complexity_score + maintainability_score

        # Provide percentages for UI bars (0-100)
        style_pct = int(round((style_score / 60) * 100)) if 60 else 0
        complexity_pct = int(round((complexity_score / 20) * 100)) if 20 else 0
        maintainability_pct = int(round((maintainability_score / 20) * 100)) if 20 else 0

        # Estimated technical debt (hours) from maintainability index.
        # High maintainability gives lower debt and vice versa.
        debt_hours = round(max(0.0, (100.0 - mi) * 0.15), 1)

        return {
            'style_score': style_score,
            'complexity_score': complexity_score,
            'maintainability_score': maintainability_score,
            'style_pct': style_pct,
            'complexity_pct': complexity_pct,
            'maintainability_pct': maintainability_pct,
            'total_score': total_score,
            'technical_debt_hours': debt_hours
        }
    
    @staticmethod
    def get_suggestions(analysis, scores):
        """Generate detailed and strict improvement suggestions"""
        suggestions = []
        metrics = analysis.get('metrics', {})
        
        # Critical issues first
        if len(analysis['syntax_issues']) > 0:
            suggestions.append("CRITICAL: Fix all syntax errors immediately. Code cannot run with syntax errors.")
        
        # Style issues
        style_count = len(analysis['style_issues'])
        if style_count > 10:
            suggestions.append("SEVERE: Code has excessive style violations. Run 'pylint' and fix all issues.")
        elif style_count > 5:
            suggestions.append("HIGH PRIORITY: Multiple style issues detected. Focus on PEP 8 compliance.")
        elif style_count > 0:
            suggestions.append("Address remaining style issues for better code quality.")

        # Specific lint hints
        if any('missing-docstring' in issue for issue in analysis['style_issues']):
            suggestions.append("Add docstrings for modules, classes, and functions to improve readability and maintenance.")
        if any('invalid-name' in issue or 'invalid-name' in issue.lower() for issue in analysis['style_issues']):
            suggestions.append("Use clear, descriptive variable/function names (snake_case) for better readability.")
        if any('unused-import' in issue for issue in analysis['style_issues']):
            suggestions.append("Remove unused imports to keep the code clean and reduce cognitive load.")
        if any('unused-variable' in issue for issue in analysis['style_issues']):
            suggestions.append("Remove or use unused variables; they often signal dead code or logic errors.")

        # Complexity issues
        complexity = analysis['complexity']
        if complexity > 15:
            suggestions.append("CRITICAL: Extremely high complexity. Refactor into multiple smaller functions immediately.")
        elif complexity > 10:
            suggestions.append("HIGH: Break down complex functions. Aim for complexity < 10 per function.")
        elif complexity > 7:
            suggestions.append("MODERATE: Consider simplifying logic to reduce complexity.")

        # Maintainability issues
        mi = analysis['maintainability']
        if mi < 30:
            suggestions.append("CRITICAL: Code is very hard to maintain. Major refactoring required.")
        elif mi < 50:
            suggestions.append("HIGH: Add comprehensive docstrings, comments, and simplify structure.")
        elif mi < 70:
            suggestions.append("MODERATE: Improve documentation and code organization.")

        # Code metrics suggestions
        if metrics.get('total_lines', 0) > 500:
            suggestions.append("File too long. Split into multiple modules for better organization.")
        if metrics.get('functions', 0) > 20:
            suggestions.append("Too many functions in one file. Consider splitting into classes or modules.")
        if metrics.get('code_lines', 0) / max(metrics.get('total_lines', 1), 1) < 0.3:
            suggestions.append("Too many comments/empty lines. Focus on actual code implementation.")
        if metrics.get('functions', 0) == 0:
            suggestions.append("No functions defined. Consider organizing code into functions.")

        # Positive feedback for good code
        if len(analysis['syntax_issues']) == 0 and style_count == 0 and complexity <= 3 and mi >= 85:
            suggestions.append("EXCELLENT: Code meets high quality standards. Keep up the good work!")
        elif scores['total_score'] >= 80:
            suggestions.append("GOOD: Code quality is solid. Minor improvements possible.")

        return suggestions

# Routes
@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if not db:
        return jsonify({'error': 'Database not available. Please configure MySQL.'}), 503
    
    if request.method == 'POST':
        # Support both JSON and form-encoded requests
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            data = request.form.to_dict()

        name = data.get('name') or data.get('full_name')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password') or data.get('confirmPassword')
        
        if not all([name, email, password, confirm_password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        try:
            result = db.register_user(name, email, password)
            if result:
                # Auto-login and redirect for regular form submissions
                if request.is_json:
                    return jsonify({'success': True, 'message': 'Registration successful!'}), 200
                user = db.get_user_by_email(email)
                if user:
                    session['user_id'] = user[0]
                    session['user_name'] = user[1]
                return redirect(url_for('dashboard'))
            else:
                if request.is_json:
                    return jsonify({'error': 'Email already exists or registration failed'}), 400
                return render_template('register.html', error='Email already exists or registration failed')
        except Exception as e:
            if request.is_json:
                return jsonify({'error': f'Registration error: {str(e)}'}), 500
            return render_template('register.html', error=f'Registration error: {str(e)}')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if not db:
        return jsonify({'error': 'Database not available. Please configure MySQL.'}), 503
    
    if request.method == 'POST':
        # Support both JSON and form-encoded requests
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            data = request.form.to_dict()

        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        try:
            user = db.get_user_by_email(email)
            if user and db.verify_password(user[3], password):
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                if request.is_json:
                    return jsonify({'success': True}), 200
                return redirect(url_for('dashboard'))
            else:
                error_msg = 'Invalid email or password'
                if request.is_json:
                    return jsonify({'error': error_msg}), 401
                return render_template('login.html', error=error_msg)
        except Exception as e:
            error_msg = f'Login error: {str(e)}'
            if request.is_json:
                return jsonify({'error': error_msg}), 500
            return render_template('login.html', error=error_msg)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        user_id = session.get('user_id')
        user = db.get_user_by_id(user_id)
        files = db.get_user_files(user_id)
        user_plan = user[3] if user and len(user) > 3 else 'free'
        return render_template('dashboard.html', user=user, files=files, user_plan=user_plan)
        
    except Exception as e:
        return jsonify({'error': f'Dashboard error: {str(e)}'}), 500   
    

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload Python file"""
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Unknown File Type'}), 400
        
        user_id=session.get('user_id')
        user=db.get_user_by_id(user_id)

        try:
            user_plan=user[3]
        except Exception:
            user_plan='free'


        language = get_language(file.filename)

        #check access
        if not is_allowed(user_plan, language):
            return jsonify({'error': f'Your current plan does not support analyzing {language.upper()} files. Please upgrade your plan.','current_plan':user_plan,'required_plan':'upgrade','upgrade_required':True}), 403
        
        try:
            # Save file
            user_id = session.get('user_id')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Record in database
            file_id = db.upload_file(user_id, filename)
            
            if file_id:
                return jsonify({'success': True, 'file_id': file_id, 'filename': file.filename}), 200
            else:
                return jsonify({'error': 'Failed to save file record'}), 400
        except Exception as e:
            return jsonify({'error': f'Upload error: {str(e)}'}), 500
    
    return render_template('upload.html')

@app.route('/analyze/<int:file_id>')
@login_required
def analyze(file_id):
    """Analyze uploaded file"""
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        user_id = session.get('user_id')
        file_info = db.get_file_by_id(file_id)
        
        if not file_info or file_info[1] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_info[2])
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Perform analysis
        analysis = CodeAnalyzer.analyze(filepath)
        scores = ScoreCalculator.calculate_score(analysis)
        suggestions = ScoreCalculator.get_suggestions(analysis, scores)

        issues = analysis['syntax_issues'] + analysis['style_issues']
        categorized_issues = categorize_issues(issues)

        # Save results to database
        issues_json = json.dumps(issues)
        suggestions_json = json.dumps(suggestions)

        db.save_analysis_result(
            file_id,
            scores['total_score'],
            analysis['complexity'],
            analysis['maintainability'],
            issues_json,
            suggestions_json
        )

        trend_percent = max(min(int(scores['total_score'] - 70), 20), -20)
        critical_paths = max(1, int(round(analysis['complexity'] * 1.1)))

        analyzed_path = os.path.abspath(filepath)
        return render_template('results.html',
                             file_id=file_id,
                             filename=file_info[2],
                             original_filename=file_info[2],
                             analyzed_path=analyzed_path,
                             score=scores['total_score'],
                             complexity=analysis['complexity'],
                             maintainability=analysis['maintainability'],
                             technical_debt_hours=scores.get('technical_debt_hours', 0),
                             trend_percent=trend_percent,
                             critical_paths=critical_paths,
                             issues=issues,
                             categorized_issues=categorized_issues,
                             suggestions=suggestions,
                             scores=scores)
    except Exception as e:
        return render_template('results.html',
                             file_id=file_id,
                             filename="Error",
                             score=0,
                             complexity=0,
                             maintainability=0,
                             trend_percent=0,
                             critical_paths=0,
                             issues=[f'Error during analysis: {str(e)}'],
                             suggestions=[],
                             scores={
                                 'style_score': 0,
                                 'complexity_score': 0,
                                 'maintainability_score': 0,
                                 'style_pct': 0,
                                 'complexity_pct': 0,
                                 'maintainability_pct': 0,
                                 'total_score': 0
                             })

@app.route('/results/<int:file_id>')
@login_required
def view_results(file_id):
    """View analysis results"""
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        user_id = session.get('user_id')
        file_info = db.get_file_by_id(file_id)
        
        if not file_info or file_info[1] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        analysis_result = db.get_analysis_result(file_id)
        
        if not analysis_result:
            return redirect(url_for('upload'))
        
        # Parse stored data as fallback
        try:
            stored_issues = json.loads(analysis_result[5]) if analysis_result[5] else []
            stored_suggestions = json.loads(analysis_result[6]) if analysis_result[6] else []
        except (json.JSONDecodeError, TypeError):
            stored_issues = []
            stored_suggestions = []

        # Run a fresh analysis to get current data (ensures consistency)
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_info[2])
            latest_analysis = CodeAnalyzer.analyze(filepath)
            scores = ScoreCalculator.calculate_score(latest_analysis)
            suggestions = ScoreCalculator.get_suggestions(latest_analysis, scores)
            issues = latest_analysis['syntax_issues'] + latest_analysis['style_issues']
            categorized_issues = categorize_issues(issues)
            
            # Use fresh data
            score = scores['total_score']
            complexity = latest_analysis['complexity']
            maintainability = latest_analysis['maintainability']
            
        except Exception as e:
            # Fall back to stored data if fresh analysis fails
            print(f"Fresh analysis failed: {e}")
            try:
                issues = json.loads(analysis_result[5]) if analysis_result[5] else []
                suggestions = json.loads(analysis_result[6]) if analysis_result[6] else []
            except (json.JSONDecodeError, TypeError):
                issues = []
                suggestions = []
            
            categorized_issues = categorize_issues(issues)
            scores = {
                'style_score': 0,
                'complexity_score': 0,
                'maintainability_score': 0,
                'style_pct': 0,
                'complexity_pct': 0,
                'maintainability_pct': 0,
                'total_score': analysis_result[2] if analysis_result[2] else 0
            }
            score = analysis_result[2] if analysis_result[2] else 0
            complexity = float(analysis_result[3]) if analysis_result[3] else 0
            maintainability = float(analysis_result[4]) if analysis_result[4] else 0

        # Estimate trend and critical-path count
        trend_percent = max(min(int(scores['total_score'] - 70), 20), -20)
        critical_paths = max(1, int(round(complexity * 1.1)))

        return render_template('results.html',
                             file_id=file_id,
                             filename=file_info[2],
                             score=score,
                             complexity=complexity,
                             maintainability=maintainability,
                             technical_debt_hours=scores.get('technical_debt_hours', 0),
                             analyzed_path=os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], file_info[2])),
                             trend_percent=trend_percent,
                             critical_paths=critical_paths,
                             issues=issues,
                             categorized_issues=categorized_issues,
                             refresh_message=None,
                             suggestions=suggestions,
                             scores=scores)
        
        return render_template('results.html',
                             file_id=file_id,
                             filename=file_info[2],
                             score=analysis_result[2] if analysis_result[2] else 0,
                             complexity=float(analysis_result[3]) if analysis_result[3] else 0,
                             maintainability=float(analysis_result[4]) if analysis_result[4] else 0,
                             issues=issues,
                             suggestions=suggestions,
                             scores=scores)
    except Exception as e:
        return jsonify({'error': f'Error viewing results: {str(e)}'}), 500

@app.route('/api/analysis/<int:file_id>')
@login_required
def get_analysis_data(file_id):
    """Get analysis data as JSON"""
    user_id = session.get('user_id')
    file_info = db.get_file_by_id(file_id)
    
    if not file_info or file_info[1] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    analysis_result = db.get_analysis_result(file_id)
    
    if not analysis_result:
        return jsonify({'error': 'No analysis found'}), 404
    
    return jsonify({
        'score': analysis_result[2],
        'complexity': float(analysis_result[3]),
        'maintainability': float(analysis_result[4]),
        'issues': json.loads(analysis_result[5]),
        'suggestions': json.loads(analysis_result[6])
    })

@app.route('/generate-pdf/<int:file_id>')
@login_required
def generate_pdf(file_id):
    """Generate PDF report"""
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        user_id = session.get('user_id')
        file_info = db.get_file_by_id(file_id)
        
        if not file_info or file_info[1] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        analysis_result = db.get_analysis_result(file_id)
        
        if not analysis_result:
            return jsonify({'error': 'No analysis found'}), 404

        # Re-run analysis to apply current scoring rules and capture full issue list
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_info[2])
        latest_analysis = CodeAnalyzer.analyze(filepath)
        latest_scores = ScoreCalculator.calculate_score(latest_analysis)
        latest_suggestions = ScoreCalculator.get_suggestions(latest_analysis, latest_scores)
        latest_issues = latest_analysis['syntax_issues'] + latest_analysis['style_issues']
        
        # Create PDF document
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        elements.append(Paragraph("Code Review Report", title_style))
        elements.append(Spacer(1, 0.3))
        
        # File info
        file_table_data = [
            ['Filename:', file_info[2]],
            ['Analysis Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        file_table = Table(file_table_data, colWidths=[150, 350])
        file_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(file_table)
        elements.append(Spacer(1, 0.5))
        
        # Scores
        elements.append(Paragraph("Quality Scores", heading_style))
        scores_data = [
            ['Metric', 'Value'],
            ['Overall Score', f"{latest_scores['total_score']}/100"],
            ['Style', f"{latest_scores['style_score']}/40"],
            ['Complexity', f"{latest_scores['complexity_score']}/30"],
            ['Maintainability', f"{latest_scores['maintainability_score']}/30"]
        ]
        scores_table = Table(scores_data, colWidths=[200, 300])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(scores_table)
        elements.append(Spacer(1, 0.5))
        
        # Issues
        elements.append(Paragraph("Issues Found", heading_style))
        if latest_issues:
            for i, issue in enumerate(latest_issues[:10], 1):
                elements.append(Paragraph(f"{i}. {issue}", styles['Normal']))
        else:
            elements.append(Paragraph("No issues found!", styles['Normal']))
        elements.append(Spacer(1, 0.5))
        
        # Suggestions
        elements.append(Paragraph("Suggestions for Improvement", heading_style))
        for i, suggestion in enumerate(latest_suggestions[:5], 1):
            elements.append(Paragraph(f"{i}. {suggestion}", styles['Normal']))
        
        doc.build(elements)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue(), 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename=code_review_{file_id}.pdf'
        }
    except Exception as e:
        return jsonify({'error': f'PDF generation error: {str(e)}'}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

@app.before_request
def check_database():
    """Check database connection"""
    if not db and request.path not in ['/', '/login', '/register', '/static/<path:filename>']:
        if request.path.startswith('/api'):
            return jsonify({'error': 'Database not available'}), 503
        
@app.route('/about')
def about():
    """About and Learn section"""
    return render_template('about.html')

@app.route('/settings', methods=['GET','POST'])
@login_required
def settings():
    """User settings page"""
    if not db:
        return jsonify({'error': 'Database not available'}), 503

    user_id = session.get('user_id')
    user = db.get_user_by_id(user_id)
    error = None
    success = None

    if request.method == 'POST':
        data = request.form.to_dict()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        bio = data.get('bio')

        if not name or not email:
            error = 'Name and email are required.'
        elif password and password != confirm_password:
            error = 'Passwords do not match.'
        elif password and len(password) < 6:
            error = 'Password must be at least 6 characters.'
        else:
            updated = db.update_user(user_id, name, email, password if password else None, bio=bio)
            if updated:
                success = 'Profile updated successfully.'
                user = db.get_user_by_id(user_id)  # refresh user object
            else:
                error = 'Failed to update profile. Email may already be in use.'

    return render_template('settings.html', user=user, error=error, success=success)

@app.route('/about.html')
def about_html():
    """Legacy route for direct file access."""
    return redirect(url_for('about'))


if __name__ == '__main__':
    print("="*60)
    print("CodeInsight - Starting Application")
    print("="*60)
    print("Server: http://localhost:5000")
    print("Database: code_reviewer on localhost")
    if not db:
        print("\n⚠ WARNING: Database not connected!")
        print("Please configure MySQL:")
        print("1. Install MySQL Server")
        print("2. Run: mysql -u root -p < database.sql")
        print("3. Update database credentials in app.py (lines 32-37)")
    print("="*60)
    print()
    app.run(debug=True, host='localhost', port=5000)



