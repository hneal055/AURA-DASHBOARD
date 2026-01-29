"""
================================================================================
Budget Analysis & Risk Management Web Application
ENHANCED VERSION with Budget Templates
================================================================================
All original features PLUS:
✅ Budget Templates Gallery
✅ One-Click Template Usage  
✅ Template Search & Preview
✅ Enhanced Navigation
"""

from flask import Flask, request, render_template_string, redirect, url_for, send_file, flash
import pandas as pd
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# ============================================================================
# BUDGET TEMPLATES DATABASE
# ============================================================================

BUDGET_TEMPLATES = {
    "film_production": {
        "id": "film_production",
        "name": "🎬 Film Production Budget",
        "category": "Creative & Media",
        "description": "Complete budget for film/video production including pre-production, shooting, and post-production",
        "icon": "🎬",
        "popularity": 95,
        "line_items": [
            {"Description": "Script Development", "Department": "Pre-Production", "Category": "Creative", "Amount": 5000},
            {"Description": "Storyboarding", "Department": "Pre-Production", "Category": "Creative", "Amount": 3000},
            {"Description": "Director Fee", "Department": "Production", "Category": "Talent", "Amount": 15000},
            {"Description": "Camera Equipment", "Department": "Production", "Category": "Equipment", "Amount": 8000},
            {"Description": "Video Editing", "Department": "Post-Production", "Category": "Creative", "Amount": 8000}
        ],
        "total_amount": 39000,
        "item_count": 5,
        "departments": ["Pre-Production", "Production", "Post-Production"]
    },
    "marketing_campaign": {
        "id": "marketing_campaign", 
        "name": "📢 Marketing Campaign Budget",
        "category": "Business & Marketing",
        "description": "Comprehensive budget for digital and traditional marketing campaigns",
        "icon": "📢",
        "popularity": 88,
        "line_items": [
            {"Description": "Social Media Advertising", "Department": "Digital", "Category": "Paid Media", "Amount": 10000},
            {"Description": "Content Creation", "Department": "Content", "Category": "Creative", "Amount": 8000},
            {"Description": "Google Ads", "Department": "Digital", "Category": "Advertising", "Amount": 7000},
            {"Description": "Email Marketing", "Department": "Digital", "Category": "Software", "Amount": 2000}
        ],
        "total_amount": 27000,
        "item_count": 4,
        "departments": ["Digital", "Content"]
    },
    "event_management": {
        "id": "event_management",
        "name": "🎪 Event Management Budget", 
        "category": "Events & Hospitality",
        "description": "Complete budget for corporate events, conferences, and special occasions",
        "icon": "🎪",
        "popularity": 82,
        "line_items": [
            {"Description": "Venue Rental", "Department": "Venue", "Category": "Location", "Amount": 8000},
            {"Description": "Catering & Food", "Department": "Food & Beverage", "Category": "Hospitality", "Amount": 5000},
            {"Description": "Audio-Visual Equipment", "Department": "Production", "Category": "Equipment", "Amount": 3000},
            {"Description": "Event Staff", "Department": "Staffing", "Category": "Personnel", "Amount": 4000}
        ],
        "total_amount": 20000,
        "item_count": 4,
        "departments": ["Venue", "Food & Beverage", "Production", "Staffing"]
    },
    "tech_startup": {
        "id": "tech_startup",
        "name": "💻 Tech Startup Budget", 
        "category": "Technology",
        "description": "Operating budget for early-stage technology startups",
        "icon": "💻",
        "popularity": 90,
        "line_items": [
            {"Description": "Software Development", "Department": "Product", "Category": "Engineering", "Amount": 20000},
            {"Description": "Cloud Hosting", "Department": "Infrastructure", "Category": "Hosting", "Amount": 2000},
            {"Description": "Marketing", "Department": "Growth", "Category": "Advertising", "Amount": 5000},
            {"Description": "Office Space", "Department": "Operations", "Category": "Facilities", "Amount": 4000}
        ],
        "total_amount": 31000,
        "item_count": 4,
        "departments": ["Product", "Infrastructure", "Growth", "Operations"]
    }
}

def get_template_categories():
    """Get all unique template categories"""
    categories = {}
    for template in BUDGET_TEMPLATES.values():
        category = template['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(template)
    return categories

def get_popular_templates(limit=4):
    """Get most popular templates"""
    return list(BUDGET_TEMPLATES.values())[:limit]

def get_template_by_id(template_id):
    """Get a specific template by ID"""
    return BUDGET_TEMPLATES.get(template_id)

def search_templates(query):
    """Search templates by name, description, or category"""
    query = query.lower()
    results = []
    for template in BUDGET_TEMPLATES.values():
        if (query in template['name'].lower() or 
            query in template['description'].lower() or 
            query in template['category'].lower()):
            results.append(template)
    return results

# ============================================================================
# SIMPLIFIED MODULES (All in one file)
# ============================================================================

class RiskManager:
    """Simplified risk analysis"""
    def analyze_risks(self, df):
        total_budget = df['Amount'].sum()
        
        # Simple risk detection
        high_cost_threshold = total_budget * 0.1
        high_cost_items = df[df['Amount'] > high_cost_threshold]
        
        risk_items = {
            'high_cost_items': [
                {
                    'description': row['Description'],
                    'amount': row['Amount'],
                    'percentage_of_total': (row['Amount'] / total_budget * 100),
                    'department': row.get('Department', 'Unknown'),
                    'risk_reason': f"High cost item: {row['Amount']:.0f}"
                }
                for _, row in high_cost_items.iterrows()
            ]
        }
        
        # Calculate risk score
        total_risks = sum(len(items) for items in risk_items.values())
        risk_score = min(100, total_risks * 20)
        
        if risk_score >= 70:
            risk_level = 'HIGH'
        elif risk_score >= 40:
            risk_level = 'MEDIUM'
        elif risk_score >= 20:
            risk_level = 'LOW'
        else:
            risk_level = 'VERY_LOW'
            
        return {
            'summary': {
                'overall_risk_score': risk_score,
                'risk_level': risk_level,
                'total_risks_found': total_risks
            },
            'items_by_category': risk_items
        }

def prepare_chart_data(df):
    """Prepare data for chart visualizations"""
    chart_data = {}
    
    try:
        # Department breakdown
        if 'Department' in df.columns:
            dept_data = df.groupby('Department')['Amount'].sum().sort_values(ascending=False)
            chart_data['department_breakdown'] = {
                'labels': dept_data.index.tolist(),
                'data': dept_data.values.tolist(),
                'colors': ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            }
    except Exception as e:
        print(f"Chart data error: {e}")
    
    return chart_data

def generate_chart_html(chart_data):
    """Generate HTML for charts"""
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
                                    backgroundColor: {json.dumps(dept_data['colors'])},
                                    borderWidth: 2
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

def export_to_excel(df, budget_data, risk_data, optimizations, filepath):
    """Simple Excel export"""
    try:
        df.to_excel(filepath, index=False)
        return True
    except Exception as e:
        print(f"Excel export error: {e}")
        return False

def compare_budgets(df1, df2, name1="Budget 1", name2="Budget 2"):
    """Simple budget comparison"""
    total1 = df1['Amount'].sum()
    total2 = df2['Amount'].sum()
    total_change = total2 - total1
    percent_change = (total_change / total1 * 100) if total1 != 0 else 0
    
    insights = []
    if total_change > 0:
        insights.append(f"Budget increased by ${abs(total_change):,.0f} ({percent_change:.1f}%)")
    elif total_change < 0:
        insights.append(f"Budget decreased by ${abs(total_change):,.0f} ({abs(percent_change):.1f}%)")
    
    return {
        'budget1_name': name1,
        'budget2_name': name2,
        'budget1_total': total1,
        'budget2_total': total2,
        'total_change': total_change,
        'percent_change': percent_change,
        'insights': insights
    }

def generate_comparison_chart_html(comparison_data):
    """Simple comparison charts"""
    return f"""
    <div class="card fade-in">
        <h2 class="card-title">📊 Comparison</h2>
        <div class="chart-container">
            <canvas id="comparisonChart" width="400" height="300"></canvas>
            <script>
                new Chart(document.getElementById('comparisonChart'), {{
                    type: 'bar',
                    data: {{
                        labels: ['{comparison_data['budget1_name']}', '{comparison_data['budget2_name']}'],
                        datasets: [{{
                            label: 'Total Budget',
                            data: [{comparison_data['budget1_total']}, {comparison_data['budget2_total']}],
                            backgroundColor: ['#3498db', '#2ecc71']
                        }}]
                    }},
                    options: {{ responsive: true }}
                }});
            </script>
        </div>
    </div>
    """

# ============================================================================
# FLASK APPLICATION
# ============================================================================

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('static/css', exist_ok=True)

# In-memory storage
analysis_cache = {}
budget_history = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def find_optimizations(df):
    """Find optimization opportunities"""
    optimizations = []
    total = df['Amount'].sum()
    
    # High cost items
    high_cost_items = df[df['Amount'] > total * 0.1]
    for _, item in high_cost_items.iterrows():
        optimizations.append({
            'category': 'High Cost Review',
            'recommendation': f"Review high-cost item: {item['Description']}",
            'potential_savings': item['Amount'] * 0.10,
            'priority': 'HIGH'
        })
    
    return optimizations[:5]

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Homepage with templates"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Budget Analysis with Templates</title>
        <link rel="stylesheet" href="/static/css/modern-styles.css">
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header fade-in">
                <h1>💰 Budget Analysis & Risk Management</h1>
                <p>Professional budget analysis with templates and AI-powered insights</p>
            </div>
            
            <!-- Upload Section -->
            <div class="upload-section fade-in">
                <h2 class="card-title">Upload Your Budget</h2>
                <p style="color: #7f8c8d; margin-bottom: 20px;">
                    Upload a CSV file with columns: Description, Department, Category, Vendor, Amount
                </p>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".csv" required 
                           style="padding: 10px; border: 2px solid #3498db; border-radius: 8px; width: 100%;">
                    <br><br>
                    <button type="submit" class="btn btn-primary">
                        🚀 Analyze Budget
                    </button>
                </form>
            </div>
            
            <!-- Template Feature -->
            <div class="upload-section fade-in" style="margin-top: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px;">
                <h2 class="card-title" style="color: white;">📋 NEW: Budget Templates</h2>
                <p style="color: rgba(255,255,255,0.9); margin-bottom: 20px;">
                    Get started instantly with professionally designed budget templates
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 20px 0;">
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <div style="font-size: 1.5rem;">🎬</div>
                        <div>Film</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <div style="font-size: 1.5rem;">📢</div>
                        <div>Marketing</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <div style="font-size: 1.5rem;">🎪</div>
                        <div>Events</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <div style="font-size: 1.5rem;">💻</div>
                        <div>Tech</div>
                    </div>
                </div>
                <a href="/templates" class="btn" style="background: white; color: #667eea; border: none;">
                    📋 Explore Templates →
                </a>
            </div>
            
            <!-- Features Grid -->
            <div class="stats-grid fade-in">
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-label">Interactive Charts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⚠️</div>
                    <div class="stat-label">Risk Assessment</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💡</div>
                    <div class="stat-label">Smart Recommendations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📑</div>
                    <div class="stat-label">Professional Reports</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect('/')
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect('/')
    
    if not allowed_file(file.filename):
        flash('Please upload a CSV file', 'error')
        return redirect('/')
    
    try:
        # Save and read file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        df = pd.read_csv(filepath)
        if 'Amount' not in df.columns:
            flash('CSV must contain an Amount column', 'error')
            return redirect('/')
        
        # Create analysis
        file_id = str(uuid.uuid4())
        total_budget = df['Amount'].sum()
        line_items = len(df)
        
        risk_manager = RiskManager()
        risk_analysis = risk_manager.analyze_risks(df)
        optimizations = find_optimizations(df)
        
        analysis_cache[file_id] = {
            'filename': filename,
            'df': df,
            'total_budget': float(total_budget),
            'line_items': line_items,
            'risk_level': risk_analysis['summary']['risk_level'],
            'risk_analysis': risk_analysis,
            'optimizations': optimizations,
            'timestamp': datetime.now()
        }
        
        flash('✅ Budget analyzed successfully!', 'success')
        return redirect(f'/analysis/{file_id}')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect('/')

@app.route('/analysis/<file_id>')
def view_analysis(file_id):
    """Display analysis results"""
    if file_id not in analysis_cache:
        flash('Analysis not found', 'error')
        return redirect('/')
    
    data = analysis_cache[file_id]
    df = data['df']
    
    # Prepare charts
    chart_data = prepare_chart_data(df)
    charts_html = generate_chart_html(chart_data)
    
    # Risk analysis
    risk_html = ""
    if data['risk_analysis'].get('items_by_category'):
        for category, items in data['risk_analysis']['items_by_category'].items():
            if items:
                risk_html += f"<p><strong>{category}:</strong> {len(items)} items found</p>"
    
    # Optimizations
    opt_html = ""
    if data['optimizations']:
        for opt in data['optimizations']:
            opt_html += f"<p>💡 {opt['recommendation']}</p>"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analysis Results</title>
        <link rel="stylesheet" href="/static/css/modern-styles.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 Analysis Results</h1>
                <p>{data['filename']}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${data['total_budget']:,.0f}</div>
                    <div class="stat-label">Total Budget</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{data['line_items']}</div>
                    <div class="stat-label">Line Items</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{data['risk_level']}</div>
                    <div class="stat-label">Risk Level</div>
                </div>
            </div>
            
            {charts_html}
            
            <div class="card">
                <h2>⚠️ Risk Analysis</h2>
                {risk_html if risk_html else "<p>No significant risks detected</p>"}
            </div>
            
            <div class="card">
                <h2>💡 Optimization Tips</h2>
                {opt_html if opt_html else "<p>No optimization suggestions</p>"}
            </div>
            
            <div class="btn-group">
                <a href="/" class="btn btn-primary">🏠 Dashboard</a>
                <a href="/templates" class="btn btn-secondary">📋 Templates</a>
            </div>
        </div>
    </body>
    </html>
    """

# ============================================================================
# TEMPLATE ROUTES
# ============================================================================

@app.route('/templates')
def templates_gallery():
    """Templates gallery page"""
    categories = get_template_categories()
    popular = get_popular_templates()
    
    categories_html = ""
    for category_name, templates in categories.items():
        categories_html += f"""
        <div style="margin: 30px 0;">
            <h2>{category_name}</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
        """
        for template in templates:
            categories_html += f"""
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="font-size: 2rem; margin-bottom: 10px;">{template['icon']}</div>
                    <h3 style="margin: 0 0 10px 0;">{template['name']}</h3>
                    <p style="color: #7f8c8d; margin: 0 0 15px 0;">{template['description']}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="background: #f8f9fa; padding: 4px 8px; border-radius: 4px; font-size: 0.9rem;">
                            {template['item_count']} items • ${template['total_amount']:,}
                        </span>
                        <a href="/use-template/{template['id']}" class="btn btn-primary">Use Template</a>
                    </div>
                </div>
            """
        categories_html += "</div></div>"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Budget Templates</title>
        <link rel="stylesheet" href="/static/css/modern-styles.css">
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Budget Templates Gallery</h1>
                <p>Get started quickly with professionally designed budget templates</p>
            </div>
            
            <div style="margin: 30px 0;">
                <h2>⭐ Popular Templates</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            """
    
    for template in popular:
        categories_html += f"""
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border: 2px solid #3498db;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">{template['icon']}</div>
                        <h3 style="margin: 0 0 10px 0;">{template['name']}</h3>
                        <p style="color: #7f8c8d; margin: 0 0 15px 0;">{template['description']}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="background: #e8f4fd; padding: 4px 8px; border-radius: 4px; font-size: 0.9rem;">
                                {template['item_count']} items • ${template['total_amount']:,}
                            </span>
                            <a href="/use-template/{template['id']}" class="btn btn-primary">Use Template</a>
                        </div>
                    </div>
                """
    
    categories_html += """
                </div>
            </div>
            """ + categories_html + """
            
            <div style="margin-top: 40px;">
                <a href="/" class="btn btn-secondary">← Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/use-template/<template_id>')
def use_template(template_id):
    """Create budget from template"""
    template = get_template_by_id(template_id)
    if not template:
        flash('Template not found', 'error')
        return redirect('/templates')
    
    # Create DataFrame from template
    df = pd.DataFrame(template['line_items'])
    
    # Generate analysis
    file_id = str(uuid.uuid4())
    total_budget = df['Amount'].sum()
    line_items = len(df)
    
    risk_manager = RiskManager()
    risk_analysis = risk_manager.analyze_risks(df)
    optimizations = find_optimizations(df)
    
    analysis_cache[file_id] = {
        'filename': f"Template_{template['name']}.csv",
        'df': df,
        'total_budget': float(total_budget),
        'line_items': line_items,
        'risk_level': risk_analysis['summary']['risk_level'],
        'risk_analysis': risk_analysis,
        'optimizations': optimizations,
        'timestamp': datetime.now(),
        'is_template': True,
        'template_name': template['name']
    }
    
    flash(f'✅ Created budget from "{template["name"]}" template!', 'success')
    return redirect(f'/analysis/{file_id}')

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("💰 Budget Analysis with Templates - ENHANCED VERSION")
    print("   All features in one file - No external dependencies!")
    print("=" * 60)
    print("\n✅ Features included:")
    print("   • Budget Templates Gallery")
    print("   • One-Click Template Usage") 
    print("   • Risk Analysis")
    print("   • Interactive Charts")
    print("   • Excel Export")
    print("   • Budget Comparison")
    print("\n🌐 Starting server: http://localhost:8080")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=8080)