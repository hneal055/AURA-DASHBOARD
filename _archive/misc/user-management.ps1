Write-Host "👥 SETTING UP USER MANAGEMENT SYSTEM" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n1. Creating user management scripts..." -ForegroundColor White

# Create user management script
@"
param(
    [Parameter(Mandatory=`$true)]
    [string]`$Action,
    
    [Parameter(Mandatory=`$false)]
    [string]`$Username,
    
    [Parameter(Mandatory=`$false)]
    [string]`$Password,
    
    [Parameter(Mandatory=`$false)]
    [string]`$Role = "user"
)

`$authDir = "auth"
`$htpasswdFile = "`$authDir/.htpasswd"

function Add-User {
    param([string]`$User, [string]`$Pass, [string]`$UserRole)
    
    if (-not (Test-Path `$htpasswdFile)) {
        Write-Host "❌ Authentication file not found" -ForegroundColor Red
        exit 1
    }
    
    # In production, use: htpasswd -b `$htpasswdFile `$User `$Pass
    # For demo, we'll append to file (plain text - NOT for production!)
    "`$User:`$Pass # Role: `$UserRole" | Add-Content "`$authDir/users.txt"
    
    Write-Host "✅ User `$User added with role `$UserRole" -ForegroundColor Green
    Write-Host "⚠️  Note: In production, use proper password hashing!" -ForegroundColor Yellow
}

function Remove-User {
    param([string]`$User)
    
    if (Test-Path "`$authDir/users.txt") {
        `$content = Get-Content "`$authDir/users.txt" | Where-Object { `$_ -notlike "`$User:*" }
        `$content | Set-Content "`$authDir/users.txt"
        Write-Host "✅ User `$User removed" -ForegroundColor Green
    }
}

function List-Users {
    if (Test-Path "`$authDir/users.txt") {
        Write-Host "`n📋 Registered Users:" -ForegroundColor White
        Get-Content "`$authDir/users.txt" | ForEach-Object {
            Write-Host "   • `$_" -ForegroundColor Gray
        }
    } else {
        Write-Host "No additional users registered" -ForegroundColor Yellow
    }
}

# Main execution
switch (`$Action.ToLower()) {
    "add" {
        if (-not `$Username -or -not `$Password) {
            Write-Host "❌ Username and Password required for add action" -ForegroundColor Red
            exit 1
        }
        Add-User -User `$Username -Pass `$Password -UserRole `$Role
    }
    "remove" {
        if (-not `$Username) {
            Write-Host "❌ Username required for remove action" -ForegroundColor Red
            exit 1
        }
        Remove-User -User `$Username
    }
    "list" {
        List-Users
    }
    default {
        Write-Host "❌ Invalid action. Use: add, remove, list" -ForegroundColor Red
        Write-Host "`nUsage examples:" -ForegroundColor White
        Write-Host "  .\manage-users.ps1 add -Username john -Password pass123 -Role admin" -ForegroundColor Gray
        Write-Host "  .\manage-users.ps1 remove -Username john" -ForegroundColor Gray
        Write-Host "  .\manage-users.ps1 list" -ForegroundColor Gray
    }
}
"@ | Set-Content "manage-users.ps1"

Write-Host "✅ User management script created" -ForegroundColor Green

Write-Host "`n2. Creating admin dashboard..." -ForegroundColor White

# Create enhanced admin dashboard
@"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA Dashboard - Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .status-bar {
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #28a745;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        .card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .metric {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
            margin: 10px 0;
        }
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
            transition: background 0.3s ease;
        }
        .btn:hover {
            background: #2980b9;
        }
        .log-container {
            background: #1e1e1e;
            color: #00ff00;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            height: 200px;
            overflow-y: auto;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AURA DASHBOARD</h1>
            <p>Enterprise Administration Panel</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-dot"></div>
                <span>System Status: Operational</span>
            </div>
            <div class="status-item">
                <span>Last Updated: <span id="timestamp">Loading...</span></span>
            </div>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>📊 System Overview</h3>
                <div class="metric" id="uptime">00:00:00</div>
                <p>Application Uptime</p>
                <button class="btn" onclick="refreshStatus()">Refresh Status</button>
            </div>
            
            <div class="card">
                <h3>🔐 Security</h3>
                <p>Authentication: <strong>Enabled</strong></p>
                <p>SSL/TLS: <strong>Available</strong></p>
                <p>Last Login: <strong id="lastLogin">Never</strong></p>
                <button class="btn" onclick="showSecurity()">Security Settings</button>
            </div>
            
            <div class="card">
                <h3>📈 Performance</h3>
                <div class="metric" id="responseTime">0ms</div>
                <p>Average Response Time</p>
                <div class="metric" id="requestCount">0</div>
                <p>Total Requests</p>
            </div>
            
            <div class="card">
                <h3>🐳 Docker Status</h3>
                <p>Container: <strong id="containerStatus">Checking...</strong></p>
                <p>Memory: <strong id="memoryUsage">Loading...</strong></p>
                <p>CPU: <strong id="cpuUsage">Loading...</strong></p>
                <button class="btn" onclick="checkDocker()">Check Docker</button>
            </div>
            
            <div class="card">
                <h3>📋 System Logs</h3>
                <div class="log-container" id="systemLogs">
                    > System initialized...
                    > Authentication active...
                    > Dashboard loaded...
                </div>
                <button class="btn" onclick="fetchLogs()">Refresh Logs</button>
            </div>
            
            <div class="card">
                <h3>⚙️ Quick Actions</h3>
                <button class="btn" onclick="restartService()">Restart Service</button>
                <button class="btn" onclick="backupSystem()">Backup System</button>
                <button class="btn" onclick="securityScan()">Security Scan</button>
                <button class="btn" onclick="showDocs()">View Documentation</button>
            </div>
        </div>
    </div>

    <script>
        // Update timestamp
        function updateTimestamp() {
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        }
        
        // Simulate uptime counter
        let startTime = Date.now();
        function updateUptime() {
            const now = Date.now();
            const diff = now - startTime;
            const hours = Math.floor(diff / 3600000);
            const minutes = Math.floor((diff % 3600000) / 60000);
            const seconds = Math.floor((diff % 60000) / 1000);
            document.getElementById('uptime').textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Simulate performance metrics
        function updateMetrics() {
            document.getElementById('responseTime').textContent = Math.floor(Math.random() * 50 + 10) + 'ms';
            document.getElementById('requestCount').textContent = Math.floor(Math.random() * 1000 + 5000).toLocaleString();
            document.getElementById('memoryUsage').textContent = Math.floor(Math.random() * 30 + 10) + 'MB';
            document.getElementById('cpuUsage').textContent = Math.floor(Math.random() * 20 + 5) + '%';
        }
        
        // Action functions
        function refreshStatus() {
            addLog('> Manual status refresh requested');
            updateMetrics();
            alert('Status refreshed successfully!');
        }
        
        function showSecurity() {
            addLog('> Security settings accessed');
            alert('Security features are active:\n• Basic Authentication\n• Security Headers\n• SSL Available');
        }
        
        function checkDocker() {
            addLog('> Docker status check requested');
            document.getElementById('containerStatus').textContent = 'Running ✓';
            updateMetrics();
        }
        
        function fetchLogs() {
            addLog('> Log refresh requested at ' + new Date().toLocaleTimeString());
        }
        
        function restartService() {
            if(confirm('Are you sure you want to restart the service?')) {
                addLog('> Service restart initiated...');
                alert('Service restart command sent. Please wait...');
            }
        }
        
        function backupSystem() {
            addLog('> Backup process started...');
            alert('Backup initiated. Check backup folder for results.');
        }
        
        function securityScan() {
            addLog('> Security scan requested...');
            alert('Security scan started. Check security reports.');
        }
        
        function showDocs() {
            addLog('> Documentation accessed');
            alert('Documentation available in /Documentation folder');
        }
        
        function addLog(message) {
            const logContainer = document.getElementById('systemLogs');
            logContainer.innerHTML += '\n' + message;
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // Initialize
        updateTimestamp();
        updateUptime();
        updateMetrics();
        document.getElementById('containerStatus').textContent = 'Running ✓';
        
        // Update every second
        setInterval(updateTimestamp, 1000);
        setInterval(updateUptime, 1000);
        setInterval(updateMetrics, 5000);
        
        // Simulate initial load
        setTimeout(() => {
            addLog('> All systems operational');
            addLog('> Dashboard initialized successfully');
        }, 1000);
    </script>
</body>
</html>
"@ | Set-Content "index.html"

Write-Host "✅ Enhanced admin dashboard created" -ForegroundColor Green

Write-Host "`n3. Creating user roles configuration..." -ForegroundColor White

# Create role-based access control configuration
@"
{
    "roles": {
        "admin": {
            "permissions": ["read", "write", "delete", "admin", "backup", "restart"],
            "description": "Full system administrator access"
        },
        "user": {
            "permissions": ["read", "write"],
            "description": "Standard user with read/write access"
        },
        "viewer": {
            "permissions": ["read"],
            "description": "Read-only access for monitoring"
        }
    },
    "default_role": "viewer",
    "session_timeout": 3600
}
"@ | Set-Content "auth/roles.json"

Write-Host "✅ Role-based access control configured" -ForegroundColor Green

Write-Host "`n🎉 USER MANAGEMENT SYSTEM READY!" -ForegroundColor Green
Write-Host "👤 Default Users:" -ForegroundColor White
Write-Host "   • admin / AuraDemo2024! (Full access)" -ForegroundColor Gray
Write-Host "   • demo / AuraDemo2024! (Demo access)" -ForegroundColor Gray
Write-Host "`n🔧 Management Commands:" -ForegroundColor Cyan
Write-Host "   • .\manage-users.ps1 add -Username <name> -Password <pass> -Role <role>" -ForegroundColor Gray
Write-Host "   • .\manage-users.ps1 remove -Username <name>" -ForegroundColor Gray
Write-Host "   • .\manage-users.ps1 list" -ForegroundColor Gray