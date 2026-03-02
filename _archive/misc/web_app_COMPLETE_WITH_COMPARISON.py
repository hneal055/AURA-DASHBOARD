"""
================================================================================
Budget Analysis & Risk Management Web Application
NOW WITH SQLITE DATABASE INTEGRATION!
Enhanced with PATH A Features: Interactive Charts, Modern UI, Excel Export
================================================================================
"""

from flask import Flask, request, render_template_string, redirect, url_for, send_file, flash
import pandas as pd
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# Import database
from database_models import db, BudgetAnalysis, BudgetLineItem, BudgetComparison, get_recent_analyses

# Import your existing modules
from risk_manager import RiskManager

# Import PATH A modules
from charts_data import prepare_chart_data, generate_chart_html
from excel_exporter import export_to_excel

# Import COMPARISON modules
from budget_comparison import compare_budgets
from comparison_charts import generate_comparison_chart_html

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_analysis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Create database tables
with app.app_context():
    db.create_all()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def find_optimizations(df):
    """
    Find optimization opportunities in the budget
    
    Args:
        df: pandas DataFrame with budget data
        
    Returns:
        list: List of optimization recommendations
    """
    optimizations = []
    
    # Check for vendor consolidation opportunities
    if 'Vendor' in df.columns:
        vendor_counts = df['Vendor'].value_counts()
        if len(vendor_counts) > 10:
            optimizations.append({
                'category': 'Vendor Management',
                'recommendation': f'Consider consolidating vendors. Currently working with {len(vendor_counts)} different vendors.',
                'potential_savings': df['Amount'].sum() * 0.05,  # Estimate 5% savings
                'priority': 'MEDIUM'
            })
    
    # Check for high-cost items
    total = df['Amount'].sum()
    high_cost_items = df[df['Amount'] > total * 0.10]
    
    if len(high_cost_items) > 0:
        optimizations.append({
            'category': 'Cost Review',
            'recommendation': f'Review {len(high_cost_items)} high-cost items that each represent >10% of total budget.',
            'potential_savings': high_cost_items['Amount'].sum() * 0.10,  # Estimate 10% savings on high items
            'priority': 'HIGH'
        })
    
    # Check for duplicate descriptions
    if 'Description' in df.columns:
        duplicates = df[df.duplicated(subset=['Description'], keep=False)]
        if len(duplicates) > 0:
            optimizations.append({
                'category': 'Budget Cleanup',
                'recommendation': f'Found {len(duplicates)} potentially duplicate line items to review.',
                'potential_savings': 0,
                'priority': 'LOW'
            })
    
    # Department-specific recommendations
    if 'Department' in df.columns:
        dept_totals = df.groupby('Department')['Amount'].sum().sort_values(ascending=False)
        if len(dept_totals) > 0:
            top_dept = dept_totals.index[0]
            top_amount = dept_totals.iloc[0]
            if top_amount > total * 0.30:
                optimizations.append({
                    'category': 'Department Analysis',
                    'recommendation': f'{top_dept} represents {(top_amount/total*100):.1f}% of total budget. Consider detailed review.',
                    'potential_savings': top_amount * 0.08,
                    'priority': 'MEDIUM'
                })
    
    return optimizations


def generate_recent_analyses():
    """
    Generate HTML for recent analyses sidebar FROM DATABASE
    """
    html = """
        <div class="recent-analyses">
            <h3>📊 Recent Analyses</h3>
            <table class="recent-table">
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Budget</th>
                        <th>Items</th>
                        <th>Risk</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Get recent analyses from database
    recent = get_recent_analyses(limit=10)
    
    for analysis in recent:
        risk_class = f"risk-{analysis.risk_level.lower()}"
        html += f"""
            <tr>
                <td><strong>{analysis.filename}</strong></td>
                <td>${analysis.total_budget:,.2f}</td>
                <td>{analysis.line_items}</td>
                <td><span class="risk-badge {risk_class}">{analysis.risk_level}</span></td>
                <td>
                    <a href="/analysis/{analysis.id}" class="btn btn-primary" style="padding: 8px 16px; font-size: 0.9rem;">
                        View
                    </a>
                </td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html


@app.route('/')
def index():
    """Homepage with upload form and recent analyses"""
    recent_analyses_html = generate_recent_analyses()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Budget Analysis & Risk Management</title>
        <link rel="stylesheet" href="/static/css/modern-styles.css">
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header fade-in">
                <h1>💰 Budget Analysis & Risk Management</h1>
                <p>Upload your budget CSV file for comprehensive analysis</p>
                <p style="font-size: 0.9rem; color: #666; margin-top: 10px;">
                    ✨ <strong>Now with Database Storage!</strong> - Your data is saved permanently
                </p>
            </div>
            
            <!-- Upload Form -->
            <div class="upload-section fade-in">
                <form action="/upload" method="post" enctype="multipart/form-data" class="upload-form">
                    <div class="form-group">
                        <label for="file">Choose CSV File:</label>
                        <input type="file" name="file" id="file" accept=".csv" required>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        📊 Analyze Budget
                    </button>
                </form>
            </div>
            
            <!-- Features Grid -->
            <div class="features-grid fade-in">
                <div class="feature-card">
                    <div class="feature-icon">📈</div>
                    <h3>Risk Assessment</h3>
                    <p>Automated risk scoring and categorization</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💡</div>
                    <h3>Smart Recommendations</h3>
                    <p>AI-powered optimization suggestions</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Visual Analytics</h3>
                    <p>Interactive charts and graphs</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📄</div>
                    <h3>Export Reports</h3>
                    <p>Excel and PDF report generation</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔄</div>
                    <h3>Budget Comparison</h3>
                    <p>Compare multiple budget versions</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💾</div>
                    <h3>Database Storage</h3>
                    <p>Never lose your analysis data!</p>
                </div>
            </div>
            
            <!-- Recent Analyses -->
            {recent_analyses_html}
        </div>
    </body>
    </html>
    """
    
    return html


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis - SAVE TO DATABASE"""
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(filepath)
        
        try:
            # Read CSV
            df = pd.read_csv(filepath)
            
            # Validate required columns
            required_cols = ['Category', 'Amount']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                flash(f'Missing required columns: {", ".join(missing_cols)}', 'error')
                return redirect(url_for('index'))
            
            # Perform risk analysis
            risk_manager = RiskManager()
            risk_analysis = risk_manager.analyze_budget(df)
            
            # Find optimizations
            optimizations = find_optimizations(df)
            
            # Calculate metrics
            total_budget = float(df['Amount'].sum())
            line_items = len(df)
            num_departments = len(set(df['Department'])) if 'Department' in df.columns else 0
            
            # Determine overall risk level
            risk_level = risk_analysis.get('overall_risk', 'MODERATE')
            risk_score = risk_analysis.get('risk_score', 0.0)
            
            # CREATE DATABASE RECORD
            analysis = BudgetAnalysis(
                id=file_id,
                filename=filename,
                total_budget=total_budget,
                line_items=line_items,
                num_departments=num_departments,
                risk_level=risk_level,
                risk_score=risk_score,
                dataframe_json=df.to_json(orient='records'),
                risk_analysis_json=json.dumps(risk_analysis),
                optimizations_json=json.dumps(optimizations),
                upload_date=datetime.now(),
                analysis_timestamp=datetime.now()
            )
            
            db.session.add(analysis)
            
            # Add individual line items
            for idx, row in df.iterrows():
                line_item = BudgetLineItem(
                    analysis_id=file_id,
                    category=str(row.get('Category', '')),
                    department=str(row.get('Department', '')) if 'Department' in df.columns else '',
                    description=str(row.get('Description', '')) if 'Description' in df.columns else '',
                    amount=float(row.get('Amount', 0)),
                    line_number=idx + 1
                )
                db.session.add(line_item)
            
            # Commit to database
            db.session.commit()
            
            flash(f'✅ Analysis complete and saved to database!', 'success')
            return redirect(url_for('view_analysis', file_id=file_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error analyzing file: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload a CSV file.', 'error')
        return redirect(url_for('index'))


@app.route('/analysis/<file_id>')
def view_analysis(file_id):
    """View detailed analysis results FROM DATABASE"""
    # Get analysis from database
    analysis = BudgetAnalysis.query.get(file_id)
    
    if not analysis:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        # Reconstruct DataFrame from JSON
        df = pd.read_json(analysis.dataframe_json)
        risk_analysis = json.loads(analysis.risk_analysis_json)
        optimizations = json.loads(analysis.optimizations_json)
        
        # Prepare chart data
        chart_data = prepare_chart_data(df)
        
        # Calculate department stats if available
        dept_stats = []
        if 'Department' in df.columns:
            total = df['Amount'].sum()
            for dept in df['Department'].unique():
                dept_df = df[df['Department'] == dept]
                dept_total = dept_df['Amount'].sum()
                dept_stats.append({
                    'name': dept,
                    'total': dept_total,
                    'percentage': (dept_total / total * 100) if total > 0 else 0,
                    'items': len(dept_df)
                })
            dept_stats.sort(key=lambda x: x['total'], reverse=True)
        
        # Generate chart HTML
        charts_html = generate_chart_html(chart_data)
        
        # Extract data safely with defaults
        filename = analysis.filename
        total_budget = analysis.total_budget
        line_items = analysis.line_items
        timestamp = analysis.analysis_timestamp
        
        # Build complete page
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Budget Analysis - {filename}</title>
            <link rel="stylesheet" href="/static/css/modern-styles.css">
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header fade-in">
                    <h1>💰 Budget Analysis Results</h1>
                    <p>{filename} - Analyzed on {timestamp.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p style="font-size: 0.9rem; color: #666;">
                        💾 Stored in database - Analysis ID: {file_id[:8]}...
                    </p>
                </div>
                
                <!-- Statistics Cards -->
                <div class="stats-grid fade-in">
                    <div class="stat-card">
                        <div class="stat-icon">💵</div>
                        <div class="stat-value">${total_budget:,.0f}</div>
                        <div class="stat-label">Total Budget</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">📋</div>
                        <div class="stat-value">{line_items}</div>
                        <div class="stat-label">Line Items</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">🏢</div>
                        <div class="stat-value">{len(set(df['Department'])) if 'Department' in df.columns else 'N/A'}</div>
                        <div class="stat-label">Departments</div>
                    </div>
                    
                    <div class="stat-card risk-{analysis.risk_level.lower()}">
                        <div class="stat-icon">⚠️</div>
                        <div class="stat-value">{analysis.risk_level}</div>
                        <div class="stat-label">Risk Level</div>
                    </div>
                </div>
"""

        # Add risk analysis section
        html += """
                <!-- Risk Analysis -->
                <div class="section-card fade-in">
                    <h2>🎯 Risk Assessment</h2>
        """
        
        if 'items_by_category' in risk_analysis:
            for category, items in risk_analysis['items_by_category'].items():
                html += f"""
                    <div class="risk-category">
                        <h3>{category.replace('_', ' ').title()} Risk ({len(items)} items)</h3>
                        <ul>
                """
                for item in items[:5]:  # Show first 5
                    html += f"""<li>{item.get('description', 'N/A')}: ${item.get('amount', 0):,.2f}</li>"""
                
                if len(items) > 5:
                    html += f"""<li><em>...and {len(items) - 5} more items</em></li>"""
                
                html += """
                        </ul>
                    </div>
                """
        
        html += """
                </div>
        """
        
        # Add charts
        html += f"""
                <!-- Visualizations -->
                <div class="section-card fade-in">
                    <h2>📊 Visual Analysis</h2>
                    {charts_html}
                </div>
        """
        
        # Add optimizations
        if optimizations:
            html += """
                <div class="section-card fade-in">
                    <h2>💡 Optimization Opportunities</h2>
                    <div class="optimizations-grid">
            """
            
            for opt in optimizations:
                priority_class = f"priority-{opt['priority'].lower()}"
                html += f"""
                    <div class="optimization-card {priority_class}">
                        <h3>{opt['category']}</h3>
                        <p>{opt['recommendation']}</p>
                        <div class="savings">
                            Potential Savings: <strong>${opt['potential_savings']:,.2f}</strong>
                        </div>
                        <div class="priority-badge">{opt['priority']} PRIORITY</div>
                    </div>
                """
            
            html += """
                    </div>
                </div>
            """
        
        # Add action buttons
        html += f"""
                <!-- Actions -->
                <div class="actions fade-in">
                    <a href="/" class="btn btn-secondary">← Back to Dashboard</a>
                    <a href="/export-excel/{file_id}" class="btn btn-success">📊 Export to Excel</a>
                    <a href="/generate-pdf/{file_id}" class="btn btn-primary">📄 Generate PDF Report</a>
                    <a href="/compare/{file_id}" class="btn btn-warning">🔄 Compare Budgets</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        flash(f'Error displaying analysis: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/export-excel/<file_id>')
def export_excel_route(file_id):
    """Export analysis to formatted Excel file FROM DATABASE"""
    analysis = BudgetAnalysis.query.get(file_id)
    
    if not analysis:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        df = pd.read_json(analysis.dataframe_json)
        
        # Prepare budget data with safe defaults
        budget_data = {
            'filename': analysis.filename,
            'total_budget': analysis.total_budget,
            'line_items': analysis.line_items,
            'num_departments': analysis.num_departments
        }
        
        # Get risk analysis
        risk_data = {
            'risk_level': analysis.risk_level,
            'overall_risk_score': analysis.risk_score
        }
        
        # Get optimizations
        optimizations = json.loads(analysis.optimizations_json)
        
        # Generate Excel file
        excel_filename = f"budget_analysis_{file_id}.xlsx"
        excel_path = os.path.join(app.config['OUTPUT_FOLDER'], excel_filename)
        
        export_to_excel(df, budget_data, risk_data, optimizations, excel_path)
        
        # Send file
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=f"{budget_data['filename']}_analysis.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error exporting to Excel: {str(e)}', 'error')
        return redirect(url_for('view_analysis', file_id=file_id))


@app.route('/generate-pdf/<file_id>')
def generate_pdf_report(file_id):
    """Generate PDF report for analysis FROM DATABASE"""
    analysis = BudgetAnalysis.query.get(file_id)
    
    if not analysis:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        from pdf_report_generator import generate_pdf_report as gen_pdf
        
        df = pd.read_json(analysis.dataframe_json)
        
        # Prepare budget data with safe defaults
        filename = analysis.filename
        budget_data = {
            'filename': filename,
            'total_budget': analysis.total_budget,
            'line_items': analysis.line_items,
            'num_departments': analysis.num_departments,
            'risk_level': analysis.risk_level,
            'departments': {}
        }
        
        # Get department breakdown
        if 'Department' in df.columns:
            total = df["Amount"].sum()
            for dept, group in df.groupby("Department"):
                dept_total = group["Amount"].sum()
                budget_data['departments'][dept] = {
                    "amount": float(dept_total),
                    "percentage": float(dept_total / total * 100) if total > 0 else 0,
                    "items": len(group)
                }
        
        # Get risk analysis
        risk_data = {
            'risk_level': analysis.risk_level,
            'overall_risk_score': analysis.risk_score,
            'risk_categories': json.loads(analysis.risk_analysis_json).get('items_by_category', {})
        }
        
        # Get optimization data
        optimizations = json.loads(analysis.optimizations_json)
        
        # Generate PDF
        pdf_filename = f"budget_report_{file_id}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        gen_pdf(budget_data, risk_data, optimizations, pdf_path, visualizations=None)
        
        # Serve the PDF
        return send_file(
            pdf_path, 
            as_attachment=True,
            download_name=f"{filename}_report.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('view_analysis', file_id=file_id))


@app.route('/compare/<file_id>')
def compare_page(file_id):
    """Show budget comparison page"""
    analysis = BudgetAnalysis.query.get(file_id)
    
    if not analysis:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    # Get all analyses for comparison selection FROM DATABASE
    all_analyses = BudgetAnalysis.query.order_by(BudgetAnalysis.upload_date.desc()).all()
    
    # Remove current analysis from options
    other_analyses = [a for a in all_analyses if a.id != file_id]
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Compare Budgets</title>
        <link rel="stylesheet" href="/static/css/modern-styles.css">
    </head>
    <body>
        <div class="container">
            <div class="header fade-in">
                <h1>🔄 Budget Comparison</h1>
                <p>Compare <strong>{analysis.filename}</strong> with another budget</p>
            </div>
            
            <div class="section-card fade-in">
                <h2>Select Budget to Compare With:</h2>
                <form action="/compare/{file_id}" method="post" class="comparison-form">
                    <div class="form-group">
                        <label for="compare_id">Choose Budget:</label>
                        <select name="compare_id" id="compare_id" required>
                            <option value="">-- Select a budget --</option>
    """
    
    for other in other_analyses:
        html += f"""
                            <option value="{other.id}">
                                {other.filename} - ${other.total_budget:,.2f} ({other.upload_date.strftime('%Y-%m-%d')})
                            </option>
        """
    
    html += """
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">🔍 Compare Budgets</button>
                    <a href="/analysis/{file_id}" class="btn btn-secondary">← Back to Analysis</a>
                </form>
            </div>
        </div>
    </body>
    </html>
    """.replace('{file_id}', file_id)
    
    return html


@app.route('/compare/<file_id>', methods=['POST'])
def compare_budgets_route(file_id):
    """Handle budget comparison FROM DATABASE"""
    compare_id = request.form.get('compare_id')
    
    if not compare_id:
        flash('Please select a budget to compare', 'error')
        return redirect(url_for('compare_page', file_id=file_id))
    
    # Get both analyses from database
    analysis1 = BudgetAnalysis.query.get(file_id)
    analysis2 = BudgetAnalysis.query.get(compare_id)
    
    if not analysis1 or not analysis2:
        flash('One or both analyses not found', 'error')
        return redirect(url_for('index'))
    
    try:
        # Reconstruct DataFrames
        df1 = pd.read_json(analysis1.dataframe_json)
        df2 = pd.read_json(analysis2.dataframe_json)
        
        # Perform comparison
        comparison_result = compare_budgets(df1, df2, analysis1.filename, analysis2.filename)
        
        # Save comparison to database
        comparison_record = BudgetComparison(
            analysis1_id=file_id,
            analysis2_id=compare_id,
            comparison_data_json=json.dumps(comparison_result),
            comparison_date=datetime.now()
        )
        db.session.add(comparison_record)
        db.session.commit()
        
        # Generate comparison charts
        comparison_charts = generate_comparison_chart_html(comparison_result)
        
        # Build comparison results page
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Budget Comparison Results</title>
            <link rel="stylesheet" href="/static/css/modern-styles.css">
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        </head>
        <body>
            <div class="container">
                <div class="header fade-in">
                    <h1>🔄 Budget Comparison Results</h1>
                    <p>Comparing: <strong>{analysis1.filename}</strong> vs <strong>{analysis2.filename}</strong></p>
                    <p style="font-size: 0.9rem; color: #666;">
                        💾 Comparison saved to database
                    </p>
                </div>
                
                <!-- Summary Stats -->
                <div class="stats-grid fade-in">
                    <div class="stat-card">
                        <div class="stat-icon">📊</div>
                        <div class="stat-value">{analysis1.filename}</div>
                        <div class="stat-label">${analysis1.total_budget:,.2f}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">📊</div>
                        <div class="stat-value">{analysis2.filename}</div>
                        <div class="stat-label">${analysis2.total_budget:,.2f}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">{'📈' if analysis2.total_budget > analysis1.total_budget else '📉'}</div>
                        <div class="stat-value">${abs(analysis2.total_budget - analysis1.total_budget):,.2f}</div>
                        <div class="stat-label">Difference</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">%</div>
                        <div class="stat-value">{((analysis2.total_budget - analysis1.total_budget) / analysis1.total_budget * 100):+.1f}%</div>
                        <div class="stat-label">Change</div>
                    </div>
                </div>
                
                <!-- Comparison Charts -->
                <div class="section-card fade-in">
                    <h2>📊 Visual Comparison</h2>
                    {comparison_charts}
                </div>
                
                <!-- Detailed Comparison -->
                <div class="section-card fade-in">
                    <h2>📋 Detailed Breakdown</h2>
        """
        
        # Add category comparison if available
        if 'category_comparison' in comparison_result:
            html += """
                    <table class="comparison-table">
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>Budget 1</th>
                                <th>Budget 2</th>
                                <th>Difference</th>
                                <th>% Change</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for category, data in comparison_result['category_comparison'].items():
                diff = data['budget2'] - data['budget1']
                pct_change = (diff / data['budget1'] * 100) if data['budget1'] > 0 else 0
                arrow = '↑' if diff > 0 else '↓' if diff < 0 else '='
                
                html += f"""
                            <tr>
                                <td><strong>{category}</strong></td>
                                <td>${data['budget1']:,.2f}</td>
                                <td>${data['budget2']:,.2f}</td>
                                <td style="color: {'red' if diff > 0 else 'green' if diff < 0 else 'black'};">
                                    {arrow} ${abs(diff):,.2f}
                                </td>
                                <td style="color: {'red' if pct_change > 0 else 'green' if pct_change < 0 else 'black'};">
                                    {pct_change:+.1f}%
                                </td>
                            </tr>
                """
            
            html += """
                        </tbody>
                    </table>
            """
        
        html += f"""
                </div>
                
                <!-- Actions -->
                <div class="actions fade-in">
                    <a href="/analysis/{file_id}" class="btn btn-secondary">← Back to Analysis</a>
                    <a href="/" class="btn btn-primary">🏠 Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error comparing budgets: {str(e)}', 'error')
        return redirect(url_for('compare_page', file_id=file_id))


if __name__ == '__main__':
    print("=" * 80)
    print(">> Budget Analysis & Risk Management System")
    print("   NOW WITH DATABASE INTEGRATION!")
    print("=" * 80)
    print("\n** Features:")
    print("  * SQLite database storage (persistent data!)")
    print("  * Interactive Chart.js visualizations")
    print("  * Modern responsive UI design")
    print("  * Excel export with formatting")
    print("  * PDF report generation")
    print("  * Risk assessment & recommendations")
    print("  * Budget comparison tool")
    print("\n>> Starting server at: http://localhost:8080")
    print("** Port 8080 is used to avoid Windows socket permission issues")
    print("=" * 80)
    print()
    
    # Use port 8080 to avoid common Windows socket permission errors
    # Port 5000 is often blocked by Windows services or Hyper-V
    app.run(debug=True, host='0.0.0.0', port=8080)