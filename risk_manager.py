
"""
Risk Management Module for Budget Analysis
AI-powered risk detection and assessment
"""

import pandas as pd
from datetime import datetime

class RiskManager:
    def __init__(self):
        self.risk_categories = {
            'high_cost_items': {
                'threshold': 0.1,
                'severity': 'HIGH',
                'description': 'Items costing more than 10% of total budget'
            }
        }
    
    def analyze_risks(self, df):
        total_budget = df['Amount'].sum()
        risk_items = {
            'high_cost_items': self._detect_high_cost_items(df, total_budget)
        }
        
        overall_score = self._calculate_overall_risk_score(risk_items)
        risk_level = self._get_risk_level(overall_score)
        
        return {
            'summary': {
                'overall_risk_score': overall_score,
                'risk_level': risk_level,
                'total_risks_found': sum(len(items) for items in risk_items.values())
            },
            'items_by_category': risk_items,
            'recommendations': []
        }
    
    def _detect_high_cost_items(self, df, total_budget):
        threshold = self.risk_categories['high_cost_items']['threshold']
        high_cost_threshold = total_budget * threshold
        high_cost_items = df[df['Amount'] > high_cost_threshold].copy()
        
        risks = []
        for _, item in high_cost_items.iterrows():
            percentage = (item['Amount'] / total_budget * 100) if total_budget > 0 else 0
            risks.append({
                'description': item.get('Description', 'Unknown'),
                'amount': item['Amount'],
                'percentage_of_total': percentage,
                'department': item.get('Department', 'Unknown')
            })
        return risks
    
    def _calculate_overall_risk_score(self, risk_items):
        total_risks = sum(len(items) for items in risk_items.values())
        return min(100, total_risks * 10)
    
    def _get_risk_level(self, score):
        if score >= 70: return 'HIGH'
        elif score >= 40: return 'MEDIUM'
        elif score >= 20: return 'LOW'
        else: return 'VERY_LOW'
