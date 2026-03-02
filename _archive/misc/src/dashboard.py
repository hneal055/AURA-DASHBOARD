"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: dashboard.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Production Budget Dashboard
--------------------------
A comprehensive dashboard for analyzing production budgets with risk assessment.
"""
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json

def analyze_budget(budget_file):
    """Main budget analysis function"""
    print(f"📊 Analyzing budget: {budget_file}")
    
    # Load the budget data
    df = pd.read_excel(budget_file)
    total_budget = df["Amount"].sum()
    
    # Basic statistics
    stats = {
        "total_budget": float(total_budget),
        "line_items": len(df),
        "departments": df["Department"].nunique(),
        "timestamp": datetime.now().isoformat()
    }
    
    # Department breakdown
    dept_breakdown = df.groupby("Department")["Amount"].agg(["sum", "count"])
    dept_breakdown["percentage"] = dept_breakdown["sum"] / total_budget * 100
    dept_breakdown = dept_breakdown.sort_values("sum", ascending=False)
    
    # Top budget items
    top_items = df.nlargest(10, "Amount")
    
    # Risk analysis
    risks = identify_risks(df)
    
    # Generate visualizations
    visuals = create_visualizations(df, os.path.dirname(budget_file))
    
    # Print summary
    print_summary(stats, dept_breakdown, top_items, risks)
    
    return {
        "stats": stats,
        "dept_breakdown": dept_breakdown.to_dict(),
        "top_items": top_items.to_dict("records"),
        "risks": risks,
        "visualizations": visuals
    }

def identify_risks(budget_df):
    """Identify production risks in the budget"""
    total_budget = budget_df["Amount"].sum()
    high_cost_threshold = total_budget * 0.05  # 5% of budget
    
    risks = {
        "high_cost": [],
        "weather_dependent": [],
        "talent_related": [],
        "equipment": [],
        "location": [],
        "post_production": [],
    }
    
    # Risk keywords
    risk_keywords = {
        "weather_dependent": ["exterior", "outdoor", "ext", "weather", "rain", "snow"],
        "talent_related": ["cast", "actor", "talent", "performer", "star"],
        "equipment": ["camera", "equipment", "gear", "rental", "crane", "helicopter"],
        "location": ["location", "permit", "travel", "international", "remote"],
        "post_production": ["vfx", "visual effects", "sound", "edit", "color", "mix"]
    }
    
    # Check each budget item
    for _, row in budget_df.iterrows():
        # High cost items
        if row["Amount"] >= high_cost_threshold:
            risks["high_cost"].append({
                "description": row["Description"],
                "department": row["Department"],
                "amount": float(row["Amount"]),
                "percentage": float(row["Amount"] / total_budget * 100)
            })
        
        # Keyword-based risks
        item_text = f"{row['Description']} {row.get('Notes', '')}".lower()
        
        for risk_type, keywords in risk_keywords.items():
            if any(keyword in item_text for keyword in keywords):
                risks[risk_type].append({
                    "description": row["Description"],
                    "department": row["Department"],
                    "amount": float(row["Amount"]),
                    "percentage": float(row["Amount"] / total_budget * 100)
                })
    
    # Calculate risk scores
    risk_score = calculate_risk_score(risks, total_budget)
    risks["risk_score"] = risk_score
    
    return risks

def calculate_risk_score(risks, total_budget):
    """Calculate an overall risk score from 0-100"""
    # Base weights for different risk types
    risk_weights = {
        "high_cost": 1.0,
        "weather_dependent": 2.5,
        "talent_related": 2.0,
        "equipment": 1.5,
        "location": 2.0,
        "post_production": 1.0
    }
    
    # Calculate weighted scores
    scores = []
    for risk_type, items in risks.items():
        if risk_type in risk_weights and items:
            # Calculate risk percentage (% of budget at risk)
            risk_amount = sum(item["amount"] for item in items)
            risk_percentage = (risk_amount / total_budget) * 100
            
            # Weight by risk type
            weighted_score = risk_percentage * risk_weights[risk_type]
            scores.append(weighted_score)
    
    # Normalize to 0-100 scale
    if not scores:
        return 0
        
    raw_score = sum(scores)
    # Cap at 100 and ensure it's at least 1 if there are risks
    normalized_score = min(100, raw_score)
    if normalized_score < 1 and len(scores) > 0:
        normalized_score = 1
        
    return normalized_score

def create_visualizations(df, output_dir):
    """Create budget visualizations"""
    os.makedirs("data/output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Department pie chart
    plt.figure(figsize=(10, 6))
    dept_data = df.groupby("Department")["Amount"].sum()
    dept_data = dept_data.sort_values(ascending=False)
    
    plt.pie(
        dept_data, 
        labels=dept_data.index, 
        autopct="%1.1f%%", 
        startangle=90
    )
    plt.title("Budget Allocation by Department")
    plt.axis("equal")
    
    pie_path = os.path.join("data/output", f"dept_breakdown_{timestamp}.png")
    plt.savefig(pie_path)
    plt.close()
    
    # 2. Top items bar chart
    plt.figure(figsize=(12, 8))
    top_items = df.nlargest(10, "Amount").sort_values("Amount")
    total_budget = df["Amount"].sum()
    
    plt.barh(top_items["Description"], top_items["Amount"], color="skyblue")
    for i, (_, row) in enumerate(top_items.iterrows()):
        plt.text(
            row["Amount"] + total_budget * 0.01, 
            i, 
            f"{row['Amount'] / total_budget * 100:.1f}%", 
            va="center"
        )
    
    plt.xlabel("Amount ($)")
    plt.ylabel("Budget Item")
    plt.title("Top 10 Budget Items")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    
    bar_path = os.path.join("data/output", f"top_items_{timestamp}.png")
    plt.savefig(bar_path)
    plt.close()
    
    return {
        "dept_chart": pie_path,
        "items_chart": bar_path
    }

def print_summary(stats, dept_breakdown, top_items, risks):
    """Print a summary of the analysis to the console"""
    print("\n" + "="*60)
    print(f"📊 BUDGET SUMMARY")
    print("="*60)
    print(f"Total Budget: ${stats['total_budget']:,.2f}")
    print(f"Line Items: {stats['line_items']}")
    print(f"Departments: {stats['departments']}")
    
    print("\n" + "="*60)
    print(f"🏢 DEPARTMENT BREAKDOWN")
    print("="*60)
    for dept, data in dept_breakdown.iterrows():
        print(f"{dept}: ${data['sum']:,.2f} ({data['percentage']:.1f}%) - {data['count']} items")
    
    print("\n" + "="*60)
    print(f"⚠️ RISK ANALYSIS")
    print("="*60)
    print(f"Overall Risk Score: {risks['risk_score']:.1f}/100")
    
    for risk_type, items in risks.items():
        if risk_type != "risk_score" and items:  # Skip the score
            risk_amount = sum(item["amount"] for item in items)
            risk_percentage = (risk_amount / stats['total_budget']) * 100
            print(f"{risk_type.replace('_', ' ').title()}: {len(items)} items (${risk_amount:,.2f}, {risk_percentage:.1f}% of budget)")
    
    print("\n" + "="*60)
    print(f"💰 TOP BUDGET ITEMS")
    print("="*60)
    for _, row in top_items.iterrows():
        percentage = (row["Amount"] / stats['total_budget']) * 100
        print(f"{row['Description']}: ${row['Amount']:,.2f} ({percentage:.1f}%)")
    
    print("\n" + "="*60)

def save_report(analysis_data, output_dir="data/output"):
    """Save analysis results to a JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Prepare serializable data
    report_data = {
        "stats": analysis_data["stats"],
        "top_items": analysis_data["top_items"],
        "risks": analysis_data["risks"],
        "visualizations": analysis_data["visualizations"]
    }
    
    # Save to JSON
    report_path = os.path.join(output_dir, f"production_analysis_{timestamp}.json")
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_path}")
    return report_path

def main():
    parser = argparse.ArgumentParser(description="Production Budget Analysis Dashboard")
    parser.add_argument("budget_file", help="Path to the Excel budget file")
    parser.add_argument("--output", "-o", default="data/output", help="Output directory for reports")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.budget_file):
        print(f"Error: Budget file not found: {args.budget_file}")
        return 1
    
    # Run the analysis
    analysis_data = analyze_budget(args.budget_file)
    
    # Save the report
    save_report(analysis_data, args.output)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

