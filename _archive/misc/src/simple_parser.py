"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: simple_parser.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""

# Simple budget parser for film/TV production
import pandas as pd

def parse_budget(excel_path):
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
            "rows": len(df)
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Test with a sample file
    import sys
    if len(sys.argv) > 1:
        result = parse_budget(sys.argv[1])
        print(result)
    else:
        print("Please provide a budget Excel file path")

