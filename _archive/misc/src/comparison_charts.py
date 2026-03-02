"""
Comparison Charts Module
Generates Chart.js configurations for budget comparison visualizations

Copyright © 2024-2025. All Rights Reserved.
PROPRIETARY AND CONFIDENTIAL
"""

from typing import Dict, List, Any
import json


def generate_side_by_side_chart(comparison_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate side-by-side bar chart comparing departments
    """
    dept_changes = comparison_data.get('department_changes', {})
    
    if not dept_changes:
        return None
    
    # Sort departments by budget2 amount
    sorted_depts = sorted(dept_changes.items(), 
                         key=lambda x: x[1]['budget2_amount'], 
                         reverse=True)
    
    departments = [dept for dept, _ in sorted_depts]
    budget1_amounts = [data['budget1_amount'] for _, data in sorted_depts]
    budget2_amounts = [data['budget2_amount'] for _, data in sorted_depts]
    
    chart_config = {
        'type': 'bar',
        'data': {
            'labels': departments,
            'datasets': [
                {
                    'label': comparison_data['budget1_name'],
                    'data': budget1_amounts,
                    'backgroundColor': 'rgba(147, 51, 234, 0.7)',  # Purple
                    'borderColor': 'rgba(147, 51, 234, 1)',
                    'borderWidth': 2
                },
                {
                    'label': comparison_data['budget2_name'],
                    'data': budget2_amounts,
                    'backgroundColor': 'rgba(59, 130, 246, 0.7)',  # Blue
                    'borderColor': 'rgba(59, 130, 246, 1)',
                    'borderWidth': 2
                }
            ]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Department Comparison: Side-by-Side',
                    'font': {
                        'size': 18,
                        'weight': 'bold'
                    }
                },
                'legend': {
                    'display': True,
                    'position': 'top'
                },
                'tooltip': {
                    'callbacks': {
                        'label': 'function(context) { return context.dataset.label + \': $\' + context.parsed.y.toLocaleString(); }'
                    }
                }
            },
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'ticks': {
                        'callback': 'function(value) { return \'$\' + value.toLocaleString(); }'
                    }
                }
            }
        }
    }
    
    return chart_config


def generate_change_chart(comparison_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate bar chart showing percentage changes by department
    """
    dept_changes = comparison_data.get('department_changes', {})
    
    if not dept_changes:
        return None
    
    # Filter out departments with no change and sort by percent change
    filtered = [(dept, data) for dept, data in dept_changes.items() 
                if data['percent_change'] != 0]
    sorted_depts = sorted(filtered, key=lambda x: x[1]['percent_change'], reverse=True)
    
    departments = [dept for dept, _ in sorted_depts]
    percent_changes = [data['percent_change'] for _, data in sorted_depts]
    
    # Color code: red for increases, green for decreases
    colors = ['rgba(239, 68, 68, 0.7)' if pc > 0 else 'rgba(34, 197, 94, 0.7)' 
              for pc in percent_changes]
    border_colors = ['rgba(239, 68, 68, 1)' if pc > 0 else 'rgba(34, 197, 94, 1)' 
                     for pc in percent_changes]
    
    chart_config = {
        'type': 'bar',
        'data': {
            'labels': departments,
            'datasets': [{
                'label': 'Percentage Change',
                'data': percent_changes,
                'backgroundColor': colors,
                'borderColor': border_colors,
                'borderWidth': 2
            }]
        },
        'options': {
            'indexAxis': 'y',  # Horizontal bars
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Budget Change by Department (%)',
                    'font': {
                        'size': 18,
                        'weight': 'bold'
                    }
                },
                'legend': {
                    'display': False
                },
                'tooltip': {
                    'callbacks': {
                        'label': 'function(context) { return context.parsed.x.toFixed(1) + \'%\'; }'
                    }
                }
            },
            'scales': {
                'x': {
                    'ticks': {
                        'callback': 'function(value) { return value + \'%\'; }'
                    }
                }
            }
        }
    }
    
    return chart_config


def generate_waterfall_chart(comparison_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate waterfall chart showing budget flow from Budget 1 to Budget 2
    """
    dept_changes = comparison_data.get('department_changes', {})
    
    if not dept_changes:
        return None
    
    # Calculate increases and decreases
    increases = [(dept, data['difference']) for dept, data in dept_changes.items() 
                 if data['difference'] > 0]
    decreases = [(dept, data['difference']) for dept, data in dept_changes.items() 
                 if data['difference'] < 0]
    
    # Sort by magnitude
    increases.sort(key=lambda x: x[1], reverse=True)
    decreases.sort(key=lambda x: abs(x[1]), reverse=True)
    
    # Build waterfall data
    labels = [comparison_data['budget1_name']]
    data = [comparison_data['budget1_total']]
    colors = ['rgba(147, 51, 234, 0.7)']  # Purple for start
    
    # Add increases
    for dept, amount in increases[:5]:  # Top 5 increases
        labels.append(f"+{dept}")
        data.append(amount)
        colors.append('rgba(34, 197, 94, 0.7)')  # Green for increases
    
    # Add decreases
    for dept, amount in decreases[:5]:  # Top 5 decreases
        labels.append(f"-{dept}")
        data.append(amount)
        colors.append('rgba(239, 68, 68, 0.7)')  # Red for decreases
    
    # Add final total
    labels.append(comparison_data['budget2_name'])
    data.append(comparison_data['budget2_total'])
    colors.append('rgba(59, 130, 246, 0.7)')  # Blue for end
    
    chart_config = {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': [{
                'label': 'Amount',
                'data': data,
                'backgroundColor': colors,
                'borderColor': [c.replace('0.7', '1') for c in colors],
                'borderWidth': 2
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Budget Flow: Waterfall Analysis',
                    'font': {
                        'size': 18,
                        'weight': 'bold'
                    }
                },
                'legend': {
                    'display': False
                },
                'tooltip': {
                    'callbacks': {
                        'label': 'function(context) { return \'$\' + Math.abs(context.parsed.y).toLocaleString(); }'
                    }
                }
            },
            'scales': {
                'y': {
                    'ticks': {
                        'callback': 'function(value) { return \'$\' + value.toLocaleString(); }'
                    }
                }
            }
        }
    }
    
    return chart_config


def generate_category_comparison_chart(comparison_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate chart comparing categories between budgets
    """
    cat_changes = comparison_data.get('category_changes', {})
    
    if not cat_changes:
        return None
    
    # Get top 10 categories by total spending across both budgets
    sorted_cats = sorted(cat_changes.items(), 
                        key=lambda x: max(x[1]['budget1_amount'], x[1]['budget2_amount']), 
                        reverse=True)[:10]
    
    categories = [cat for cat, _ in sorted_cats]
    budget1_amounts = [data['budget1_amount'] for _, data in sorted_cats]
    budget2_amounts = [data['budget2_amount'] for _, data in sorted_cats]
    
    chart_config = {
        'type': 'bar',
        'data': {
            'labels': categories,
            'datasets': [
                {
                    'label': comparison_data['budget1_name'],
                    'data': budget1_amounts,
                    'backgroundColor': 'rgba(147, 51, 234, 0.7)',
                    'borderColor': 'rgba(147, 51, 234, 1)',
                    'borderWidth': 2
                },
                {
                    'label': comparison_data['budget2_name'],
                    'data': budget2_amounts,
                    'backgroundColor': 'rgba(59, 130, 246, 0.7)',
                    'borderColor': 'rgba(59, 130, 246, 1)',
                    'borderWidth': 2
                }
            ]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Top 10 Categories: Comparison',
                    'font': {
                        'size': 18,
                        'weight': 'bold'
                    }
                },
                'legend': {
                    'display': True,
                    'position': 'top'
                },
                'tooltip': {
                    'callbacks': {
                        'label': 'function(context) { return context.dataset.label + \': $\' + context.parsed.y.toLocaleString(); }'
                    }
                }
            },
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'ticks': {
                        'callback': 'function(value) { return \'$\' + value.toLocaleString(); }'
                    }
                }
            }
        }
    }
    
    return chart_config


def generate_all_comparison_charts(comparison_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate all comparison charts and return as JSON strings
    
    Returns:
        Dictionary with chart names as keys and JSON config strings as values
    """
    charts = {}
    
    # Generate each chart
    side_by_side = generate_side_by_side_chart(comparison_data)
    if side_by_side:
        charts['sideBySideChart'] = json.dumps(side_by_side)
    
    change_chart = generate_change_chart(comparison_data)
    if change_chart:
        charts['changeChart'] = json.dumps(change_chart)
    
    waterfall = generate_waterfall_chart(comparison_data)
    if waterfall:
        charts['waterfallChart'] = json.dumps(waterfall)
    
    category_chart = generate_category_comparison_chart(comparison_data)
    if category_chart:
        charts['categoryChart'] = json.dumps(category_chart)
    
    return charts


def generate_comparison_chart_html(comparison_data: Dict[str, Any]) -> str:
    """
    Generate HTML for comparison charts section
    """
    charts = generate_all_comparison_charts(comparison_data)
    
    html = """
    <div class="section fade-in">
        <h2>📊 Visual Comparison</h2>
        <div class="charts-grid">
    """
    
    # Side-by-side chart
    if 'sideBySideChart' in charts:
        html += """
            <div class="chart-card">
                <canvas id="sideBySideChart"></canvas>
            </div>
        """
    
    # Change percentage chart
    if 'changeChart' in charts:
        html += """
            <div class="chart-card">
                <canvas id="changeChart"></canvas>
            </div>
        """
    
    # Category comparison
    if 'categoryChart' in charts:
        html += """
            <div class="chart-card">
                <canvas id="categoryChart"></canvas>
            </div>
        """
    
    # Waterfall chart
    if 'waterfallChart' in charts:
        html += """
            <div class="chart-card">
                <canvas id="waterfallChart"></canvas>
            </div>
        """
    
    html += """
        </div>
    </div>
    
    <script>
    // Initialize comparison charts
    (function() {
        const chartConfigs = """ + json.dumps(charts) + """;
        
        // Parse and fix function strings in configs
        function parseFunctions(obj) {
            if (typeof obj === 'string' && obj.startsWith('function')) {
                return eval('(' + obj + ')');
            }
            if (typeof obj === 'object' && obj !== null) {
                for (let key in obj) {
                    obj[key] = parseFunctions(obj[key]);
                }
            }
            return obj;
        }
        
        // Create each chart
        for (let chartId in chartConfigs) {
            const canvas = document.getElementById(chartId);
            if (canvas) {
                const config = JSON.parse(chartConfigs[chartId]);
                const processedConfig = parseFunctions(config);
                new Chart(canvas, processedConfig);
            }
        }
    })();
    </script>
    """
    
    return html


# Example usage
if __name__ == '__main__':
    print("Comparison Charts Module")
    print("Import this module to generate comparison visualizations")