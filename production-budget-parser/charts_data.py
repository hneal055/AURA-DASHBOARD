"""
================================================================================
INTERACTIVE CHARTS MODULE
Chart.js Implementation for Budget Analysis
================================================================================
"""

# This file contains the Python functions to generate chart data
# The actual charts are rendered in JavaScript (see charts.js)

import json

def prepare_chart_data(df):
    """
    Prepare all chart data for visualization
    
    Args:
        df: pandas DataFrame with budget data
        
    Returns:
        dict: Dictionary containing all chart data in JSON-ready format
    """
    chart_data = {
        'department_pie': prepare_department_pie(df),
        'top_items_bar': prepare_top_items_bar(df),
        'category_breakdown': prepare_category_breakdown(df),
        'risk_distribution': prepare_risk_distribution(df),
        'spending_trend': prepare_spending_trend(df)
    }
    
    return chart_data


def prepare_department_pie(df):
    """Prepare data for department allocation pie chart"""
    if 'Department' not in df.columns:
        return {'labels': [], 'values': [], 'colors': []}
    
    dept_totals = df.groupby('Department')['Amount'].sum().sort_values(ascending=False)
    
    # Color palette
    colors = [
        '#3498db', '#e74c3c', '#2ecc71', '#f39c12', 
        '#9b59b6', '#1abc9c', '#34495e', '#e67e22',
        '#16a085', '#c0392b', '#27ae60', '#d35400'
    ]
    
    return {
        'labels': dept_totals.index.tolist(),
        'values': [float(v) for v in dept_totals.values],
        'colors': colors[:len(dept_totals)]
    }


def prepare_top_items_bar(df):
    """Prepare data for top budget items bar chart"""
    top_items = df.nlargest(10, 'Amount')
    
    # Truncate long descriptions
    labels = [desc[:40] + '...' if len(desc) > 40 else desc 
              for desc in top_items['Description'].fillna('Unknown')]
    
    return {
        'labels': labels,
        'values': [float(v) for v in top_items['Amount'].values],
        'departments': top_items['Department'].fillna('Unknown').tolist() if 'Department' in top_items.columns else []
    }


def prepare_category_breakdown(df):
    """Prepare data for category breakdown chart"""
    if 'Category' not in df.columns:
        return {'labels': [], 'values': []}
    
    category_totals = df.groupby('Category')['Amount'].sum().sort_values(ascending=False).head(8)
    
    return {
        'labels': category_totals.index.tolist(),
        'values': [float(v) for v in category_totals.values]
    }


def prepare_risk_distribution(df):
    """Prepare data for risk distribution doughnut chart"""
    # This is a simplified version - you can enhance with actual risk calculations
    total_amount = df['Amount'].sum()
    
    # Simple risk categorization based on amount thresholds
    high_risk = df[df['Amount'] > total_amount * 0.1]['Amount'].sum()
    medium_risk = df[(df['Amount'] > total_amount * 0.02) & (df['Amount'] <= total_amount * 0.1)]['Amount'].sum()
    low_risk = total_amount - high_risk - medium_risk
    
    return {
        'labels': ['Low Risk', 'Medium Risk', 'High Risk'],
        'values': [float(low_risk), float(medium_risk), float(high_risk)],
        'colors': ['#2ecc71', '#f39c12', '#e74c3c']
    }


def prepare_spending_trend(df):
    """Prepare data for spending trend line chart (if dates available)"""
    # Placeholder - you can enhance this if your data has dates
    if 'Date' not in df.columns and 'Month' not in df.columns:
        return {'labels': [], 'values': []}
    
    # Example implementation if you have date data
    return {
        'labels': [],
        'values': []
    }


def generate_chart_html(chart_data):
    """
    Generate HTML with embedded chart data
    
    Args:
        chart_data: Dictionary of chart data from prepare_chart_data()
        
    Returns:
        str: HTML string with charts
    """
    
    html = f"""
    <div class="charts-section">
        <h2 class="section-title">📊 Visual Analysis</h2>
        
        <div class="charts-grid">
            <!-- Department Allocation Pie Chart -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3>Department Allocation</h3>
                    <span class="chart-subtitle">Budget distribution across departments</span>
                </div>
                <canvas id="departmentPieChart"></canvas>
            </div>
            
            <!-- Top Items Bar Chart -->
            <div class="chart-container chart-wide">
                <div class="chart-header">
                    <h3>Top 10 Budget Items</h3>
                    <span class="chart-subtitle">Highest spending line items</span>
                </div>
                <canvas id="topItemsBarChart"></canvas>
            </div>
            
            <!-- Category Breakdown -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3>Category Breakdown</h3>
                    <span class="chart-subtitle">Spending by category</span>
                </div>
                <canvas id="categoryChart"></canvas>
            </div>
            
            <!-- Risk Distribution -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3>Risk Distribution</h3>
                    <span class="chart-subtitle">Budget allocation by risk level</span>
                </div>
                <canvas id="riskChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // Chart data embedded from Python
        const chartData = {json.dumps(chart_data, indent=2)};

        // Run after all deferred scripts (charts.js) have loaded
        window.addEventListener('load', function() {{
            if (typeof initializeCharts === 'function') {{
                initializeCharts(chartData);
            }} else {{
                // Fallback: retry once after short delay
                setTimeout(function() {{
                    if (typeof initializeCharts === 'function') {{
                        initializeCharts(chartData);
                    }}
                }}, 200);
            }}
        }});
    </script>
    """
    
    return html


# Example usage in your Flask route:
"""
@app.route('/analysis/<file_id>')
def view_analysis(file_id):
    # ... existing code ...
    
    # Prepare chart data
    chart_data = prepare_chart_data(df)
    
    # Generate chart HTML
    charts_html = generate_chart_html(chart_data)
    
    # Add to your existing HTML
    html += charts_html
    
    return render_template_string(html)
"""