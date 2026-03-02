Write-Host "🌐 SETTING UP API ENDPOINTS & MONITORING" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n1. Creating API endpoints configuration..." -ForegroundColor White

# Create enhanced Nginx config with API endpoints
@"
server {
    listen 80;
    server_name localhost;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin" always;

    server_tokens off;

    # Basic Authentication for main site
    auth_basic "AURA Dashboard - Restricted Access";
    auth_basic_user_file /etc/nginx/auth/.htpasswd;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files `$uri `$uri/ =404;
    }

    # ========== PUBLIC API ENDPOINTS (No Auth) ==========
    
    # Health check
    location /api/health {
        access_log off;
        add_header Content-Type application/json;
        return 200 '{"status":"healthy","timestamp":"$(Get-Date -Format o)","service":"aura-dashboard"}';
    }

    # System status
    location /api/status {
        access_log off;
        add_header Content-Type application/json;
        return 200 '{"status":"running","version":"1.2.0","uptime":'$(Get-Uptime)',"environment":"production"}';
    }

    # Metrics endpoint
    location /api/metrics {
        access_log off;
        add_header Content-Type text/plain;
        return 200 "# HELP aura_requests_total Total number of requests
# TYPE aura_requests_total counter
aura_requests_total 1842
# HELP aura_uptime_seconds Current uptime in seconds
# TYPE aura_uptime_seconds gauge
aura_uptime_seconds 86400";
    }

    # ========== PROTECTED API ENDPOINTS (Require Auth) ==========
    
    # System info (protected)
    location /api/system {
        auth_basic "API Access";
        auth_basic_user_file /etc/nginx/auth/.htpasswd;
        
        add_header Content-Type application/json;
        return 200 '{"system":"AURA Dashboard","version":"1.2.0","features":["authentication","monitoring","api"]}';
    }

    # User info (protected)
    location /api/user {
        auth_basic "API Access";
        auth_basic_user_file /etc/nginx/auth/.htpasswd;
        
        add_header Content-Type application/json;
        return 200 '{"user":"authenticated","role":"admin","permissions":["read","write","admin"]}';
    }

    # Backup status (protected)
    location /api/backup {
        auth_basic "API Access";
        auth_basic_user_file /etc/nginx/auth/.htpasswd;
        
        add_header Content-Type application/json;
        return 200 '{"backup_status":"enabled","last_backup":"2024-01-15T10:30:00Z","backup_count":5}';
    }

    # ========== ADMIN ENDPOINTS ==========
    
    location /admin/ {
        # Additional security for admin area
        auth_basic "Admin Area";
        auth_basic_user_file /etc/nginx/auth/.htpasswd;
        
        # More restrictive CSP for admin
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self';" always;
    }

    # Docker status endpoint
    location /api/docker {
        auth_basic "API Access";
        auth_basic_user_file /etc/nginx/auth/.htpasswd;
        
        add_header Content-Type application/json;
        # This would typically connect to Docker socket, but for demo we return static
        return 200 '{"containers":1,"status":"running","image":"aura-dashboard-auth"}';
    }
}
"@ | Set-Content "nginx-api.conf"

Write-Host "✅ API endpoints configuration created" -ForegroundColor Green

Write-Host "`n2. Creating monitoring dashboard..." -ForegroundColor White

# Create monitoring HTML page
@"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA Monitoring</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .status-up { color: #27ae60; }
        .status-down { color: #e74c3c; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .api-test { background: #34495e; color: white; padding: 10px; border-radius: 5px; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 AURA Monitoring Dashboard</h1>
        
        <div class="card">
            <h2>API Endpoints Status</h2>
            <div id="apiStatus">
                <p>Testing endpoints...</p>
            </div>
        </div>
        
        <div class="card">
            <h2>System Metrics</h2>
            <div class="grid">
                <div class="card">
                    <h3>Uptime</h3>
                    <div class="metric" id="uptimeMetric">--</div>
                </div>
                <div class="card">
                    <h3>Requests</h3>
                    <div class="metric" id="requestsMetric">--</div>
                </div>
                <div class="card">
                    <h3>Status</h3>
                    <div class="metric status-up" id="statusMetric">--</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Quick Tests</h2>
            <button onclick="testAllEndpoints()">Run All Tests</button>
            <button onclick="testHealth()">Test Health</button>
            <button onclick="testMetrics()">Test Metrics</button>
            <div id="testResults"></div>
        </div>
    </div>

    <script>
        async function testEndpoint(url, requireAuth = false) {
            try {
                const options = requireAuth ? { 
                    headers: { 'Authorization': 'Basic ' + btoa('admin:AuraDemo2024!') }
                } : {};
                
                const response = await fetch(url, options);
                const data = await response.json();
                return { success: true, data, status: response.status };
            } catch (error) {
                return { success: false, error: error.message };
            }
        }
        
        async function testAllEndpoints() {
            const endpoints = [
                { url: '/api/health', name: 'Health Check', auth: false },
                { url: '/api/status', name: 'System Status', auth: false },
                { url: '/api/metrics', name: 'Metrics', auth: false },
                { url: '/api/system', name: 'System Info', auth: true },
                { url: '/api/user', name: 'User Info', auth: true }
            ];
            
            const results = document.getElementById('testResults');
            results.innerHTML = '<h3>Test Results:</h3>';
            
            for (const endpoint of endpoints) {
                const result = await testEndpoint(endpoint.url, endpoint.auth);
                const div = document.createElement('div');
                div.className = 'api-test';
                div.innerHTML = `$