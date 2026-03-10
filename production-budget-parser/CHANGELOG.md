# CHANGELOG — Production Budget Parser

All notable changes to this project are documented here.

---

## [2.1.0] — 2026-03-10

### UI/UX Overhaul — Interactive Dashboard

#### New Features
- **Interactive Stat Cards**: All four dashboard stat cards (Total Budget, Line Items, Departments, Risk Level) are now clickable and open detailed modal overlays
  - **Total Budget modal**: Category breakdown table with amounts and percentages
  - **Line Items modal**: Full scrollable table of every budget line item with department, category, and amount
  - **Departments modal**: Per-department totals, percentages, and item counts
  - **Risk Level modal**: Overall risk score, risk category matrix, and high-risk items table (dynamic color-coded by severity)
- **Chart rendering fixed**: Department Allocation, Top 10 Budget Items, Category Breakdown, and Risk Distribution charts now render correctly on the analysis page
  - Added `charts.js` script tag (`defer`) to analysis page `<head>`
  - Changed chart initialization from `DOMContentLoaded` → `window.load` event with 200 ms fallback retry

#### Visual Changes
- **Background**: Changed from purple gradient (`linear-gradient(135deg, #667eea, #764ba2)`) to dark slate (`#0f172a`) for clear card contrast and improved readability across all pages
- **Stat card hover effects**: Cards lift and scale on hover with blue top border and gradient highlight; stat value turns blue; icon scales up
- **Section title**: Color updated from `white` (low contrast) to `#e2e8f0` (legible on dark background)
- **Chart containers**: Minimum height set (`360px`), flex layout ensures canvas fills available space without collapsing

#### Bug Fixes
- Fixed `upload_file()` calling non-existent `analyze_budget()` → corrected to `analyze_risks()`
- Fixed flash messages never displaying on index page (Python f-string HTML, no Jinja2 — now uses `get_flashed_messages()` called in Python before HTML generation)
- Removed duplicate `<h2>📊 Visual Comparison</h2>` heading on budget comparison page
- Fixed chart title readability on comparison charts: font color set to `#2c3e50`, size reduced from 18 → 15 px

#### Files Changed
- `web_app.py` — stat card modals, flash message support, chart script tag, upload route fix
- `static/css/modern-styles.css` — background, hover effects, chart container sizing, new utility classes
- `charts_data.py` — `window.load` event listener with fallback retry
- `comparison_charts.py` — chart title color and size fixes

---

## [2.0.0] — 2024-12-05

### Initial Release (v2.0.0)
- Flask web application with SQLite (SQLAlchemy)
- CSV budget upload and parsing
- Risk assessment via 8-category weighted system (patent pending)
- Budget comparison (2–4 files, variance calculation)
- Excel export and PDF report generation
- Chart.js interactive visualizations
- Basic authentication via `flask_auth.py`
