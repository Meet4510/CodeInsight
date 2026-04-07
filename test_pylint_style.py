from app import CodeAnalyzer

filepath = 'uploads/20260405_180241_main (2) (1).py'
style = CodeAnalyzer.check_code_style(filepath)
print('STYLE ISSUES COUNT:', len(style))
for issue in style[:20]:
    print(issue)
