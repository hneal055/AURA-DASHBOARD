
"""
Budget Templates Database
"""

BUDGET_TEMPLATES = {
    "film_production": {
        "id": "film_production",
        "name": "🎬 Film Production Budget",
        "category": "Creative & Media",
        "description": "Complete budget for film/video production",
        "icon": "🎬",
        "popularity": 95,
        "line_items": [
            {"Description": "Script Development", "Department": "Pre-Production", "Category": "Creative", "Amount": 5000},
            {"Description": "Director Fee", "Department": "Production", "Category": "Talent", "Amount": 15000},
            {"Description": "Camera Equipment", "Department": "Production", "Category": "Equipment", "Amount": 8000}
        ],
        "total_amount": 28000,
        "item_count": 3,
        "departments": ["Pre-Production", "Production"]
    },
    "marketing_campaign": {
        "id": "marketing_campaign", 
        "name": "📢 Marketing Campaign Budget",
        "category": "Business & Marketing",
        "description": "Budget for digital marketing",
        "icon": "📢",
        "popularity": 88,
        "line_items": [
            {"Description": "Social Media Ads", "Department": "Digital", "Category": "Advertising", "Amount": 10000},
            {"Description": "Content Creation", "Department": "Content", "Category": "Creative", "Amount": 8000}
        ],
        "total_amount": 18000,
        "item_count": 2,
        "departments": ["Digital", "Content"]
    }
}

def get_template_categories():
    categories = {}
    for template in BUDGET_TEMPLATES.values():
        category = template['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(template)
    return categories

def get_popular_templates(limit=6):
    return list(BUDGET_TEMPLATES.values())[:limit]

def get_template_by_id(template_id):
    return BUDGET_TEMPLATES.get(template_id)

def search_templates(query):
    query = query.lower()
    results = []
    for template in BUDGET_TEMPLATES.values():
        if (query in template['name'].lower() or 
            query in template['description'].lower()):
            results.append(template)
    return results
