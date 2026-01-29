@'
"""
Fix for OneDrive sync issues
Run this with: python fix_onedrive.py
"""

import os
import sys

print("=== SIMPLE FIX FOR ONEDRIVE ===")
print("=" * 40)

# Get current location
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current location: {current_dir}")

# Check if in OneDrive
if "OneDrive" in current_dir:
    print("⚠️ WARNING: Project is in OneDrive folder!")
    print("This may cause file sync issues with Python scripts.")
    
    print("\nRECOMMENDED FIX:")
    print("1. Manually copy your project folder to:")
    print("   C:\\Users\\hneal\\Desktop\\PythonProjects\\")
    print("2. Work from the new location")
    print("3. Delete the OneDrive copy if needed")
    
    print("\nQUICK FIX (for now):")
    print("Create test files on Desktop instead of in project folder")
    
    # Create a simple test generator that saves to Desktop
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    print(f"\nWill save test files to: {desktop}\\aura_test_files\\")
    
    response = input("\nCreate simple test generator on Desktop? (y/n): ").strip().lower()
    
    if response == 'y':
        # Create the test generator code
        test_code = '''import pandas as pd
import os

print("=== TEST FILE GENERATOR ===")

# Save to Desktop to avoid OneDrive issues
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
output_dir = os.path.join(desktop, "aura_test_files")
os.makedirs(output_dir, exist_ok=True)

print(f"Test files will be saved to: {output_dir}")

# Create basic test data
data = {
    "Description": ["Office Rent", "Employee Salaries", "Software Licenses", 
                   "Marketing Campaign", "Travel Expenses"],
    "Department": ["Operations", "HR", "IT", "Marketing", "Sales"],
    "Category": ["Facilities", "Personnel", "Software", "Advertising", "Travel"],
    "Amount": [5000, 45000, 3000, 12000, 8000]
}

df = pd.DataFrame(data)
file_path = os.path.join(output_dir, "basic_budget.csv")
df.to_csv(file_path, index=False)

print(f"\\n✅ Created: basic_budget.csv")
print(f"Total: ${df['Amount'].sum():,}")
print(f"Items: {len(df)}")

# Create edge case test
edge_data = {
    "Description": ["Very Small", "Very Large", "Negative (Refund)", 
                   "Zero", "Duplicate A", "Duplicate B"],
    "Department": ["IT", "Executive", "Finance", "Test", "HR", "HR"],
    "Category": ["Software", "Bonus", "Adjustment", "Test", "Training", "Training"],
    "Amount": [10, 75000, -1500, 0, 2000, 2000]
}

df_edge = pd.DataFrame(edge_data)
edge_path = os.path.join(output_dir, "edge_cases.csv")
df_edge.to_csv(edge_path, index=False)

print(f"✅ Created: edge_cases.csv")

print("\\n=== TEST FILES READY ===")
print(f"Upload these files from: {output_dir}")
print("\\nGenerated 2 test files:")
print("1. basic_budget.csv - Normal business expenses")
print("2. edge_cases.csv - Tests error handling")
'''
        
        # Save the test generator to Desktop
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        generator_path = os.path.join(desktop, "generate_tests.py")
        
        with open(generator_path, 'w') as f:
            f.write(test_code)
        
        print(f"\n✅ Created test generator: {generator_path}")
        print(f"Run it with: python {generator_path}")
        
else:
    print("✅ Good! Project is not in OneDrive.")
    print("You can run your scripts normally.")

print("\n" + "=" * 40)
print("DONE!")
'@ | Out-File -FilePath "fix_onedrive.py" -Encoding utf8