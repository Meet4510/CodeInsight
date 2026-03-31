from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
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

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
except Exception:
    cc_visit = None
    mi_visit = None

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
    """Analyze code for syntax, style, and complexity"""
    
    @staticmethod
    def get_file_language(filepath):
        """Detect language from file extension"""
        ext = filepath.rsplit('.', 1)[-1].lower()
        lang_map = {'py': 'python', 'java': 'java', 'js': 'javascript', 'css': 'css', 'html': 'html'}
        return lang_map.get(ext, 'unknown')
    
    @staticmethod
    def check_java_syntax(filepath):
        """Basic Java syntax checking"""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            lines = code.split('\n')
            
            # Check for common Java syntax issues
            brace_count = 0
            paren_count = 0
            bracket_count = 0
            in_string = False
            escape_next = False
            string_char = None
            
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip comments
                if stripped.startswith('//'):
                    continue
                
                # Check for unmatched braces
                for i, char in enumerate(line):
                    if escape_next:
                        escape_next = False
                        continue
                    if char == '\\':
                        escape_next = True
                        continue
                    if char in ('"', "'") and not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char and in_string:
                        in_string = False
                    elif not in_string:
                        if char == '{': brace_count += 1
                        elif char == '}': brace_count -= 1
                        elif char == '(': paren_count += 1
                        elif char == ')': paren_count -= 1
                        elif char == '[': bracket_count += 1
                        elif char == ']': bracket_count -= 1
                
                # Common Java issues
                if 'public class' in line and '{' not in line:
                    issues.append(f"Line {line_no}: Missing opening brace after class declaration")
                if 'public static void main' in line and 'String[] args' not in line:
                    issues.append(f"Line {line_no}: main method should have String[] args parameter")
                if re.search(r'System\.out\.println\s*\([^)]*\);', line):
                    pass  # Valid print statement
                if re.search(r'\)\s*\{?\s*$', line) and 'import' not in line and '{' not in line:
                    if 'public' in line or 'private' in line or 'protected' in line:
                        issues.append(f"Line {line_no}: Missing opening brace after method declaration")
            
            if brace_count != 0:
                issues.append(f"Unmatched braces: {abs(brace_count)} missing closing brace(s)")
            if paren_count != 0:
                issues.append(f"Unmatched parentheses: {abs(paren_count)} missing")
            if bracket_count != 0:
                issues.append(f"Unmatched brackets: {abs(bracket_count)} missing")
            
            return issues
        except Exception as e:
            return [f"Java syntax check error: {str(e)}"]
    
    @staticmethod
    def get_java_metrics(filepath):
        """Get comprehensive Java code metrics"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            lines = code.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('//')
                            and not line.strip().startswith('/*') and '*/'
                            not in line])
            
            # Count methods, classes, and interfaces
            methods = len(re.findall(r'(public|private|protected|static)*\s+(void|int|String|boolean|double|float|long|.*?)\s+\w+\s*\([^)]*\)\s*\{', code))
            classes = len(re.findall(r'(public|private)?\s*class\s+\w+', code))
            interfaces = len(re.findall(r'(public|private)?\s*interface\s+\w+', code))
            
            # Count nested blocks (indicator of complexity)
            max_nesting = 0
            current_nesting = 0
            for char in code:
                if char == '{':
                    current_nesting += 1
                    max_nesting = max(max_nesting, current_nesting)
                elif char == '}':
                    current_nesting = max(0, current_nesting - 1)
            
            return {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'functions': methods,
                'classes': classes,
                'interfaces': interfaces,
                'max_nesting': max_nesting
            }
        except Exception as e:
            return {'total_lines': 0, 'code_lines': 0, 'functions': 0, 'classes': 0, 'interfaces': 0, 'max_nesting': 0, 'error': str(e)}
    
    @staticmethod
    def calculate_java_complexity(filepath):
        """Calculate cyclomatic complexity for Java code"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            # Count decision points
            decision_points = 0
            decision_keywords = ['if', 'else if', 'else', 'for', 'while', 'switch', 'case', 'catch', '?', ':']
            
            for keyword in decision_keywords:
                # Use word boundaries to avoid matching partial words
                if keyword in ['?', ':']:
                    matches = len(re.findall(re.escape(keyword), code))
                else:
                    matches = len(re.findall(r'\b' + keyword + r'\b', code))
                decision_points += matches
            
            # Method/lambda complexity
            methods = len(re.findall(r'\b(public|private|protected|static)*\s+(void|int|String|boolean|\w+)\s+\w+\s*\([^)]*\)\s*\{', code))
            lambdas = len(re.findall(r'->', code))
            
            # Base complexity: 1 + (decision_points / method_count)
            if methods > 0:
                avg_complexity = 1 + (decision_points / methods) * 0.15
            else:
                avg_complexity = 1 + (decision_points * 0.05)

            # Penalize high decision density (many branches per LOC)
            metrics = CodeAnalyzer.get_java_metrics(filepath)
            code_lines = max(1, metrics.get('code_lines', 1))
            decision_density = (decision_points / code_lines) * 100
            if decision_density > 12:
                avg_complexity += 2.5
            elif decision_density > 8:
                avg_complexity += 1.5
            elif decision_density > 5:
                avg_complexity += 0.8
            
            # Adjust for nesting depth (penalize deep nesting)
            max_nesting = metrics.get('max_nesting', 0)
            if max_nesting > 10:
                avg_complexity += (max_nesting - 10) * 0.7 + 2.0
            elif max_nesting > 5:
                avg_complexity += (max_nesting - 5) * 0.45
            
            # Add lambda complexity
            avg_complexity += lambdas * 0.2
            
            return min(round(avg_complexity, 2), 10.0)  # Cap at 10, round to 2 decimals
        except Exception as e:
            return 1.0
    
    @staticmethod
    def calculate_java_maintainability(filepath):
        """Calculate maintainability index for Java code"""
        try:
            metrics = CodeAnalyzer.get_java_metrics(filepath)
            complexity = CodeAnalyzer.calculate_java_complexity(filepath)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            lines_text = code.split('\n')
            
            lines = metrics.get('code_lines', 1)
            methods = metrics.get('functions', 0)
            classes = metrics.get('classes', 0)
            interfaces = metrics.get('interfaces', 0)
            
            # Improved Maintainability Index (0-100) based on code quality indicators
            # This should reward clean, well-structured code and penalize problematic patterns
            
            # Start with good base score
            mi = 85
            
            # PENALIZE: Very deep nesting (sign of complex control flow)
            max_nesting = metrics.get('max_nesting', 0)
            if max_nesting > 10:
                mi -= 25  # Severe penalty for very deep nesting
            elif max_nesting > 7:
                mi -= 15  # Major penalty for deeply nested code
            elif max_nesting > 5:
                mi -= 8   # Medium penalty
            elif max_nesting > 3:
                mi -= 3   # Minor penalty
            else:
                mi += 5   # Bonus for shallow, readable nesting
            
            # PENALIZE: Very high complexity indicates too many decision points
            # A score of 5+ is concerning, 10+ is very bad
            if complexity > 10:
                mi -= 20
            elif complexity > 8:
                mi -= 12
            elif complexity > 6:
                mi -= 6
            elif complexity <= 2:
                mi += 10  # Bonus for simple, understandable code
            
            # PENALIZE: Extremely long methods (>150 LOC average per method)
            if methods > 0:
                avg_method_lines = lines / methods
                if avg_method_lines > 150:
                    mi -= 15
                elif avg_method_lines > 100:
                    mi -= 8
                elif avg_method_lines < 20 and complexity <= 3 and max_nesting <= 4:
                    mi += 5  # Bonus for well-refactored, small methods
            
            # REWARD: Multiple classes indicate good separation of concerns
            if classes >= 3:
                mi += 5
            if interfaces > 0:
                mi += 5
            
            # Reasonable LOC is fine - modern code can be 500+ lines
            # Only penalize if EXTREMELY large (>1000 LOC)
            if lines > 1000:
                mi -= 10
            elif lines > 500 and complexity > 6:
                mi -= 5  # Only penalize large files with high complexity

            # Penalize risky patterns found in source
            raw_type_count = 0
            for src_line in lines_text:
                s = src_line.strip()
                if s.startswith('import ') or s.startswith('package '):
                    continue
                if re.search(r'(ArrayList|HashMap|HashSet|LinkedList|TreeMap|Vector|Hashtable)\s+[A-Za-z_]', s) and '<' not in s:
                    raw_type_count += 1

            generic_catch_count = len(re.findall(r'catch\s*\(\s*Exception\s+\w+\s*\)', code))
            hardcoded_secret_count = len(re.findall(r'(password|passwd|pwd|secret|api[_-]?key|token)\s*=\s*["\']', code, re.IGNORECASE))
            public_static_mutable_count = len(re.findall(r'public\s+static\s+(?!final)\w+\s+\w+\s*[=;]', code))
            dead_code_count = len(re.findall(r'if\s*\(\s*false\s*\)', code))
            sql_concat_count = len(re.findall(r'SELECT\s+.*\+|INSERT\s+.*\+|UPDATE\s+.*\+|DELETE\s+.*\+', code, re.IGNORECASE))

            risk_penalty = (
                raw_type_count * 2
                + generic_catch_count * 2
                + hardcoded_secret_count * 5
                + public_static_mutable_count * 3
                + dead_code_count * 3
                + sql_concat_count * 6
            )
            mi -= min(35, risk_penalty)
            
            # Clamp between 0 and 100
            return max(0, min(100, mi))
        except Exception as e:
            return 50.0
    
    @staticmethod
    def check_java_style(filepath):
        """Comprehensive Java code style and conventions checking"""
        issues = []
        errors = []  # Critical issues like missing JavaDoc, raw types, hardcoded credentials
        warnings = []  # Important issues like string concat in loops, too many params, deep nesting
        infos = []  # Minor style issues
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            lines = code.split('\n')
            
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip empty lines and pure comment lines
                if not stripped or stripped.startswith('//') or stripped.startswith('import ') or stripped.startswith('package '):
                    continue
                
                # **CRITICAL ERRORS**
                # Check for missing JavaDoc on public class
                if 'public class' in line and line_no > 1:
                    # Look back up to 10 lines for JavaDoc
                    has_javadoc = False
                    for i in range(max(0, line_no - 10), line_no - 1):
                        if '/**' in lines[i] or '@' in lines[i]:
                            has_javadoc = True
                            break
                    if not has_javadoc:
                        errors.append(f"[ERROR] Line {line_no}: Public class missing JavaDoc")
                
                # Check for public methods without JavaDoc (skip trivial/override methods)
                method_decl = re.search(
                    r'public\s+(?:static\s+)?(?:final\s+)?[\w<>\[\], ?]+\s+(\w+)\s*\(',
                    line
                )
                if method_decl:
                    method_name = method_decl.group(1)

                    # Exempt common trivial/standard methods from mandatory JavaDoc.
                    # This avoids over-penalizing clean code with concise getters/overrides.
                    trivial_method = (
                        method_name == 'main'
                        or method_name.startswith('get')
                        or method_name.startswith('set')
                        or method_name.startswith('is')
                        or method_name in ['toString', 'equals', 'hashCode', 'compareTo']
                    )

                    # Skip if method is likely constructor-like naming pattern.
                    if trivial_method:
                        pass
                    else:
                        # Skip if preceded by @Override or other annotation
                        has_annotation = any('@' in lines[i].strip() for i in range(max(0, line_no - 3), line_no - 1))

                        # Skip ultra-short single-line methods declared inline.
                        inline_one_liner = '{' in line and '}' in line

                        if not has_annotation and not inline_one_liner:
                            has_javadoc = False
                            for i in range(max(0, line_no - 10), line_no - 1):
                                if '/**' in lines[i]:
                                    has_javadoc = True
                                    break
                            if not has_javadoc:
                                errors.append(f"[ERROR] Line {line_no}: Public method missing JavaDoc")
                
                # Check for raw types (ArrayList, HashMap, etc without generics)
                if re.search(r'(ArrayList|HashMap|HashSet|LinkedList|TreeMap|Vector|Hashtable)\s*[=;{(]', line):
                    if '<' not in line or '>' not in line:
                        errors.append(f"[ERROR] Line {line_no}: Raw type - use generics")
                
                # Check for public mutable static fields
                if re.search(r'public\s+static\s+(?!final)\w+\s+\w+\s*[=;]', line):
                    errors.append(f"[ERROR] Line {line_no}: Public static field should be 'final'")
                
                # Check for hardcoded credentials/passwords
                if re.search(r'(password|passwd|pwd|secret|credential|api[_-]?key|token)\s*=\s*["\']', line, re.IGNORECASE):
                    errors.append(f"[ERROR] Line {line_no}: Hardcoded credential detected")
                
                # Check for suspicious hardcoded strings
                if re.search(r'(root|admin|test123|password|pass123)', line, re.IGNORECASE) and '=' in line and 'final' not in line:
                    errors.append(f"[ERROR] Line {line_no}: Suspicious hardcoded value")
                
                # **IMPORTANT WARNINGS**
                # Check for too many parameters
                params_match = re.search(r'\(([^)]*)\)', line)
                if params_match and 'public' in line:
                    params = params_match.group(1)
                    param_count = len([p for p in params.split(',') if p.strip()]) if params.strip() else 0
                    if param_count > 5:
                        warnings.append(f"[WARNING] Line {line_no}: Too many parameters ({param_count})")
                
                # Check for string concatenation in loops
                if '+=' in line and (any(lw in'\n'.join(lines[max(0, line_no-6):line_no]) for lw in ['for (', 'while ('])):
                    if '"' in line or "'" in line:
                        warnings.append(f"[WARNING] Line {line_no}: String concatenation in loop")
                
                # Check for catching generic Exception
                if re.search(r'catch\s*\(\s*Exception\s+\w+', line):
                    warnings.append(f"[WARNING] Line {line_no}: Catching generic Exception")
                
                # Check for dead code
                if 'if (false)' in line or 'if(false)' in line:
                    warnings.append(f"[WARNING] Line {line_no}: Dead code block")
                
                # Check for SQL injection
                if any(sql in line for sql in ['executeQuery', 'execute(']):
                    if '+' in line:
                        warnings.append(f"[WARNING] Line {line_no}: Potential SQL injection")
                
                # Check line length
                if len(line) > 120:
                    warnings.append(f"[WARNING] Line {line_no}: Line exceeds 120 characters")
                
                # **MINOR STYLE ISSUES**
                # Check for magic numbers (only 2+ digit assignments)
                if '=' in line and not stripped.startswith('for'):
                    assignment_match = re.search(r'=\s*([0-9]{2,})\s*[;,)]', line)
                    if assignment_match:
                        number = assignment_match.group(1)
                        common = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '16', 
                                '24', '32', '60', '100', '256', '512', '1000', '1024', '10000', '100000', 
                                '360', '180', '255', '127', '128', '65535']
                        if number not in common:
                            infos.append(f"[INFO] Line {line_no}: Magic number '{number}'")

            
            # Combine and sort by severity (errors first, then warnings, then infos)
            # Strict limits prevent over-flagging good code
            all_issues = errors[:12] + warnings[:12] + infos[:6]  # Capture enough issues to score severe files accurately
            
            return all_issues if all_issues else ["[INFO] Code meets quality standards"]
        
        except Exception as e:
            return [f"[ERROR] Java style check error: {str(e)}"]
    
    @staticmethod
    def check_syntax(filepath):
        """Check for syntax errors using AST"""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            ast.parse(code)
            return issues
        except SyntaxError as e:
            issues.append(f"Syntax Error: {e.msg} (Line {e.lineno})")
            return issues
        except UnicodeDecodeError:
            issues.append("File encoding error: Unable to read file as UTF-8")
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
                timeout=60
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
        except subprocess.TimeoutExpired:
            return ["Pylint analysis timed out - file may be too large or complex"]
        except Exception as e:
            return [f"Pylint check failed: {str(e)}"]
    
    @staticmethod
    def calculate_complexity(filepath):
        """Calculate cyclomatic complexity using Radon"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            # Prefer Radon's Python API for stable parsing.
            if cc_visit is not None:
                blocks = cc_visit(code)
                if not blocks:
                    # Script files may have no function blocks; estimate from decision points.
                    decision_points = len(re.findall(r'\b(if|elif|for|while|except|and|or|try|with|match|case)\b', code))
                    return min(10.0, round(1.0 + (decision_points * 0.9), 2))

                avg_complexity = sum(block.complexity for block in blocks) / len(blocks)
                max_complexity = max(block.complexity for block in blocks)
                blended = (avg_complexity * 0.7) + (max_complexity * 0.3)
                return min(10.0, round(max(1.0, blended), 2))

            # Fallback: parse CLI JSON output.
            result = subprocess.run(
                ['radon', 'cc', filepath, '-j'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and (result.stdout or '').strip():
                payload = json.loads(result.stdout)
                entries = payload.get(filepath) or payload.get(os.path.abspath(filepath)) or []
                if entries:
                    avg_complexity = sum(item.get('complexity', 1.0) for item in entries) / len(entries)
                    max_complexity = max(item.get('complexity', 1.0) for item in entries)
                    blended = (avg_complexity * 0.7) + (max_complexity * 0.3)
                    return min(10.0, round(max(1.0, blended), 2))
                return 1.0

            # If analysis fails, treat as high complexity rather than good complexity.
            return 10.0
        except Exception as e:
            return 10.0
    
    @staticmethod
    def calculate_maintainability(filepath):
        """Calculate maintainability index using Radon"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            # Prefer Radon's Python API for stable numeric MI.
            if mi_visit is not None:
                mi = float(mi_visit(code, multi=True))
                return round(max(0.0, min(100.0, mi)), 2)

            # Fallback: parse CLI JSON output.
            result = subprocess.run(
                ['radon', 'mi', filepath, '-j'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and (result.stdout or '').strip():
                payload = json.loads(result.stdout)
                record = payload.get(filepath) or payload.get(os.path.abspath(filepath))
                if isinstance(record, dict):
                    mi = float(record.get('mi', 20.0))
                    return round(max(0.0, min(100.0, mi)), 2)
                if isinstance(record, (int, float)):
                    return round(max(0.0, min(100.0, float(record))), 2)

            # If analysis fails, avoid optimistic maintainability values.
            return 20.0
        except Exception as e:
            return 20.0
    
    @staticmethod
    def get_code_metrics(filepath):
        """Get basic code metrics"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
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
        except UnicodeDecodeError:
            return {'total_lines': 0, 'code_lines': 0, 'functions': 0, 'classes': 0, 'error': 'Encoding error'}
        except Exception as e:
            return {'total_lines': 0, 'code_lines': 0, 'functions': 0, 'classes': 0, 'error': str(e)}
    
    @staticmethod
    def analyze(filepath):
        """Complete code analysis with language detection"""
        language = CodeAnalyzer.get_file_language(filepath)
        
        if language == 'java':
            # Java analysis with calculated metrics
            analysis = {
                'syntax_issues': CodeAnalyzer.check_java_syntax(filepath),
                'style_issues': CodeAnalyzer.check_java_style(filepath),
                'complexity': CodeAnalyzer.calculate_java_complexity(filepath),
                'maintainability': CodeAnalyzer.calculate_java_maintainability(filepath),
                'metrics': CodeAnalyzer.get_java_metrics(filepath)
            }
        else:
            # Python analysis (default)
            analysis = {
                'syntax_issues': CodeAnalyzer.check_syntax(filepath),
                'style_issues': CodeAnalyzer.check_code_style(filepath),
                'complexity': CodeAnalyzer.calculate_complexity(filepath),
                'maintainability': CodeAnalyzer.calculate_maintainability(filepath),
                'metrics': CodeAnalyzer.get_code_metrics(filepath)
            }
        
        return analysis

# Scoring Module
def categorize_issues(issues, language='python'):
    """Group issues into categories with language awareness."""
    categories = {
        'Formatting': [],
        'Naming': [],
        'Documentation': [],
        'Logic': [],
        'Other': []
    }

    for issue in issues:
        key = issue.lower()
        if language == 'java':
            if any(tag in key for tag in ['line exceeds', 'magic number', 'multiple statements', 'missing spaces', 'line length']):
                categories['Formatting'].append(issue)
            elif any(tag in key for tag in ['should start with uppercase', 'should use camelcase', 'snake_case', 'naming']):
                categories['Naming'].append(issue)
            elif any(tag in key for tag in ['todo', 'fixme', 'docstring', 'documentation', 'comment']):
                categories['Documentation'].append(issue)
            elif any(tag in key for tag in ['unmatched', 'brace', 'parenthes', 'bracket', 'syntax error', 'invalid']):
                categories['Logic'].append(issue)
            else:
                categories['Other'].append(issue)
        else:
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
        """Calculate overall score (0-100) rewarding clean, well-structured code"""
        
        metrics = analysis.get('metrics', {})
        syntax_issue_count = len(analysis.get('syntax_issues', []))
        
        # Style Score (0-50)
        style_issues = analysis['style_issues']
        has_java_severity_tags = any(issue.startswith('[') for issue in style_issues)

        if has_java_severity_tags:
            # Java path: preserve existing Java severity model.
            error_count = len([i for i in style_issues if '[ERROR]' in i])
            warning_count = len([i for i in style_issues if '[WARNING]' in i])

            if error_count == 0 and warning_count == 0:
                style_score = 50
            elif error_count == 0 and warning_count <= 2:
                style_score = 45
            elif error_count == 0 and warning_count <= 5:
                style_score = 40
            elif error_count <= 2:
                style_score = 30
            elif error_count <= 5:
                style_score = 20
            else:
                style_score = 10
        else:
            # Python path: parse pylint categories (E/F severe, W medium, C/R minor).
            py_error_count = 0
            py_warning_count = 0
            py_minor_count = 0

            for issue in style_issues:
                m = re.search(r':\s*([A-Z])\d{4}:', issue)
                if not m:
                    py_warning_count += 1
                    continue
                code_class = m.group(1)
                if code_class in ['E', 'F']:
                    py_error_count += 1
                elif code_class == 'W':
                    py_warning_count += 1
                else:
                    py_minor_count += 1

            total_style_issues = py_error_count + py_warning_count + py_minor_count
            if py_error_count == 0 and py_warning_count == 0 and py_minor_count == 0:
                style_score = 50
            elif py_error_count == 0 and py_warning_count <= 2 and py_minor_count <= 3:
                style_score = 45
            elif py_error_count == 0 and py_warning_count <= 4 and py_minor_count <= 8:
                style_score = 32
            elif py_error_count <= 1 and py_warning_count <= 6:
                style_score = 22
            elif py_error_count <= 3:
                style_score = 12
            else:
                style_score = 5

            # Volume penalty: many issues should not retain a high style score.
            if total_style_issues >= 15:
                style_score = min(style_score, 10)
            elif total_style_issues >= 10:
                style_score = min(style_score, 20)
        
        # Complexity Score (0-25) - REWARD simple code
        complexity = analysis['complexity']
        if complexity <= 1.5:
            complexity_score = 25  # Excellent: very simple
        elif complexity <= 2.5:
            complexity_score = 23  # Very good: simple code
        elif complexity <= 4:
            complexity_score = 20  # Good: low complexity
        elif complexity <= 6:
            complexity_score = 15  # Fair: moderate complexity
        elif complexity <= 8:
            complexity_score = 10  # Poor: too complex
        elif complexity <= 10:
            complexity_score = 5   # Very poor
        else:
            complexity_score = 0   # Unacceptable
        
        # Maintainability Score (0-25) - REWARD well-structured code  
        mi = analysis['maintainability']
        if mi >= 85:
            maintainability_score = 25  # Excellent: highly maintainable
        elif mi >= 75:
            maintainability_score = 22  # Very good: well-maintained
        elif mi >= 65:
            maintainability_score = 18  # Good: maintainable
        elif mi >= 50:
            maintainability_score = 12  # Fair: somewhat maintainable
        elif mi >= 35:
            maintainability_score = 6   # Poor: hard to maintain
        else:
            maintainability_score = 0   # Very poor

        # Syntax errors should heavily impact overall scoring.
        if syntax_issue_count > 0:
            style_score = min(style_score, 5)
            complexity_score = min(complexity_score, 5)
            maintainability_score = min(maintainability_score, 6)
        
        # Total score: sum of weighted components (50 + 25 + 25 = 100)
        total_score = style_score + complexity_score + maintainability_score

        # Provide percentages for UI bars (0-100)
        style_pct = int(round((style_score / 50) * 100)) if 50 else 0
        complexity_pct = int(round((complexity_score / 25) * 100)) if 25 else 0
        maintainability_pct = int(round((maintainability_score / 25) * 100)) if 25 else 0

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
    def get_suggestions(analysis, scores, language='python'):
        """Generate detailed and strict improvement suggestions with language awareness."""
        suggestions = []
        metrics = analysis.get('metrics', {})
        
        # Critical issues first
        if len(analysis['syntax_issues']) > 0:
            if language == 'java':
                suggestions.append("CRITICAL: Fix all syntax errors immediately. Unmatched braces/parentheses prevent compilation.")
            else:
                suggestions.append("CRITICAL: Fix all syntax errors immediately. Code cannot run with syntax errors.")
        
        # Style issues
        style_count = len(analysis['style_issues'])
        if style_count > 10:
            if language == 'java':
                suggestions.append("SEVERE: Code has excessive style violations. Focus on Java naming conventions (CamelCase) and formatting.")
            else:
                suggestions.append("SEVERE: Code has excessive style violations. Run 'pylint' and fix all issues.")
        elif style_count > 5:
            if language == 'java':
                suggestions.append("HIGH PRIORITY: Multiple style issues detected. Focus on Java code conventions and structure.")
            else:
                suggestions.append("HIGH PRIORITY: Multiple style issues detected. Focus on PEP 8 compliance.")
        elif style_count > 0:
            suggestions.append("Address remaining style issues for better code quality.")

        # Specific hints based on language
        if language == 'java':
            if any('camelcase' in issue.lower() or 'method name' in issue.lower() for issue in analysis['style_issues']):
                suggestions.append("Use camelCase for method and variable names (e.g., calculateTotal, getUserName).")
            if any('uppercase' in issue.lower() or 'class name' in issue.lower() for issue in analysis['style_issues']):
                suggestions.append("Use PascalCase for class names (e.g., DataProcessor, UserManager).")
            if any('magic number' in issue.lower() for issue in analysis['style_issues']):
                suggestions.append("Replace magic numbers with named constants (static final) for clarity and maintainability.")
            if any('line length' in issue.lower() or 'exceeds' in issue.lower() for issue in analysis['style_issues']):
                suggestions.append("Keep line length under 120 characters for better readability.")
        else:
            if any('missing-docstring' in issue for issue in analysis['style_issues']):
                suggestions.append("Add docstrings for modules, classes, and functions to improve readability and maintenance.")
            if any('invalid-name' in issue for issue in analysis['style_issues']):
                suggestions.append("Use clear, descriptive variable/function names (snake_case) for better readability.")
            if any('unused-import' in issue for issue in analysis['style_issues']):
                suggestions.append("Remove unused imports to keep the code clean and reduce cognitive load.")
            if any('unused-variable' in issue for issue in analysis['style_issues']):
                suggestions.append("Remove or use unused variables; they often signal dead code or logic errors.")

        # Complexity issues
        complexity = analysis['complexity']
        if complexity > 15:
            suggestions.append("CRITICAL: Extremely high complexity. Refactor into multiple smaller methods/functions immediately.")
        elif complexity > 10:
            suggestions.append("HIGH: Code is too complex. Break down into smaller, focused methods/functions.")
        elif complexity > 7:
            suggestions.append("MODERATE: Consider simplifying logic and reducing decision points (if/else, loops, etc.).")

        # Nesting depth (Java-specific)
        if language == 'java' and metrics.get('max_nesting', 0) > 5:
            suggestions.append(f"JAVA: Maximum nesting depth is {metrics['max_nesting']} - reduce to 3-4 levels for readability.")

        # Maintainability issues
        mi = analysis['maintainability']
        if mi < 30:
            suggestions.append("CRITICAL: Code is very hard to maintain. Major refactoring required.")
        elif mi < 50:
            if language == 'java':
                suggestions.append("HIGH: Add comments/JavaDoc, break down complex methods, and reduce nesting depth.")
            else:
                suggestions.append("HIGH: Add comprehensive docstrings, comments, and simplify structure.")
        elif mi < 70:
            suggestions.append("MODERATE: Improve documentation and code organization.")

        # Code metrics suggestions
        if metrics.get('total_lines', 0) > 500:
            if language == 'java':
                suggestions.append("File too long. Consider splitting into multiple classes or extracting helper classes.")
            else:
                suggestions.append("File too long. Split into multiple modules for better organization.")
        
        methods_or_functions = metrics.get('functions', 0)
        classes_or_modules = metrics.get('classes', 0)
        if methods_or_functions > 20 and classes_or_modules > 0:
            if language == 'java':
                suggestions.append(f"Too many methods per class ({methods_or_functions} methods). Consider breaking into multiple classes.")
            else:
                suggestions.append("Too many functions in one file. Consider splitting into classes or modules.")
        if metrics.get('code_lines', 0) / max(metrics.get('total_lines', 1), 1) < 0.3:
            suggestions.append("Too many comments/empty lines. Focus on actual code implementation.")
        if methods_or_functions == 0 and classes_or_modules == 0:
            if language == 'java':
                suggestions.append("No classes or methods defined. Consider organizing code with proper class structure.")
            else:
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

    user_id = session.get('user_id')
    user = db.get_user_by_id(user_id)
    
    return render_template('upload.html',user=user)

@app.route('/analyze/<int:file_id>')
@login_required
def analyze(file_id):
    """Analyze uploaded file"""
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        user_id = session.get('user_id')
        user = db.get_user_by_id(user_id)
        file_info = db.get_file_by_id(file_id)
        
        if not file_info or file_info[1] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_info[2])
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        print(f"Analyzing file: {filepath}")
        
        # Perform analysis
        try:
            analysis = CodeAnalyzer.analyze(filepath)
            language = CodeAnalyzer.get_file_language(filepath)
            print(f"Analysis results: {analysis}")
            scores = ScoreCalculator.calculate_score(analysis)
            print(f"Scores: {scores}")
            suggestions = ScoreCalculator.get_suggestions(analysis, scores, language)

            issues = analysis['syntax_issues'] + analysis['style_issues']
            categorized_issues = categorize_issues(issues, language)
        except Exception as e:
            print(f"Analysis error: {e}")
            return render_template('results.html', 
                                 error=f'Analysis failed: {str(e)}',
                                 file_id=file_id,
                                 filename=file_info[2],
                                 performance="N/A",
                                 user=user)

        # Save results to database
        try:
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
        except Exception as e:
            print(f"Warning: Could not save analysis results to database: {e}")
            # Continue anyway to show results

        trend_percent = max(min(int(scores['total_score'] - 70), 20), -20)
        critical_paths = max(1, int(round(analysis['complexity'] * 1.1)))

        analyzed_path = os.path.abspath(filepath)
        response = make_response(render_template('results.html',
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
                             scores=scores,
                             performance="Optimized" if analysis['complexity'] <= 5 else "Needs Optimization",
                             user=user))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        user = db.get_user_by_id(session.get('user_id')) if db else None
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
                             },
                             user=user)

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    """Delete an uploaded file"""
    if not db:
        return jsonify({'error': 'Database not available'}), 503

    user_id = session.get('user_id')
    file_info = db.get_file_by_id(file_id)

    if not file_info or file_info[1] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Delete physical file from disk
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_info[2])
    if os.path.exists(filepath):
        os.remove(filepath)

    # Delete DB record (cascades to analysis_results)
    db.delete_file(file_id, user_id)

    return redirect(url_for('dashboard'))


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
        
        user = db.get_user_by_id(user_id)
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
            language = CodeAnalyzer.get_file_language(filepath)
            scores = ScoreCalculator.calculate_score(latest_analysis)
            suggestions = ScoreCalculator.get_suggestions(latest_analysis, scores, language)
            issues = latest_analysis['syntax_issues'] + latest_analysis['style_issues']
            categorized_issues = categorize_issues(issues, language)
            
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
                             suggestions=suggestions,
                             scores=scores,
                             user=user)
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
        language = CodeAnalyzer.get_file_language(filepath)
        latest_scores = ScoreCalculator.calculate_score(latest_analysis)
        latest_suggestions = ScoreCalculator.get_suggestions(latest_analysis, latest_scores, language)
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
    user = None
    if 'user_id' in session and db:
        user = db.get_user_by_id(session['user_id'])
    return render_template('about.html', user=user)

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

    AVATAR_FOLDER = os.path.join('static', 'avatars')
    os.makedirs(AVATAR_FOLDER, exist_ok=True)
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

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
            # Handle avatar upload
            avatar_filename = None
            avatar_file = request.files.get('avatar')
            if avatar_file and avatar_file.filename:
                ext = avatar_file.filename.rsplit('.', 1)[-1].lower()
                if ext not in ALLOWED_IMAGE_EXTENSIONS:
                    error = 'Invalid image format. Allowed: PNG, JPG, JPEG, GIF, WEBP.'
                else:
                    avatar_filename = f"avatar_{user_id}.{ext}"
                    avatar_file.save(os.path.join(AVATAR_FOLDER, avatar_filename))

            if not error:
                # Handle removal first
                if data.get('remove_avatar') == '1':
                    # Delete the old file from disk
                    if user and user[5]:
                        old_path = os.path.join(AVATAR_FOLDER, user[5])
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    avatar_filename = ''  # empty string clears the DB column
                    updated = db.update_user(
                        user_id, name, email,
                        password if password else None,
                        bio=bio,
                        avatar=avatar_filename
                    )
                else:
                    updated = db.update_user(
                        user_id, name, email,
                        password if password else None,
                        bio=bio,
                        avatar=avatar_filename
                    )
                if updated:
                    success = 'Profile updated successfully.'
                    user = db.get_user_by_id(user_id)
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