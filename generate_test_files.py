"""
Generate 10 Test CSV Files for Budget Analysis Testing
Covers all edge cases and real-world scenarios
Fixed for OneDrive issues
"""

import pandas as pd
import numpy as np
import os
import sys

print("=== GENERATING TEST FILES FOR BUDGET ANALYSIS ===")
print("=" * 60)

# Try different locations for test files
possible_locations = [
    os.path.join(os.path.expanduser("~"), "Desktop", "test_files"),  # Desktop
    "C:\\temp\\test_files",  # C: drive temp folder
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files")  # Current dir
]

# Choose the first location that works
test_dir = None
for location in possible_locations:
    try:
        os.makedirs(location, exist_ok=True)
        # Test if we can write to this location
        test_file = os.path.join(location, "test_write.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        test_dir = location
        print(f"Using location: {test_dir}")
        break
    except Exception as e:
        print(f"Cannot write to {location}: {e}")
        continue

if test_dir is None:
    print("ERROR: Cannot find a writable location for test files!")
    print("Please run this script outside of OneDrive sync folder.")
    sys.exit(1)

# ============================================================================
# 1. BASIC BUDGET - Normal business budget
# ============================================================================
basic_data = {
    'Description': [
        'Office Rent', 'Employee Salaries', 'Software Licenses', 
        'Marketing Campaign', 'Utilities', 'Travel Expenses',
        'Office Supplies', 'Professional Services', 'Equipment Purchase',
        'Insurance Premium', 'Training Programs', 'Client Entertainment'
    ],
    'Department': [
        'Operations', 'HR', 'IT', 'Marketing', 'Operations', 'Sales',
        'Operations', 'Executive', 'IT', 'Finance', 'HR', 'Sales'
    ],
    'Category': [
        'Facilities', 'Personnel', 'Software', 'Advertising', 'Utilities',
        'Travel', 'Supplies', 'Consulting', 'Hardware', 'Insurance',
        'Development', 'Entertainment'
    ],
    'Vendor': [
        'ABC Properties', 'Internal', 'TechCorp', 'Media Agency',
        'Power Co', 'Travel Plus', 'Office Depot', 'Consulting Inc',
        'Tech Store', 'InsureCo', 'Training Pro', 'Various'
    ],
    'Amount': [
        5000, 45000, 3000, 12000, 1500, 8000,
        800, 5000, 7500, 3200, 4500, 2500
    ]
}

df = pd.DataFrame(basic_data)
df.to_csv(f'{test_dir}/1_basic_budget.csv', index=False)
print("[OK] 1. Basic Budget: Normal business expenses")

# ============================================================================
# 2. FILM PRODUCTION BUDGET - Creative industry
# ============================================================================
film_data = {
    'Description': [
        'Script Development', 'Director Fee', 'Cinematographer',
        'Camera Equipment Rental', 'Lighting Equipment', 'Sound Equipment',
        'Actors', 'Location Fees', 'Catering & Meals',
        'Post-Production Editing', 'Visual Effects', 'Music Licensing',
        'Insurance', 'Contingency (10%)'
    ],
    'Department': [
        'Pre-Production', 'Production', 'Production',
        'Production', 'Production', 'Production',
        'Talent', 'Logistics', 'Hospitality',
        'Post-Production', 'Post-Production', 'Post-Production',
        'Administrative', 'Contingency'
    ],
    'Category': [
        'Creative', 'Talent', 'Crew',
        'Equipment', 'Equipment', 'Equipment',
        'Talent', 'Location', 'Hospitality',
        'Editing', 'VFX', 'Music',
        'Insurance', 'Contingency'
    ],
    'Vendor': [
        'Writer Studio', 'Director LLC', 'DP Services',
        'Camera Rentals', 'Lighting Co', 'Sound Pro',
        'Talent Agency', 'Location Mgmt', 'Catering Co',
        'Edit Studio', 'VFX House', 'Music Library',
        'Film Insure', 'Internal'
    ],
    'Amount': [
        8000, 25000, 15000, 12000, 8000, 5000,
        40000, 15000, 10000, 20000, 15000, 5000,
        3000, 17300  # 10% of total
    ]
}

df = pd.DataFrame(film_data)
df.to_csv(f'{test_dir}/2_film_production.csv', index=False)
print("[OK] 2. Film Production: Creative industry budget")

# ============================================================================
# 3. TECH STARTUP - High-growth company
# ============================================================================
startup_data = {
    'Description': [
        'Software Development Team', 'Cloud Infrastructure (AWS)',
        'Marketing & Customer Acquisition', 'Office Space (WeWork)',
        'Salaries - Engineering', 'Salaries - Sales',
        'Salaries - Marketing', 'Software Tools (Slack, Notion, etc.)',
        'Legal & Accounting Services', 'Travel & Conferences',
        'Employee Benefits', 'Hardware (Laptops, Servers)',
        'Customer Support Tools', 'Research & Development'
    ],
    'Department': [
        'Engineering', 'Infrastructure', 'Growth',
        'Operations', 'Engineering', 'Sales',
        'Marketing', 'Operations', 'Administrative',
        'Business Dev', 'HR', 'IT',
        'Customer Success', 'R&D'
    ],
    'Category': [
        'Development', 'Hosting', 'Marketing',
        'Facilities', 'Salaries', 'Salaries',
        'Salaries', 'Software', 'Professional Services',
        'Travel', 'Benefits', 'Hardware',
        'Software', 'Research'
    ],
    'Vendor': [
        'Internal', 'Amazon AWS', 'Google/FB Ads',
        'WeWork', 'Internal', 'Internal',
        'Internal', 'Various', 'Law Firm & CPA',
        'Various', 'Benefits Co', 'Apple/Dell',
        'Zendesk', 'Internal'
    ],
    'Amount': [
        80000, 15000, 30000, 12000,
        120000, 80000, 50000, 5000,
        15000, 10000, 25000, 30000,
        8000, 20000
    ]
}

df = pd.DataFrame(startup_data)
df.to_csv(f'{test_dir}/3_tech_startup.csv', index=False)
print("[OK] 3. Tech Startup: High-growth company budget")

# ============================================================================
# 4. EVENT MANAGEMENT - Conference/Event budget
# ============================================================================
event_data = {
    'Description': [
        'Venue Rental (3 days)', 'Catering (Breakfast, Lunch, Dinner)',
        'Audio-Visual Equipment', 'Keynote Speaker Fee',
        'Marketing & Promotion', 'Event Staff (50 people)',
        'Decorations & Theming', 'Registration System',
        'Print Materials (Badges, Programs)', 'Security Services',
        'WiFi & Internet', 'Swag Bags & Giveaways',
        'Photography & Videography', 'Contingency (15%)'
    ],
    'Department': [
        'Venue', 'Food & Beverage', 'Production',
        'Talent', 'Marketing', 'Staffing',
        'Design', 'Technology', 'Materials',
        'Security', 'Technology', 'Attendees',
        'Media', 'Contingency'
    ],
    'Category': [
        'Location', 'Hospitality', 'Equipment',
        'Professional', 'Advertising', 'Personnel',
        'Design', 'Software', 'Print',
        'Security', 'Technology', 'Materials',
        'Media', 'Contingency'
    ],
    'Vendor': [
        'Convention Center', 'Catering Co', 'AV Rentals',
        'Speaker Bureau', 'Marketing Agency', 'Staffing Agency',
        'Design Studio', 'Eventbrite', 'Print Shop',
        'Security Inc', 'ISP Provider', 'Promo Items Co',
        'Photo Studio', 'Internal'
    ],
    'Amount': [
        25000, 18000, 12000, 15000,
        8000, 20000, 6000, 3000,
        4000, 5000, 2000, 5000,
        6000, 14700  # 15% of total
    ]
}

df = pd.DataFrame(event_data)
df.to_csv(f'{test_dir}/4_event_conference.csv', index=False)
print("[OK] 4. Event Conference: Large event budget")

# ============================================================================
# 5. NON-PROFIT ORGANIZATION - Grant-funded budget
# ============================================================================
nonprofit_data = {
    'Description': [
        'Executive Director Salary', 'Program Staff Salaries',
        'Office Rent & Utilities', 'Program Materials & Supplies',
        'Website & Technology', 'Fundraising Events',
        'Grant Writing Services', 'Insurance & Legal',
        'Travel for Field Work', 'Volunteer Appreciation',
        'Marketing & Outreach', 'Professional Development',
        'Bank Fees & Accounting', 'Miscellaneous (5%)'
    ],
    'Department': [
        'Administration', 'Programs', 'Operations',
        'Programs', 'Operations', 'Fundraising',
        'Fundraising', 'Administration', 'Programs',
        'Volunteers', 'Marketing', 'Staff Development',
        'Finance', 'Contingency'
    ],
    'Category': [
        'Salaries', 'Salaries', 'Facilities',
        'Supplies', 'Technology', 'Events',
        'Professional Services', 'Insurance', 'Travel',
        'Recognition', 'Marketing', 'Training',
        'Finance', 'Contingency'
    ],
    'Vendor': [
        'Internal', 'Internal', 'Landlord',
        'Various', 'Web Developer', 'Event Planner',
        'Grant Writer', 'Legal Firm', 'Various',
        'Internal', 'Marketing Agency', 'Training Org',
        'Bank', 'Internal'
    ],
    'Amount': [
        60000, 80000, 12000, 5000,
        3000, 8000, 5000, 4000,
        6000, 2000, 4000, 3000,
        1000, 4900  # 5% of total
    ]
}

df = pd.DataFrame(nonprofit_data)
df.to_csv(f'{test_dir}/5_nonprofit_org.csv', index=False)
print("[OK] 5. Non-Profit Organization: Grant-funded budget")

# ============================================================================
# 6. EDGE CASES - Testing error handling
# ============================================================================
edge_data = {
    'Description': [
        'Very Small Item', 'Normal Item', 'Very Large Item (>50%)',
        'Duplicate Entry', 'Duplicate Entry', 'Item with Missing Dept',
        'Item with Missing Category', 'Negative Value (Credit/Refund)',
        'Zero Value Item', 'Item with Special Characters: @#$%',
        'Very Long Description That Might Break Layout Testing',
        'Item with Commas, in description', 'Multiple     Spaces',
        'ALL CAPS ITEM', 'mixed CASE Item'
    ],
    'Department': [
        'IT', 'Marketing', 'Executive',
        'HR', 'HR', '',  # Empty department
        'Finance', 'Accounting', 'Testing',
        'Operations', 'Administrative', 'Sales',
        'IT', 'HR', 'Marketing'
    ],
    'Category': [
        'Software', 'Advertising', 'Bonus',
        'Training', 'Training', 'Supplies',
        '',  # Empty category
        'Adjustment', 'Test', 'Special',
        'Administrative', 'Sales', 'IT',
        'HR', 'Marketing'
    ],
    'Vendor': [
        'Small Co', 'Medium Co', 'Big Corp',
        'Training Inc', 'Training Inc', 'Supply Co',
        'Finance Corp', 'Internal', 'Test Vendor',
        'Special Vendor', 'Long Name Vendor Corp LLC',
        'Sales, Inc', 'IT Vendor', 'HR Services', 'Marketing Agency'
    ],
    'Amount': [
        10,  # Very small
        5000,  # Normal
        75000,  # Very large (will be >50% of total)
        2000,  # Duplicate 1
        2000,  # Duplicate 2
        300,
        800,
        -1500,  # Negative value
        0,  # Zero value
        2500,
        1800,
        3200,
        950,
        1100,
        2750
    ]
}

df = pd.DataFrame(edge_data)
df.to_csv(f'{test_dir}/6_edge_cases.csv', index=False)
print("[OK] 6. Edge Cases: Tests error handling and special characters")

# ============================================================================
# 7. DEPARTMENT HEAVY - One department dominates
# ============================================================================
dept_heavy_data = {
    'Description': [f'Engineering Cost {i+1}' for i in range(15)] +
                   [f'Other Dept Cost {i+1}' for i in range(5)],
    'Department': ['Engineering'] * 15 + ['Marketing', 'Sales', 'HR', 'Finance', 'Operations'],
    'Category': ['Development'] * 15 + ['Ads', 'Commissions', 'Salaries', 'Fees', 'Supplies'],
    'Vendor': ['Internal'] * 20,
    'Amount': [10000] * 15 + [2000, 1500, 3000, 1000, 800]
}

df = pd.DataFrame(dept_heavy_data)
df.to_csv(f'{test_dir}/7_department_heavy.csv', index=False)
print("[OK] 7. Department Heavy: Engineering dominates budget")

# ============================================================================
# 8. MANY SMALL ITEMS - Many line items, small amounts
# ============================================================================
np.random.seed(42)
many_items = {
    'Description': [f'Small Expense Item {i:03d}' for i in range(1, 101)],
    'Department': np.random.choice(['IT', 'Marketing', 'Sales', 'HR', 'Operations'], 100),
    'Category': np.random.choice(['Software', 'Ads', 'Travel', 'Training', 'Supplies'], 100),
    'Vendor': [f'Vendor {(i % 20)+1:02d}' for i in range(100)],
    'Amount': np.random.randint(50, 500, 100)
}

df = pd.DataFrame(many_items)
df.to_csv(f'{test_dir}/8_many_small_items.csv', index=False)
print("[OK] 8. Many Small Items: 100 line items, small amounts")

# ============================================================================
# 9. INTERNATIONAL - Multiple currencies (converted to USD)
# ============================================================================
international_data = {
    'Description': [
        'Tokyo Office Rent', 'London Consultant Fee',
        'Berlin Team Offsite', 'Singapore Conference',
        'Sydney Software License', 'Dubai Client Meeting',
        'Paris Marketing Agency', 'Mumbai Development Team',
        'São Paulo Sales Office', 'Toronto Training',
        'Seoul Equipment Purchase', 'Hong Kong Legal Services'
    ],
    'Department': [
        'International', 'Consulting', 'Team Building',
        'Professional Development', 'IT', 'Sales',
        'Marketing', 'Engineering', 'Sales',
        'HR', 'Operations', 'Legal'
    ],
    'Category': [
        'Facilities', 'Professional Services', 'Travel',
        'Conference', 'Software', 'Client Relations',
        'Marketing', 'Development', 'Office',
        'Training', 'Equipment', 'Legal'
    ],
    'Vendor': [
        'Tokyo Realty', 'London Consulting', 'Berlin Hotel',
        'Singapore Conf Center', 'Sydney Tech', 'Dubai Hotel',
        'Paris Agency', 'Mumbai Dev', 'São Paulo Office',
        'Toronto Trainer', 'Seoul Electronics', 'HK Law Firm'
    ],
    'Amount': [
        8000,  # Tokyo
        12000,  # London
        6000,   # Berlin
        4500,   # Singapore
        3200,   # Sydney
        7500,   # Dubai
        9000,   # Paris
        15000,  # Mumbai
        5000,   # São Paulo
        3800,   # Toronto
        4200,   # Seoul
        5500    # Hong Kong
    ]
}

df = pd.DataFrame(international_data)
df.to_csv(f'{test_dir}/9_international.csv', index=False)
print("[OK] 9. International: Multi-country expenses")

# ============================================================================
# 10. QUARTERLY COMPARISON - Same categories, different quarters
# ============================================================================
quarters = ['Q1', 'Q2', 'Q3', 'Q4']
quarterly_data = []

base_amounts = {
    'Marketing': 15000,
    'Sales': 12000,
    'IT': 8000,
    'Operations': 6000,
    'HR': 4000
}

for quarter in quarters:
    for dept, base in base_amounts.items():
        # Add some variance (+/- 20%)
        variance = np.random.uniform(0.8, 1.2)
        amount = int(base * variance)
        
        quarterly_data.append({
            'Description': f'{dept} Expenses - {quarter}',
            'Department': dept,
            'Category': 'Operating Expenses',
            'Vendor': 'Various',
            'Amount': amount,
            'Quarter': quarter
        })

df = pd.DataFrame(quarterly_data)
# Remove Quarter column for CSV (optional field)
df_csv = df.drop('Quarter', axis=1)
df_csv.to_csv(f'{test_dir}/10_quarterly_comparison.csv', index=False)
print("[OK] 10. Quarterly Comparison: Same categories across quarters")

# ============================================================================
# SUMMARY & INSTRUCTIONS
# ============================================================================
print("\n" + "=" * 60)
print("TEST FILES GENERATED SUCCESSFULLY!")
print("=" * 60)
print(f"\nLocation: {test_dir}")
print("\nFile Summary:")
print("-" * 40)

files = os.listdir(test_dir)
for i, filename in enumerate(sorted(files), 1):
    filepath = os.path.join(test_dir, filename)
    size_kb = os.path.getsize(filepath) / 1024
    df = pd.read_csv(filepath)
    total = df['Amount'].sum()
    items = len(df)
    
    print(f"{i:2d}. {filename:25s} | {items:3d} items | ${total:>9,.0f} | {size_kb:.1f} KB")

print("\nTESTING RECOMMENDATIONS:")
print("1. Start with: 1_basic_budget.csv (simplest)")
print("2. Try: 6_edge_cases.csv (tests error handling)")
print("3. Test: 2_film_production.csv (real-world example)")
print("4. Upload: 10_quarterly_comparison.csv (for comparison feature)")
print("\nUpload these files to your Budget Analysis dashboard!")
print("=" * 60)