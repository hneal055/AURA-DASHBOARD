"""
================================================================================
Budget Analysis & Risk Management Web Application
NOW WITH SQLITE DATABASE INTEGRATION!
Enhanced with PATH A Features: Interactive Charts, Modern UI, Excel Export
================================================================================
"""

from flask import Flask, request, render_template_string, redirect, url_for, send_file, flash, jsonify, get_flashed_messages
import pandas as pd
import io
import os
import json
import uuid
import html as html_lib
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import anthropic

load_dotenv(override=True)

# API key auth for protected endpoints
from flask_auth import require_api_key
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
_secret_key = os.environ.get('SECRET_KEY')
if not _secret_key:
    raise RuntimeError('SECRET_KEY is not set. Add it to your .env file.')
app.secret_key = _secret_key

# Session cookie security
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=['200 per day', '60 per hour'],
    storage_uri='memory://'
)

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
    # Add ai_insights_json column to existing databases (idempotent)
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE budget_analyses ADD COLUMN ai_insights_json TEXT'))
            conn.commit()
    except Exception:
        pass  # Column already exists


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

    # Build flash messages HTML
    messages = get_flashed_messages(with_categories=True)
    flash_html = ''
    for category, message in messages:
        color = '#c0392b' if category == 'error' else '#27ae60'
        flash_html += f'<div style="background:{color};color:white;padding:12px 20px;border-radius:8px;margin-bottom:12px;font-weight:600;">{message}</div>'

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

            {flash_html}

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
@limiter.limit('20 per hour')
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
            risk_analysis = risk_manager.analyze_risks(df)
            
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
            logger.error('Error analyzing file: %s', e, exc_info=True)
            flash('An error occurred while analyzing the file. Please check the file format and try again.', 'error')
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
        df = pd.read_json(io.StringIO(analysis.dataframe_json))
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
        
        # Build line items table rows
        line_item_rows = ''
        cols = [c for c in ['Category', 'Department', 'Description', 'Vendor', 'Amount'] if c in df.columns]
        for _, row in df.iterrows():
            cells = ''
            for c in cols:
                val = row[c]
                if c == 'Amount':
                    cells += f'<td style="text-align:right;font-weight:600;">${float(val):,.2f}</td>'
                else:
                    cells += f'<td>{html_lib.escape(str(val))}</td>'
            line_item_rows += f'<tr>{cells}</tr>'

        header_cells = ''.join(f'<th>{html_lib.escape(c)}</th>' for c in cols)

        # Build budget (category) breakdown modal rows
        budget_rows = ''
        num_categories = 0
        if 'Category' in df.columns:
            cat_totals = df.groupby('Category')['Amount'].agg(['sum', 'count']).reset_index()
            cat_totals.columns = ['Category', 'Total', 'Items']
            cat_totals = cat_totals.sort_values('Total', ascending=False)
            num_categories = len(cat_totals)
            for _, row in cat_totals.iterrows():
                pct = (row['Total'] / total_budget * 100) if total_budget > 0 else 0
                bar_w = min(100, pct)
                budget_rows += f"""
                <tr>
                    <td><strong>{html_lib.escape(str(row['Category']))}</strong></td>
                    <td style="text-align:right;font-weight:600;">${row['Total']:,.2f}</td>
                    <td style="text-align:right;">{int(row['Items'])}</td>
                    <td style="min-width:160px;">
                        <div style="background:#e8f5e9;border-radius:4px;height:10px;overflow:hidden;">
                            <div style="width:{bar_w:.1f}%;background:#27ae60;height:100%;border-radius:4px;"></div>
                        </div>
                        <span style="font-size:0.8rem;color:#555;">{pct:.1f}%</span>
                    </td>
                </tr>"""

        # Build risk modal content
        risk_summary = risk_analysis.get('summary', {})
        risk_score = risk_summary.get('overall_risk_score', 0)
        risk_metrics = risk_analysis.get('metrics', {})
        risk_amount = risk_metrics.get('risk_amount', 0)
        risk_pct = risk_metrics.get('risk_percentage', 0)
        risk_level_label = risk_summary.get('risk_level', analysis.risk_level)

        risk_level_color = {'low': '#27ae60', 'moderate': '#f39c12', 'high': '#e74c3c', 'critical': '#8e0000'}.get(risk_level_label.lower(), '#f39c12')

        # Category rows
        risk_cat_rows = ''
        for cat_key, cat_data in risk_summary.get('risk_categories', {}).items():
            if cat_data['count'] == 0:
                continue
            label = cat_key.replace('_', ' ').title()
            pct = cat_data.get('percentage', 0)
            bar_w = min(100, pct)
            desc = cat_data.get('description', '')
            risk_cat_rows += f"""
            <tr>
                <td>
                    <strong>{html_lib.escape(label)}</strong>
                    <div style="font-size:0.78rem;color:#888;margin-top:2px;">{html_lib.escape(desc)}</div>
                </td>
                <td style="text-align:right;">{cat_data['count']}</td>
                <td style="text-align:right;font-weight:600;">${cat_data['amount']:,.2f}</td>
                <td style="min-width:140px;">
                    <div style="background:#fce4e4;border-radius:4px;height:10px;overflow:hidden;">
                        <div style="width:{bar_w:.1f}%;background:#e74c3c;height:100%;border-radius:4px;"></div>
                    </div>
                    <span style="font-size:0.78rem;color:#555;">{pct:.1f}%</span>
                </td>
            </tr>"""

        # Top risk items rows
        risk_item_rows = ''
        for item in risk_summary.get('high_risk_items', []):
            item_pct = item.get('percentage', 0)
            risk_item_rows += f"""
            <tr>
                <td>{html_lib.escape(str(item.get('description', 'Unknown')))}</td>
                <td>{html_lib.escape(str(item.get('department', '—')))}</td>
                <td style="text-align:right;font-weight:600;">${item.get('amount', 0):,.2f}</td>
                <td style="text-align:right;">{item_pct:.1f}%</td>
            </tr>"""

        # Build department modal rows
        dept_rows = ''
        num_depts = len(dept_stats)
        for d in dept_stats:
            bar_w = min(100, d['percentage'])
            dept_rows += f"""
            <tr>
                <td><strong>{html_lib.escape(str(d['name']))}</strong></td>
                <td style="text-align:right;font-weight:600;">${d['total']:,.2f}</td>
                <td style="text-align:right;">{d['items']}</td>
                <td style="min-width:140px;">
                    <div style="background:#e8eaf6;border-radius:4px;height:10px;overflow:hidden;">
                        <div style="width:{bar_w:.1f}%;background:var(--primary-color);height:100%;border-radius:4px;"></div>
                    </div>
                    <span style="font-size:0.8rem;color:#555;">{d['percentage']:.1f}%</span>
                </td>
            </tr>"""

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
            <script src="/static/js/charts.js" defer></script>
            <style>
                /* Line Items Modal */
                #li-modal-overlay {{
                    display: none;
                    position: fixed;
                    inset: 0;
                    background: rgba(0,0,0,0.55);
                    z-index: 1000;
                    align-items: flex-start;
                    justify-content: center;
                    padding: 40px 20px;
                    overflow-y: auto;
                }}
                #li-modal-overlay.open {{ display: flex; }}
                #li-modal {{
                    background: white;
                    border-radius: 14px;
                    width: 100%;
                    max-width: 1050px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                    animation: slideDown 0.22s ease;
                }}
                @keyframes slideDown {{
                    from {{ transform: translateY(-30px); opacity: 0; }}
                    to  {{ transform: translateY(0);     opacity: 1; }}
                }}
                #li-modal-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 18px 24px;
                    background: var(--primary-color);
                    color: white;
                }}
                #li-modal-header h2 {{ margin: 0; font-size: 1.2rem; }}
                #li-close {{
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.6rem;
                    cursor: pointer;
                    line-height: 1;
                    padding: 0 4px;
                }}
                #li-search {{
                    width: 100%;
                    padding: 10px 16px;
                    border: none;
                    border-bottom: 1px solid #e0e0e0;
                    font-size: 0.95rem;
                    outline: none;
                }}
                #li-table-wrap {{ overflow-x: auto; max-height: 60vh; overflow-y: auto; }}
                #li-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }}
                #li-table thead th {{
                    position: sticky;
                    top: 0;
                    background: #f4f6f9;
                    padding: 10px 14px;
                    text-align: left;
                    font-weight: 700;
                    color: var(--dark-color);
                    border-bottom: 2px solid #ddd;
                    text-transform: uppercase;
                    font-size: 0.78rem;
                    letter-spacing: 0.5px;
                }}
                #li-table tbody tr {{ border-bottom: 1px solid #f0f0f0; }}
                #li-table tbody tr:hover {{ background: #f0f7ff; }}
                #li-table tbody td {{ padding: 9px 14px; color: #444; }}
                #li-modal-footer {{
                    padding: 12px 20px;
                    background: #f9f9f9;
                    border-top: 1px solid #eee;
                    font-size: 0.85rem;
                    color: #888;
                }}
                .stat-card.clickable {{ cursor: pointer; }}

                /* Risk Modal */
                #risk-modal-overlay {{
                    display: none;
                    position: fixed;
                    inset: 0;
                    background: rgba(0,0,0,0.55);
                    z-index: 1000;
                    align-items: flex-start;
                    justify-content: center;
                    padding: 40px 20px;
                    overflow-y: auto;
                }}
                #risk-modal-overlay.open {{ display: flex; }}
                #risk-modal {{
                    background: white;
                    border-radius: 14px;
                    width: 100%;
                    max-width: 860px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                    animation: slideDown 0.22s ease;
                }}
                #risk-modal-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 18px 24px;
                    color: white;
                }}
                #risk-modal-header h2 {{ margin: 0; font-size: 1.2rem; }}
                #risk-close {{
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.6rem;
                    cursor: pointer;
                    line-height: 1;
                    padding: 0 4px;
                }}
                .risk-modal-section {{
                    padding: 16px 20px 6px;
                    font-size: 0.82rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    color: #888;
                    border-bottom: 1px solid #eee;
                }}
                #risk-modal table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }}
                #risk-modal table thead th {{
                    background: #f4f6f9;
                    padding: 9px 16px;
                    text-align: left;
                    font-weight: 700;
                    color: var(--dark-color);
                    border-bottom: 2px solid #ddd;
                    text-transform: uppercase;
                    font-size: 0.76rem;
                    letter-spacing: 0.5px;
                }}
                #risk-modal table tbody tr {{ border-bottom: 1px solid #f5f5f5; }}
                #risk-modal table tbody tr:hover {{ background: #fff5f5; }}
                #risk-modal table tbody td {{ padding: 10px 16px; color: #444; }}
                #risk-modal-footer {{
                    padding: 12px 20px;
                    background: #f9f9f9;
                    border-top: 1px solid #eee;
                    font-size: 0.85rem;
                    color: #888;
                }}

                /* Budget Breakdown Modal */
                #budget-modal-overlay {{
                    display: none;
                    position: fixed;
                    inset: 0;
                    background: rgba(0,0,0,0.55);
                    z-index: 1000;
                    align-items: flex-start;
                    justify-content: center;
                    padding: 40px 20px;
                    overflow-y: auto;
                }}
                #budget-modal-overlay.open {{ display: flex; }}
                #budget-modal {{
                    background: white;
                    border-radius: 14px;
                    width: 100%;
                    max-width: 750px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                    animation: slideDown 0.22s ease;
                }}
                #budget-modal-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 18px 24px;
                    background: #27ae60;
                    color: white;
                }}
                #budget-modal-header h2 {{ margin: 0; font-size: 1.2rem; }}
                #budget-close {{
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.6rem;
                    cursor: pointer;
                    line-height: 1;
                    padding: 0 4px;
                }}
                #budget-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }}
                #budget-table thead th {{
                    background: #f4f6f9;
                    padding: 10px 16px;
                    text-align: left;
                    font-weight: 700;
                    color: var(--dark-color);
                    border-bottom: 2px solid #ddd;
                    text-transform: uppercase;
                    font-size: 0.78rem;
                    letter-spacing: 0.5px;
                }}
                #budget-table tbody tr {{ border-bottom: 1px solid #f0f0f0; }}
                #budget-table tbody tr:hover {{ background: #f0fff4; }}
                #budget-table tbody td {{ padding: 11px 16px; color: #444; }}
                #budget-modal-footer {{
                    padding: 12px 20px;
                    background: #f9f9f9;
                    border-top: 1px solid #eee;
                    font-size: 0.85rem;
                    color: #888;
                }}

                /* Department Modal */
                #dept-modal-overlay {{
                    display: none;
                    position: fixed;
                    inset: 0;
                    background: rgba(0,0,0,0.55);
                    z-index: 1000;
                    align-items: flex-start;
                    justify-content: center;
                    padding: 40px 20px;
                    overflow-y: auto;
                }}
                #dept-modal-overlay.open {{ display: flex; }}
                #dept-modal {{
                    background: white;
                    border-radius: 14px;
                    width: 100%;
                    max-width: 750px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                    animation: slideDown 0.22s ease;
                }}
                #dept-modal-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 18px 24px;
                    background: #6c5ce7;
                    color: white;
                }}
                #dept-modal-header h2 {{ margin: 0; font-size: 1.2rem; }}
                #dept-close {{
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.6rem;
                    cursor: pointer;
                    line-height: 1;
                    padding: 0 4px;
                }}
                #dept-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }}
                #dept-table thead th {{
                    background: #f4f6f9;
                    padding: 10px 16px;
                    text-align: left;
                    font-weight: 700;
                    color: var(--dark-color);
                    border-bottom: 2px solid #ddd;
                    text-transform: uppercase;
                    font-size: 0.78rem;
                    letter-spacing: 0.5px;
                }}
                #dept-table tbody tr {{ border-bottom: 1px solid #f0f0f0; }}
                #dept-table tbody tr:hover {{ background: #f5f3ff; }}
                #dept-table tbody td {{ padding: 11px 16px; color: #444; }}
                #dept-modal-footer {{
                    padding: 12px 20px;
                    background: #f9f9f9;
                    border-top: 1px solid #eee;
                    font-size: 0.85rem;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <!-- Line Items Modal -->
            <div id="li-modal-overlay">
                <div id="li-modal">
                    <div id="li-modal-header">
                        <h2>📋 Line Items — {filename}</h2>
                        <button id="li-close" onclick="closeLI()" title="Close">×</button>
                    </div>
                    <input id="li-search" type="text" placeholder="🔍  Filter by any column..." oninput="filterLI(this.value)">
                    <div id="li-table-wrap">
                        <table id="li-table">
                            <thead><tr>{header_cells}</tr></thead>
                            <tbody id="li-tbody">{line_item_rows}</tbody>
                        </table>
                    </div>
                    <div id="li-modal-footer" id="li-count">{line_items} items total</div>
                </div>
            </div>

            <!-- Risk Modal -->
            <div id="risk-modal-overlay">
                <div id="risk-modal">
                    <div id="risk-modal-header" style="background:{risk_level_color};">
                        <h2>⚠️ Risk Assessment — {filename}</h2>
                        <button id="risk-close" onclick="closeRisk()" title="Close">×</button>
                    </div>
                    <!-- Score banner -->
                    <div style="display:flex;gap:24px;padding:16px 20px;background:#fafafa;border-bottom:1px solid #eee;flex-wrap:wrap;">
                        <div style="text-align:center;min-width:100px;">
                            <div style="font-size:2rem;font-weight:700;color:{risk_level_color};">{risk_score:.0f}</div>
                            <div style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:1px;">Risk Score</div>
                        </div>
                        <div style="text-align:center;min-width:100px;">
                            <div style="font-size:2rem;font-weight:700;color:{risk_level_color};">{risk_level_label}</div>
                            <div style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:1px;">Risk Level</div>
                        </div>
                        <div style="text-align:center;min-width:120px;">
                            <div style="font-size:2rem;font-weight:700;color:#e74c3c;">${risk_amount:,.0f}</div>
                            <div style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:1px;">Amount at Risk</div>
                        </div>
                        <div style="text-align:center;min-width:100px;">
                            <div style="font-size:2rem;font-weight:700;color:#e74c3c;">{risk_pct:.1f}%</div>
                            <div style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:1px;">Budget at Risk</div>
                        </div>
                    </div>
                    <!-- Risk categories -->
                    <div class="risk-modal-section">Risk Categories Detected</div>
                    <div style="overflow-x:auto;max-height:260px;overflow-y:auto;">
                        <table>
                            <thead><tr><th>Category</th><th style="text-align:right;">Items</th><th style="text-align:right;">Amount ($)</th><th>Exposure</th></tr></thead>
                            <tbody>{risk_cat_rows if risk_cat_rows else '<tr><td colspan="4" style="padding:16px;color:#aaa;text-align:center;">No keyword-matched risk categories found</td></tr>'}</tbody>
                        </table>
                    </div>
                    <!-- Top risk items -->
                    <div class="risk-modal-section">Top Risk Items by Amount</div>
                    <div style="overflow-x:auto;max-height:260px;overflow-y:auto;">
                        <table>
                            <thead><tr><th>Description</th><th>Department</th><th style="text-align:right;">Amount ($)</th><th style="text-align:right;">% of Budget</th></tr></thead>
                            <tbody>{risk_item_rows if risk_item_rows else '<tr><td colspan="4" style="padding:16px;color:#aaa;text-align:center;">No high-cost risk items flagged</td></tr>'}</tbody>
                        </table>
                    </div>
                    <div id="risk-modal-footer">Risk score 0–100 · Items flagged by keyword matching and cost threshold (≥5% of total budget)</div>
                </div>
            </div>

            <!-- Budget Breakdown Modal -->
            <div id="budget-modal-overlay">
                <div id="budget-modal">
                    <div id="budget-modal-header">
                        <h2>💵 Budget Breakdown — {filename}</h2>
                        <button id="budget-close" onclick="closeBudget()" title="Close">×</button>
                    </div>
                    <div style="overflow-x:auto;max-height:65vh;overflow-y:auto;">
                        <table id="budget-table">
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th style="text-align:right;">Total ($)</th>
                                    <th style="text-align:right;">Items</th>
                                    <th>% of Budget</th>
                                </tr>
                            </thead>
                            <tbody>{budget_rows}</tbody>
                        </table>
                    </div>
                    <div id="budget-modal-footer">{num_categories} categories · Total ${total_budget:,.2f}</div>
                </div>
            </div>

            <!-- Department Modal -->
            <div id="dept-modal-overlay">
                <div id="dept-modal">
                    <div id="dept-modal-header">
                        <h2>🏢 Departments — {filename}</h2>
                        <button id="dept-close" onclick="closeDept()" title="Close">×</button>
                    </div>
                    <div style="overflow-x:auto;">
                        <table id="dept-table">
                            <thead>
                                <tr>
                                    <th>Department</th>
                                    <th style="text-align:right;">Total ($)</th>
                                    <th style="text-align:right;">Items</th>
                                    <th>% of Budget</th>
                                </tr>
                            </thead>
                            <tbody>{dept_rows}</tbody>
                        </table>
                    </div>
                    <div id="dept-modal-footer">{num_depts} departments · Total ${total_budget:,.2f}</div>
                </div>
            </div>

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
                    <div class="stat-card clickable" onclick="openBudget()" title="Click to view budget breakdown">
                        <div class="stat-icon">💵</div>
                        <div class="stat-value">${total_budget:,.0f}</div>
                        <div class="stat-label">Total Budget</div>
                        <div style="font-size:0.75rem;color:#27ae60;margin-top:6px;font-weight:600;">Click to view ↗</div>
                    </div>

                    <div class="stat-card clickable" onclick="openLI()" title="Click to view all line items">
                        <div class="stat-icon">📋</div>
                        <div class="stat-value">{line_items}</div>
                        <div class="stat-label">Line Items</div>
                        <div style="font-size:0.75rem;color:var(--primary-color);margin-top:6px;font-weight:600;">Click to view ↗</div>
                    </div>

                    <div class="stat-card clickable" onclick="openDept()" title="Click to view departments">
                        <div class="stat-icon">🏢</div>
                        <div class="stat-value">{len(set(df['Department'])) if 'Department' in df.columns else 'N/A'}</div>
                        <div class="stat-label">Departments</div>
                        <div style="font-size:0.75rem;color:#6c5ce7;margin-top:6px;font-weight:600;">Click to view ↗</div>
                    </div>

                    <div class="stat-card clickable" onclick="openRisk()" title="Click to view risk details" style="border-top-color:{risk_level_color};">
                        <div class="stat-icon">⚠️</div>
                        <div class="stat-value" style="color:{risk_level_color};">{analysis.risk_level}</div>
                        <div class="stat-label">Risk Level</div>
                        <div style="font-size:0.75rem;color:{risk_level_color};margin-top:6px;font-weight:600;">Click to view ↗</div>
                    </div>
                </div>

                <script>
                    function openRisk() {{
                        document.getElementById('risk-modal-overlay').classList.add('open');
                    }}
                    function closeRisk() {{
                        document.getElementById('risk-modal-overlay').classList.remove('open');
                    }}
                    document.getElementById('risk-modal-overlay').addEventListener('click', function(e) {{
                        if (e.target === this) closeRisk();
                    }});
                    function openBudget() {{
                        document.getElementById('budget-modal-overlay').classList.add('open');
                    }}
                    function closeBudget() {{
                        document.getElementById('budget-modal-overlay').classList.remove('open');
                    }}
                    document.getElementById('budget-modal-overlay').addEventListener('click', function(e) {{
                        if (e.target === this) closeBudget();
                    }});
                    function openLI() {{
                        document.getElementById('li-modal-overlay').classList.add('open');
                        document.getElementById('li-search').focus();
                    }}
                    function closeLI() {{
                        document.getElementById('li-modal-overlay').classList.remove('open');
                        document.getElementById('li-search').value = '';
                        filterLI('');
                    }}
                    document.getElementById('li-modal-overlay').addEventListener('click', function(e) {{
                        if (e.target === this) closeLI();
                    }});
                    function openDept() {{
                        document.getElementById('dept-modal-overlay').classList.add('open');
                    }}
                    function closeDept() {{
                        document.getElementById('dept-modal-overlay').classList.remove('open');
                    }}
                    document.getElementById('dept-modal-overlay').addEventListener('click', function(e) {{
                        if (e.target === this) closeDept();
                    }});
                    document.addEventListener('keydown', function(e) {{
                        if (e.key === 'Escape') {{ closeLI(); closeDept(); closeBudget(); closeRisk(); }}
                    }});
                    function filterLI(query) {{
                        const q = query.toLowerCase();
                        const rows = document.querySelectorAll('#li-tbody tr');
                        let visible = 0;
                        rows.forEach(r => {{
                            const match = r.textContent.toLowerCase().includes(q);
                            r.style.display = match ? '' : 'none';
                            if (match) visible++;
                        }});
                        document.getElementById('li-modal-footer').textContent =
                            q ? visible + ' of {line_items} items match' : '{line_items} items total';
                    }}
                </script>
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
        logger.error('Error displaying analysis %s: %s', file_id, e, exc_info=True)
        flash('Unable to display analysis. Please try again or re-upload the file.', 'error')
        return redirect(url_for('index'))


@app.route('/export-excel/<file_id>')
def export_excel_route(file_id):
    """Export analysis to formatted Excel file FROM DATABASE"""
    analysis = BudgetAnalysis.query.get(file_id)
    
    if not analysis:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    try:
        df = pd.read_json(io.StringIO(analysis.dataframe_json))
        
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
        logger.error('Error exporting Excel for %s: %s', file_id, e, exc_info=True)
        flash('Unable to generate Excel export. Please try again.', 'error')
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
        
        df = pd.read_json(io.StringIO(analysis.dataframe_json))
        
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
        logger.error('Error generating PDF for %s: %s', file_id, e, exc_info=True)
        flash('Unable to generate PDF report. Please try again.', 'error')
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
        df1 = pd.read_json(io.StringIO(analysis1.dataframe_json))
        df2 = pd.read_json(io.StringIO(analysis2.dataframe_json))
        
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
                        <div class="stat-icon">📁</div>
                        <div class="stat-value" style="font-size:1.3rem;word-break:break-word;line-height:1.3;" title="{analysis1.filename}">{analysis1.filename[:28] + '…' if len(analysis1.filename) > 28 else analysis1.filename}</div>
                        <div class="stat-label">Budget A &nbsp;·&nbsp; ${analysis1.total_budget:,.2f}</div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">📁</div>
                        <div class="stat-value" style="font-size:1.3rem;word-break:break-word;line-height:1.3;" title="{analysis2.filename}">{analysis2.filename[:28] + '…' if len(analysis2.filename) > 28 else analysis2.filename}</div>
                        <div class="stat-label">Budget B &nbsp;·&nbsp; ${analysis2.total_budget:,.2f}</div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">{'📈' if analysis2.total_budget > analysis1.total_budget else '📉'}</div>
                        <div class="stat-value">${abs(analysis2.total_budget - analysis1.total_budget):,.2f}</div>
                        <div class="stat-label">Difference</div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">{'🔺' if analysis2.total_budget > analysis1.total_budget else '🔻'}</div>
                        <div class="stat-value" style="color:{'#e74c3c' if analysis2.total_budget > analysis1.total_budget else '#27ae60'};">{((analysis2.total_budget - analysis1.total_budget) / analysis1.total_budget * 100):+.1f}%</div>
                        <div class="stat-label">Change</div>
                    </div>
                </div>
                
                <!-- Comparison Charts -->
                <div class="section-card fade-in">
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
        logger.error('Error comparing budgets %s vs %s: %s', file_id, compare_id, e, exc_info=True)
        flash('Unable to complete budget comparison. Please try again.', 'error')
        return redirect(url_for('compare_page', file_id=file_id))


@app.route('/api/ai-insights/<file_id>', methods=['POST'])
@require_api_key
def ai_insights(file_id):
    """
    Generate AI-powered narrative insights for a budget analysis.
    Protected by API key: pass X-API-Key header (see api_keys.json / BUDGET_API_KEY in .env).
    """
    analysis = BudgetAnalysis.query.get(file_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404

    # Return cached insights if already generated
    if analysis.ai_insights_json:
        return jsonify({'success': True, 'insights': json.loads(analysis.ai_insights_json), 'cached': True})

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return jsonify({'error': 'ANTHROPIC_API_KEY not configured'}), 500

    try:
        risk_data = json.loads(analysis.risk_analysis_json or '{}')
        optimizations = json.loads(analysis.optimizations_json or '[]')

        prompt = f"""You are a senior film/TV production financial analyst. Review the following budget analysis and provide concise, actionable executive insights.

BUDGET SUMMARY:
- File: {analysis.filename}
- Total Budget: ${analysis.total_budget:,.2f}
- Line Items: {analysis.line_items}
- Departments: {analysis.num_departments}
- Risk Level: {analysis.risk_level} (score: {analysis.risk_score:.2f})
- Analyzed: {analysis.analysis_timestamp.strftime('%Y-%m-%d')}

RISK FLAGS:
{json.dumps(risk_data.get('items_by_category', {}), indent=2)[:2000]}

OPTIMIZATION OPPORTUNITIES:
{json.dumps(optimizations, indent=2)[:1000]}

Return ONLY a valid JSON object with this structure:
{{
  "executive_summary": "<2-3 sentence overview of the budget health>",
  "key_concerns": ["<concern 1>", "<concern 2>", "<concern 3>"],
  "top_recommendations": [
    {{"action": "<what to do>", "rationale": "<why>", "priority": "<HIGH|MEDIUM|LOW>"}},
    {{"action": "<what to do>", "rationale": "<why>", "priority": "<HIGH|MEDIUM|LOW>"}},
    {{"action": "<what to do>", "rationale": "<why>", "priority": "<HIGH|MEDIUM|LOW>"}}
  ],
  "budget_health_score": <integer 0-100>,
  "outlook": "<POSITIVE|CAUTIONARY|CRITICAL>"
}}"""

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1]
            response_text = response_text.rsplit('```', 1)[0]

        insights = json.loads(response_text)

        # Cache in database
        analysis.ai_insights_json = json.dumps(insights)
        db.session.commit()

        return jsonify({'success': True, 'insights': insights, 'cached': False})

    except Exception as e:
        logger.error('Error generating AI insights for %s: %s', file_id, e, exc_info=True)
        return jsonify({'error': 'Unable to generate insights. Please try again.'}), 500


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
    print("\n>> Starting server at: http://localhost:8082")
    print("=" * 80)
    print()
    
    app.run(debug=False, host='127.0.0.1', port=8082)