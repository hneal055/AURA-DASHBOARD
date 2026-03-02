"""
Budget Comparison Module
Compares two budget DataFrames and generates comprehensive analysis

Copyright © 2024-2025. All Rights Reserved.
PROPRIETARY AND CONFIDENTIAL
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DataFrame for comparison
    Ensures consistent column names and data types
    """
    df = df.copy()
    
    # Ensure Amount column is numeric
    if 'Amount' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    # Fill NaN values
    df = df.fillna('')
    
    # Standardize string columns
    string_columns = ['Description', 'Department', 'Category', 'Vendor']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    return df


def calculate_department_changes(df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate changes at department level
    """
    changes = {}
    
    if 'Department' not in df1.columns or 'Department' not in df2.columns:
        return changes
    
    # Get department totals for both budgets
    dept1 = df1.groupby('Department')['Amount'].sum()
    dept2 = df2.groupby('Department')['Amount'].sum()
    
    # Get all unique departments
    all_depts = set(dept1.index) | set(dept2.index)
    
    for dept in all_depts:
        amount1 = dept1.get(dept, 0)
        amount2 = dept2.get(dept, 0)
        
        difference = amount2 - amount1
        percent_change = ((amount2 - amount1) / amount1 * 100) if amount1 > 0 else (100 if amount2 > 0 else 0)
        
        changes[dept] = {
            'budget1_amount': float(amount1),
            'budget2_amount': float(amount2),
            'difference': float(difference),
            'percent_change': float(percent_change),
            'status': 'increased' if difference > 0 else ('decreased' if difference < 0 else 'unchanged')
        }
    
    return changes


def calculate_category_changes(df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate changes at category level
    """
    changes = {}
    
    if 'Category' not in df1.columns or 'Category' not in df2.columns:
        return changes
    
    # Get category totals for both budgets
    cat1 = df1.groupby('Category')['Amount'].sum()
    cat2 = df2.groupby('Category')['Amount'].sum()
    
    # Get all unique categories
    all_cats = set(cat1.index) | set(cat2.index)
    
    for cat in all_cats:
        amount1 = cat1.get(cat, 0)
        amount2 = cat2.get(cat, 0)
        
        difference = amount2 - amount1
        percent_change = ((amount2 - amount1) / amount1 * 100) if amount1 > 0 else (100 if amount2 > 0 else 0)
        
        changes[cat] = {
            'budget1_amount': float(amount1),
            'budget2_amount': float(amount2),
            'difference': float(difference),
            'percent_change': float(percent_change),
            'status': 'increased' if difference > 0 else ('decreased' if difference < 0 else 'unchanged')
        }
    
    return changes


def calculate_vendor_changes(df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate changes at vendor level
    """
    changes = {}
    
    if 'Vendor' not in df1.columns or 'Vendor' not in df2.columns:
        return changes
    
    # Get vendor totals for both budgets
    vendor1 = df1.groupby('Vendor')['Amount'].sum()
    vendor2 = df2.groupby('Vendor')['Amount'].sum()
    
    # Get all unique vendors
    all_vendors = set(vendor1.index) | set(vendor2.index)
    
    for vendor in all_vendors:
        if vendor == '' or vendor == 'nan':
            continue
            
        amount1 = vendor1.get(vendor, 0)
        amount2 = vendor2.get(vendor, 0)
        
        difference = amount2 - amount1
        percent_change = ((amount2 - amount1) / amount1 * 100) if amount1 > 0 else (100 if amount2 > 0 else 0)
        
        changes[vendor] = {
            'budget1_amount': float(amount1),
            'budget2_amount': float(amount2),
            'difference': float(difference),
            'percent_change': float(percent_change),
            'status': 'increased' if difference > 0 else ('decreased' if difference < 0 else 'unchanged')
        }
    
    return changes


def identify_new_items(df1: pd.DataFrame, df2: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Identify items that appear in budget2 but not in budget1
    """
    new_items = []
    
    # Create a composite key for matching items
    df1['_key'] = df1.apply(lambda x: f"{x.get('Description', '')}_{x.get('Department', '')}_{x.get('Category', '')}", axis=1)
    df2['_key'] = df2.apply(lambda x: f"{x.get('Description', '')}_{x.get('Department', '')}_{x.get('Category', '')}", axis=1)
    
    # Find keys in df2 that aren't in df1
    keys1 = set(df1['_key'])
    keys2 = set(df2['_key'])
    new_keys = keys2 - keys1
    
    for key in new_keys:
        item = df2[df2['_key'] == key].iloc[0]
        new_items.append({
            'description': str(item.get('Description', 'N/A')),
            'department': str(item.get('Department', 'N/A')),
            'category': str(item.get('Category', 'N/A')),
            'vendor': str(item.get('Vendor', 'N/A')),
            'amount': float(item.get('Amount', 0))
        })
    
    # Clean up temporary column
    df1.drop('_key', axis=1, inplace=True)
    df2.drop('_key', axis=1, inplace=True)
    
    # Sort by amount descending
    new_items = sorted(new_items, key=lambda x: x['amount'], reverse=True)
    
    return new_items


def identify_removed_items(df1: pd.DataFrame, df2: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Identify items that appear in budget1 but not in budget2
    """
    removed_items = []
    
    # Create a composite key for matching items
    df1['_key'] = df1.apply(lambda x: f"{x.get('Description', '')}_{x.get('Department', '')}_{x.get('Category', '')}", axis=1)
    df2['_key'] = df2.apply(lambda x: f"{x.get('Description', '')}_{x.get('Department', '')}_{x.get('Category', '')}", axis=1)
    
    # Find keys in df1 that aren't in df2
    keys1 = set(df1['_key'])
    keys2 = set(df2['_key'])
    removed_keys = keys1 - keys2
    
    for key in removed_keys:
        item = df1[df1['_key'] == key].iloc[0]
        removed_items.append({
            'description': str(item.get('Description', 'N/A')),
            'department': str(item.get('Department', 'N/A')),
            'category': str(item.get('Category', 'N/A')),
            'vendor': str(item.get('Vendor', 'N/A')),
            'amount': float(item.get('Amount', 0))
        })
    
    # Clean up temporary column
    df1.drop('_key', axis=1, inplace=True)
    df2.drop('_key', axis=1, inplace=True)
    
    # Sort by amount descending
    removed_items = sorted(removed_items, key=lambda x: x['amount'], reverse=True)
    
    return removed_items


def generate_insights(comparison_data: Dict[str, Any], threshold: float = 10.0) -> List[str]:
    """
    Generate AI-powered insights based on comparison data
    
    Args:
        comparison_data: The comparison results
        threshold: Percentage threshold for significant changes (default 10%)
    
    Returns:
        List of insight strings
    """
    insights = []
    
    # Overall budget change insight
    total_change = comparison_data['total_change']
    percent_change = comparison_data['percent_change']
    
    if abs(percent_change) >= threshold:
        direction = "increased" if percent_change > 0 else "decreased"
        insights.append(
            f"Overall budget {direction} by {abs(percent_change):.1f}% (${abs(total_change):,.0f}). "
            f"This is a {'significant increase' if percent_change > 20 else 'moderate change' if percent_change > 10 else 'notable change'}."
        )
    else:
        insights.append(f"Overall budget remained relatively stable with only a {abs(percent_change):.1f}% change.")
    
    # Department changes
    dept_changes = comparison_data.get('department_changes', {})
    significant_dept_changes = [(dept, data) for dept, data in dept_changes.items() 
                                if abs(data['percent_change']) >= threshold]
    
    if significant_dept_changes:
        # Sort by absolute change
        significant_dept_changes.sort(key=lambda x: abs(x[1]['difference']), reverse=True)
        
        for dept, data in significant_dept_changes[:3]:  # Top 3
            direction = "increased" if data['difference'] > 0 else "decreased"
            insights.append(
                f"{dept} department {direction} by {abs(data['percent_change']):.1f}% "
                f"(${abs(data['difference']):,.0f}). "
                f"{'Consider reviewing this significant increase.' if data['difference'] > 0 else 'Good cost savings achieved.'}"
            )
    
    # New items insight
    new_items = comparison_data.get('new_items', [])
    if len(new_items) > 0:
        total_new = sum(item['amount'] for item in new_items)
        insights.append(
            f"Added {len(new_items)} new line items totaling ${total_new:,.0f}. "
            f"{'This represents significant scope expansion.' if total_new > comparison_data['budget1_total'] * 0.1 else 'New additions are within reasonable limits.'}"
        )
    
    # Removed items insight
    removed_items = comparison_data.get('removed_items', [])
    if len(removed_items) > 0:
        total_removed = sum(item['amount'] for item in removed_items)
        insights.append(
            f"Removed {len(removed_items)} line items totaling ${total_removed:,.0f}. "
            f"This represents {(total_removed / comparison_data['budget1_total'] * 100):.1f}% of the original budget."
        )
    
    # Vendor changes
    vendor_changes = comparison_data.get('vendor_changes', {})
    new_vendors = [v for v, data in vendor_changes.items() if data['budget1_amount'] == 0]
    
    if len(new_vendors) > 3:
        insights.append(
            f"Added {len(new_vendors)} new vendors. Consider whether this increased vendor diversification "
            f"is strategic or if vendor consolidation could achieve better rates."
        )
    
    # Category analysis
    category_changes = comparison_data.get('category_changes', {})
    significant_cat_changes = [(cat, data) for cat, data in category_changes.items() 
                               if abs(data['percent_change']) >= threshold and data['budget1_amount'] > 1000]
    
    if significant_cat_changes:
        significant_cat_changes.sort(key=lambda x: abs(x[1]['difference']), reverse=True)
        top_cat = significant_cat_changes[0]
        
        direction = "increased" if top_cat[1]['difference'] > 0 else "decreased"
        insights.append(
            f"{top_cat[0]} category {direction} by {abs(top_cat[1]['percent_change']):.1f}%. "
            f"This is the largest category change and warrants investigation."
        )
    
    # Risk assessment
    if percent_change > 25:
        insights.append(
            "⚠️ Budget increased by more than 25%. Ensure stakeholders are aware and additional "
            "funding is secured. Consider implementing stricter cost controls."
        )
    elif percent_change < -15:
        insights.append(
            "Budget decreased significantly. Verify that all necessary expenses are accounted for "
            "and that cost cutting hasn't eliminated critical items."
        )
    
    return insights


def compare_budgets(df1: pd.DataFrame, df2: pd.DataFrame, 
                   budget1_name: str = "Budget 1", 
                   budget2_name: str = "Budget 2") -> Dict[str, Any]:
    """
    Main comparison function that analyzes two budgets comprehensively
    
    Args:
        df1: First budget DataFrame
        df2: Second budget DataFrame
        budget1_name: Name/label for first budget (e.g., "Q1 2025")
        budget2_name: Name/label for second budget (e.g., "Q2 2025")
    
    Returns:
        Dictionary containing comprehensive comparison data
    """
    # Normalize both DataFrames
    df1 = normalize_dataframe(df1)
    df2 = normalize_dataframe(df2)
    
    # Calculate basic totals
    total1 = float(df1['Amount'].sum())
    total2 = float(df2['Amount'].sum())
    total_change = total2 - total1
    percent_change = ((total2 - total1) / total1 * 100) if total1 > 0 else 0
    
    # Calculate detailed changes
    department_changes = calculate_department_changes(df1, df2)
    category_changes = calculate_category_changes(df1, df2)
    vendor_changes = calculate_vendor_changes(df1, df2)
    
    # Identify new and removed items
    new_items = identify_new_items(df1, df2)
    removed_items = identify_removed_items(df1, df2)
    
    # Build comparison result
    comparison_data = {
        'budget1_name': budget1_name,
        'budget2_name': budget2_name,
        'budget1_total': total1,
        'budget2_total': total2,
        'total_change': total_change,
        'percent_change': percent_change,
        'budget1_items': len(df1),
        'budget2_items': len(df2),
        'items_change': len(df2) - len(df1),
        'department_changes': department_changes,
        'category_changes': category_changes,
        'vendor_changes': vendor_changes,
        'new_items': new_items[:10],  # Top 10 new items
        'removed_items': removed_items[:10],  # Top 10 removed items
        'total_new_items': len(new_items),
        'total_removed_items': len(removed_items),
    }
    
    # Generate AI insights
    comparison_data['insights'] = generate_insights(comparison_data)
    
    # Get top changes for highlighting
    comparison_data['top_increases'] = get_top_changes(department_changes, increase=True)
    comparison_data['top_decreases'] = get_top_changes(department_changes, increase=False)
    
    return comparison_data


def get_top_changes(changes_dict: Dict[str, Dict], increase: bool = True, limit: int = 5) -> List[Tuple[str, Dict]]:
    """
    Get top increases or decreases from changes dictionary
    
    Args:
        changes_dict: Dictionary of changes (department, category, or vendor)
        increase: If True, get increases; if False, get decreases
        limit: Maximum number of items to return
    
    Returns:
        List of tuples (name, change_data) sorted by magnitude
    """
    filtered = [(name, data) for name, data in changes_dict.items() 
                if (data['difference'] > 0) == increase and data['budget1_amount'] > 0]
    
    sorted_changes = sorted(filtered, key=lambda x: abs(x[1]['difference']), reverse=True)
    
    return sorted_changes[:limit]


# Example usage
if __name__ == '__main__':
    # This is for testing purposes
    print("Budget Comparison Module")
    print("Import this module to use compare_budgets() function")