"""
================================================================================
Budget Analysis & Risk Management Web Application
VERSION 2.0 - With Budget Templates Feature
================================================================================
Version: 2.0
Date: 2024
Enhancements:
✅ Budget Templates Gallery (NEW!)
✅ Template Search & Preview  
✅ One-Click Template Usage
✅ Professional Template Styling
✅ Enhanced Navigation
✅ All V1 features preserved
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

# Import COMPARISON modules
from budget_comparison import compare_budgets
from comparison_charts import generate_comparison_chart_html

# Import TEMPLATES modules (NEW!)
from budget_templates import get_template_categories, get_popular_templates, get_template_by_id, search_templates

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

# Budget history for comparison feature
budget_history = {}


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
    """Homepage with modern UI and template features"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Budget Analysis & Risk Management v2.0</title>
        <link rel="stylesheet" href="/static/css/modern-styles.css">
        <link rel="stylesheet" href="/static/css/template-styles.css">
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header fade-in">
                <h1>💰 Budget Analysis & Risk Management v2.0</h1>
                <p>Now with Budget Templates! Professional analysis with AI-powered insights and templates</p>
                <div style="background: #e8f4fd; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <strong>🎉 NEW:</strong> Budget Templates Gallery • One-Click Templates • Industry-Specific Budgets
                </div>
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
            
            <!-- Template Feature Highlight -->
            <div class="upload-section fade-in" style="margin-top: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px;">
                <h2 class="card-title" style="color: white;">📋 NEW: Budget Templates</h2>
                <p style="color: rgba(255,255,255,0.9); margin-bottom: 20px; font-size: 1.1rem;">
                    Get started instantly with professionally designed budget templates for your industry
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.2); border-radius: 8px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem;">🎬</div>
                        <div style="font-weight: 600;">Film Production</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.2); border-radius: 8px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem;">📢</div>
                        <div style="font-weight: 600;">Marketing</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.2); border-radius: 8px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem;">💻</div>
                        <div style="font-weight: 600;">Tech Startup</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,255,255,0.2); border-radius: 8px; backdrop-filter: blur(10px);">
                        <div style="font-size: 2rem;">💍</div>
                        <div style="font-weight: 600;">Wedding</div>
                    </div>
                </div>
                <a href="/templates" class="btn btn-primary" style="font-size: 1.1rem; padding: 12px 32px; background: white; color: #667eea; border: none;">
                    📋 Explore Templates Gallery →
                </a>
            </div>
            
            <!-- Comparison Feature Highlight -->
            <div class="upload-section fade-in" style="margin-top: 40px;">
                <h2 class="card-title">🔄 Budget Comparison</h2>
                <p style="color: #7f8c8d; margin-bottom: 20px;">
                    Compare multiple budgets side-by-side to track changes and optimize spending
                </p>
                <a href="/budget-history" class="btn btn-secondary" style="font-size: 1.1rem; padding: 12px 32px;">
                    📊 View History & Compare →
                </a>
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

# ... (rest of the code remains the same as previous enhanced version)