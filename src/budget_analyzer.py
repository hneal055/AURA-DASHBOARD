"""
BudgetAnalyzer - Core functionality for budget analysis
"""

import pandas as pd
from typing import Dict, List, Optional


class BudgetAnalyzer:
    """Analyze budget data from CSV files."""
    
    def __init__(self):
        """Initialize the budget analyzer."""
        self.data = None
        self.summary = {}
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load budget data from a CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame with budget data
        """
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = {"Description", "Department", "Category", "Amount"}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing required columns: {missing}")
        
        self.data = df
        return df
    
    def get_summary(self) -> Dict:
        """
        Generate summary statistics.
        
        Returns:
            Dictionary with summary statistics
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        df = self.data
        self.summary = {
            "total_items": len(df),
            "total_amount": df["Amount"].sum(),
            "average_amount": df["Amount"].mean(),
            "min_amount": df["Amount"].min(),
            "max_amount": df["Amount"].max(),
            "departments": df["Department"].nunique(),
            "categories": df["Category"].nunique(),
        }
        
        return self.summary
    
    def analyze_by_department(self) -> pd.DataFrame:
        """
        Analyze expenses by department.
        
        Returns:
            DataFrame with department analysis
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        dept_analysis = self.data.groupby("Department")["Amount"].agg([
            ("count", "count"),
            ("total", "sum"),
            ("average", "mean"),
            ("min", "min"),
            ("max", "max")
        ]).reset_index()
        
        dept_analysis["percentage"] = (dept_analysis["total"] / dept_analysis["total"].sum() * 100).round(2)
        dept_analysis = dept_analysis.sort_values("total", ascending=False)
        
        return dept_analysis
    
    def analyze_by_category(self) -> pd.DataFrame:
        """
        Analyze expenses by category.
        
        Returns:
            DataFrame with category analysis
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        cat_analysis = self.data.groupby("Category")["Amount"].agg([
            ("count", "count"),
            ("total", "sum"),
            ("average", "mean")
        ]).reset_index()
        
        cat_analysis = cat_analysis.sort_values("total", ascending=False)
        
        return cat_analysis
    
    def get_top_expenses(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N expenses by amount.
        
        Args:
            n: Number of top expenses to return
            
        Returns:
            DataFrame with top expenses
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        top_expenses = self.data.nlargest(n, "Amount")[["Description", "Department", "Category", "Amount"]]
        top_expenses = top_expenses.reset_index(drop=True)
        
        return top_expenses
    
    def generate_insights(self) -> List[str]:
        """
        Generate insights from the data.
        
        Returns:
            List of insight strings
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        insights = []
        df = self.data
        
        # Total insights
        total = df["Amount"].sum()
        insights.append(f"Total budget: ${total:,.2f}")
        insights.append(f"Number of line items: {len(df)}")
        
        # Department insights
        dept_totals = df.groupby("Department")["Amount"].sum()
        if not dept_totals.empty:
            top_dept = dept_totals.idxmax()
            top_dept_amount = dept_totals.max()
            top_dept_pct = (top_dept_amount / total * 100)
            insights.append(f"Highest spending department: {top_dept} (${top_dept_amount:,.2f}, {top_dept_pct:.1f}%)")
        
        # Category insights
        cat_totals = df.groupby("Category")["Amount"].sum()
        if not cat_totals.empty:
            top_cat = cat_totals.idxmax()
            top_cat_amount = cat_totals.max()
            insights.append(f"Highest spending category: {top_cat} (${top_cat_amount:,.2f})")
        
        # Large expense insights
        if len(df) > 0:
            max_expense = df["Amount"].max()
            max_desc = df.loc[df["Amount"].idxmax(), "Description"]
            insights.append(f"Largest single expense: {max_desc} (${max_expense:,.2f})")
        
        return insights


def main():
    """Example usage."""
    analyzer = BudgetAnalyzer()
    print("BudgetAnalyzer created successfully!")
    
    # Try to load test file if it exists
    import os
    if os.path.exists("test_files/basic_budget.csv"):
        print("Loading test file...")
        df = analyzer.load_csv("test_files/basic_budget.csv")
        print(f"Loaded {len(df)} records")
        summary = analyzer.get_summary()
        print(f"Total: ${summary['total_amount']:,}")
    else:
        print("Test files not found. Run generate_tests.py first.")


if __name__ == "__main__":
    main()
