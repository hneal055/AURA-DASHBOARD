"""
================================================================================
BUDGET ANALYSIS - STARTUP EDITION
Simple, working budget analysis application
================================================================================
✅ File upload & processing
✅ Basic analysis & insights
✅ Department breakdown
✅ High-cost item detection
✅ Clean modern interface
✅ No external dependencies
"""

from flask import Flask, request, render_template_string, redirect, url_for, flash
import pandas as pd
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# ============================================================================
# INITIALIZATION
# ============================================================================

app = Flask(__name__)
app.secret_key = 'budget-analysis-startup-2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simple in-memory storage
analysis_cache = {}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_budget(df):
    """Perform basic budget analysis"""
    total = df['Amount'].sum()
    items = len(df)
    
    # High cost items (more than 10% of total)
    high_cost_threshold = total * 0.1
    high_cost_items = df[df['Amount'] > high_cost_threshold]
    
    # Department breakdown
    department_data = {}
    if 'Department' in df.columns:
        for dept, group in df.groupby('Department'):
            department_data[dept] = {
                'total': group['Amount'].sum(),
                'items': len(group),
                'percentage': (group['Amount'].sum() / total * 100) if total > 0 else 0
            }
    
    # Category breakdown
    category_data = {}
    if 'Category' in df.columns:
        for cat, group in df.groupby('Category'):
            category_data[cat] = {
                'total': group['Amount'].sum(),
                'items': len(group)
            }
    
    return {
        'total_budget': total,
        'total_items': items,
        'high_cost_items': high_cost_items.to_dict('records'),
        'high_cost_count': len(high_cost_items),
        'departments': department_data,
        'categories': category_data,
        'average_item': total / items if items > 0 else 0
    }

# ============================================================================
# HTML TEMPLATES (Embedded CSS & JavaScript)
# ============================================================================

BASE_CSS = """
<style>
    /* Reset & Base */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        color: #333;
        line-height: 1.6;
    }
    
    /* Layout */
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header */
    .header {
        text-align: center;
        color: white;
        margin-bottom: 40px;
        padding: 20px;
    }
    .header h1 {
        font-size: 2.8rem;
        margin-bottom: 10px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .header p {
        font-size: 1.2rem;
        opacity: 0.9;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    .stat-card {
        background: rgba(255,255,255,0.95);
        padding: 25px;
        border-radius: 10px;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
        transition: transform 0.3s ease;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-icon {
        font-size: 2.8rem;
        margin-bottom: 15px;
        display: block;
    }
    .stat-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2d3436;
        margin-bottom: 5px;
    }
    .stat-label {
        color: #636e72;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* Buttons */
    .btn {
        display: inline-block;
        padding: 14px 32px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 8px;
        border: none;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    .btn-secondary {
        background: #636e72;
        box-shadow: 0 4px 15px rgba(99, 110, 114, 0.4);
    }
    
    /* Forms */
    .upload-area {
        border: 3px dashed #667eea;
        border-radius: 12px;
        padding: 50px 30px;
        text-align: center;
        background: rgba(255,255,255,0.9);
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    .upload-area:hover {
        border-color: #764ba2;
        background: rgba(255,255,255,0.95);
    }
    .upload-icon {
        font-size: 4rem;
        margin-bottom: 20px;
        color: #667eea;
    }
    
    /* Tables */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
    }
    .data-table th {
        background: #f8f9fa;
        padding: 15px;
        text-align: left;
        font-weight: 600;
        color: #2d3436;
        border-bottom: 2px solid #dee2e6;
    }
    .data-table td {
        padding: 12px 15px;
        border-bottom: 1px solid #e9ecef;
    }
    .data-table tr:hover {
        background: #f8f9fa;
    }
    
    /* Alerts */
    .alert {
        padding: 15px 20px;
        border-radius: 8px;
        margin: 20px 0;
        border-left: 4px solid;
    }
    .alert-success {
        background: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    .alert-error {
        background: #f8d7da;
        border-color: #dc3545;
        color: #721c24;
    }
    
    /* Animations */
    .fade-in {
        animation: fadeIn 0.8s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .container { padding: 15px; }
        .header h1 { font-size: 2rem; }
        .stats-grid { grid-template-columns: 1fr; }
        .card { padding: 20px; }
    }
</style>
"""

HOME_PAGE = BASE_CSS + """
<div class="container">
    <div class="header fade-in">
        <h1>💰 Budget Analysis Pro</h1>
        <p>Professional budget analysis with instant insights and actionable recommendations</p>
    </div>
    
    <div class="card fade-in">
        <h2 style="margin-bottom: 10px; color: #2d3436;">📁 Upload Your Budget</h2>
        <p style="color: #636e72; margin-bottom: 25px;">
            Upload a CSV file with columns: <strong>Description, Amount</strong> (Department, Category optional)
        </p>
        
        <div class="upload-area">
            <div class="upload-icon">📊</div>
            <h3 style="margin-bottom: 10px; color: #2d3436;">Drag & Drop or Click to Browse</h3>
            <p style="color: #636e72; margin-bottom: 25px;">Supports CSV files up to 16MB</p>
            
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".csv" required 
                       style="padding: 15px; border: 2px solid #667eea; border-radius: 8px; 
                              width: 100%; font-size: 1rem; margin-bottom: 20px;">
                <button type="submit" class="btn" style="font-size: 1.1rem;">
                    🚀 Analyze Budget Now
                </button>
            </form>
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
            <h4 style="margin-bottom: 15px; color: #2d3436;">💡 Need a sample file?</h4>
            <p style="color: #636e72; margin-bottom: 15px;">Download this sample CSV to get started:</p>
            <a href="/sample-csv" class="btn btn-secondary" style="font-size: 0.95rem;">
                📥 Download Sample CSV
            </a>
        </div>
    </div>
    
    <div class="stats-grid fade-in" style="margin-top: 40px;">
        <div class="stat-card">
            <span class="stat-icon">⚡</span>
            <div class="stat-value">Instant</div>
            <div class="stat-label">Real-time Analysis</div>
        </div>
        <div class="stat-card">
            <span class="stat-icon">🔍</span>
            <div class="stat-value">Smart</div>
            <div class="stat-label">Risk Detection</div>
        </div>
        <div class="stat-card">
            <span class="stat-icon">📈</span>
            <div class="stat-value">Actionable</div>
            <div class="stat-label">Insights & Tips</div>
        </div>
        <div class="stat-card">
            <span class="stat-icon">🛡️</span>
            <div class="stat-value">Secure</div>
            <div class="stat-label">Local Processing</div>
        </div>
    </div>
</div>
"""

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def home():
    """Homepage"""
    return HOME_PAGE

@app.route('/sample-csv')
def sample_csv():
    """Download sample CSV file"""
    sample_content = """Description,Department,Category,Amount
Office Rent,Operations,Facilities,5000
Software Licenses,IT,Technology,2000
Marketing Campaign,Marketing,Advertising,8000
Employee Salaries,HR,Personnel,25000
Team Lunch,HR,Morale,500
Cloud Services,IT,Infrastructure,1200
Office Supplies,Operations,Supplies,300
Travel Expenses,Sales,Travel,3500
Training & Development,HR,Development,1800
Equipment Purchase,Operations,Assets,4200"""
    
    from flask import make_response
    response = make_response(sample_content)
    response.headers["Content-Disposition"] = "attachment; filename=sample_budget.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('No file uploaded. Please select a CSV file.', 'error')
        return redirect('/')
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected. Please choose a CSV file.', 'error')
        return redirect('/')
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a CSV file.', 'error')
        return redirect('/')
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read and validate CSV
        df = pd.read_csv(filepath)
        
        if 'Amount' not in df.columns:
            flash('CSV must contain an "Amount" column', 'error')
            return redirect('/')
        
        # Generate unique ID for this analysis
        file_id = str(uuid.uuid4())
        
        # Perform analysis
        analysis = analyze_budget(df)
        
        # Store results
        analysis_cache[file_id] = {
            'filename': filename,
            'filepath': filepath,
            'df': df,
            'analysis': analysis,
            'timestamp': datetime.now()
        }
        
        # Redirect to results page
        flash('✅ Budget analyzed successfully!', 'success')
        return redirect(f'/results/{file_id}')
        
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect('/')

@app.route('/results/<file_id>')
def show_results(file_id):
    """Display analysis results"""
    if file_id not in analysis_cache:
        flash('Analysis not found or has expired', 'error')
        return redirect('/')
    
    data = analysis_cache[file_id]
    analysis = data['analysis']
    df = data['df']
    
    # Format currency
    def format_currency(value):
        return f"${value:,.2f}"
    
    # Generate HTML for analysis
    results_html = BASE_CSS + f"""
    <div class="container">
        <div class="header">
            <h1>📊 Analysis Results</h1>
            <p>{data['filename']} • Analyzed on {data['timestamp'].strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <!-- Key Statistics -->
        <div class="stats-grid fade-in">
            <div class="stat-card">
                <span class="stat-icon">💰</span>
                <div class="stat-value">{format_currency(analysis['total_budget'])}</div>
                <div class="stat-label">Total Budget</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">📋</span>
                <div class="stat-value">{analysis['total_items']}</div>
                <div class="stat-label">Line Items</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">⚠️</span>
                <div class="stat-value">{analysis['high_cost_count']}</div>
                <div class="stat-label">High-Cost Items</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">📊</span>
                <div class="stat-value">{format_currency(analysis['average_item'])}</div>
                <div class="stat-label">Average Per Item</div>
            </div>
        </div>
        
        <!-- Department Breakdown -->
        {f'''
        <div class="card fade-in">
            <h2 style="margin-bottom: 20px; color: #2d3436;">🏢 Department Breakdown</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Department</th>
                        <th>Total Amount</th>
                        <th>Percentage</th>
                        <th>Items</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td><strong>{dept}</strong></td>
                        <td>{format_currency(stats['total'])}</td>
                        <td>{stats['percentage']:.1f}%</td>
                        <td>{stats['items']}</td>
                    </tr>
                    ''' for dept, stats in analysis['departments'].items()])}
                </tbody>
            </table>
        </div>
        ''' if analysis['departments'] else ''}
        
        <!-- High Cost Items -->
        {f'''
        <div class="card fade-in">
            <h2 style="margin-bottom: 20px; color: #2d3436;">⚠️ High-Cost Items (Over 10% of Budget)</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Department</th>
                        <th>Category</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td>{item.get('Description', 'N/A')}</td>
                        <td>{format_currency(item.get('Amount', 0))}</td>
                        <td>{item.get('Department', 'N/A')}</td>
                        <td>{item.get('Category', 'N/A')}</td>
                    </tr>
                    ''' for item in analysis['high_cost_items']])}
                </tbody>
            </table>
        </div>
        ''' if analysis['high_cost_items'] else ''}
        
        <!-- Recommendations -->
        <div class="card fade-in">
            <h2 style="margin-bottom: 20px; color: #2d3436;">💡 Recommendations</h2>
            <div style="display: grid; gap: 15px;">
                <div style="padding: 15px; background: #e3f2fd; border-radius: 8px; border-left: 4px solid #2196f3;">
                    <strong>Review High-Cost Items</strong>
                    <p style="margin-top: 5px; color: #636e72;">
                        {analysis['high_cost_count']} items cost more than 10% of your total budget. 
                        Consider breaking these down or negotiating better rates.
                    </p>
                </div>
                
                {f'''
                <div style="padding: 15px; background: #e8f5e9; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <strong>Department Optimization</strong>
                    <p style="margin-top: 5px; color: #636e72;">
                        Your budget spans {len(analysis['departments'])} departments. 
                        Look for opportunities to consolidate spending in key areas.
                    </p>
                </div>
                ''' if analysis['departments'] else ''}
                
                <div style="padding: 15px; background: #fff3e0; border-radius: 8px; border-left: 4px solid #ff9800;">
                    <strong>Regular Review</strong>
                    <p style="margin-top: 5px; color: #636e72;">
                        Schedule monthly budget reviews to track spending patterns 
                        and identify cost-saving opportunities early.
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Action Buttons -->
        <div style="display: flex; gap: 15px; margin-top: 30px; flex-wrap: wrap;">
            <a href="/" class="btn">🏠 Analyze Another Budget</a>
            <a href="/sample-csv" class="btn btn-secondary">📥 Download Sample CSV</a>
        </div>
    </div>
    """
    
    return results_html

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("💰 BUDGET ANALYSIS PRO - STARTUP EDITION")
    print("=" * 70)
    print("\n🎯 READY TO LAUNCH!")
    print("   • Professional budget analysis")
    print("   • Instant insights & recommendations")
    print("   • No external dependencies")
    print("   • Built-in sample data")
    print("\n📡 STARTING SERVER...")
    print("   Open your browser and visit:")
    print("   🌐 http://localhost:5000")
    print("=" * 70)
    print("\n✅ Press CTRL+C to stop the server")
    print("=" * 70)
    
    # Run the application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )