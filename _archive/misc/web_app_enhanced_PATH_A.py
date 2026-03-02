"""
================================================================================
Budget Analysis & Risk Management Web Application
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

# Import your existing modules
from risk_manager import RiskManager

# Import PATH A modules
from charts_data import prepare_chart_data, generate_chart_html
from excel_exporter import export_to_excel

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

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

# In-memory cache for analysis results
analysis_cache = {}


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
    high_cost_items = df[df['Amount'] > total * 0.1]
    if len(high_cost_items) > 0:
        for _, item in high_cost_items.iterrows():
            optimizations.append({
                'category': 'High Cost Review',
                'recommendation': f"Review high-cost item: {item.get('Description', 'Unknown')} (${item['Amount']:,.2f})",
                'potential_savings': item['Amount'] * 0.10,  # Estimate 10% savings
                'priority': 'HIGH'
            })
    
    # Check for duplicate or similar items
    if 'Description' in df.columns:
        descriptions = df['Description'].str.lower().str.strip()
        duplicates = descriptions[descriptions.duplicated(keep=False)]
        if len(duplicates) > 0:
            optimizations.append({
                'category': 'Duplicate Items',
                'recommendation': f'Found {len(duplicates)} potential duplicate line items. Review for consolidation.',
                'potential_savings': df[df['Description'].str.lower().str.strip().isin(duplicates)]['Amount'].sum() * 0.15,
                'priority': 'MEDIUM'
            })
    
    return optimizations[:10]  # Return top 10 recommendations


@app.route('/')
def index():
    """Homepage with modern UI"""
    html = """
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
                <p>Professional budget analysis with AI-powered insights and interactive visualizations</p>
            </div>
            
            <!-- Upload Section -->
            <div class="upload-section fade-in">
                <h2 class="card-title">Upload Your Budget</h2>
                <p style="color: #7f8c8d; margin-bottom: 20px;">
                    Upload a CSV file with columns: Description, Department, Category, Vendor, Amount
                </p>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <div class="upload-area">
                        <div class="upload-icon">📁</div>
                        <div class="upload-text">Drop your CSV file here or click to browse</div>
                        <div class="upload-hint">Supports CSV files up to 16MB</div>
                        <br><br>
                        <input type="file" name="file" accept=".csv" required 
                               style="padding: 10px; font-size: 1rem; border: 2px solid #3498db; border-radius: 8px;">
                    </div>
                    <br>
                    <button type="submit" class="btn btn-primary" style="font-size: 1.2rem; padding: 15px 40px;">
                        🚀 Analyze Budget
                    </button>
                </form>
            </div>
            
            <!-- Features Grid -->
            <div class="stats-grid fade-in">
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-label">Interactive Charts</div>
                    <p style="font-size: 0.9rem; color: #7f8c8d; margin-top: 10px;">
                        Beautiful visualizations with Chart.js
                    </p>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⚠️</div>
                    <div class="stat-label">Risk Assessment</div>
                    <p style="font-size: 0.9rem; color: #7f8c8d; margin-top: 10px;">
                        AI-powered risk detection
                    </p>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💡</div>
                    <div class="stat-label">Smart Recommendations</div>
                    <p style="font-size: 0.9rem; color: #7f8c8d; margin-top: 10px;">
                        Actionable optimization tips
                    </p>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📑</div>
                    <div class="stat-label">Professional Reports</div>
                    <p style="font-size: 0.9rem; color: #7f8c8d; margin-top: 10px;">
                        PDF & Excel exports
                    </p>
                </div>
            </div>
            
            <!-- Recent Analyses (if any in cache) -->
            """ + generate_recent_analyses() + """
            
        </div>
    </body>
    </html>
    """
    return html


def generate_recent_analyses():
    """Generate HTML for recent analyses in cache"""
    if not analysis_cache:
        return ""
    
    html = """
    <div class="card fade-in">
        <h2 class="card-title">📋 Recent Analyses</h2>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Budget</th>
                    <th>Items</th>
                    <th>Risk</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for file_id, data in list(analysis_cache.items())[:10]:  # Show last 10
        risk_class = f"risk-{data['risk_level'].lower()}"
        html += f"""
            <tr>
                <td><strong>{data['filename']}</strong></td>
                <td>${data['total_budget']:,.2f}</td>
                <td>{data['line_items']}</td>
                <td><span class="risk-badge {risk_class}">{data['risk_level']}</span></td>
                <td>
                    <a href="/analysis/{file_id}" class="btn btn-primary" style="padding: 8px 16px; font-size: 0.9rem;">
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


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a CSV file.', 'error')
            return redirect(url_for('index'))
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read and analyze
        df = pd.read_csv(filepath)
        
        # Validate required columns
        if 'Amount' not in df.columns:
            flash('CSV must contain an "Amount" column', 'error')
            return redirect(url_for('index'))
        
        # Generate unique ID for this analysis
        file_id = str(uuid.uuid4())
        
        # Calculate basic metrics
        total_budget = df['Amount'].sum()
        line_items = len(df)
        
        # Run risk analysis
        risk_manager = RiskManager()
        risk_analysis = risk_manager.analyze_risks(df)
        
        # Find optimizations
        optimizations = find_optimizations(df)
        
        # Store in cache
        analysis_cache[file_id] = {
            'filename': filename,
            'filepath': filepath,
            'df': df,
            'total_budget': float(total_budget),
            'line_items': line_items,
            'risk_level': risk_analysis['summary']['risk_level'],
            'risk_score': risk_analysis['summary']['overall_risk_score'],
            'risk_analysis': risk_analysis,
            'optimizations': optimizations,
            'timestamp': datetime.now()
        }
        
        return redirect(url_for('view_analysis', file_id=file_id))
        
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('index'))


@app.route('/analysis/<file_id>')
def view_analysis(file_id):
    """Display analysis results with interactive charts"""
    if file_id not in analysis_cache:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        data = analysis_cache[file_id]
        df = data['df']
        risk_analysis = data['risk_analysis']
        optimizations = data['optimizations']
        
        # Prepare chart data
        chart_data = prepare_chart_data(df)
        
        # Calculate department stats if available
        dept_html = ""
        if 'Department' in df.columns:
            dept_totals = df.groupby('Department')['Amount'].agg(['sum', 'count']).sort_values('sum', ascending=False)
            total = df['Amount'].sum()
            
            dept_html = """
            <div class="card fade-in">
                <div class="card-header">
                    <h2 class="card-title">🏢 Department Breakdown</h2>
                    <p class="card-subtitle">Budget allocation by department</p>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Department</th>
                            <th>Amount</th>
                            <th>Percentage</th>
                            <th>Items</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for dept, row in dept_totals.iterrows():
                amount = row['sum']
                count = row['count']
                percentage = (amount / total * 100) if total > 0 else 0
                
                dept_html += f"""
                    <tr>
                        <td><strong>{dept}</strong></td>
                        <td>${amount:,.2f}</td>
                        <td>{percentage:.1f}%</td>
                        <td>{int(count)}</td>
                    </tr>
                """
            
            dept_html += """
                    </tbody>
                </table>
            </div>
            """
        
        # Risk categories
        risk_html = ""
        if risk_analysis.get('items_by_category', {}):
            risk_html = """
            <div class="card fade-in">
                <div class="card-header">
                    <h2 class="card-title">⚠️ Risk Analysis</h2>
                    <p class="card-subtitle">Items flagged for review</p>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Count</th>
                            <th>Total Amount</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for category, items in risk_analysis.get('items_by_category', {}).items():
                if items:
                    total_amount = sum(item.get('amount', 0) for item in items)
                    risk_html += f"""
                        <tr>
                            <td><strong>{category.replace('_', ' ').title()}</strong></td>
                            <td>{len(items)}</td>
                            <td>${total_amount:,.2f}</td>
                        </tr>
                    """
            
            risk_html += """
                    </tbody>
                </table>
            </div>
            """
        
        # Optimizations
        opt_html = ""
        if optimizations:
            opt_html = """
            <div class="card fade-in">
                <div class="card-header">
                    <h2 class="card-title">💡 Optimization Recommendations</h2>
                    <p class="card-subtitle">Actionable ways to improve your budget</p>
                </div>
            """
            
            total_savings = sum(opt.get('potential_savings', 0) for opt in optimizations)
            
            for i, opt in enumerate(optimizations[:5], 1):  # Show top 5
                priority = opt.get('priority', 'MEDIUM')
                priority_class = f"risk-{priority.lower()}"
                savings = opt.get('potential_savings', 0)
                
                opt_html += f"""
                <div style="padding: 15px; margin: 10px 0; background: #f8f9fa; border-left: 4px solid #3498db; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{i}. {opt.get('recommendation', '')}</strong>
                            <br>
                            <span class="risk-badge {priority_class}" style="margin-top: 5px; display: inline-block;">
                                {priority} Priority
                            </span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2rem; font-weight: bold; color: #27ae60;">
                                ${savings:,.2f}
                            </div>
                            <div style="font-size: 0.85rem; color: #7f8c8d;">
                                Potential Savings
                            </div>
                        </div>
                    </div>
                </div>
                """
            
            opt_html += f"""
                <div style="margin-top: 20px; padding: 15px; background: #d5f4e6; border-radius: 8px; text-align: center;">
                    <strong style="font-size: 1.2rem; color: #27ae60;">
                        Total Potential Savings: ${total_savings:,.2f}
                    </strong>
                </div>
            </div>
            """
        
        # Generate chart HTML
        charts_html = generate_chart_html(chart_data)
        
        # Build complete page
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Budget Analysis - {data['filename']}</title>
            <link rel="stylesheet" href="/static/css/modern-styles.css">
            <script src="/static/js/chart.umd.js"></script>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header fade-in">
                    <h1>💰 Budget Analysis Results</h1>
                    <p>{data['filename']} - Analyzed on {data['timestamp'].strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <!-- Statistics Cards -->
                <div class="stats-grid fade-in">
                    <div class="stat-card">
                        <div class="stat-icon">💵</div>
                        <div class="stat-value">${data['total_budget']:,.0f}</div>
                        <div class="stat-label">Total Budget</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">📋</div>
                        <div class="stat-value">{data['line_items']}</div>
                        <div class="stat-label">Line Items</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">🏢</div>
                        <div class="stat-value">{len(set(df['Department'])) if 'Department' in df.columns else 'N/A'}</div>
                        <div class="stat-label">Departments</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">⚠️</div>
                        <div class="stat-value">{data['risk_level'].upper()}</div>
                        <div class="stat-label">Risk Level</div>
                    </div>
                </div>
                
                <!-- Charts -->
                {charts_html}
                
                <!-- Department Breakdown -->
                {dept_html}
                
                <!-- Risk Analysis -->
                {risk_html}
                
                <!-- Optimizations -->
                {opt_html}
                
                <!-- Action Buttons -->
                <div class="btn-group fade-in" style="margin: 40px 0;">
                    <a href="/" class="btn btn-primary">🏠 Back to Dashboard</a>
                    <a href="/export-excel/{file_id}" class="btn btn-success">📊 Download Excel</a>
                    <a href="/generate-pdf/{file_id}" class="btn btn-warning">📑 Download PDF</a>
                </div>
            </div>
            
            <!-- Load charts JavaScript -->
            <script src="/static/js/charts.js"></script>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        flash(f'Error displaying analysis: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('index'))


@app.route('/export-excel/<file_id>')
def export_excel_route(file_id):
    """Export analysis to formatted Excel file"""
    if file_id not in analysis_cache:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        data = analysis_cache[file_id]
        df = data['df']
        
        # Prepare budget data
        budget_data = {
            'filename': data['filename'],
            'total_budget': data['total_budget'],
            'line_items': data['line_items'],
            'num_departments': len(set(df['Department'])) if 'Department' in df.columns else 0
        }
        
        # Get risk analysis
        risk_data = {
            'risk_level': data['risk_level'],
            'overall_risk_score': data['risk_score']
        }
        
        # Get optimizations
        optimizations = data['optimizations']
        
        # Generate Excel file
        excel_filename = f"budget_analysis_{file_id}.xlsx"
        excel_path = os.path.join(app.config['OUTPUT_FOLDER'], excel_filename)
        
        export_to_excel(df, budget_data, risk_data, optimizations, excel_path)
        
        # Send file
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=f"{data['filename']}_analysis.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error generating Excel: {str(e)}', 'error')
        print(f"Excel Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('view_analysis', file_id=file_id))


@app.route('/generate-pdf/<file_id>')
def generate_pdf_report(file_id):
    """Generate PDF report for analysis"""
    if file_id not in analysis_cache:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        from pdf_report_generator import generate_pdf_report as gen_pdf
        
        data = analysis_cache[file_id]
        df = data['df']
        
        # Prepare budget data
        budget_data = {
            'filename': data['filename'],
            'total_budget': data['total_budget'],
            'line_items': data['line_items'],
            'num_departments': len(set(df['Department'])) if 'Department' in df.columns else 0,
            'risk_level': data['risk_level'],
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
            'risk_level': data['risk_level'],
            'overall_risk_score': data['risk_score'],
            'risk_categories': data['risk_analysis'].get('items_by_category', {})
        }
        
        # Get optimization data
        optimizations = data['optimizations']
        
        # Generate PDF
        pdf_filename = f"budget_report_{file_id}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        gen_pdf(budget_data, risk_data, optimizations, pdf_path, visualizations=None)
        
        # Serve the PDF
        return send_file(
            pdf_path, 
            as_attachment=True,
            download_name=f"{data['filename']}_report.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        print(f"PDF Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('view_analysis', file_id=file_id))


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Budget Analysis & Risk Management System")
    print("   Enhanced with PATH A Features!")
    print("=" * 80)
    print("\n✨ Features:")
    print("  • Interactive Chart.js visualizations")
    print("  • Modern responsive UI design")
    print("  • Excel export with formatting")
    print("  • PDF report generation")
    print("  • Risk assessment & recommendations")
    print("\n📊 Starting server at: http://localhost:5000")
    print("=" * 80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
