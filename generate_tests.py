import pandas as pd
import os

print("=== AURA DASHBOARD TEST GENERATOR ===")
print("=" * 50)

# Create output directory
output_dir = "test_files"
os.makedirs(output_dir, exist_ok=True)

print(f"Creating test files in: {os.path.abspath(output_dir)}")

# 1. Basic budget file
basic_data = {
    "Description": ["Office Rent", "Employee Salaries", "Software Licenses", 
                   "Marketing Campaign", "Travel Expenses", "Utilities"],
    "Department": ["Operations", "HR", "IT", "Marketing", "Sales", "Operations"],
    "Category": ["Facilities", "Personnel", "Software", "Advertising", "Travel", "Utilities"],
    "Amount": [5000, 45000, 3000, 12000, 8000, 1500]
}

df_basic = pd.DataFrame(basic_data)
df_basic.to_csv(f"{output_dir}/basic_budget.csv", index=False)
print(f"\n✅ 1. basic_budget.csv")
print(f"   Items: {len(df_basic)}")
print(f"   Total: ${df_basic['Amount'].sum():,}")

# 2. Edge cases file
edge_data = {
    "Description": ["Tiny Expense", "Huge Cost", "Negative Refund", 
                   "Zero Cost Item", "Duplicate A", "Duplicate B"],
    "Department": ["IT", "Executive", "Finance", "Test", "HR", "HR"],
    "Category": ["Software", "Bonus", "Adjustment", "Test", "Training", "Training"],
    "Amount": [10, 75000, -2000, 0, 1500, 1500]
}

df_edge = pd.DataFrame(edge_data)
df_edge.to_csv(f"{output_dir}/edge_cases.csv", index=False)
print(f"\n✅ 2. edge_cases.csv")
print(f"   Items: {len(df_edge)}")
print(f"   Total: ${df_edge['Amount'].sum():,}")

# 3. Multiple departments file
import numpy as np
np.random.seed(42)

many_items = {
    "Description": [f"Expense {i:03d}" for i in range(1, 21)],
    "Department": np.random.choice(["IT", "Marketing", "Sales", "HR", "Operations"], 20),
    "Category": np.random.choice(["Software", "Ads", "Travel", "Training", "Supplies"], 20),
    "Amount": np.random.randint(100, 5000, 20)
}

df_many = pd.DataFrame(many_items)
df_many.to_csv(f"{output_dir}/multiple_items.csv", index=False)
print(f"\n✅ 3. multiple_items.csv")
print(f"   Items: {len(df_many)}")
print(f"   Total: ${df_many['Amount'].sum():,}")

print("\n" + "=" * 50)
print("📁 TEST FILES CREATED SUCCESSFULLY!")
print("=" * 50)
print(f"\nLocation: {os.path.abspath(output_dir)}")
print("\n🎯 Testing recommendations:")
print("1. Start with: basic_budget.csv")
print("2. Then test: edge_cases.csv")
print("3. Finally: multiple_items.csv")
