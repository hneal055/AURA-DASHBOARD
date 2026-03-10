# CHANGELOG — Production Budget Parser

All notable changes to this project are documented here.

---

## [2.2.0] — 2026-03-10

### Production Hardening

#### Security

- CSRF protection on all POST forms (Flask-WTF `CSRFProtect`)
- `debug=False`, `host=127.0.0.1` — no longer binds to all interfaces
- XSS: all user-supplied CSV values escaped via `html.escape()` before HTML injection
- Session cookie flags: `HTTPONLY=True`, `SAMESITE=Lax`
- API key query-string support removed — header and JSON body only
- All exception handlers log full tracebacks server-side; users receive generic messages

#### Rate Limiting

- Flask-Limiter added: 200 req/day + 60 req/hr global, 20 uploads/hr per IP

#### Input Validation

- `Amount` column coerced to numeric on upload; fully non-numeric files rejected
- Partial non-numeric rows zeroed and logged as warnings

#### Infrastructure

- Startup script auto-detects gunicorn and uses it as WSGI server; falls back to Flask dev server
- `/api/health` endpoint added (no auth required) — returns `{"status": "ok", "analyses": N}`
- `api_keys.json` cached in memory after first read (was re-read on every API request)
- All dependencies pinned to exact versions in `requirements.txt`

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

- **Background**: Changed from purple gradient to dark slate (`#0f172a`) for clear card contrast
- **Stat card hover effects**: Cards lift and scale on hover with blue top border and gradient highlight
- **Section title**: Color updated from `white` to `#e2e8f0` (legible on dark background)
- **Chart containers**: Minimum height set (`360px`), flex layout ensures canvas fills available space

#### Bug Fixes

- Fixed `upload_file()` calling non-existent `analyze_budget()` → corrected to `analyze_risks()`
- Fixed flash messages never displaying on index page
- Fixed `pd.read_json()` pandas 2.x compatibility — wrapped all calls in `io.StringIO()`
- Removed duplicate `<h2>📊 Visual Comparison</h2>` heading on comparison page
- Fixed chart title readability on comparison charts

#### Files Changed

- `web_app.py` — stat card modals, flash message support, chart script tag, upload route fix
- `static/css/modern-styles.css` — background, hover effects, chart container sizing
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
