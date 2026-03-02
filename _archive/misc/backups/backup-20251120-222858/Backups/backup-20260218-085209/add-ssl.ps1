Write-Host "🔐 SETTING UP SSL/TLS ENCRYPTION" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Create SSL directory
$sslDir = "ssl"
if (-not (Test-Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir | Out-Null
}

Write-Host "`n1. Generating SSL Certificate..." -ForegroundColor White

# Check if OpenSSL is available
$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl) {
    Write-Host "❌ OpenSSL not found. Installing required dependencies..." -ForegroundColor Red
    
    # For Windows, we can use chocolatey or provide alternative
    Write-Host "💡 Please install OpenSSL:" -ForegroundColor Yellow
    Write-Host "   Option 1: Install Chocolatey, then: choco install openssl" -ForegroundColor White
    Write-Host "   Option 2: Download from: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor White
    Write-Host "   Option 3: Use mkcert (simpler): choco install mkcert" -ForegroundColor White
    exit 1
}

# Generate private key
openssl genrsa -out "$sslDir/private.key" 2048

# Generate certificate signing request
openssl req -new -key "$sslDir/private.key" -out "$sslDir/certificate.csr" -subj "/C=US/ST=State/L=City/O=Organization/OU=IT/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -days 365 -in "$sslDir/certificate.csr" -signkey "$sslDir/private.key" -out "$sslDir/certificate.crt"

if (Test-Path "$sslDir/certificate.crt") {
    Write-Host "✅ SSL certificates generated successfully" -ForegroundColor Green
} else {
    Write-Host "❌ SSL certificate generation failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Creating SSL-enabled Dockerfile..." -ForegroundColor White

# Create SSL-enabled Dockerfile
@"
FROM nginx:alpine

# Install SSL certificates
COPY ssl/certificate.crt /etc/nginx/ssl/certificate.crt
COPY ssl/private.key /etc/nginx/ssl/private.key

# Copy custom nginx config with SSL
COPY nginx-ssl.conf /etc/nginx/conf.d/default.conf

# Copy web content
COPY . /usr/share/nginx/html

# Expose both HTTP and HTTPS ports
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
"@ | Set-Content "Dockerfile.ssl"

Write-Host "✅ SSL Dockerfile created" -ForegroundColor Green

Write-Host "`n3. Creating SSL Nginx configuration..." -ForegroundColor White

# Create SSL-enabled nginx config
@"
server {
    listen 80;
    server_name localhost;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin" always;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }
}
"@ | Set-Content "nginx-ssl.conf"

Write-Host "✅ SSL Nginx configuration created" -ForegroundColor Green

Write-Host "`n4. Building SSL-enabled container..." -ForegroundColor White

# Stop existing container
docker stop aura-dashboard 2>$null
docker rm aura-dashboard 2>$null

# Build SSL version
docker build -t aura-dashboard-ssl -f Dockerfile.ssl .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSL-enabled image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ SSL build failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n5. Starting HTTPS container..." -ForegroundColor White

# Run with both HTTP and HTTPS ports
docker run -d -p 8080:80 -p 8443:443 --name aura-dashboard-ssl aura-dashboard-ssl

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 SSL/TLS SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "📍 HTTP Access:  http://localhost:8080" -ForegroundColor Cyan
    Write-Host "📍 HTTPS Access: https://localhost:8443" -ForegroundColor Cyan
    Write-Host "🔒 Note: Browser will warn about self-signed certificate" -ForegroundColor Yellow
    Write-Host "   This is normal for development. Click 'Advanced' → 'Proceed'" -ForegroundColor White
} else {
    Write-Host "❌ Failed to start SSL container" -ForegroundColor Red
}