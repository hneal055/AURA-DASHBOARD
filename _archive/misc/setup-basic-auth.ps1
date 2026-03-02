Write-Host "🔐 SETTING UP HTTP BASIC AUTHENTICATION" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check for required tools
$openssl = Get-Command openssl -ErrorAction SilentlyContinue
$htpasswd = Get-Command htpasswd -ErrorAction SilentlyContinue

if (-not $openssl -and -not $htpasswd) {
    Write-Host "❌ Neither OpenSSL nor htpasswd (Apache) is available." -ForegroundColor Red
    Write-Host "💡 Please install one of them to generate password hashes." -ForegroundColor Yellow
    Write-Host "   - OpenSSL: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor White
    Write-Host "   - Apache (for htpasswd): https://httpd.apache.org/docs/current/programs/htpasswd.html" -ForegroundColor White
    exit 1
}

Write-Host "✅ Required tool found: $($openssl ? 'OpenSSL' : 'htpasswd')" -ForegroundColor Green

# Get username and password
$username = Read-Host "Enter username"
$password = Read-Host "Enter password" -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

# Create .htpasswd file
$htpasswdContent = if ($openssl) {
    # Use OpenSSL to generate APR1-MD5
    $hash = openssl passwd -apr1 $plainPassword
    "${username}:${hash}"
} else {
    # Use htpasswd command
    $tempFile = New-TemporaryFile
    & htpasswd -b -c $tempFile $username $plainPassword
    Get-Content $tempFile
    Remove-Item $tempFile
}

# Write .htpasswd file
$htpasswdContent | Set-Content ".htpasswd" -Force

Write-Host "✅ .htpasswd file created" -ForegroundColor Green

Write-Host "`n2. Creating Nginx configuration with basic auth..." -ForegroundColor White

# Create Nginx configuration with basic auth
@"
server {
    listen 80;
    server_name localhost;

    # Security Headers (from previous setup)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; frame-ancestors 'self';" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    server_tokens off;

    # Basic Authentication
    auth_basic "Restricted Area";
    auth_basic_user_file /etc/nginx/.htpasswd;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }

    # Health check endpoint (without authentication)
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
"@ | Set-Content "nginx-basic-auth.conf"

Write-Host "✅ Nginx configuration with basic auth created" -ForegroundColor Green

Write-Host "`n3. Creating Dockerfile for basic auth..." -ForegroundColor White

# Create Dockerfile that copies the .htpasswd file and uses the new nginx config
@"
FROM nginx:alpine

# Copy .htpasswd file
COPY .htpasswd /etc/nginx/.htpasswd

# Copy nginx configuration
COPY nginx-basic-auth.conf /etc/nginx/conf.d/default.conf

# Copy web content
COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"@ | Set-Content "Dockerfile.basic-auth"

Write-Host "✅ Dockerfile for basic auth created" -ForegroundColor Green

Write-Host "`n4. Building and starting container with basic auth..." -ForegroundColor White

# Stop and remove existing container
docker stop aura-dashboard 2>$null
docker rm aura-dashboard 2>$null

# Build the image
docker build -t aura-dashboard-basic-auth -f Dockerfile.basic-auth .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

# Run the container
docker run -d -p 8080:80 --name aura-dashboard aura-dashboard-basic-auth

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Container started successfully" -ForegroundColor Green
    Write-Host "🔒 Dashboard is now protected by HTTP Basic Authentication" -ForegroundColor Green
    Write-Host "📍 Access: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "   Username: $username" -ForegroundColor White
    Write-Host "   Password: (the one you entered)" -ForegroundColor White
} else {
    Write-Host "❌ Failed to start container" -ForegroundColor Red
}