# Phase 4: Frontend Integration
Write-Host "🚀 Starting Phase 4: Frontend Integration" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan

# Check if backend is running
Write-Host "🔍 Checking backend status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 5
    Write-Host "✅ Backend is running: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is not running. Please start it first." -ForegroundColor Red
    exit 1
}

# Create updated frontend files
Write-Host "📝 Creating enhanced frontend with API integration..." -ForegroundColor Yellow

# Create the main dashboard with API integration
$enhancedDashboard = @'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA Enterprise Dashboard</title>
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #64748b;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1e293b;
            --light: #f8fafc;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            width: 90%;
            max-width: 1200px;
            min-height: 80vh;
        }
        
        /* Login Screen */
        .login-container {
            padding: 3rem;
            text-align: center;
        }
        
        .login-form {
            max-width: 400px;
            margin: 0 auto;
        }
        
        .login-form input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
        }
        
        .login-form button {
            width: 100%;
            padding: 12px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px 0;
        }
        
        .login-form button:hover {
            background: var(--primary-dark);
        }
        
        /* Dashboard */
        .dashboard {
            display: none;
            padding: 2rem;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .logout-btn {
            background: var(--danger);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid var(--primary);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--dark);
        }
        
        .stat-label {
            color: var(--secondary);
            font-size: 0.9rem;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        .progress-bar {
            background: #e2e8f0;
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--primary);
            transition: width 0.3s ease;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: var(--secondary);
        }
        
        .error {
            background: var(--danger);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .success {
            background: var(--success);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Login Screen -->
        <div id="loginScreen" class="login-container">
            <h1>🔒 AURA Dashboard</h1>
            <p>Enterprise System Monitoring Platform</p>
            
            <div class="login-form">
                <h2>Sign In</h2>
                <div id="loginError" class="error" style="display: none;"></div>
                <input type="text" id="username" placeholder="Username" value="admin">
                <input type="password" id="password" placeholder="Password" value="AuraDemo2024!">
                <button onclick="login()">Login to Dashboard</button>
                <p><small>Demo: admin / AuraDemo2024!</small></p>
            </div>
        </div>
        
        <!-- Dashboard -->
        <div id="dashboard" class="dashboard">
            <div class="header">
                <h1>📊 AURA Enterprise Dashboard</h1>
                <div class="user-info">
                    <span>Welcome, <strong id="userDisplayName">User</strong></span>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                </div>
            </div>
            
            <div id="loadingMessage" class="loading">
                Loading dashboard data...
            </div>
            
            <div id="dashboardContent" style="display: none;">
                <!-- System Stats -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">System Status</div>
                        <div class="stat-value" id="systemStatus">Healthy</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">CPU Usage</div>
                        <div class="stat-value" id="cpuUsage">--%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Memory Usage</div>
                        <div class="stat-value" id="memoryUsage">--%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Database</div>
                        <div class="stat-value" id="databaseStatus">Connected</div>
                    </div>
                </div>
                
                <!-- Real-time Metrics -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>🖥️ CPU Performance</h3>
                        <div class="metric-value" id="cpuMetric">--%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="cpuProgress" style="width: 0%"></div>
                        </div>
                        <small>Real-time CPU utilization</small>
                    </div>
                    
                    <div class="metric-card">
                        <h3>💾 Memory Usage</h3>
                        <div class="metric-value" id="memoryMetric">--%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="memoryProgress" style="width: 0%"></div>
                        </div>
                        <small>System memory consumption</small>
                    </div>
                </div>
                
                <!-- API Status -->
                <div class="metric-card" style="margin-top: 1.5rem;">
                    <h3>🔌 Backend API Status</h3>
                    <div id="apiStatus">Checking...</div>
                    <small>Connection to backend services</small>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = 'http://localhost:5000/api/v1';
        let authToken = localStorage.getItem('aura_token');
        let userData = null;
        let refreshInterval = null;

        // Check if already logged in
        if (authToken) {
            verifyTokenAndLoadDashboard();
        }

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('loginError');

            errorDiv.style.display = 'none';

            try {
                const response = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    // Store token and user data
                    authToken = data.access_token;
                    userData = data.user;
                    localStorage.setItem('aura_token', authToken);
                    localStorage.setItem('aura_user', JSON.stringify(userData));
                    
                    showDashboard();
                    startDataRefresh();
                } else {
                    throw new Error(data.message || 'Login failed');
                }
            } catch (error) {
                errorDiv.textContent = error.message;
                errorDiv.style.display = 'block';
            }
        }

        async function verifyTokenAndLoadDashboard() {
            try {
                const response = await fetch(`${API_BASE}/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    userData = data.user;
                    showDashboard();
                    startDataRefresh();
                } else {
                    throw new Error('Token invalid');
                }
            } catch (error) {
                localStorage.removeItem('aura_token');
                localStorage.removeItem('aura_user');
                authToken = null;
                userData = null;
            }
        }

        function showDashboard() {
            document.getElementById('loginScreen').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
            
            if (userData) {
                document.getElementById('userDisplayName').textContent = userData.username;
            }
            
            loadDashboardData();
        }

        function showLogin() {
            document.getElementById('loginScreen').style.display = 'block';
            document.getElementById('dashboard').style.display = 'none';
            stopDataRefresh();
        }

        function logout() {
            localStorage.removeItem('aura_token');
            localStorage.removeItem('aura_user');
            authToken = null;
            userData = null;
            showLogin();
        }

        async function loadDashboardData() {
            const loadingMessage = document.getElementById('loadingMessage');
            const dashboardContent = document.getElementById('dashboardContent');
            
            try {
                // Load system health data
                const systemResponse = await fetch(`${API_BASE}/system/health`);
                const systemData = await systemResponse.json();

                if (systemData.status === 'success') {
                    updateSystemMetrics(systemData.data);
                    loadingMessage.style.display = 'none';
                    dashboardContent.style.display = 'block';
                }

                // Update API status
                document.getElementById('apiStatus').innerHTML = 
                    '<span style="color: var(--success)">✅ Connected</span>';

            } catch (error) {
                document.getElementById('apiStatus').innerHTML = 
                    '<span style="color: var(--danger)">❌ Connection Failed</span>';
                console.error('Dashboard data error:', error);
            }
        }

        function updateSystemMetrics(data) {
            // Update CPU metrics
            document.getElementById('cpuUsage').textContent = `${data.cpu_usage}%`;
            document.getElementById('cpuMetric').textContent = `${data.cpu_usage}%`;
            document.getElementById('cpuProgress').style.width = `${data.cpu_usage}%`;
            
            // Update memory metrics
            document.getElementById('memoryUsage').textContent = `${data.memory_usage}%`;
            document.getElementById('memoryMetric').textContent = `${data.memory_usage}%`;
            document.getElementById('memoryProgress').style.width = `${data.memory_usage}%`;
            
            // Update database status
            const dbStatus = data.database_status === 'connected' ? 
                '<span style="color: var(--success)">✅ Connected</span>' :
                `<span style="color: var(--danger)">❌ ${data.database_status}</span>`;
            document.getElementById('databaseStatus').innerHTML = dbStatus;
            
            // Update system status based on metrics
            const systemStatus = data.cpu_usage < 80 && data.memory_usage < 85 ? 
                '<span style="color: var(--success)">✅ Healthy</span>' :
                '<span style="color: var(--warning)">⚠️ Warning</span>';
            document.getElementById('systemStatus').innerHTML = systemStatus;
        }

        function startDataRefresh() {
            // Refresh data every 5 seconds
            refreshInterval = setInterval(loadDashboardData, 5000);
        }

        function stopDataRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        }

        // Handle page visibility to pause/refresh data
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                stopDataRefresh();
            } else if (authToken) {
                startDataRefresh();
                loadDashboardData(); // Immediate refresh when returning to tab
            }
        });
    </script>
</body>
</html>
'@

# Write the enhanced dashboard
$enhancedDashboard | Out-File -FilePath "dashboard/index.html" -Encoding UTF8
Write-Host "✅ Created enhanced dashboard with API integration" -ForegroundColor Green

# Create updated Docker configuration for frontend
Write-Host "🐳 Creating updated frontend Docker configuration..." -ForegroundColor Yellow

$frontendDockerfile = @'
FROM nginx:alpine

# Copy frontend files
COPY dashboard/ /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx-frontend.conf /etc/nginx/conf.d/default.conf

# Create health check
RUN echo '#!/bin/sh' > /health-check.sh && \
    echo 'wget --no-verbose --tries=1 --spider http://localhost/ || exit 1' >> /health-check.sh && \
    chmod +x /health-check.sh

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /health-check.sh

CMD ["nginx", "-g", "daemon off;"]
'@

$frontendDockerfile | Out-File -FilePath "Dockerfile.frontend" -Encoding UTF8
Write-Host "✅ Created Dockerfile.frontend" -ForegroundColor Green

# Create Nginx configuration for frontend
$nginxConfig = @'
server {
    listen 80;
    server_name localhost;
    
    # Frontend static files
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://aura-backend:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
        add_header 'Access-Control-Allow-Headers' 'X-Requested-With,Content-Type,Authorization' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
'@

$nginxConfig | Out-File -FilePath "nginx-frontend.conf" -Encoding UTF8
Write-Host "✅ Created nginx-frontend.conf" -ForegroundColor Green

# Build and deploy the updated frontend
Write-Host "🔨 Building updated frontend image..." -ForegroundColor Yellow
docker build -t aura-frontend -f Dockerfile.frontend .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend build failed" -ForegroundColor Red
    exit 1
}

# Stop and replace existing frontend
Write-Host "🚀 Deploying updated frontend..." -ForegroundColor Yellow
docker stop aura-dashboard 2>&1 | Out-Null
docker rm aura-dashboard 2>&1 | Out-Null

docker run -d `
    --name aura-dashboard `
    -p 8080:80 `
    --link aura-backend:aura-backend `
    aura-frontend

Write-Host "✅ Updated frontend deployed" -ForegroundColor Green

# Test the integration
Write-Host "🧪 Testing frontend-backend integration..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $frontendHealth = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5
    Write-Host "✅ Frontend is running: http://localhost:8080" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend health check failed" -ForegroundColor Red
}

Write-Host "`n🎉 Phase 4: Frontend Integration Complete!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "🌐 New Dashboard: http://localhost:8080" -ForegroundColor White
Write-Host "🔐 Features:" -ForegroundColor Cyan
Write-Host "   • API-based authentication" -ForegroundColor White
Write-Host "   • Real-time system metrics" -ForegroundColor White
Write-Host "   • JWT token management" -ForegroundColor White
Write-Host "   • Dynamic data refresh" -ForegroundColor White
Write-Host "   • Responsive design" -ForegroundColor White
Write-Host "`n👤 Login with: admin / AuraDemo2024!" -ForegroundColor Yellow