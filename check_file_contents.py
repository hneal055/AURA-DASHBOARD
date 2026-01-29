import os

def check_file_content(filename):
    """Check if file exists and has content"""
    if not os.path.exists(filename):
        return "MISSING"
    
    size = os.path.getsize(filename)
    if size == 0:
        return "EMPTY"
    
    # Read first few lines to check content
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            first_lines = []
            for i, line in enumerate(f):
                if i >= 5:  # Check first 5 lines
                    break
                first_lines.append(line.strip())
        
        # Check if it looks like Python code
        has_python_content = any('import' in line or 'def ' in line or 'class ' in line for line in first_lines)
        if has_python_content:
            return f"VALID ({size} bytes)"
        else:
            return f"INVALID CONTENT ({size} bytes)"
            
    except Exception as e:
        return f"ERROR READING: {e}"

print("📄 FILE CONTENT CHECK")
print("=" * 50)

files_to_check = [
    'risk_manager.py',
    'charts_data.py', 
    'excel_exporter.py',
    'budget_comparison.py',
    'comparison_charts.py',
    'budget_templates.py'
]

for file in files_to_check:
    status = check_file_content(file)
    print(f"{file}: {status}")