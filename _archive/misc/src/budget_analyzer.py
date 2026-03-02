"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: budget_analyzer.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
import pandas as pd
import sys

def analyze_budget(excel_path):
    """Analyze a budget Excel file"""
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        print(f"Loaded budget file: {excel_path}")
        print(f"Found {len(df)} budget items")
        print(f"Total budget: ${df['Amount'].sum():,.2f}")
        
        # Identify high-cost items (>5% of total)
        total_budget = df['Amount'].sum()
        threshold = total_budget * 0.05
        high_cost_items = df[df['Amount'] >= threshold]
        
        print("\n--- HIGH COST ITEMS ---")
        for _, row in high_cost_items.iterrows():
            percentage = (row['Amount'] / total_budget) * 100
            print(f"{row['Description']}: ${row['Amount']:,.2f} ({percentage:.1f}%)")
        
        # Analyze by department
        if 'Department' in df.columns:
            print("\n--- DEPARTMENT BREAKDOWN ---")
            dept_summary = df.groupby('Department')['Amount'].sum()
            for dept, amount in dept_summary.items():
                percentage = (amount / total_budget) * 100
                print(f"{dept}: ${amount:,.2f} ({percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Please provide a budget Excel file path")
    else:
        analyze_budget(sys.argv[1])

