"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: report_generator.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import sys
import datetime

def generate_report(budget_file, output_dir="data/output", include_visualizations=True):
    """Generate a comprehensive budget report"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load budget data
    df = pd.read_excel(budget_file)
    total_budget = df["Amount"].sum()
    
    # Create timestamp for file names
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Generate JSON report with analysis
    report_data = {
        "report_generated": datetime.datetime.now().isoformat(),
        "budget_file": os.path.basename(budget_file),
        "total_budget": float(total_budget),
        "line_items": len(df),
        "departments": {
            dept: {
                "amount": float(amount),
                "percentage": float(amount / total_budget * 100)
            }
            for dept, amount in df.groupby("Department")["Amount"].sum().items()
        },
        "top_items": [
            {
                "description": row["Description"],
                "department": row["Department"],
                "amount": float(row["Amount"]),
                "percentage": float(row["Amount"] / total_budget * 100)
            }
            for _, row in df.nlargest(10, "Amount").iterrows()
        ]
    }
    
    # Save JSON report
    json_path = os.path.join(output_dir, f"budget_report_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=2)
    
    # 2. Create visualizations if requested
    vis_paths = []
    if include_visualizations:
        # Department breakdown pie chart
        plt.figure(figsize=(10, 6))
        dept_data = df.groupby("Department")["Amount"].sum().sort_values(ascending=False)
        plt.pie(
            dept_data, 
            labels=dept_data.index, 
            autopct="%1.1f%%", 
            startangle=90
        )
        plt.title("Budget Allocation by Department")
        plt.axis("equal")
        pie_path = os.path.join(output_dir, f"dept_breakdown_{timestamp}.png")
        plt.savefig(pie_path)
        plt.close()
        vis_paths.append(pie_path)
        
        # Top items bar chart
        plt.figure(figsize=(12, 8))
        top_items = df.nlargest(10, "Amount").sort_values("Amount")
        plt.barh(top_items["Description"], top_items["Amount"], color="skyblue")
        for i, (_, row) in enumerate(top_items.iterrows()):
            plt.text(row["Amount"] + total_budget * 0.01, i, f"{row['Amount'] / total_budget * 100:.1f}%", va="center")
        plt.xlabel("Amount ($)")
        plt.ylabel("Budget Item")
        plt.title("Top 10 Budget Items")
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout()
        bar_path = os.path.join(output_dir, f"top_items_{timestamp}.png")
        plt.savefig(bar_path)
        plt.close()
        vis_paths.append(bar_path)
    
    print(f"Report generated at: {json_path}")
    if include_visualizations:
        print(f"Visualizations saved to: {output_dir}")
    
    return {
        "json_report": json_path,
        "visualizations": vis_paths
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_report(sys.argv[1])
    else:
        print("Please provide a budget Excel file path")

