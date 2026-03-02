# Build and Run Minimal Backend - Complete Solution
Write-Host "🚀 Building and Running Minimal Backend" -ForegroundColor Green

# Clean up
docker stop aura-backend 2>&1 | Out-Null
docker rm aura-backend 2>&1 | Out-Null

# Create directory structure
if (-not (Test-Path "backend-minimal")) {
    New-Item -ItemType Directory -Path "backend-minimal" -Force
}

# Create requirements
"Flask==2.3.3
psycopg2-binary==2.9.7
python-dotenv==1.0.0" | Out-File -FilePath "backend-minimal/requirements.txt" -Encoding UTF8

# Create app.py
@'
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import datetime

app = Flask(__name__)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'aura-postgres'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'aura_dashboard'),
            user=os.getenv('DB_USER', 'aura_admin'),
            password=os.getenv('DB_PASSWORD', 'AuraDB2024!'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'AURA Minimal Backend'})

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'status': 'error', 'message': 'Username and password required'}), 400
    
    if data['username'] == 'admin' and data['password'] == 'AuraDemo2024!':
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'access_token': 'demo-token-' + datetime.datetime.now().isoformat(),
            'user': {
                'id': 1,
                'username': 'admin',
                'email': 'admin@auradashboard.com',
                'role': 'admin'
            }
        })
    else:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/api/v1/system/health')
def system_health():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()
            cursor.close()
            conn.close()
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {e}"
    else:
        db_status = "no connection"
    
    return jsonify({
        'status': 'success',
        'data': {
            'cpu_usage': 25.5,
            'memory_usage': 45.2,
            'database_status': db_status,
            'timestamp': datetime.datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
'@ | Out-File -FilePath "backend-minimal/app.py" -Encoding UTF8

# Create Dockerfile
@'
FROM python:3.11-alpine
WORKDIR /app
RUN apk update && apk add --no-cache postgresql-dev gcc python3-dev musl-dev linux-headers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
'@ | Out-File -FilePath "backend-minimal/Dockerfile" -Encoding UTF8

# Build and run
Write-Host "🔨 Building image..." -ForegroundColor Yellow
docker build -t aura-backend-minimal -f backend-minimal/Dockerfile backend-minimal/

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Image built" -ForegroundColor Green
    
    Write-Host "🚀 Starting container..." -ForegroundColor Yellow
    docker run -d --name aura-backend -p 5000:5000 -e DB_HOST=aura-postgres -e DB_PORT=5432 -e DB_NAME=aura_dashboard -e DB_USER=aura_admin -e DB_PASSWORD=AuraDB2024! --link aura-postgres:postgres aura-backend-minimal
    
    Write-Host "✅ Container started" -ForegroundColor Green
    Write-Host "⏳ Waiting for startup..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Test
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 5
        Write-Host "✅ Backend is running: $($health.status)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Backend not responding" -ForegroundColor Red
        docker logs aura-backend
    }
} else {
    Write-Host "❌ Build failed" -ForegroundColor Red
}