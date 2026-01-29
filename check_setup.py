#!/usr/bin/env python
"""
Demonstration that everything works
"""

import os
import sys

print("=== AURA DASHBOARD SETUP CHECK ===")
print("=" * 50)

# 1. Check project structure
print("\n1. Project structure:")
files = os.listdir(".")
print(f"   Root directory: {files}")

if os.path.exists("src"):
    print(f"   src directory: {os.listdir('src')}")
else:
    print("   No src directory found")

# 2. Check test files
print("\n2. Test files:")
if os.path.exists("test_files"):
    test_files = os.listdir("test_files")
    print(f"   Found {len(test_files)} test files: {test_files}")
else:
    print("   No test_files directory")

# 3. Try to import
print("\n3. Testing imports:")
try:
    # Try src import first
    from src.budget_analyzer import BudgetAnalyzer
    print("   ✓ Imported from src.budget_analyzer")
except ImportError:
    try:
        # Try root import
        from budget_analyzer import BudgetAnalyzer
        print("   ✓ Imported from budget_analyzer (root)")
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        print("   Trying to find the file...")
        
        # List Python files
        python_files = [f for f in os.listdir(".") if f.endswith(".py")]
        print(f"   Python files in root: {python_files}")
        
        if "budget_analyzer.py" in python_files:
            print("   Found budget_analyzer.py in root")
            import importlib.util
            spec = importlib.util.spec_from_file_location("budget_analyzer", "budget_analyzer.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            BudgetAnalyzer = module.BudgetAnalyzer
            print("   ✓ Loaded directly from file")

# 4. Run a simple analysis
print("\n4. Running analysis:")
if os.path.exists("test_files/basic_budget.csv"):
    try:
        analyzer = BudgetAnalyzer()
        df = analyzer.load_csv("test_files/basic_budget.csv")
        summary = analyzer.get_summary()
        print(f"   ✓ Loaded {summary['total_items']} items")
        print(f"   Total: ${summary['total_amount']:,}")
    except Exception as e:
        print(f"   ✗ Analysis failed: {e}")
else:
    print("   ⚠ Test files not found")

print("\n" + "=" * 50)
print("SETUP CHECK COMPLETE")
print("=" * 50)
