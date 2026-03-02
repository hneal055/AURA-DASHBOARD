# This script combines SSL and basic auth

Write-Host "🔐 SETTING UP SSL WITH BASIC AUTHENTICATION" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check for required tools (same as above)

# ... (same as above for creating .htpasswd)

# Then create an Nginx configuration that uses both SSL and basic auth

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
"@ | Set-Content "nginx-ssl-basic-auth.conf"

# Then build a Dockerfile that includes the SSL certificates, .htpasswd, and the new nginx config

# ... (similar to above)
