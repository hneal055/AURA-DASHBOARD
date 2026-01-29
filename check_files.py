import os
import sys

print("🔍 CHECKING FILE STRUCTURE")
print("=" * 50)

# List all files in current directory
print("\n📁 CURRENT DIRECTORY FILES:")
current_files = [f for f in os.listdir('.') if os.path.isfile(f)]
for file in sorted(current_files):
    print(f"  - {file}")

# Check for specific required files
print("\n✅ REQUIRED FILES STATUS:")
required_files = [
    'web_app_v2_with_templates.py',
    'risk_manager.py', 
    'charts_data.py',
    'excel_exporter.py',
    'budget_comparison.py',
    'comparison_charts.py',
    'budget_templates.py'
]

missing_files = []
for file in required_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"  ✅ {file} - EXISTS ({size} bytes)")
    else:
        print(f"  ❌ {file} - MISSING")
        missing_files.append(file)

# Check directories
print("\n📁 DIRECTORY STATUS:")
directories = ['static/css', 'uploads', 'outputs', 'static/js']
for dir_path in directories:
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"  ✅ {dir_path}/ - EXISTS")
    else:
        print(f"  ❌ {dir_path}/ - MISSING")

print("\n" + "=" * 50)
if missing_files:
    print(f"🚨 MISSING FILES: {len(missing_files)}")
    for file in missing_files:
        print(f"   - {file}")
else:
    print("🎉 ALL REQUIRED FILES EXIST!")

# Check Python module imports
print("\n🔧 CHECKING PYTHON IMPORTS:")
try:
    from risk_manager import RiskManager
    print("  ✅ risk_manager - SUCCESS")
except ImportError as e:
    print(f"  ❌ risk_manager - FAILED: {e}")

try:
    from charts_data import prepare_chart_data, generate_chart_html
    print("  ✅ charts_data - SUCCESS")
except ImportError as e:
    print(f"  ❌ charts_data - FAILED: {e}")

try:
    from excel_exporter import export_to_excel
    print("  ✅ excel_exporter - SUCCESS")
except ImportError as e:
    print(f"  ❌ excel_exporter - FAILED: {e}")

try:
    from budget_comparison import compare_budgets
    print("  ✅ budget_comparison - SUCCESS")
except ImportError as e:
    print(f"  ❌ budget_comparison - FAILED: {e}")

try:
    from comparison_charts import generate_comparison_chart_html
    print("  ✅ comparison_charts - SUCCESS")
except ImportError as e:
    print(f"  ❌ comparison_charts - FAILED: {e}")

try:
    from budget_templates import get_template_categories
    print("  ✅ budget_templates - SUCCESS")
except ImportError as e:
    print(f"  ❌ budget_templates - FAILED: {e}")