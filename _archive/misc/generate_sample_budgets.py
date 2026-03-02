"""
================================================================================
Sample Budget Generator
Creates realistic budget CSV files for testing
================================================================================
"""

import pandas as pd
import random
from datetime import datetime
import os

# Sample data pools
DEPARTMENTS = [
    'Production', 'Marketing', 'Technology', 'Operations', 
    'Human Resources', 'Finance', 'Sales', 'Creative'
]

CATEGORIES = {
    'Production': ['Equipment', 'Talent', 'Location', 'Props', 'Catering', 'Transportation'],
    'Marketing': ['Advertising', 'Social Media', 'PR', 'Events', 'Content Creation'],
    'Technology': ['Software Licenses', 'Hardware', 'Cloud Services', 'IT Support'],
    'Operations': ['Office Supplies', 'Utilities', 'Rent', 'Maintenance', 'Insurance'],
    'Human Resources': ['Salaries', 'Benefits', 'Training', 'Recruitment'],
    'Finance': ['Accounting', 'Legal', 'Banking Fees', 'Auditing'],
    'Sales': ['Commission', 'Travel', 'Client Entertainment', 'CRM Software'],
    'Creative': ['Design Tools', 'Stock Media', 'Freelancers', 'Studio Rental']
}

VENDORS = [
    'ABC Equipment Co', 'XYZ Productions', 'Tech Solutions Inc', 
    'Premier Rentals', 'Global Services LLC', 'Creative Studios',
    'Metro Supplies', 'Digital Marketing Pro', 'Cloud Systems',
    'Professional Services', 'Elite Consulting', 'Modern Office Supply',
    'Innovate Tech', 'Prime Logistics', 'Quality Catering',
    'Talent Agency Plus', 'Media Experts', 'Design Hub'
]

def generate_description(department, category):
    """Generate a realistic description based on department and category"""
    templates = {
        'Equipment': ['Camera rental', 'Lighting setup', 'Audio equipment', 'Studio gear'],
        'Talent': ['Actor fees', 'Director services', 'Crew wages', 'Consultant fees'],
        'Location': ['Location rental', 'Permit fees', 'Set construction', 'Location scouting'],
        'Software Licenses': ['Adobe Creative Cloud', 'Microsoft 365', 'Salesforce', 'Slack Premium'],
        'Advertising': ['Google Ads campaign', 'Facebook ads', 'Billboard rental', 'TV commercial'],
        'Office Supplies': ['Printer paper', 'Desk supplies', 'Conference room equipment'],
        'Salaries': ['Monthly payroll', 'Contractor payment', 'Executive compensation'],
        'Travel': ['Flight tickets', 'Hotel accommodation', 'Car rental', 'Per diem']
    }
    
    if category in templates:
        base = random.choice(templates[category])
    else:
        base = f"{category} expense"
    
    return f"{base} - {department}"


def generate_amount(category, size='medium'):
    """Generate realistic amounts based on category and budget size"""
    # Base ranges for different categories
    ranges = {
        'Equipment': (500, 15000),
        'Talent': (2000, 50000),
        'Location': (1000, 25000),
        'Software Licenses': (100, 5000),
        'Advertising': (1000, 30000),
        'Salaries': (3000, 150000),
        'Office Supplies': (50, 2000),
        'Travel': (200, 5000),
        'default': (100, 10000)
    }
    
    # Get range or use default
    min_amt, max_amt = ranges.get(category, ranges['default'])
    
    # Adjust for budget size
    multipliers = {'small': 0.5, 'medium': 1.0, 'large': 2.0}
    multiplier = multipliers.get(size, 1.0)
    
    min_amt *= multiplier
    max_amt *= multiplier
    
    # Generate amount
    amount = random.uniform(min_amt, max_amt)
    
    # Round to realistic values
    if amount < 100:
        return round(amount, 2)
    elif amount < 1000:
        return round(amount / 10) * 10
    else:
        return round(amount / 100) * 100


def generate_budget(name, num_items=50, size='medium'):
    """
    Generate a complete budget CSV file
    
    Args:
        name: Filename for the budget
        num_items: Number of line items
        size: Budget size ('small', 'medium', 'large')
    """
    data = []
    
    for _ in range(num_items):
        department = random.choice(DEPARTMENTS)
        category = random.choice(CATEGORIES[department])
        vendor = random.choice(VENDORS)
        description = generate_description(department, category)
        amount = generate_amount(category, size)
        
        data.append({
            'Description': description,
            'Department': department,
            'Category': category,
            'Vendor': vendor,
            'Amount': amount
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Sort by Department and Amount
    df = df.sort_values(['Department', 'Amount'], ascending=[True, False])
    
    # Save to CSV
    filename = f"{name}.csv"
    df.to_csv(filename, index=False)
    
    # Print summary
    total = df['Amount'].sum()
    print(f"✓ Generated: {filename}")
    print(f"  Total Budget: ${total:,.2f}")
    print(f"  Line Items: {len(df)}")
    print(f"  Departments: {df['Department'].nunique()}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    return filename


def generate_all_samples():
    """Generate multiple sample budgets for different scenarios"""
    print("=" * 70)
    print("📊 GENERATING SAMPLE BUDGETS")
    print("=" * 70)
    print()
    
    samples = [
        ('sample_budget_small', 25, 'small'),
        ('sample_budget_medium', 50, 'medium'),
        ('sample_budget_large', 100, 'large'),
        ('sample_film_production', 75, 'large'),
        ('sample_marketing_campaign', 40, 'medium'),
        ('sample_tech_startup', 60, 'medium')
    ]
    
    generated_files = []
    
    for name, items, size in samples:
        filename = generate_budget(name, items, size)
        generated_files.append(filename)
    
    print("=" * 70)
    print(f"✅ Generated {len(generated_files)} sample budget files!")
    print("=" * 70)
    print()
    print("📂 Files created:")
    for f in generated_files:
        print(f"   • {f}")
    print()
    print("🚀 Ready to test! Upload these files to your web app at:")
    print("   http://localhost:5000")
    print()
    
    return generated_files


if __name__ == '__main__':
    # Generate all sample budgets
    generate_all_samples()
    
    print("=" * 70)
    print("💡 TIP: These files are perfect for testing PATH A features:")
    print("   • Interactive charts will show department breakdowns")
    print("   • Risk analysis will flag high-cost items")
    print("   • Excel export will create formatted reports")
    print("   • PDF export will generate professional documents")
    print("=" * 70)
