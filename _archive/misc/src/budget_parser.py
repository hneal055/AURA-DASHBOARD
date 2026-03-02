"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: budget_parser.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Basic budget file parser for production budgeting.
"""
import os
import pandas as pd

def parse_excel_budget(file_path):
    """
    Parse an Excel budget file.
    
    Args:
        file_path: Path to the Excel budget file
        
    Returns:
        Dictionary with parsed budget data
    """
    try:
        print(f"Parsing Excel budget file: {file_path}")
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=None)
        
        # Basic structure for results
        budget_data = {
            "filename": os.path.basename(file_path),
            "total_amount": 0,
            "departments": {},
            "line_items": []
        }
        
        # Process each sheet
        for sheet_name, sheet_df in df.items():
            print(f"Processing sheet: {sheet_name}")
            
            # Try to identify amount/cost columns
            amount_columns = [col for col in sheet_df.columns if any(
                term in str(col).lower() 
                for term in ["amount", "cost", "budget", "total", "price", "subtotal"]
            )]
            
            if amount_columns:
                # If we found potential amount columns
                for col in amount_columns:
                    # Convert to numeric, ignoring errors
                    numeric_values = pd.to_numeric(sheet_df[col], errors='coerce')
                    sheet_total = numeric_values.sum()
                    
                    # Add to departments
                    budget_data["departments"][sheet_name] = {
                        "total": float(sheet_total),
                        "item_count": len(sheet_df)
                    }
                    
                    # Add to total
                    budget_data["total_amount"] += float(sheet_total)
                    
                    # Add line items
                    for _, row in sheet_df.iterrows():
                        if pd.notna(row.get(col)):
                            item = {
                                "department": sheet_name,
                                "amount": float(row.get(col, 0))
                            }
                            # Add other fields from the row
                            for column, value in row.items():
                                if column != col and pd.notna(value):
                                    item[column] = value
                            
                            budget_data["line_items"].append(item)
        
        return budget_data
        
    except Exception as e:
        print(f"Error parsing budget: {str(e)}")
        return {"error": str(e), "file": file_path}

def identify_risk_factors(budget_data):
    """
    Identify basic risk factors in budget data.
    
    Args:
        budget_data: Parsed budget data dictionary
        
    Returns:
        Dictionary of identified risk factors
    """
    risks = {
        "high_cost_items": [],
        "weather_dependent": [],
        "special_equipment": [],
        "locations": []
    }
    
    # Define risk keywords
    risk_keywords = {
        "weather_dependent": ["exterior", "ext.", "ext ", "outdoor", "rain", "snow", "daylight"],
        "special_equipment": ["crane", "helicopter", "underwater", "pyrotechnics", "stunt", "special effect"],
        "locations": ["location", "travel", "international", "remote"]
    }
    
    # Calculate threshold for high-cost items (items > 5% of total budget)
    if budget_data.get("total_amount", 0) > 0:
        threshold = budget_data["total_amount"] * 0.05
        
        # Check each line item
        for item in budget_data.get("line_items", []):
            # Check for high cost items
            if item.get("amount", 0) > threshold:
                risks["high_cost_items"].append(item)
            
            # Check for risk keywords in any field
            item_text = str(item).lower()
            
            for risk_type, keywords in risk_keywords.items():
                if any(keyword in item_text for keyword in keywords):
                    risks[risk_type].append(item)
    
    return risks

# Basic risk report
def generate_risk_report(budget_data, risk_data, output_file=None):
    """Generate a simple risk report"""
    report = {
        "budget_file": budget_data.get("filename", "Unknown"),
        "total_budget": budget_data.get("total_amount", 0),
        "risk_summary": {
            "high_cost_items": len(risk_data.get("high_cost_items", [])),
            "weather_dependent": len(risk_data.get("weather_dependent", [])),
            "special_equipment": len(risk_data.get("special_equipment", [])),
            "locations": len(risk_data.get("locations", []))
        },
        "risk_details": risk_data
    }
    
    # Calculate risk score (simple version)
    risk_score = 0
    risk_score += len(risk_data.get("high_cost_items", [])) * 5
    risk_score += len(risk_data.get("weather_dependent", [])) * 3
    risk_score += len(risk_data.get("special_equipment", [])) * 4
    risk_score += len(risk_data.get("locations", [])) * 2
    
    report["risk_score"] = risk_score
    
    # Save report if output file specified
    if output_file:
        import json
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"Risk report saved to: {output_file}")
    
    return report

