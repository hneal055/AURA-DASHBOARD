"""
Auto-Create Missing CSS File
Run this to automatically create comparison-styles.css
"""

import os

# CSS content
css_content = """/*
Comparison Styles CSS
Styles for budget comparison feature

Copyright © 2024-2025. All Rights Reserved.
PROPRIETARY AND CONFIDENTIAL
*/

/* Comparison Summary Grid */
.comparison-summary-grid {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 30px;
    margin: 30px 0;
    align-items: center;
}

.comparison-summary-card {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.comparison-summary-card h3 {
    margin: 0 0 15px 0;
    color: #6b21a8;
    font-size: 18px;
}

.big-number {
    font-size: 42px;
    font-weight: bold;
    color: #1e293b;
    margin: 15px 0;
}

.comparison-arrow-card {
    text-align: center;
    padding: 20px;
}

.change-indicator {
    font-size: 48px;
    font-weight: bold;
    margin-bottom: 10px;
}

.change-indicator.red {
    color: #ef4444;
}

.change-indicator.green {
    color: #22c55e;
}

/* Comparison Form */
.comparison-form-card {
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 30px 0;
}

.comparison-form {
    max-width: 900px;
    margin: 30px auto 0;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 30px;
    align-items: end;
    margin-bottom: 30px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group label {
    font-weight: 600;
    margin-bottom: 10px;
    color: #1e293b;
    font-size: 16px;
}

.form-control {
    padding: 12px 16px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.3s ease;
    background: white;
}

.form-control:focus {
    outline: none;
    border-color: #9333ea;
    box-shadow: 0 0 0 3px rgba(147, 51, 234, 0.1);
}

.comparison-arrow {
    font-size: 36px;
    color: #9333ea;
    padding-bottom: 10px;
    font-weight: bold;
}

.btn-large {
    padding: 16px 48px;
    font-size: 18px;
    font-weight: 600;
}

/* Insights List */
.insights-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.insight-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: start;
    gap: 15px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.insight-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.insight-icon {
    font-size: 32px;
    flex-shrink: 0;
}

.insight-text {
    flex: 1;
    line-height: 1.6;
    color: #475569;
    font-size: 16px;
}

/* Comparison Table */
.table-responsive {
    overflow-x: auto;
    margin: 20px 0;
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.comparison-table thead {
    background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%);
    color: white;
}

.comparison-table th {
    padding: 16px;
    text-align: left;
    font-weight: 600;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.comparison-table td {
    padding: 14px 16px;
    border-bottom: 1px solid #f1f5f9;
    color: #475569;
}

.comparison-table tbody tr:last-child td {
    border-bottom: none;
}

.comparison-table tbody tr:hover {
    background: #f8fafc;
}

/* Row status colors */
.comparison-table tr.increase {
    border-left: 4px solid #ef4444;
}

.comparison-table tr.decrease {
    border-left: 4px solid #22c55e;
}

.comparison-table tr.unchanged {
    border-left: 4px solid #94a3b8;
}

.comparison-table tr.new-item {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
}

.comparison-table tr.removed-item {
    background: #fef2f2;
    border-left: 4px solid #ef4444;
}

/* Budget Grid (for history view) */
.budget-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.budget-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.budget-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.budget-card-header {
    background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%);
    color: white;
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.budget-card-header h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
}

.budget-badge {
    background: rgba(255, 255, 255, 0.2);
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
}

.budget-card-body {
    padding: 20px;
}

.budget-card-body p {
    margin: 8px 0;
    color: #64748b;
    font-size: 14px;
}

.budget-card-footer {
    padding: 15px 20px;
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
}

.btn-sm {
    padding: 8px 16px;
    font-size: 14px;
}

/* Budget List (simple list view) */
.budget-list {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    margin: 20px 0;
}

.budget-list h3 {
    margin-top: 0;
    color: #1e293b;
}

.budget-list ul {
    list-style: none;
    padding: 0;
}

.budget-list li {
    padding: 15px;
    border-bottom: 1px solid #e2e8f0;
    font-size: 16px;
}

.budget-list li:last-child {
    border-bottom: none;
}

/* Alerts */
.alert {
    padding: 24px;
    border-radius: 12px;
    margin: 20px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.alert h3 {
    margin-top: 0;
    font-size: 20px;
}

.alert p {
    margin: 10px 0;
    line-height: 1.6;
}

.alert-info {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    color: #1e40af;
}

.alert-warning {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #92400e;
}

.alert-success {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    color: #166534;
}

/* Section subtitle */
.section-subtitle {
    color: #64748b;
    font-size: 16px;
    margin: 10px 0 20px 0;
}

/* Responsive Design */
@media (max-width: 968px) {
    .comparison-summary-grid {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .comparison-arrow-card {
        order: 2;
    }
    
    .form-row {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    
    .comparison-arrow {
        transform: rotate(90deg);
        padding: 10px 0;
    }
    
    .budget-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .comparison-form-card {
        padding: 20px;
    }
    
    .big-number {
        font-size: 32px;
    }
    
    .change-indicator {
        font-size: 36px;
    }
    
    .comparison-table {
        font-size: 14px;
    }
    
    .comparison-table th,
    .comparison-table td {
        padding: 10px 12px;
    }
    
    .btn-large {
        padding: 14px 32px;
        font-size: 16px;
    }
}

/* Print styles */
@media print {
    body {
        background: white;
    }
    
    .btn-group {
        display: none;
    }
    
    .comparison-form-card {
        display: none;
    }
    
    .chart-card {
        page-break-inside: avoid;
    }
    
    .comparison-table {
        page-break-inside: avoid;
    }
}
"""

# Create the CSS file
css_path = os.path.join('static', 'css', 'comparison-styles.css')

# Make sure directory exists
os.makedirs(os.path.dirname(css_path), exist_ok=True)

# Write the file
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css_content)

print("=" * 80)
print("✅ SUCCESS! comparison-styles.css created!")
print("=" * 80)
print()
print(f"File created at: {os.path.abspath(css_path)}")
print(f"File size: {len(css_content):,} bytes")
print()
print("🚀 Now run your app:")
print("   python web_app_COMPLETE_WITH_COMPARISON.py")
print()
print("=" * 80)