"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: main.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Main script for budget analysis.
"""
import os
import sys
import argparse
from budget_parser import parse_excel_budget, identify_risk_factors, generate_risk_report

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Production Budget Parser and Risk Analyzer")
    parser.add_argument("--input", "-i", required=True, help="Input budget file path")
    parser.add_argument("--output", "-o", default="./data/output", help="Output directory for reports")
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    # Check if input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    # Get file extension
    _, ext = os.path.splitext(args.input)
    if ext.lower() not in ['.xlsx', '.xls']:
        print(f"Error: Only Excel files are supported in this version. Found: {ext}")
        return 1
    
    # Process the file
    try:
        # Parse budget
        budget_data = parse_excel_budget(args.input)
        
        # Generate output filename
        basename = os.path.basename(args.input)
        filename_without_ext = os.path.splitext(basename)[0]
        output_file = os.path.join(args.output, f"{filename_without_ext}_risk_report.json")
        
        # Identify risks
        risk_data = identify_risk_factors(budget_data)
        
        # Generate report
        report = generate_risk_report(budget_data, risk_data, output_file)
        
        # Print summary
        print("
Risk Analysis Summary:")
        print(f"Budget Total: ${report['total_budget']:,.2f}")
        print(f"Risk Score: {report['risk_score']}")
        print("Risk Factors:")
        for factor, count in report['risk_summary'].items():
            print(f"  - {factor}: {count} items")
        
        print(f"
Full report saved to: {output_file}")
        return 0
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

