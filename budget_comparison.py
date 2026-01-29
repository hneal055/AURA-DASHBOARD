
"""
Budget comparison functionality
"""

import pandas as pd

def compare_budgets(df1, df2, name1="Budget 1", name2="Budget 2"):
    total1 = df1['Amount'].sum()
    total2 = df2['Amount'].sum()
    total_change = total2 - total1
    percent_change = (total_change / total1 * 100) if total1 != 0 else 0
    
    dept_changes = {}
    if 'Department' in df1.columns and 'Department' in df2.columns:
        all_depts = set(df1['Department'].unique()) | set(df2['Department'].unique())
        for dept in all_depts:
            amount1 = df1[df1['Department'] == dept]['Amount'].sum()
            amount2 = df2[df2['Department'] == dept]['Amount'].sum()
            difference = amount2 - amount1
            dept_changes[dept] = {
                'budget1_amount': amount1,
                'budget2_amount': amount2,
                'difference': difference,
                'percent_change': (difference / amount1 * 100) if amount1 != 0 else 0,
                'status': 'increased' if difference > 0 else 'decreased' if difference < 0 else 'unchanged'
            }
    
    insights = []
    if total_change > 0:
        insights.append(f"Budget increased by ${abs(total_change):,.0f}")
    elif total_change < 0:
        insights.append(f"Budget decreased by ${abs(total_change):,.0f}")
    
    return {
        'budget1_name': name1,
        'budget2_name': name2,
        'budget1_total': total1,
        'budget2_total': total2,
        'total_change': total_change,
        'percent_change': percent_change,
        'department_changes': dept_changes,
        'insights': insights
    }
