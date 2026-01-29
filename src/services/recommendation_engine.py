"""
Recommendation Engine for Budget Analysis
Generates intelligent, data-driven recommendations based on budget patterns
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import uuid


class RecommendationEngine:
    """
    Intelligent recommendation engine that analyzes budget data and generates
    actionable, prioritized recommendations.
    """

    # Thresholds for analysis
    CONCENTRATION_THRESHOLD = 0.40  # 40% in one department is considered concentrated
    CRITICAL_CONCENTRATION = 0.60   # 60% is critical
    HIGH_HHI = 2500  # Herfindahl-Hirschman Index threshold
    OUTLIER_MULTIPLIER = 2.0  # Std deviations for outlier detection
    CONSOLIDATION_SAVINGS = 0.12  # Estimated 12% savings from consolidation

    def __init__(self):
        """Initialize the recommendation engine."""
        self.recommendations = []

    def generate_recommendations(
        self,
        df: pd.DataFrame,
        dept_analysis: pd.DataFrame,
        cat_analysis: pd.DataFrame,
        risk_analysis: Dict
    ) -> List[Dict[str, Any]]:
        """
        Generate comprehensive recommendations based on budget data.

        Args:
            df: Raw budget DataFrame
            dept_analysis: Department analysis DataFrame
            cat_analysis: Category analysis DataFrame
            risk_analysis: Risk analysis results

        Returns:
            List of recommendation dictionaries, sorted by priority
        """
        self.recommendations = []

        # Run all analysis algorithms
        self._analyze_concentration(df, dept_analysis)
        self._detect_outliers(df, dept_analysis)
        self._analyze_balance(dept_analysis)
        self._find_optimization_opportunities(df, cat_analysis)
        self._analyze_department_dominance(dept_analysis)

        # Sort by priority (ascending) and impact score (descending)
        self.recommendations.sort(key=lambda x: (x['priority'], -x['impact_score']))

        return self.recommendations

    def _analyze_concentration(self, df: pd.DataFrame, dept_analysis: pd.DataFrame) -> None:
        """Analyze budget concentration using HHI."""
        if dept_analysis.empty:
            return

        # Calculate HHI
        hhi = (dept_analysis['percentage'] ** 2).sum()

        if hhi > self.HIGH_HHI:
            # Identify top departments
            top_depts = dept_analysis.nlargest(3, 'total')
            top_total = top_depts['total'].sum()
            total_budget = df['Amount'].sum()
            top_pct = (top_total / total_budget * 100) if total_budget > 0 else 0

            priority = 1 if hhi > 4000 else 2
            impact_score = min(100, hhi / 40)  # Scale to 0-100

            self.recommendations.append({
                'id': str(uuid.uuid4()),
                'type': 'concentration',
                'priority': priority,
                'title': f'Budget Concentrated in {len(top_depts)} Departments',
                'insight': f'{len(top_depts)} departments account for {top_pct:.1f}% of total budget (HHI: {hhi:.0f})',
                'description': 'Your budget is heavily concentrated in a few departments. High concentration can create risk if priorities shift or if these departments need budget cuts.',
                'action': f'Review spending in {", ".join(top_depts["Department"].tolist())} for potential redistribution opportunities to improve budget diversity.',
                'impact_score': impact_score,
                'estimated_savings': None,
                'affected_items': df[df['Department'].isin(top_depts['Department'])].to_dict('records'),
                'metrics': {
                    'hhi': hhi,
                    'top_departments_count': len(top_depts),
                    'concentration_percentage': top_pct
                }
            })

    def _detect_outliers(self, df: pd.DataFrame, dept_analysis: pd.DataFrame) -> None:
        """Detect statistical outliers within departments."""
        if dept_analysis.empty:
            return

        for _, dept_row in dept_analysis.iterrows():
            dept_name = dept_row['Department']
            dept_data = df[df['Department'] == dept_name].copy()

            if len(dept_data) < 3:  # Need at least 3 items for meaningful outlier detection
                continue

            # Calculate statistics
            mean = dept_data['Amount'].mean()
            std = dept_data['Amount'].std()

            if std == 0:  # All items same price
                continue

            # Find outliers (> mean + 2*std)
            threshold = mean + (self.OUTLIER_MULTIPLIER * std)
            outliers = dept_data[dept_data['Amount'] > threshold]

            if len(outliers) >= 2:  # At least 2 outliers to be significant
                outlier_total = outliers['Amount'].sum()
                dept_total = dept_data['Amount'].sum()
                outlier_pct = (outlier_total / dept_total * 100) if dept_total > 0 else 0

                # Estimate potential savings if consolidated
                estimated_savings = outlier_total * self.CONSOLIDATION_SAVINGS

                priority = 2 if len(outliers) >= 3 else 3
                impact_score = min(100, (outlier_pct * 0.8) + (len(outliers) * 5))

                self.recommendations.append({
                    'id': str(uuid.uuid4()),
                    'type': 'outlier',
                    'priority': priority,
                    'title': f'{len(outliers)} Anomalous Expenses in {dept_name}',
                    'insight': f'{dept_name} has {len(outliers)} items that are {self.OUTLIER_MULTIPLIER}x above the department average (${mean:,.2f})',
                    'description': f'Multiple high-cost items detected that deviate significantly from typical spending patterns in this department ({outlier_pct:.1f}% of department budget).',
                    'action': f'Investigate these {len(outliers)} items for potential consolidation, renegotiation, or one-time vs recurring expense classification.',
                    'impact_score': impact_score,
                    'estimated_savings': estimated_savings,
                    'affected_items': outliers.to_dict('records'),
                    'metrics': {
                        'outlier_count': len(outliers),
                        'department_mean': mean,
                        'threshold': threshold,
                        'outlier_percentage': outlier_pct
                    }
                })

    def _analyze_balance(self, dept_analysis: pd.DataFrame) -> None:
        """Analyze budget balance using Gini coefficient."""
        if len(dept_analysis) < 2:
            return

        gini = self.calculate_gini(dept_analysis)

        if gini > 0.5:  # High inequality
            # Find the imbalance
            sorted_depts = dept_analysis.sort_values('total', ascending=False)
            top_dept = sorted_depts.iloc[0]
            bottom_half = sorted_depts[len(sorted_depts)//2:]

            top_pct = top_dept['percentage']
            bottom_pct = bottom_half['percentage'].sum()

            priority = 2 if gini > 0.65 else 3
            impact_score = gini * 100

            self.recommendations.append({
                'id': str(uuid.uuid4()),
                'type': 'balance',
                'priority': priority,
                'title': 'Significant Budget Imbalance Detected',
                'insight': f'Budget distribution shows high inequality (Gini: {gini:.2f}). Top department ({top_dept["Department"]}) has {top_pct:.1f}% while bottom {len(bottom_half)} departments have {bottom_pct:.1f}% combined.',
                'description': 'Unbalanced budget distribution can indicate over-investment in some areas and under-investment in others, potentially limiting organizational flexibility.',
                'action': f'Review whether {top_dept["Department"]}\'s {top_pct:.1f}% allocation aligns with strategic priorities. Consider if resources could be reallocated to support growth in other areas.',
                'impact_score': impact_score,
                'estimated_savings': None,
                'affected_items': [],
                'metrics': {
                    'gini_coefficient': gini,
                    'top_department': top_dept['Department'],
                    'top_percentage': top_pct,
                    'bottom_half_percentage': bottom_pct
                }
            })

    def _find_optimization_opportunities(self, df: pd.DataFrame, cat_analysis: pd.DataFrame) -> None:
        """Find consolidation and optimization opportunities."""
        if cat_analysis.empty or len(df) < 10:
            return

        # Find categories that appear in multiple departments
        category_dept_counts = df.groupby('Category')['Department'].nunique()
        multi_dept_categories = category_dept_counts[category_dept_counts >= 2]

        for category in multi_dept_categories.index:
            cat_data = df[df['Category'] == category].copy()
            cat_total = cat_data['Amount'].sum()
            dept_count = cat_data['Department'].nunique()

            # Only recommend if total is significant (> 2% of budget)
            total_budget = df['Amount'].sum()
            cat_pct = (cat_total / total_budget * 100) if total_budget > 0 else 0

            if cat_pct > 2.0 and dept_count >= 2:
                estimated_savings = cat_total * self.CONSOLIDATION_SAVINGS

                priority = 3
                impact_score = cat_pct * 2  # Higher percentage = higher impact

                self.recommendations.append({
                    'id': str(uuid.uuid4()),
                    'type': 'optimization',
                    'priority': priority,
                    'title': f'{category} Consolidation Opportunity',
                    'insight': f'{category} spending is spread across {dept_count} departments, totaling ${cat_total:,.2f} ({cat_pct:.1f}% of budget)',
                    'description': f'Similar expenses in the {category} category are being purchased separately by multiple departments. Consolidating these purchases could yield volume discounts or better negotiating leverage.',
                    'action': f'Review {category} expenses across departments for potential centralized purchasing or enterprise agreements. Coordinate with {", ".join(cat_data["Department"].unique()[:3])}.',
                    'impact_score': impact_score,
                    'estimated_savings': estimated_savings,
                    'affected_items': cat_data.to_dict('records'),
                    'metrics': {
                        'category': category,
                        'department_count': dept_count,
                        'total_amount': cat_total,
                        'percentage_of_budget': cat_pct
                    }
                })

    def _analyze_department_dominance(self, dept_analysis: pd.DataFrame) -> None:
        """Identify departments with disproportionate budget share."""
        if dept_analysis.empty:
            return

        dominant_depts = dept_analysis[dept_analysis['percentage'] > (self.CONCENTRATION_THRESHOLD * 100)]

        for _, dept_row in dominant_depts.iterrows():
            dept_name = dept_row['Department']
            dept_pct = dept_row['percentage']
            dept_total = dept_row['total']

            # Determine priority based on dominance level
            if dept_pct > (self.CRITICAL_CONCENTRATION * 100):
                priority = 1
                severity = 'critical'
            elif dept_pct > 50:
                priority = 2
                severity = 'high'
            else:
                priority = 3
                severity = 'moderate'

            impact_score = min(100, dept_pct * 1.2)

            self.recommendations.append({
                'id': str(uuid.uuid4()),
                'type': 'dominance',
                'priority': priority,
                'title': f'{severity.title()} Budget Concentration in {dept_name}',
                'insight': f'{dept_name} department accounts for {dept_pct:.1f}% (${dept_total:,.2f}) of total budget',
                'description': f'A single department consuming {dept_pct:.1f}% of the budget creates {severity} risk. Budget cuts or changes to this department would have outsized impact on the organization.',
                'action': f'Review {dept_name} expenses for optimization opportunities. Consider whether this allocation reflects strategic priorities or if there are opportunities to redistribute spending.',
                'impact_score': impact_score,
                'estimated_savings': None,
                'affected_items': [],
                'metrics': {
                    'department': dept_name,
                    'percentage': dept_pct,
                    'severity': severity
                }
            })

    def calculate_health_score(self, df: pd.DataFrame) -> int:
        """
        Calculate overall budget health score (0-100).

        Higher score = healthier budget

        Args:
            df: Budget DataFrame

        Returns:
            Health score from 0-100
        """
        if df.empty:
            return 50

        score = 100

        # Penalize for high-cost items concentration
        total = df['Amount'].sum()
        if total > 0:
            high_cost_threshold = total * 0.1
            high_cost_pct = (df[df['Amount'] > high_cost_threshold]['Amount'].sum() / total * 100)
            score -= min(20, high_cost_pct * 0.5)  # Up to -20 points

        # Penalize for department concentration (HHI)
        if 'Department' in df.columns:
            dept_totals = df.groupby('Department')['Amount'].sum()
            dept_pcts = (dept_totals / total * 100) if total > 0 else dept_totals
            hhi = (dept_pcts ** 2).sum()
            if hhi > 2500:
                score -= min(25, (hhi - 2500) / 100)  # Up to -25 points

        # Penalize for imbalance (Gini)
        if 'Department' in df.columns and len(dept_totals) >= 2:
            dept_analysis_temp = pd.DataFrame({
                'Department': dept_totals.index,
                'total': dept_totals.values,
                'percentage': dept_pcts.values
            })
            gini = self.calculate_gini(dept_analysis_temp)
            score -= gini * 25  # Up to -25 points

        # Penalize for too few or too many line items
        item_count = len(df)
        if item_count < 5:
            score -= 10  # Very few items = lack of detail
        elif item_count > 100:
            score -= 5  # Too many items = might need consolidation

        # Bonus for good diversity
        if 'Category' in df.columns:
            cat_diversity = df['Category'].nunique()
            if cat_diversity >= 5:
                score += min(10, cat_diversity)  # Up to +10 points

        return max(0, min(100, int(score)))

    def calculate_hhi(self, dept_analysis: pd.DataFrame) -> float:
        """
        Calculate Herfindahl-Hirschman Index for department concentration.

        Args:
            dept_analysis: Department analysis DataFrame with 'percentage' column

        Returns:
            HHI value (0-10000, higher = more concentrated)
        """
        if dept_analysis.empty or 'percentage' not in dept_analysis.columns:
            return 0.0

        return float((dept_analysis['percentage'] ** 2).sum())

    def calculate_gini(self, dept_analysis: pd.DataFrame) -> float:
        """
        Calculate Gini coefficient for budget inequality.

        Args:
            dept_analysis: Department analysis DataFrame with 'total' column

        Returns:
            Gini coefficient (0-1, higher = more unequal)
        """
        if dept_analysis.empty or 'total' not in dept_analysis.columns:
            return 0.0

        values = dept_analysis['total'].values
        values = np.sort(values)
        n = len(values)

        if n == 0 or values.sum() == 0:
            return 0.0

        index = np.arange(1, n + 1)
        gini = (2 * np.sum(index * values)) / (n * np.sum(values)) - (n + 1) / n

        return float(max(0.0, min(1.0, gini)))
