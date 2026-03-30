#!/usr/bin/env python3
"""Fix Java style checker to improve issue detection"""

with open('app.py', 'r') as f:
    content = f.read()

# Find and replace the check_java_style method
old_method = '''    @staticmethod
    def check_java_style(filepath):
        """Check Java code style and conventions"""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            lines = code.split('\\n')
            
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip empty lines and comments
                if not stripped or stripped.startswith('//'):
                    continue
                
                # Check for proper naming conventions
                # Class names should be PascalCase
                class_match = re.search(r'class\\s+([a-z_][a-zA-Z0-9_]*)', line)
                if class_match:
                    class_name = class_match.group(1)
                    if not class_name[0].isupper():
                        issues.append(f"Line {line_no}: Class name '{class_name}' should start with uppercase (PascalCase)")
                
                # Method names should be camelCase
                method_match = re.search(r'\\b(public|private|protected)\\s+\\w+\\s+([a-z_][a-zA-Z0-9_]*)\\s*\\(', line)
                if method_match:
                    method_name = method_match.group(2)
                    if '_' in method_name and method_name != 'main':
                        issues.append(f"Line {line_no}: Method name '{method_name}' should use camelCase, not snake_case")
                
                # Check for TODO/FIXME comments without description
                if re.search(r'//\\s*(TODO|FIXME)\\s*$', line):
                    issues.append(f"Line {line_no}: {re.search(r'(TODO|FIXME)', line).group(1)} comment without description")
                
                # Check for multiple statements on one line
                if re.search(r';.*[a-zA-Z].*[;{}]', line) and 'for' not in line:
                    issues.append(f"Line {line_no}: Multiple statements on single line - reduce complexity")
                
                # Check for missing spaces around operators
                if re.search(r'[a-zA-Z0-9]=[a-zA-Z0-9]', line) and '==' not in line:
                    issues.append(f"Line {line_no}: Missing spaces around assignment operator")
                
                # Check line length
                if len(line) > 120:
                    issues.append(f"Line {line_no}: Line exceeds 120 characters (length: {len(line)})")
                
                # Check for magic numbers (naked numbers in code)
                if re.search(r'[^/]\\b(\\d+)\\b[^/]', line) and 'for' not in line:
                    # Check if we haven't already flagged this line
                    has_magic_number_issue = any(f"Line {line_no}:" in issue and "Magic number" in issue for issue in issues)
                    if not has_magic_number_issue:
                        if not stripped.startswith('*') and not stripped.startswith('/'):
                            numbers = re.findall(r'\\b(\\d+)\\b', line)
                            if numbers and numbers[0] not in ['0', '1', '2', '3', '10', '100']:
                                issues.append(f"Line {line_no}: Magic number detected - consider using named constant")
            
            return issues[:30]  # Limit to 30 style issues
        except Exception as e:
            return [f"Java style check error: {str(e)}"]'''

new_method = '''    @staticmethod
    def check_java_style(filepath):
        """Check Java code style and conventions with severity levels"""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            lines = code.split('\\n')
            flagged_lines_magic = set()
            
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip empty lines and comment blocks
                if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                    continue
                
                # Check for proper naming conventions (HIGH priority)
                class_match = re.search(r'class\\s+([a-z_][a-zA-Z0-9_]*)', line)
                if class_match:
                    class_name = class_match.group(1)
                    if not class_name[0].isupper():
                        issues.append(f"[ERROR] Line {line_no}: Class name should be PascalCase")
                
                # Method names should be camelCase (HIGH priority)
                method_match = re.search(r'\\b(public|private|protected)\\s+\\w+\\s+([a-z_][a-zA-Z0-9_]*)\\s*\\(', line)
                if method_match:
                    method_name = method_match.group(2)
                    if '_' in method_name and method_name != 'main':
                        issues.append(f"[WARNING] Line {line_no}: Method name should be camelCase")
                
                # Check for TODO/FIXME without description (INFO priority)
                if re.search(r'//\\s*(TODO|FIXME)\\s*$', line):
                    tag = re.search(r'(TODO|FIXME)', line).group(1)
                    issues.append(f"[INFO] Line {line_no}: {tag} comment needs description")
                
                # Multiple statements on one line (MEDIUM priority)
                if re.search(r';.*[a-zA-Z].*[;{}]', line) and 'for' not in line and not stripped.startswith('import'):
                    issues.append(f"[WARNING] Line {line_no}: Multiple statements on one line")
                
                # Missing spaces around operators (LOW priority)
                if re.search(r'[a-zA-Z0-9]=[a-zA-Z0-9]', line) and '==' not in line and '!=' not in line:
                    issues.append(f"[INFO] Line {line_no}: Missing spaces around operator")
                
                # Line length check (MEDIUM priority)
                if len(line) > 120:
                    issues.append(f"[WARNING] Line {line_no}: Line too long ({len(line)} chars)")
                
                # Selective magic number detection (LOW priority)
                if line_no not in flagged_lines_magic:
                    assignment_match = re.search(r'=\\s*([0-9]+)\\s*[;,)]', line)
                    if assignment_match:
                        number = assignment_match.group(1)
                        common_numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '16', '24', '32', 
                                        '60', '100', '256', '512', '1000', '1024', '10000', '100000', '360', '180', '255']
                        if number not in common_numbers and len(number) <= 5:
                            issues.append(f"[INFO] Line {line_no}: Magic number - use named constant")
                            flagged_lines_magic.add(line_no)
            
            return issues[:20]  # Limit to 20 most important issues
        except Exception as e:
            return [f"[ERROR] Java style check error: {str(e)}"]'''

# Replace the old method with the new one
if old_method in content:
    content = content.replace(old_method, new_method)
    with open('app.py', 'w') as f:
        f.write(content)
    print("✓ Successfully updated check_java_style method")
    print("  - Added severity levels [ERROR], [WARNING], [INFO]")
    print("  - Improved magic number detection")
    print("  - Reduced to top 20 issues")
else:
    print("✗ Could not find the exact method to replace")
    print("  The file structure may have changed")
