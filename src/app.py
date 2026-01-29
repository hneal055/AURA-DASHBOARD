"""
================================================================================
BUDGET ANALYSIS - PROFESSIONAL EDITION
Professional budget analysis application with proper structure
================================================================================
✅ Flask templates for maintainability
✅ Modular code organization
✅ File upload & processing
✅ Basic analysis & insights
✅ Department breakdown
✅ High-cost item detection
✅ Clean modern interface
"""

from flask import Flask, request, render_template, redirect, url_for, flash, make_response
import pandas as pd
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# Import analysis modules
from src.models.budget_analyzer import BudgetAnalyzer
from src.services.risk_manager import RiskManager
from src.services.recommendation_engine import RecommendationEngine

# ============================================================================
# INITIALIZATION
# ============================================================================

app = Flask(__name__, template_folder='templates', static_folder='../static')

# TODO: Move to environment variable
app.secret_key = os.environ.get('SECRET_KEY', 'budget-analysis-startup-2024')

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

def _format_dept_data(dept_df):
    """Convert department DataFrame to dict format for template"""
    dept_dict = {}
    for _, row in dept_df.iterrows():
        dept_dict[row['Department']] = {
            'total': row['total'],
            'items': row['count'],
            'percentage': row['percentage']
        }
    return dept_dict

def _format_cat_data(cat_df):
    """Convert category DataFrame to dict format for template"""
    cat_dict = {}
    for _, row in cat_df.iterrows():
        cat_dict[row['Category']] = {
            'total': row['total'],
            'items': row['count'],
            'percentage': row.get('percentage', 0)
        }
    return cat_dict

def analyze_budget(df):
    """
    Perform comprehensive budget analysis with intelligent recommendations.

    This enhanced version uses BudgetAnalyzer, RiskManager, and RecommendationEngine
    to provide data-driven insights and actionable recommendations.
    """
    # Initialize analysis services
    budget_analyzer = BudgetAnalyzer()
    budget_analyzer.data = df

    # Get comprehensive analysis
    summary = budget_analyzer.get_summary()
    dept_analysis = budget_analyzer.analyze_by_department()
    cat_analysis = budget_analyzer.analyze_by_category()

    # Add percentage to category analysis
    cat_total = cat_analysis['total'].sum()
    if cat_total > 0:
        cat_analysis['percentage'] = (cat_analysis['total'] / cat_total * 100).round(2)
    else:
        cat_analysis['percentage'] = 0

    # Risk analysis
    risk_manager = RiskManager()
    risk_analysis = risk_manager.analyze_risks(df)

    # Generate intelligent recommendations
    rec_engine = RecommendationEngine()
    recommendations = rec_engine.generate_recommendations(
        df=df,
        dept_analysis=dept_analysis,
        cat_analysis=cat_analysis,
        risk_analysis=risk_analysis
    )

    return {
        # Core metrics
        'total_budget': summary['total_amount'],
        'total_items': summary['total_items'],
        'average_item': summary['average_amount'],

        # Breakdowns (formatted for template)
        'departments': _format_dept_data(dept_analysis),
        'categories': _format_cat_data(cat_analysis),

        # High-cost items
        'high_cost_items': risk_analysis['items_by_category']['high_cost_items'],
        'high_cost_count': len(risk_analysis['items_by_category']['high_cost_items']),

        # NEW: Enhanced features
        'recommendations': recommendations,
        'insights': budget_analyzer.generate_insights(),
        'health_score': rec_engine.calculate_health_score(df),
        'concentration_index': rec_engine.calculate_hhi(dept_analysis),
        'balance_score': rec_engine.calculate_gini(dept_analysis)
    }

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def home():
    """Homepage"""
    return render_template('index.html')

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

    # Prepare data for template
    template_data = {
        'filename': data['filename'],
        'timestamp': data['timestamp'].strftime('%B %d, %Y at %I:%M %p'),
        'analysis': data['analysis']
    }

    return render_template('results.html', **template_data)

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("BUDGET ANALYSIS PRO - PROFESSIONAL EDITION")
    print("=" * 70)
    print("\nREADY TO LAUNCH!")
    print("   - Professional budget analysis")
    print("   - Instant insights & recommendations")
    print("   - Modular architecture")
    print("   - Built-in sample data")
    print("\nSTARTING SERVER...")
    print("   Open your browser and visit:")
    print("   >>> http://localhost:5000")
    print("=" * 70)
    print("\nPress CTRL+C to stop the server")
    print("=" * 70)

    # Run the application
    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
