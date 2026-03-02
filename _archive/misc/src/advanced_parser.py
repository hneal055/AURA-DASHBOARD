"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: advanced_parser.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Advanced Budget Parser
---------------------
Parses different budget file formats including Excel, CSV, and attempts to parse PDF.
"""
import os
import pandas as pd
import re
from datetime import datetime

class BudgetParser:
    def __init__(self):
        """Initialize the budget parser"""
        # Define common column mappings
        self.column_mappings = {
            "amount": ["amount", "cost", "total", "budget", "subtotal", "price", "estimate", "actual"],
            "description": ["description", "item", "account", "detail", "narrative", "line item"],
            "department": ["department", "dept", "category", "group", "section"],
            "notes": ["notes", "comment", "memo", "remarks", "description"]
        }
    
    def parse(self, file_path):
        """Parse a budget file based on its extension"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in ['.xlsx', '.xls']:
            return self.parse_excel(file_path)
        elif ext == '.csv':
            return self.parse_csv(file_path)
        elif ext == '.pdf':
            return self.parse_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def parse_excel(self, file_path):
        """Parse an Excel budget file"""
        try:
            # Try to read all sheets
            excel_data = pd.read_excel(file_path, sheet_name=None)
            
            # If there are multiple sheets, we need to decide which to use
            if len(excel_data) > 1:
                # Strategy: Look for sheets with budget-like keywords
                budget_sheets = []
                for sheet_name, df in excel_data.items():
                    # Check if sheet name contains budget keywords
                    if any(kw in sheet_name.lower() for kw in ["budget", "cost", "expense", "summary"]):
                        budget_sheets.append((sheet_name, df))
                
                # If we found potential budget sheets, use those
                if budget_sheets:
                    # For now, just use the first identified budget sheet
                    sheet_name, df = budget_sheets[0]
                    print(f"Using sheet: {sheet_name}")
                else:
                    # Otherwise use the first sheet that has numeric data
                    for sheet_name, df in excel_data.items():
                        if df.select_dtypes(include=['number']).shape[1] > 0:
                            print(f"Using sheet: {sheet_name}")
                            break
            else:
                # Only one sheet, use it
                sheet_name = list(excel_data.keys())[0]
                df = excel_data[sheet_name]
            
            # Process the selected sheet
            return self._process_dataframe(df)
            
        except Exception as e:
            print(f"Error parsing Excel file: {str(e)}")
            raise
    
    def parse_csv(self, file_path):
        """Parse a CSV budget file"""
        try:
            df = pd.read_csv(file_path)
            return self._process_dataframe(df)
        except Exception as e:
            print(f"Error parsing CSV file: {str(e)}")
            raise
    
    def parse_pdf(self, file_path):
        """Attempt to parse a PDF budget file (basic implementation)"""
        try:
            # This is a placeholder - PDF parsing requires more specialized libraries
            # like PyPDF2, pdfplumber, or tabula-py
            print("PDF parsing is limited. Consider converting to Excel or CSV for better results.")
            
            # Return a basic structure
            return {
                "status": "limited",
                "message": "PDF parsing is limited. Please convert to Excel or CSV.",
                "file": file_path
            }
        except Exception as e:
            print(f"Error parsing PDF file: {str(e)}")
            raise
    
    def _process_dataframe(self, df):
        """Process a dataframe to extract budget information"""
        # 1. Identify key columns
        amount_col = self._identify_column(df, self.column_mappings["amount"])
        desc_col = self._identify_column(df, self.column_mappings["description"])
        dept_col = self._identify_column(df, self.column_mappings["department"])
        notes_col = self._identify_column(df, self.column_mappings["notes"])
        
        # If we couldn't identify an amount column, we can't proceed
        if amount_col is None:
            raise ValueError("Could not identify an amount column in the budget file")
        
        # 2. Standardize the dataframe
        budget_df = pd.DataFrame()
        
        # Add Amount column (required)
        budget_df['Amount'] = df[amount_col]
        
        # Add Description column (required if found)
        if desc_col:
            budget_df['Description'] = df[desc_col]
        else:
            # Try to generate descriptions from other columns
            budget_df['Description'] = df.apply(
                lambda row: f"Item {row.name + 1}" if pd.notna(row.name) else "Unknown Item",
                axis=1
            )
        
        # Add Department column if found
        if dept_col:
            budget_df['Department'] = df[dept_col]
        
        # Add Notes column if found
        if notes_col and notes_col != desc_col:  # Don't duplicate description as notes
            budget_df['Notes'] = df[notes_col]
        
        # 3. Clean up the data
        # Convert Amount to numeric, handling currency symbols and commas
        budget_df['Amount'] = budget_df['Amount'].apply(self._clean_amount)
        
        # Drop rows with NaN or zero amounts
        budget_df = budget_df.dropna(subset=['Amount'])
        budget_df = budget_df[budget_df['Amount'] != 0]
        
        # 4. Return processed data
        return {
            "status": "success",
            "data": budget_df,
            "total_amount": budget_df['Amount'].sum(),
            "line_items": len(budget_df),
            "original_columns": list(df.columns),
            "mapped_columns": {
                "amount": amount_col,
                "description": desc_col,
                "department": dept_col,
                "notes": notes_col
            }
        }
    
    def _identify_column(self, df, possible_names):
        """Identify a column from a list of possible names"""
        # Check for exact matches first
        for col in df.columns:
            if col.lower() in possible_names:
                return col
        
        # Check for partial matches
        for col in df.columns:
            col_lower = col.lower()
            for name in possible_names:
                if name in col_lower:
                    return col
        
        # No match found
        return None
    
    def _clean_amount(self, value):
        """Clean amount values, handling currency symbols and formatting"""
        if pd.isna(value):
            return 0
            
        if isinstance(value, (int, float)):
            return value
            
        # Convert to string and clean
        value_str = str(value)
        
        # Remove currency symbols, commas, and other non-numeric characters
        # Keep negative signs and decimal points
        cleaned = re.sub(r'[^\d.-]', '', value_str)
        
        try:
            return float(cleaned)
        except:
            return 0

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        parser = BudgetParser()
        try:
            result = parser.parse(sys.argv[1])
            print(f"Successfully parsed budget file: {sys.argv[1]}")
            print(f"Total amount: ${result['total_amount']:,.2f}")
            print(f"Line items: {result['line_items']}")
            
            # Display a sample of the data
            if result['status'] == 'success':
                print("\nSample of parsed data:")
                print(result['data'].head())
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print("Please provide a budget file path")

