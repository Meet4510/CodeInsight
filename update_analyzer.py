import re

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Update categorize_issues function signature
content = re.sub(
    r'def categorize_issues\(issues\):',
    'def categorize_issues(issues, language=\'python\'):',
    content
)

# Update the categorization logic to handle Java
old_categorize = '''    for issue in issues:
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
            categories['Other'].append(issue)'''

new_categorize = '''    for issue in issues:
        key = issue.lower()
        
        if language == 'java':
            # Java-specific categorization
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
            # Python-specific categorization
            if any(tag in key for tag in ['bad-indentation', 'trailing-whitespace', 'missing-final-newline', 'line-too-long', 'superfluous-parens', 'wrong-import-position', 'ungrouped-imports']):
                categories['Formatting'].append(issue)
            elif 'invalid-name' in key:
                categories['Naming'].append(issue)
            elif any(tag in key for tag in ['missing-module-docstring', 'missing-function-docstring', 'missing-class-docstring']):
                categories['Documentation'].append(issue)
            elif any(tag in key for tag in ['unused-import', 'unused-variable', 'undefined-variable', 'broad-except', 'too-many-branches', 'too-many-statements', 'too-many-locals', 'unused-argument', 'redefined-outer-name']):
                categories['Logic'].append(issue)
            else:
                categories['Other'].append(issue)'''

content = content.replace(old_categorize, new_categorize)

# Fix get_suggestions signature (add language parameter)
content = re.sub(
    r'def get_suggestions\(analysis, scores\):',
    'def get_suggestions(analysis, scores, language=\'python\'):',
    content
)

# Update calls to get_suggestions to pass language
content = re.sub(
    r'suggestions = ScoreCalculator\.get_suggestions\(analysis, scores\)(\n\s+issues)',
    r'language = CodeAnalyzer.get_file_language(filepath)\n            suggestions = ScoreCalculator.get_suggestions(analysis, scores, language)\n\n            issues',
    content,
    count=1
)

content = re.sub(
    r'categorized_issues = categorize_issues\(issues\)(\n)',
    r'categorized_issues = categorize_issues(issues, language)\1',
    content,
    count=1
)

# Write the file back
with open('app.py', 'w') as f:
    f.write(content)

print("✓ Updated app.py successfully")
