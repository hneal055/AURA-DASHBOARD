"""
Test file for BudgetAnalyzer - Fixed with absolute imports
"""

import sys
import os
import pandas as pd
import tempfile

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Project root: {project_root}")
print(f"Current dir: {os.getcwd()}")

# Add project root to Python path
sys.path.insert(0, project_root)

# Now import should work
try:
    from src.budget_analyzer import BudgetAnalyzer
    print("✓ SUCCESS: Imported BudgetAnalyzer")
except ImportError as e:
    print(f"✗ FAILED to import: {e}")
    print(f"sys.path: {sys.path}")
    
    # Try alternative import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "budget_analyzer",
        os.path.join(project_root, "src", "budget_analyzer.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    BudgetAnalyzer = module.BudgetAnalyzer
    print("✓ Imported via importlib")


def test_analyzer_initialization():
    """Test that BudgetAnalyzer initializes correctly."""
    print("\nRunning test_analyzer_initialization...")
    analyzer = BudgetAnalyzer()
    assert analyzer.data is None
    assert analyzer.summary == {}
    print("✓ Initialization test passed")


def test_load_valid_csv():
    """Test loading a valid CSV file."""
    print("\nRunning test_load_valid_csv...")
    analyzer = BudgetAnalyzer()
    
    # Create test data
    test_data = {
        "Description": ["Test Item 1", "Test Item 2"],
        "Department": ["IT", "HR"],
        "Category": ["Software", "Training"],
        "Amount": [1000, 2000]
    }
    
    df = pd.DataFrame(test_data)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_file = f.name
    
    try:
        # Load the file
        loaded_df = analyzer.load_csv(temp_file)
        
        # Verify the data
        assert len(loaded_df) == 2
        assert loaded_df["Amount"].sum() == 3000
        print("✓ CSV loading test passed")
        
    finally:
        # Clean up
        os.unlink(temp_file)


def test_summary_statistics():
    """Test summary statistics calculation."""
    print("\nRunning test_summary_statistics...")
    analyzer = BudgetAnalyzer()
    
    test_data = {
        "Description": ["A", "B", "C"],
        "Department": ["IT", "HR", "IT"],
        "Category": ["X", "Y", "X"],
        "Amount": [100, 200, 300]
    }
    
    df = pd.DataFrame(test_data)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_file = f.name
    
    try:
        analyzer.load_csv(temp_file)
        summary = analyzer.get_summary()
        
        # Verify summary
        assert summary["total_items"] == 3
        assert summary["total_amount"] == 600
        assert summary["average_amount"] == 200
        print("✓ Summary statistics test passed")
        
    finally:
        os.unlink(temp_file)


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("RUNNING TESTS")
    print("="*60)
    
    tests = [
        test_analyzer_initialization,
        test_load_valid_csv,
        test_summary_statistics,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
