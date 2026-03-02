"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: budget_visualizer.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Budget Visualizer
----------------
Creates visualizations for production budget analysis.
"""
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
from datetime import datetime

def visualize_budget(budget_df, output_dir="data/output"):
    """Create visualizations for budget analysis"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get total budget
    total_budget = budget_df["Amount"].sum()
    
    # Create a list to track all visualization paths
    visualization_paths = {}
    
    # 1. Department Pie Chart (if Department column exists)
    if "Department" in budget_df.columns:
        plt.figure(figsize=(10, 6))
        dept_data = budget_df.groupby("Department")["Amount"].sum()
        dept_data = dept_data.sort_values(ascending=False)
        
        plt.pie(
            dept_data, 
            labels=dept_data.index, 
            autopct="%1.1f%%", 
            startangle=90
        )
        plt.title("Budget Allocation by Department")
        plt.axis("equal")
        
        pie_path = os.path.join(output_dir, f"department_allocation_{timestamp}.png")
        plt.savefig(pie_path)
        plt.close()
        visualization_paths["department_pie"] = pie_path
        print(f"Created department allocation pie chart: {os.path.basename(pie_path)}")
    
    # 2. Top Items Bar Chart
    plt.figure(figsize=(12, 8))
    top_items = budget_df.nlargest(10, "Amount").sort_values("Amount")
    
    plt.barh(top_items["Description"], top_items["Amount"], color="skyblue")
    for i, (_, row) in enumerate(top_items.iterrows()):
        percentage = row["Amount"] / total_budget * 100
        plt.text(
            row["Amount"] + total_budget * 0.01, 
            i, 
            f"{percentage:.1f}%", 
            va="center"
        )
    
    plt.xlabel("Amount ($)")
    plt.ylabel("Budget Item")
    plt.title("Top 10 Budget Items")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    
    bar_path = os.path.join(output_dir, f"top_items_{timestamp}.png")
    plt.savefig(bar_path)
    plt.close()
    visualization_paths["top_items_bar"] = bar_path
    print(f"Created top items bar chart: {os.path.basename(bar_path)}")
    
    # 3. Budget Distribution (optional)
    try:
        plt.figure(figsize=(10, 6))
        plt.hist(budget_df["Amount"], bins=20, color="green", alpha=0.7)
        plt.xlabel("Amount ($)")
        plt.ylabel("Number of Items")
        plt.title("Budget Item Distribution")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        
        hist_path = os.path.join(output_dir, f"budget_distribution_{timestamp}.png")
        plt.savefig(hist_path)
        plt.close()
        visualization_paths["distribution_histogram"] = hist_path
        print(f"Created budget distribution histogram: {os.path.basename(hist_path)}")
    except Exception as e:
        print(f"Note: Could not create distribution histogram: {str(e)}")
    
    return visualization_paths

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            # Read the budget file
            df = pd.read_excel(sys.argv[1])
            
            # Generate visualizations
            visualize_budget(df)
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print("Please provide a budget Excel file path")

