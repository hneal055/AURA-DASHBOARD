#!/usr/bin/env python
"""
Simple test to verify imports work
"""

import sys
import os

print("=== TESTING IMPORTS ===")
print(f"Python path: {sys.executable}")
print(f"Working dir: {os.getcwd()}")

# Try different import methods
print("\n1. Trying direct import from src...")
try:
    from src.budget_analyzer import BudgetAnalyzer
    print("✓ SUCCESS: Imported from src.budget_analyzer")
    analyzer = BudgetAnalyzer()
    print(f"✓ Created analyzer instance: {analyzer}")
except ImportError as e:
    print(f"✗ FAILED: {e}")

print("\n2. Trying to add project root to sys.path...")
sys.path.insert(0, os.getcwd())
try:
    from src.budget_analyzer import BudgetAnalyzer
    print("✓ SUCCESS: Imported after adding project root to path")
except ImportError as e:
    print(f"✗ FAILED: {e}")

print("\n3. Testing if module file exists...")
budget_analyzer_path = os.path.join("src", "budget_analyzer.py")
print(f"Checking: {budget_analyzer_path}")
print(f"Exists: {os.path.exists(budget_analyzer_path)}")

if os.path.exists(budget_analyzer_path):
    print("\n4. Trying importlib import...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("budget_analyzer", budget_analyzer_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    BudgetAnalyzer = module.BudgetAnalyzer
    print("✓ SUCCESS: Imported via importlib")
    analyzer = BudgetAnalyzer()
    print(f"✓ Created analyzer: {analyzer}")

print("\n" + "="*50)
print("IMPORT TEST COMPLETE")
