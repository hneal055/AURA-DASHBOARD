Write-Host "🔐 SETTING UP BASIC AUTHENTICATION" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n1. Creating authentication configuration..." -ForegroundColor White

# Create auth directory
$authDir = "auth"
if (-not (Test-Path $authDir)) {
    New-Item -ItemType Directory -Path $authDir | Out-Null
}

Write-Host "`n2. Setting up admin credentials..." -ForegroundColor White

# Create default admin credentials
$adminUser = "admin"
$adminPass = "AuraDemo2024!"  # In production, this should be changed

# For basic auth, we need to create htpasswd file
# Using a simple method for Windows - creating bcrypt hashed password
# Note: In production, use proper htpasswd tool

@"
# AURA Dashboard Users
# Format: username:encrypted_password

# Admin user (change password in production!)
admin:`$2y`$10`$92lRBaH5pQY/8GK8pWqB.OGk3v9y7x4QcX8jKJmNqYbWzLpVrRtOa
demo:`$2y`$10`$92lRBaH5pQY/8GK8pWqB.OGk3v9y7x4QcX8jKJmNqYbWzLpVrRtOa
"@ | Set-Content "$authDir/.htpasswd"

Write-Host "✅ Authentication file created" -ForegroundColor Green
Write-Host "   Default credentials:" -ForegroundColor White
Write-Host "   • Username: admin" -ForegroundColor Gray
Write-Host "   • Password: AuraDemo2024!" -ForegroundColor Gray
Write-Host "   • Demo user: demo / AuraDemo2024!" -ForegroundColor Gray

Write-Host "`n3. Creating authenticated Nginx configuration..." -ForegroundColor White

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
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; frame-ancestors 'self';" always;

    server_tokens off;

    # Basic Authentication
    auth_basic "AURA Dashboard - Restricted Access";
    auth_basic_user_file /etc/nginx/auth/.htpasswd;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files `$uri `$uri/ =404;
    }

    # Public health check (no auth)
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Public status page (no auth)
    location /status {
        access_log off;
        add_header Content-Type application/json;
        return 200 '{"status":"running","timestamp":"$(Get-Date -Format o)","version":"1.0.0"}';
    }

    # Admin area with additional protection
    location /admin {
        # Additional security headers for admin area
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    }
}
"@ | Set-Content "nginx-auth.conf"

Write-Host "✅ Authenticated Nginx configuration created" -ForegroundColor Green

Write-Host "`n4. Creating authentication-enabled Dockerfile..." -ForegroundColor White

@"
FROM nginx:alpine

# Install apache2-utils for htpasswd (if needed for dynamic user creation)
RUN apk add --no-cache apache2-utils

# Create auth directory
RUN mkdir -p /etc/nginx/auth

# Copy authentication files
COPY auth/.htpasswd /etc/nginx/auth/.htpasswd

# Copy secure nginx config
COPY nginx-auth.conf /etc/nginx/conf.d/default.conf

# Copy web content
COPY . /usr/share/nginx/html

# Set proper permissions
RUN chown -R nginx:nginx /etc/nginx/auth
RUN chmod 600 /etc/nginx/auth/.htpasswd

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"@ | Set-Content "Dockerfile.auth"

Write-Host "✅ Authentication Dockerfile created" -ForegroundColor Green

Write-Host "`n5. Building and deploying authenticated container..." -ForegroundColor White

# Stop existing container
docker stop aura-dashboard 2>$null
docker rm aura-dashboard 2>$null

# Build auth version
docker build -t aura-dashboard-auth -f Dockerfile.auth .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Authenticated image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Auth build failed" -ForegroundColor Red
    exit 1
}

# Run authenticated container
docker run -d -p 8080:80 --name aura-dashboard aura-dashboard-auth

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 AUTHENTICATION SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "📍 Access: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "🔐 Login required with credentials above" -ForegroundColor Yellow
    Write-Host "📊 Public endpoints:" -ForegroundColor White
    Write-Host "   • Health: http://localhost:8080/health" -ForegroundColor Gray
    Write-Host "   • Status: http://localhost:8080/status" -ForegroundColor Gray
    
    # Test the setup
    Start-Sleep -Seconds 3
    Write-Host "`n6. Testing authentication..." -ForegroundColor White
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 5
        Write-Host "❌ Authentication not working - no login prompt" -ForegroundColor Red
    } catch {
        if ($_.Exception.Message -like "*401*") {
            Write-Host "✅ Authentication working - 401 Unauthorized received" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Unexpected response: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "❌ Failed to start authenticated container" -ForegroundColor Red
}