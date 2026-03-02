"""
================================================================================
Production Budget & Risk Management System
Copyright © 2024-2025. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL

This file contains trade secrets and proprietary information. Unauthorized
copying, distribution, modification, or use is strictly prohibited.

File: web_app_enhanced.py
Module: Enhanced Web Application with Budget Comparison
Purpose: Advanced dashboard with risk analysis and multi-budget comparison
Version: 1.1.0
Last Modified: November 2024

PATENT PENDING: The budget comparison methodology, variance calculation 
algorithms, and multi-dimensional analysis techniques employed in this file 
may be subject to patent protection.

TRADE SECRETS: This file contains proprietary algorithms including:
- Multi-budget comparison methodology
- Variance calculation and normalization
- Department-level variance analysis
- Color-coded highlighting algorithms
- Statistical summary calculations

For licensing inquiries: [your-email@example.com]
================================================================================
"""
from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash
import os
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import hashlib

from risk_manager import RiskManager
from budget_tool import create_visualizations
from budget_optimizer import find_optimizations

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data/input'
app.config['OUTPUT_FOLDER'] = 'data/output'
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024
app.secret_key = 'enhanced-prod-budget-2024'

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

analysis_cache = {}

# Styles
STYLES = """
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
.container { max-width: 1400px; margin: 0 auto; padding: 30px; }
.header { background: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
h1 { font-size: 2.5em; color: #2c3e50; margin-bottom: 10px; }
.subtitle { color: #666; font-size: 1.1em; }
.nav-menu { background: white; padding: 15px 30px; border-radius: 10px; margin-bottom: 20px; display: flex; gap: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.nav-link { color: #666; text-decoration: none; padding: 10px 20px; border-radius: 5px; transition: all 0.3s; font-weight: 500; }
.nav-link:hover, .nav-link.active { background: #667eea; color: white; }
.content-box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 20px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
.stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); }
.stat-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
.stat-label { font-size: 0.9em; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; }
.upload-zone { border: 3px dashed #667eea; border-radius: 15px; padding: 80px 40px; text-align: center; background: rgba(102, 126, 234, 0.05); transition: all 0.3s; cursor: pointer; }
.upload-zone:hover { background: rgba(102, 126, 234, 0.1); transform: scale(1.02); }
.upload-icon { font-size: 4em; color: #667eea; margin-bottom: 20px; }
.btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-block; margin: 5px; transition: all 0.3s; }
.btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }
.btn-secondary { background: #6c757d; }
.btn-success { background: #28a745; }
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { text-align: left; padding: 15px; border-bottom: 1px solid #e0e0e0; }
th { background: #f8f9fa; color: #667eea; font-weight: 600; text-transform: uppercase; font-size: 0.9em; }
tr:hover { background: rgba(102, 126, 234, 0.05); }
.alert { padding: 20px; border-radius: 10px; margin-bottom: 20px; display: flex; align-items: center; gap: 15px; }
.alert-success { background: #d4edda; border-left: 4px solid #28a745; color: #155724; }
.alert-error { background: #f8d7da; border-left: 4px solid #dc3545; color: #721c24; }
.alert-info { background: #d1ecf1; border-left: 4px solid #17a2b8; color: #0c5460; }
.badge { padding: 6px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600; }
.badge-low { background: #d4edda; color: #155724; }
.badge-medium { background: #fff3cd; color: #856404; }
.badge-high { background: #fff0e6; color: #d63900; }
.badge-critical { background: #f8d7da; color: #721c24; }
input[type="file"] { display: none; }
.chart-img { max-width: 100%; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 20px 0; }
.upload-multiple { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
.file-upload-box { border: 2px dashed #667eea; border-radius: 10px; padding: 30px; text-align: center; background: rgba(102, 126, 234, 0.05); cursor: pointer; transition: all 0.3s; }
.file-upload-box:hover { background: rgba(102, 126, 234, 0.1); transform: scale(1.02); }
.file-uploaded { border-color: #28a745; background: rgba(40, 167, 69, 0.05); }
.file-name { color: #667eea; font-weight: 600; margin-top: 10px; font-size: 0.9em; }
.variance-positive { color: #dc3545; font-weight: bold; }
.variance-negative { color: #28a745; font-weight: bold; }
.highlight-max { background: #fff3cd !important; }
.highlight-min { background: #d4edda !important; }
</style>
"""

@app.route('/')
def index():
    total = len(analysis_cache)
    total_val = sum(a.get('total_budget', 0) for a in analysis_cache.values())
    avg_risk_val = sum(a.get('risk_score', 0) for a in analysis_cache.values()) / max(total, 1)
    savings_val = sum(a.get('potential_savings', 0) for a in analysis_cache.values())
    
    recent = []
    for file_id, data in list(analysis_cache.items())[-5:]:
        if not file_id.startswith('comparison_'):
            recent.append({
                'id': file_id,
                'filename': data.get('filename', 'Unknown'),
                'timestamp': data.get('timestamp', 'Unknown'),
                'total_budget': data.get('total_budget', 0),
                'risk_level': data.get('risk_level', 'Unknown')
            })
    recent.reverse()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Production Budget Pro</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link active">🏠 Dashboard</a>
                <a href="/upload" class="nav-link">📤 Upload</a>
                <a href="/compare" class="nav-link">🔍 Compare</a>
                <a href="/history" class="nav-link">📋 History</a>
            </div>
    """
    
    html += """
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">
                            <strong>{{ '✓' if category == 'success' else '⚠' }}</strong>
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
    """
    
    html += """
            <div class="header">
                <h1>🎬 Production Budget Pro</h1>
                <p class="subtitle">Advanced Budget Analysis & Risk Management</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Analyzed</div>
                    <div class="stat-value">""" + str(total) + """</div>
                    <div>Budget files processed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Budget Value</div>
                    <div class="stat-value">$""" + f"{total_val/1000:.0f}" + """K</div>
                    <div>Across all projects</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Risk Score</div>
                    <div class="stat-value">""" + f"{avg_risk_val:.1f}" + """/100</div>
                    <div>""" + ('Low' if avg_risk_val < 50 else 'Medium') + """ risk level</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Potential Savings</div>
                    <div class="stat-value">$""" + f"{savings_val/1000:.0f}" + """K</div>
                    <div>Optimization opportunities</div>
                </div>
            </div>
            
            <div class="content-box">
                <h2>Quick Actions</h2>
                <div style="margin-top: 20px;">
                    <a href="/upload" class="btn">📤 Upload New Budget</a>
                    <a href="/compare" class="btn btn-secondary">🔍 Compare Budgets</a>
                    <a href="/history" class="btn btn-secondary">📋 View History</a>
                </div>
            </div>
    """
    
    if recent:
        html += """
            <div class="content-box">
                <h2>Recent Analysis</h2>
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Date</th>
                            <th>Budget</th>
                            <th>Risk Level</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        for file in recent:
            html += f"""
                        <tr>
                            <td><strong>{file['filename']}</strong></td>
                            <td>{file['timestamp']}</td>
                            <td>${file['total_budget']:,.2f}</td>
                            <td><span class="badge badge-{file['risk_level'].lower()}">{file['risk_level']}</span></td>
                            <td><a href="/analyze/{file['id']}" class="btn" style="padding: 8px 16px; font-size: 12px;">View</a></td>
                        </tr>
            """
        html += """
                    </tbody>
                </table>
            </div>
        """
    else:
        html += """
            <div class="content-box">
                <div class="alert alert-info">
                    <span>ℹ️</span>
                    <div>
                        <strong>No budgets analyzed yet</strong><br>
                        Upload your first budget to get started
                    </div>
                </div>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html)

@app.route('/upload')
def upload_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Budget</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/upload" class="nav-link active">📤 Upload</a>
                <a href="/compare" class="nav-link">🔍 Compare</a>
                <a href="/history" class="nav-link">📋 History</a>
            </div>
    """
    
    html += """
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
    """
    
    html += """
            <div class="header">
                <h1>Upload Production Budget</h1>
                <p class="subtitle">Upload Excel or CSV file for analysis</p>
            </div>
            
            <div class="content-box">
                <form method="POST" action="/process-upload" enctype="multipart/form-data" id="uploadForm">
                    <div class="upload-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
                        <div class="upload-icon">📁</div>
                        <h2>Drag & Drop your budget file here</h2>
                        <p style="color: #666; margin: 15px 0;">or click to browse</p>
                        <input type="file" id="fileInput" name="file" accept=".xlsx,.xls,.csv" required onchange="showFile()">
                        <div id="fileInfo" style="margin-top: 20px; display: none;">
                            <p style="color: #667eea; font-weight: 600;" id="fileName"></p>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 30px;">
                        <button type="submit" class="btn" id="analyzeBtn" disabled>Analyze Budget</button>
                        <a href="/" class="btn btn-secondary">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            function showFile() {
                const input = document.getElementById('fileInput');
                const fileInfo = document.getElementById('fileInfo');
                const fileName = document.getElementById('fileName');
                const btn = document.getElementById('analyzeBtn');
                
                if (input.files.length > 0) {
                    fileName.textContent = '📄 ' + input.files[0].name;
                    fileInfo.style.display = 'block';
                    btn.disabled = false;
                }
            }
            
            const dropZone = document.getElementById('dropZone');
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(e => {
                dropZone.addEventListener(e, evt => evt.preventDefault(), false);
            });
            
            dropZone.addEventListener('drop', e => {
                document.getElementById('fileInput').files = e.dataTransfer.files;
                showFile();
            }, false);
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html)

@app.route('/process-upload', methods=['POST'])
def process_upload():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = hashlib.md5(f"{timestamp}{filename}".encode()).hexdigest()[:12]
        unique_filename = f"{file_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        try:
            df = pd.read_excel(filepath) if filename.endswith(('.xlsx', '.xls')) else pd.read_csv(filepath)
            total_budget = df["Amount"].sum()
            
            risk_manager = RiskManager()
            risk_analysis = risk_manager.analyze_risks(df)
            optimizations = find_optimizations(df)
            
            analysis_cache[file_id] = {
                'id': file_id,
                'filename': filename,
                'filepath': filepath,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_budget': float(total_budget),
                'line_items': len(df),
                'risk_score': risk_analysis['summary']['overall_risk_score'],
                'risk_level': risk_analysis['summary']['risk_level'],
                'potential_savings': optimizations['potential_savings'],
                'df': df
            }
            
            flash('Budget analyzed successfully!', 'success')
            return redirect(url_for('view_analysis', file_id=file_id))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('upload_page'))
    
    flash('Invalid file type', 'error')
    return redirect(url_for('upload_page'))

@app.route('/compare')
def compare_page():
    """Budget comparison page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compare Budgets</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/upload" class="nav-link">📤 Upload</a>
                <a href="/compare" class="nav-link active">🔍 Compare</a>
                <a href="/history" class="nav-link">📋 History</a>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="header">
                <h1>Compare Budgets</h1>
                <p class="subtitle">Upload 2-4 budget versions for side-by-side comparison</p>
            </div>
            
            <div class="content-box">
                <form method="POST" action="/process-comparison" enctype="multipart/form-data" id="compareForm">
                    <div class="upload-multiple">
                        <div class="file-upload-box" onclick="document.getElementById('file1').click()">
                            <div style="font-size: 3em;">📄</div>
                            <h3>Budget Version 1</h3>
                            <input type="file" id="file1" name="file1" accept=".xlsx,.xls,.csv" required onchange="showFileNum(1)">
                            <div id="fileName1" class="file-name"></div>
                        </div>
                        
                        <div class="file-upload-box" onclick="document.getElementById('file2').click()">
                            <div style="font-size: 3em;">📄</div>
                            <h3>Budget Version 2</h3>
                            <input type="file" id="file2" name="file2" accept=".xlsx,.xls,.csv" required onchange="showFileNum(2)">
                            <div id="fileName2" class="file-name"></div>
                        </div>
                        
                        <div class="file-upload-box" onclick="document.getElementById('file3').click()">
                            <div style="font-size: 3em;">📄</div>
                            <h3>Budget Version 3</h3>
                            <p style="color: #999; font-size: 0.9em;">(Optional)</p>
                            <input type="file" id="file3" name="file3" accept=".xlsx,.xls,.csv" onchange="showFileNum(3)">
                            <div id="fileName3" class="file-name"></div>
                        </div>
                        
                        <div class="file-upload-box" onclick="document.getElementById('file4').click()">
                            <div style="font-size: 3em;">📄</div>
                            <h3>Budget Version 4</h3>
                            <p style="color: #999; font-size: 0.9em;">(Optional)</p>
                            <input type="file" id="file4" name="file4" accept=".xlsx,.xls,.csv" onchange="showFileNum(4)">
                            <div id="fileName4" class="file-name"></div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <button type="submit" class="btn" id="compareBtn" disabled>Compare Budgets</button>
                        <a href="/" class="btn btn-secondary">Cancel</a>
                    </div>
                </form>
            </div>
            
            <div class="content-box">
                <h2>What You'll Get</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <strong>📊 Side-by-Side</strong>
                        <p style="color: #666; font-size: 0.9em; margin-top: 10px;">All budgets in one view</p>
                    </div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <strong>💰 Variances</strong>
                        <p style="color: #666; font-size: 0.9em; margin-top: 10px;">Dollar & percentage differences</p>
                    </div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <strong>📈 Highlights</strong>
                        <p style="color: #666; font-size: 0.9em; margin-top: 10px;">Biggest changes shown</p>
                    </div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
                        <strong>🎯 Summary</strong>
                        <p style="color: #666; font-size: 0.9em; margin-top: 10px;">Min/max/average stats</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function showFileNum(num) {
                const input = document.getElementById('file' + num);
                const fileName = document.getElementById('fileName' + num);
                const box = input.closest('.file-upload-box');
                
                if (input.files.length > 0) {
                    fileName.textContent = input.files[0].name;
                    box.classList.add('file-uploaded');
                    checkCanCompare();
                }
            }
            
            function checkCanCompare() {
                const file1 = document.getElementById('file1').files.length > 0;
                const file2 = document.getElementById('file2').files.length > 0;
                const btn = document.getElementById('compareBtn');
                btn.disabled = !(file1 && file2);
            }
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html)

@app.route('/process-comparison', methods=['POST'])
def process_comparison():
    """Process multiple budgets for comparison"""
    uploaded_files = []
    
    for i in range(1, 5):
        file_key = f'file{i}'
        if file_key in request.files:
            file = request.files[file_key]
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_{i}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                
                try:
                    df = pd.read_excel(filepath) if filename.endswith(('.xlsx', '.xls')) else pd.read_csv(filepath)
                    uploaded_files.append({
                        'name': filename,
                        'df': df,
                        'total': float(df['Amount'].sum()),
                        'items': len(df)
                    })
                except Exception as e:
                    flash(f'Error reading {filename}: {str(e)}', 'error')
                    return redirect(url_for('compare_page'))
    
    if len(uploaded_files) < 2:
        flash('Please upload at least 2 budget files', 'error')
        return redirect(url_for('compare_page'))
    
    comparison_data = compare_budgets_data(uploaded_files)
    
    comparison_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12]
    analysis_cache[f"comparison_{comparison_id}"] = {
        'files': uploaded_files,
        'comparison': comparison_data,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    flash(f'Successfully compared {len(uploaded_files)} budgets!', 'success')
    return redirect(url_for('view_comparison', comparison_id=comparison_id))

def compare_budgets_data(budgets):
    """Compare multiple budgets"""
    comparison = {
        'totals': [],
        'departments': {},
        'variances': [],
        'summary': {}
    }
    
    for budget in budgets:
        comparison['totals'].append({
            'name': budget['name'],
            'total': budget['total'],
            'items': budget['items']
        })
    
    all_departments = set()
    for budget in budgets:
        if 'Department' in budget['df'].columns:
            all_departments.update(budget['df']['Department'].unique())
    
    for dept in all_departments:
        comparison['departments'][dept] = []
        
        for budget in budgets:
            if 'Department' in budget['df'].columns:
                dept_data = budget['df'][budget['df']['Department'] == dept]
                if not dept_data.empty:
                    dept_total = float(dept_data['Amount'].sum())
                    dept_pct = (dept_total / budget['total']) * 100
                else:
                    dept_total = 0.0
                    dept_pct = 0.0
            else:
                dept_total = 0.0
                dept_pct = 0.0
            
            comparison['departments'][dept].append({
                'budget_name': budget['name'],
                'amount': dept_total,
                'percentage': dept_pct
            })
    
    if len(budgets) >= 2:
        base_budget = budgets[0]
        for budget in budgets[1:]:
            variance = budget['total'] - base_budget['total']
            variance_pct = (variance / base_budget['total']) * 100 if base_budget['total'] > 0 else 0
            
            comparison['variances'].append({
                'budget_name': budget['name'],
                'variance': variance,
                'variance_pct': variance_pct
            })
    
    comparison['summary'] = {
        'min_budget': min(b['total'] for b in budgets),
        'max_budget': max(b['total'] for b in budgets),
        'avg_budget': sum(b['total'] for b in budgets) / len(budgets),
        'total_variance': max(b['total'] for b in budgets) - min(b['total'] for b in budgets)
    }
    
    return comparison

@app.route('/comparison/<comparison_id>')
def view_comparison(comparison_id):
    """View comparison results"""
    cache_key = f"comparison_{comparison_id}"
    
    if cache_key not in analysis_cache:
        flash('Comparison not found', 'error')
        return redirect(url_for('compare_page'))
    
    data = analysis_cache[cache_key]
    budgets = data['files']
    comparison = data['comparison']
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Budget Comparison Results</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/upload" class="nav-link">📤 Upload</a>
                <a href="/compare" class="nav-link active">🔍 Compare</a>
                <a href="/history" class="nav-link">📋 History</a>
            </div>
            
            <div class="header">
                <h1>📊 Budget Comparison Results</h1>
                <p class="subtitle">""" + str(len(budgets)) + """ budgets compared</p>
            </div>
            
            <div class="stats-grid">
    """
    
    for budget_total in comparison['totals']:
        is_max = budget_total['total'] == comparison['summary']['max_budget']
        is_min = budget_total['total'] == comparison['summary']['min_budget']
        badge = ""
        if is_max and len(budgets) > 2:
            badge = " 📈"
        elif is_min and len(budgets) > 2:
            badge = " 📉"
        
        html += f"""
                <div class="stat-card">
                    <div class="stat-label">{budget_total['name']}{badge}</div>
                    <div class="stat-value">${budget_total['total']:,.0f}</div>
                    <div>{budget_total['items']} items</div>
                </div>
        """
    
    html += """
            </div>
            
            <div class="content-box">
                <h2>Total Budget Comparison</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Budget Version</th>
                            <th>Total Amount</th>
                            <th>Line Items</th>
    """
    
    if len(budgets) >= 2:
        html += "<th>Variance from " + budgets[0]['name'] + "</th>"
    
    html += """
                        </tr>
                    </thead>
                    <tbody>
    """
    
    html += f"""
                        <tr>
                            <td><strong>{budgets[0]['name']}</strong> (Baseline)</td>
                            <td>${budgets[0]['total']:,.2f}</td>
                            <td>{budgets[0]['items']}</td>
    """
    if len(budgets) >= 2:
        html += "<td>—</td>"
    html += "</tr>"
    
    for i, variance in enumerate(comparison['variances']):
        html += f"""
                        <tr>
                            <td><strong>{variance['budget_name']}</strong></td>
                            <td>${budgets[i+1]['total']:,.2f}</td>
                            <td>{budgets[i+1]['items']}</td>
                            <td class="variance-{'positive' if variance['variance'] > 0 else 'negative'}">
                                {'▲' if variance['variance'] > 0 else '▼'} ${abs(variance['variance']):,.2f} 
                                ({variance['variance_pct']:+.1f}%)
                            </td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
            
            <div class="content-box">
                <h2>Department Comparison</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Department</th>
    """
    
    for budget in budgets:
        html += f"<th>{budget['name']}<br><small>Amount / %</small></th>"
    
    html += """
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for dept, dept_data in sorted(comparison['departments'].items()):
        html += f"<tr><td><strong>{dept}</strong></td>"
        
        amounts = [d['amount'] for d in dept_data]
        max_amt = max(amounts) if amounts else 0
        min_amt = min(amounts) if amounts else 0
        
        for budget_dept in dept_data:
            highlight = ""
            if len(budgets) > 2:
                if budget_dept['amount'] == max_amt and max_amt > 0:
                    highlight = " class='highlight-max'"
                elif budget_dept['amount'] == min_amt and min_amt < max_amt:
                    highlight = " class='highlight-min'"
            
            html += f"""
                            <td{highlight}>
                                ${budget_dept['amount']:,.0f}<br>
                                <small style="color: #666;">{budget_dept['percentage']:.1f}%</small>
                            </td>
            """
        
        html += "</tr>"
    
    html += """
                    </tbody>
                </table>
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    <small>
                        <strong>Legend:</strong>
                        <span style="background: #fff3cd; padding: 3px 8px; margin: 0 5px; border-radius: 3px;">Highest</span>
                        <span style="background: #d4edda; padding: 3px 8px; margin: 0 5px; border-radius: 3px;">Lowest</span>
                    </small>
                </div>
            </div>
            
            <div class="content-box">
                <h2>Summary Statistics</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div style="padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <strong>Minimum Budget</strong>
                        <div style="font-size: 1.5em; color: #28a745; margin-top: 10px;">
                            $""" + f"{comparison['summary']['min_budget']:,.0f}" + """
                        </div>
                    </div>
                    <div style="padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <strong>Maximum Budget</strong>
                        <div style="font-size: 1.5em; color: #dc3545; margin-top: 10px;">
                            $""" + f"{comparison['summary']['max_budget']:,.0f}" + """
                        </div>
                    </div>
                    <div style="padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <strong>Average Budget</strong>
                        <div style="font-size: 1.5em; color: #667eea; margin-top: 10px;">
                            $""" + f"{comparison['summary']['avg_budget']:,.0f}" + """
                        </div>
                    </div>
                    <div style="padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <strong>Total Variance</strong>
                        <div style="font-size: 1.5em; color: #fd7e14; margin-top: 10px;">
                            $""" + f"{comparison['summary']['total_variance']:,.0f}" + """
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="/compare" class="btn">Compare More Budgets</a>
                <a href="/" class="btn btn-secondary">Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/analyze/<file_id>')
def view_analysis(file_id):
    if file_id not in analysis_cache:
        flash('Analysis not found', 'error')
        return redirect(url_for('index'))
    
    data = analysis_cache[file_id]
    df = data['df']
    
    departments = {}
    if "Department" in df.columns:
        total = df["Amount"].sum()
        for dept, group in df.groupby("Department"):
            dept_total = group["Amount"].sum()
            departments[dept] = {
                "amount": float(dept_total),
                "percentage": float(dept_total / total * 100),
                "items": len(group)
            }
    
    risk_manager = RiskManager()
    risk_analysis = risk_manager.analyze_risks(df)
    
    vis_paths = create_visualizations(df, app.config['OUTPUT_FOLDER'])
    visualizations = []
    for key, path in vis_paths.items():
        if os.path.exists(path):
            visualizations.append({
                'title': key.replace('_', ' ').title(),
                'filename': os.path.basename(path)
            })
    
    report_file = f"analysis_{file_id}.json"
    report_path = os.path.join(app.config['OUTPUT_FOLDER'], report_file)
    with open(report_path, 'w') as f:
        json.dump({
            'filename': data['filename'],
            'total_budget': data['total_budget'],
            'risk_analysis': risk_analysis['summary']
        }, f, indent=2)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analysis Results</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/upload" class="nav-link">📤 Upload</a>
                <a href="/compare" class="nav-link">🔍 Compare</a>
                <a href="/history" class="nav-link">📋 History</a>
            </div>
            
            <div class="header">
                <h1>📊 Analysis Results</h1>
                <p class="subtitle">""" + data['filename'] + """</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Budget</div>
                    <div class="stat-value">$""" + f"{data['total_budget']:.0f}" + """</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Line Items</div>
                    <div class="stat-value">""" + str(data['line_items']) + """</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Departments</div>
                    <div class="stat-value">""" + str(len(departments)) + """</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Risk Level</div>
                    <div class="stat-value">""" + data['risk_level'] + """</div>
                </div>
            </div>
            
            <div class="content-box">
                <h2>Department Breakdown</h2>
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
    
    for dept, dept_data in departments.items():
        html += f"""
                        <tr>
                            <td>{dept}</td>
                            <td>${dept_data['amount']:,.2f}</td>
                            <td>{dept_data['percentage']:.1f}%</td>
                            <td>{dept_data['items']}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
            
            <div class="content-box">
                <h2>Risk Analysis</h2>
                <p>Overall Risk Score: <strong>""" + f"{data['risk_score']:.1f}" + """/100</strong> (""" + data['risk_level'] + """)</p>
                <table>
                    <thead>
                        <tr>
                            <th>Risk Category</th>
                            <th>Items</th>
                            <th>Amount</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for cat, cat_data in risk_analysis['summary']['risk_categories'].items():
        if cat_data['count'] > 0:
            html += f"""
                        <tr>
                            <td>{cat.replace('_', ' ').title()}</td>
                            <td>{cat_data['count']}</td>
                            <td>${cat_data['amount']:,.2f}</td>
                            <td>{cat_data['percentage']:.1f}%</td>
                        </tr>
            """
    
    html += """
                    </tbody>
                </table>
            </div>
    """
    
    if visualizations:
        html += """
            <div class="content-box">
                <h2>Visualizations</h2>
        """
        for viz in visualizations:
            html += f"""
                <div style="text-align: center; margin: 30px 0;">
                    <h3>{viz['title']}</h3>
                    <img src="/output/{viz['filename']}" class="chart-img">
                </div>
            """
        html += """
            </div>
        """
    
    html += f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="/" class="btn">Back to Dashboard</a>
                <a href="/download/{report_file}" class="btn btn-success">Download Report</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/history')
def history_page():
    files = [v for k, v in analysis_cache.items() if not k.startswith('comparison_')]
    files.reverse()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analysis History</title>
        """ + STYLES + """
    </head>
    <body>
        <div class="container">
            <div class="nav-menu">
                <a href="/" class="nav-link">🏠 Dashboard</a>
                <a href="/upload" class="nav-link">📤 Upload</a>
                <a href="/compare" class="nav-link">🔍 Compare</a>
                <a href="/history" class="nav-link active">📋 History</a>
            </div>
            
            <div class="header">
                <h1>📋 Analysis History</h1>
                <p class="subtitle">Previously analyzed budgets</p>
            </div>
    """
    
    if files:
        html += """
            <div class="content-box">
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Date</th>
                            <th>Budget</th>
                            <th>Items</th>
                            <th>Risk</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        for file in files:
            html += f"""
                        <tr>
                            <td><strong>{file['filename']}</strong></td>
                            <td>{file['timestamp']}</td>
                            <td>${file['total_budget']:,.2f}</td>
                            <td>{file['line_items']}</td>
                            <td><span class="badge badge-{file['risk_level'].lower()}">{file['risk_level']}</span></td>
                            <td><a href="/analyze/{file['id']}" class="btn" style="padding: 8px 16px;">View</a></td>
                        </tr>
            """
        html += """
                    </tbody>
                </table>
            </div>
        """
    else:
        html += """
            <div class="content-box">
                <div class="alert alert-info">
                    <span>ℹ️</span>
                    <div>No analysis history. <a href="/upload">Upload a budget</a> to get started.</div>
                </div>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/output/<filename>')
def serve_output(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename))

@app.route('/download/<filename>')
def download_report(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    os.makedirs('data/input', exist_ok=True)
    os.makedirs('data/output', exist_ok=True)
    
    print("=" * 70)
    print("🎬 Production Budget Pro - ENHANCED with Comparison")
    print("=" * 70)
    print("\n✨ Features:")
    print("  • Dashboard with real-time analytics")
    print("  • 8-category risk assessment")
    print("  • Budget optimization")
    print("  • Budget comparison (NEW!)")
    print("  • Visual reports and charts")
    print("\n🚀 Starting server...")
    print("📱 Open: http://localhost:5000")
    print("⚡ Press CTRL+C to stop")
    print("=" * 70)
    
    app.run(debug=True, port=5000)


