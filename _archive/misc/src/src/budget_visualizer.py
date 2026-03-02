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
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys

def visualize_budget(budget_file, output_dir="data/output"):
    """Create visualizations for budget analysis"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the data
    df = pd.read_excel(budget_file)
    total_budget = df["Amount"].sum()
    
    # 1. Create pie chart of departments
    plt.figure(figsize=(10, 6))
    dept_data = df.groupby("Department")["Amount"].sum()
    dept_data = dept_data.sort_values(ascending=False)
    
    # Plot
    plt.pie(
        dept_data, 
        labels=dept_data.index, 
        autopct='%1.1f%%', 
        startangle=90,
        explode=[0.05 if i < 3 else 0 for i in range(len(dept_data))]  # Explode top 3 slices
    )
    plt.title("Budget Allocation by Department")
    plt.axis('equal')  # Equal aspect ratio ensures pie is circular
    
    # Save
    pie_chart_path = os.path.join(output_dir, "department_allocation.png")
    plt.savefig(pie_chart_path)
    plt.close()
    
    # 2. Create bar chart of top items
    plt.figure(figsize=(12, 8))
    top_items = df.nlargest(10, "Amount").sort_values("Amount")
    
    # Calculate percentages
    top_items["Percentage"] = top_items["Amount"] / total_budget * 100
    
    # Plot horizontal bar chart
    plt.barh(top_items["Description"], top_items["Amount"], color="skyblue")
    
    # Add percentage annotations
    for i, (_, row) in enumerate(top_items.iterrows()):
        plt.text(row["Amount"] + total_budget * 0.01, i, f"{row['Percentage']:.1f}%", va='center')
    
    plt.xlabel("Amount ($)")
    plt.ylabel("Budget Item")
    plt.title("Top 10 Budget Items")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save
    bar_chart_path = os.path.join(output_dir, "top_budget_items.png")
    plt.savefig(bar_chart_path)
    plt.close()
    
    print(f"Visualizations saved to: {output_dir}")
    return {
        "pie_chart": pie_chart_path,
        "bar_chart": bar_chart_path
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        visualize_budget(sys.argv[1])
    else:
        print("Please provide a budget Excel file path")
