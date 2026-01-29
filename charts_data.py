
"""
Chart data preparation and HTML generation
"""

import json

def prepare_chart_data(df):
    chart_data = {}
    try:
        if 'Department' in df.columns:
            dept_data = df.groupby('Department')['Amount'].sum().sort_values(ascending=False)
            chart_data['department_breakdown'] = {
                'labels': dept_data.index.tolist(),
                'data': dept_data.values.tolist(),
                'colors': ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
            }
    except Exception as e:
        print(f"Chart data error: {e}")
    return chart_data

def generate_chart_html(chart_data):
    if not chart_data:
        return "<div>No chart data available</div>"
    
    html = """
    <div class="card fade-in">
        <h2 class="card-title">📊 Budget Visualizations</h2>
        <div class="charts-grid">
    """
    
    if 'department_breakdown' in chart_data:
        dept_data = chart_data['department_breakdown']
        html += f"""
            <div class="chart-container">
                <h3>🏢 Department Allocation</h3>
                <canvas id="deptChart" width="400" height="300"></canvas>
                <script>
                    setTimeout(() => {{
                        new Chart(document.getElementById('deptChart'), {{
                            type: 'doughnut',
                            data: {{
                                labels: {json.dumps(dept_data['labels'])},
                                datasets: [{{
                                    data: {json.dumps(dept_data['data'])},
                                    backgroundColor: {json.dumps(dept_data['colors'])}
                                }}]
                            }},
                            options: {{ responsive: true }}
                        }});
                    }}, 100);
                </script>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    return html
