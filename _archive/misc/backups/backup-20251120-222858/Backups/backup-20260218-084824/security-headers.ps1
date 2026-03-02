Write-Host "🛡️  CONFIGURING SECURITY HEADERS" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n1. Creating security-enhanced Nginx configuration..." -ForegroundColor White

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
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Remove server tokens
    server_tokens off;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
        
        # Additional security for sensitive paths
        location ~* \.(env|config|key)$ {
            deny all;
            return 404;
        }
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
"@ | Set-Content "nginx-secure.conf"

Write-Host "✅ Security headers configuration created" -ForegroundColor Green

Write-Host "`n2. Creating security-enhanced Dockerfile..." -ForegroundColor White

@"
FROM nginx:alpine

# Copy secure nginx config
COPY nginx-secure.conf /etc/nginx/conf.d/default.conf

# Copy web content
COPY . /usr/share/nginx/html

# Remove default nginx configurations
RUN rm -f /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"@ | Set-Content "Dockerfile.secure"

Write-Host "✅ Secure Dockerfile created" -ForegroundColor Green

Write-Host "`n3. Building secure container..." -ForegroundColor White

docker build -t aura-dashboard-secure -f Dockerfile.secure .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Secure image built successfully" -ForegroundColor Green
    
    # Update main container
    docker stop aura-dashboard 2>$null
    docker rm aura-dashboard 2>$null
    docker run -d -p 8080:80 --name aura-dashboard aura-dashboard-secure
    
    Write-Host "🎉 SECURITY HARDENING COMPLETE!" -ForegroundColor Green
    Write-Host "📍 Access: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "🛡️  Security headers now active:" -ForegroundColor White
    Write-Host "   • HSTS, X-Frame-Options, CSP" -ForegroundColor Gray
    Write-Host "   • XSS Protection, No Sniff" -ForegroundColor Gray
    Write-Host "   • Referrer Policy, Permissions Policy" -ForegroundColor Gray
} else {
    Write-Host "❌ Secure build failed" -ForegroundColor Red
}