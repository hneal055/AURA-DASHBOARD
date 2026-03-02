"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: risk_manager.py
Version: 1.0.0
Last Modified: November 2025

For licensing inquiries: [YOUR_EMAIL]
================================================================================
"""
"""
Production Risk Manager
---------------------
Identifies, quantifies, and manages production risks based on budget analysis.
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

class RiskManager:
    def __init__(self):
        """Initialize the risk manager"""
        # Define risk categories and keywords
        self.risk_categories = {
            "weather_dependent": {
                "keywords": ["exterior", "outdoor", "ext", "ext.", "location", "rain", "snow", "daylight", "night", "weather"],
                "weight": 2.5,
                "description": "Items affected by weather conditions"
            },
            "talent_related": {
                "keywords": ["cast", "actor", "talent", "performer", "star", "celebrity", "principal"],
                "weight": 2.0,
                "description": "Risks related to talent/cast availability and costs"
            },
            "special_equipment": {
                "keywords": ["camera", "equipment", "gear", "rental", "crane", "helicopter", "underwater", "aerial", "specialized"],
                "weight": 1.8,
                "description": "Specialized or expensive equipment"
            },
            "location_risks": {
                "keywords": ["location", "permit", "travel", "international", "remote", "foreign", "distant"],
                "weight": 2.2,
                "description": "Risks related to filming locations"
            },
            "schedule_sensitive": {
                "keywords": ["schedule", "timeline", "deadline", "delivery", "date", "time", "calendar"],
                "weight": 1.5,
                "description": "Items with tight scheduling constraints"
            },
            "vfx_heavy": {
                "keywords": ["vfx", "visual effects", "cgi", "animation", "post", "composite", "green screen", "motion capture"],
                "weight": 1.7,
                "description": "Visual effects intensive elements"
            },
            "stunts_action": {
                "keywords": ["stunt", "action", "fight", "explosion", "fire", "practical effects", "special effects", "sfx"],
                "weight": 2.3,
                "description": "Stunt and action sequences"
            },
            "regulatory_compliance": {
                "keywords": ["permit", "legal", "compliance", "regulation", "insurance", "liability", "requirement", "certification"],
                "weight": 1.6,
                "description": "Regulatory and compliance issues"
            }
        }
        
        # High cost threshold (percentage of total budget)
        self.high_cost_threshold = 0.05  # 5%
    
    def analyze_risks(self, budget_df):
        """
        Analyze budget data for production risks.
        
        Args:
            budget_df: DataFrame with budget data
            
        Returns:
            Dictionary of risk analysis results
        """
        total_budget = budget_df["Amount"].sum()
        high_cost_threshold = total_budget * self.high_cost_threshold
        
        # Initialize risks dictionary
        risks = {category: [] for category in self.risk_categories.keys()}
        risks["high_cost"] = []
        
        # Analyze each budget item
        for _, row in budget_df.iterrows():
            # Check for high cost items
            if row["Amount"] >= high_cost_threshold:
                risks["high_cost"].append(self._create_risk_item(row, total_budget))
            
            # Check for keyword-based risks
            item_text = ""
            for col in ["Description", "Notes", "Department"]:
                if col in row and pd.notna(row[col]):
                    item_text += str(row[col]).lower() + " "
            
            for risk_type, data in self.risk_categories.items():
                if any(keyword in item_text for keyword in data["keywords"]):
                    risks[risk_type].append(self._create_risk_item(row, total_budget))
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(risks, total_budget)
        
        # Generate risk summary
        risk_summary = {
            "overall_risk_score": risk_metrics["overall_risk_score"],
            "risk_level": self._determine_risk_level(risk_metrics["overall_risk_score"]),
            "total_budget": float(total_budget),
            "risk_categories": {
                category: {
                    "count": len(items),
                    "amount": sum(item["amount"] for item in items),
                    "percentage": sum(item["amount"] for item in items) / total_budget * 100 if items else 0,
                    "description": self.risk_categories[category]["description"] if category in self.risk_categories else "High cost items"
                }
                for category, items in risks.items() if category != "high_cost" or items
            },
            "high_risk_items": sorted(
                [item for sublist in risks.values() for item in sublist],
                key=lambda x: x["amount"],
                reverse=True
            )[:10],  # Top 10 risk items by amount
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "risks": risks,
            "metrics": risk_metrics,
            "summary": risk_summary
        }
    
    def _create_risk_item(self, row, total_budget):
        """Create a standardized risk item from a budget row"""
        return {
            "description": row.get("Description", "Unknown"),
            "department": row.get("Department", "Unknown"),
            "amount": float(row["Amount"]),
            "percentage": float(row["Amount"] / total_budget * 100),
            "notes": row.get("Notes", "")
        }
    
    def _calculate_risk_metrics(self, risks, total_budget):
        """Calculate risk metrics from identified risks"""
        # Calculate weighted risk score
        risk_score = 0
        risk_amount = 0
        risk_weights = {k: v["weight"] for k, v in self.risk_categories.items()}
        risk_weights["high_cost"] = 1.0  # Weight for high cost items
        
        for risk_type, items in risks.items():
            if items:
                # Calculate amount at risk for this category
                type_amount = sum(item["amount"] for item in items)
                risk_amount += type_amount
                
                # Apply weighting
                weight = risk_weights.get(risk_type, 1.0)
                risk_score += (type_amount / total_budget * 100) * weight
        
        # Calculate risk percentage (% of budget at risk)
        risk_percentage = risk_amount / total_budget * 100
        
        # Normalize risk score to 0-100
        normalized_score = min(100, risk_score)
        if normalized_score < 1 and risk_amount > 0:
            normalized_score = 1
        
        return {
            "overall_risk_score": float(normalized_score),
            "risk_percentage": float(risk_percentage),
            "risk_amount": float(risk_amount)
        }
    
    def _determine_risk_level(self, risk_score):
        """Determine risk level based on score"""
        if risk_score < 20:
            return "Low"
        elif risk_score < 50:
            return "Medium"
        elif risk_score < 75:
            return "High"
        else:
            return "Critical"
    
    def generate_risk_report(self, risk_analysis, output_dir="data/output"):
        """Generate a risk report from analysis results"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create report file
        report_path = os.path.join(output_dir, f"risk_report_{timestamp}.json")
        with open(report_path, "w") as f:
            json.dump(risk_analysis["summary"], f, indent=2)
        
        print(f"Risk report generated at: {report_path}")
        
        # Print risk summary
        summary = risk_analysis["summary"]
        print("\n" + "="*60)
        print("⚠️ PRODUCTION RISK SUMMARY")
        print("="*60)
        print(f"Overall Risk Score: {summary['overall_risk_score']:.1f}/100 ({summary['risk_level']} Risk)")
        print(f"Total Budget: ${summary['total_budget']:,.2f}")
        
        print("\nRisk Categories:")
        for category, data in summary["risk_categories"].items():
            if data["count"] > 0:
                print(f"- {category.replace('_', ' ').title()}: {data['count']} items (${data['amount']:,.2f}, {data['percentage']:.1f}%)")
                print(f"  {data['description']}")
        
        print("\nTop High-Risk Items:")
        for i, item in enumerate(summary["high_risk_items"][:5], 1):  # Show top 5
            print(f"{i}. {item['description']}: ${item['amount']:,.2f} ({item['percentage']:.1f}%)")
        
        return report_path

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        try:
            # Load budget data
            budget_df = pd.read_excel(sys.argv[1])
            
            # Analyze risks
            risk_manager = RiskManager()
            risk_analysis = risk_manager.analyze_risks(budget_df)
            
            # Generate report
            risk_manager.generate_risk_report(risk_analysis)
            
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print("Please provide a budget file path")

