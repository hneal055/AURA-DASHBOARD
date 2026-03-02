"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: enhanced_parser.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
# Save this as src/enhanced_parser.py
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

def parse_budget(excel_path):
    """Parse a budget Excel file"""
    print(f"Parsing budget file: {excel_path}")
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        print(f"Found {len(df)} rows of data")
        
        # Simple analysis
        total = df['Amount'].sum() if 'Amount' in df.columns else 0
        print(f"Total budget: ${total:,.2f}")
        
        return {
            "status": "success",
            "total": total,
            "rows": len(df),
            "data": df  # Include the dataframe in the result
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}

def identify_risks(budget_data, threshold_percentage=0.05):
    """
    Identify potential risks in the budget.
    
    Args:
        budget_data: DataFrame of budget data
        threshold_percentage: Percentage of total budget to flag as high-cost
        
    Returns:
        Dictionary of identified risks
    """
    total_budget = budget_data['Amount'].sum()
    high_cost_threshold = total_budget * threshold_percentage
    
    risks = {
        'high_cost_items': [],
        'special_equipment': [],
        'location_risks': [],
        'cast_related': []
    }
    
    # Keywords to look for in descriptions and notes
    risk_keywords = {
        'special_equipment': ['equipment', 'camera', 'underwater', 'aerial', 'crane', 'helicopter'],
        'location_risks': ['location', 'exterior', 'permit', 'travel', 'international'],
        'cast_related': ['cast', 'actor', 'talent', 'star']
    }
    
    # Analyze each budget line
    for _, row in budget_data.iterrows():
        # Check for high cost items
        if row['Amount'] >= high_cost_threshold:
            risks['high_cost_items'].append({
                'description': row['Description'],
                'amount': float(row['Amount']),
                'percentage': float(row['Amount'] / total_budget * 100)
            })
        
        # Check for keyword risks
        for risk_type, keywords in risk_keywords.items():
            # Combine description and notes (if available)
            text_fields = [str(row['Description'])]
            if 'Notes' in row and pd.notna(row['Notes']):
                text_fields.append(str(row['Notes']))
            
            text_to_check = " ".join(text_fields).lower()
            
            if any(keyword in text_to_check for keyword in keywords):
                risks[risk_type].append({
                    'description': row['Description'],
                    'amount': float(row['Amount'])
                })
    
    return risks

def analyze_by_department(budget_data):
    """Generate a breakdown of budget by department."""
    if 'Department' not in budget_data.columns:
        print("Warning: No 'Department' column found in the budget.")
        return None
        
    dept_summary = budget_data.groupby('Department')['Amount'].agg(['sum', 'count'])
    dept_summary['percentage'] = dept_summary['sum'] / budget_data['Amount'].sum() * 100
    return dept_summary.sort_values('sum', ascending=False)

def generate_basic_report(budget_data, risks, output_dir="data/output"):
    """Generate a basic report with the budget analysis"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a report name based on time
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"budget_report_{timestamp}"
    
    # Create JSON report
    report_data = {
        "total_budget": float(budget_data['Amount'].sum()),
        "line_items": len(budget_data),
        "risks": risks
    }
    
    # Add department data if available
    if 'Department' in budget_data.columns:
        report_data["departments"] = budget_data['Department'].nunique()
        report_data["summary_by_department"] = {}
        
        dept_summary = budget_data.groupby('Department')['Amount'].sum().to_dict()
        for dept, amount in dept_summary.items():
            report_data["summary_by_department"][dept] = float(amount)
    
    # Save JSON report
    json_path = os.path.join(output_dir, f"{report_name}.json")
    import json
    with open(json_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"Report saved to: {json_path}")
    return json_path

def main():
    """Main function to run the parser"""
    if len(sys.argv) <= 1:
        print("Please provide a budget Excel file path")
        return 1
    
    # Parse the budget
    excel_path = sys.argv[1]
    parse_result = parse_budget(excel_path)
    
    if parse_result['status'] == 'error':
        print(f"Error: {parse_result['message']}")
        return 1
    
    # Get the data for analysis
    budget_df = parse_result['data']
    
    # Identify risks
    risks = identify_risks(budget_df)
    
    # Print risk summary
    print("\n--- RISK ANALYSIS ---")
    print(f"High-cost items: {len(risks['high_cost_items'])}")
    print(f"Special equipment risks: {len(risks['special_equipment'])}")
    print(f"Location-related risks: {len(risks['location_risks'])}")
    print(f"Cast-related risks: {len(risks['cast_related'])}")
    
    # Print details of high-cost items
    if risks['high_cost_items']:
        print("\nHigh-cost items (>5% of budget):")
        for item in risks['high_cost_items']:
            print(f"  - {item['description']}: ${item['amount']:,.2f} ({item['percentage']:.1f}%)")
    
    # Analyze by department if possible
    dept_analysis = analyze_by_department(budget_df)
    if dept_analysis is not None:
        print("\n--- DEPARTMENT BREAKDOWN ---")
        for dept, data in dept_analysis.iterrows():
            print(f"{dept}: ${data['sum']:,.2f} ({data['percentage']:.1f}%) - {data['count']} items")
    
    # Generate a report
    report_path = generate_basic_report(budget_df, risks)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
