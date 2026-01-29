
"""
Comparison chart generation
"""

import json

def generate_comparison_chart_html(comparison_data):
    if not comparison_data:
        return ""
    
    return f"""
    <div class="card fade-in">
        <h2 class="card-title">📊 Comparison Visualizations</h2>
        <div class="chart-container">
            <h3>💰 Overall Budget Change</h3>
            <canvas id="overallComparisonChart" width="400" height="400"></canvas>
            <script>
                new Chart(document.getElementById('overallComparisonChart'), {{
                    type: 'bar',
                    data: {{
                        labels: ['{comparison_data['budget1_name']}', '{comparison_data['budget2_name']}'],
                        datasets: [{{
                            label: 'Total Budget',
                            data: [{comparison_data['budget1_total']}, {comparison_data['budget2_total']}],
                            backgroundColor: ['rgba(52, 152, 219, 0.7)', 'rgba(46, 204, 113, 0.7)']
                        }}]
                    }},
                    options: {{ responsive: true }}
                }});
            </script>
        </div>
    </div>
    """
