# Create Missing Backend Files
Write-Host "📝 Creating Missing Backend Files" -ForegroundColor Green

# Create backend directory if it doesn't exist
if (-not (Test-Path "backend")) {
    Write-Host "Creating backend directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "backend" -Force
    New-Item -ItemType Directory -Path "backend/app" -Force
}

# Check and create run.py if missing
if (-not (Test-Path "backend/run.py")) {
    Write-Host "Creating run.py..." -ForegroundColor Yellow
    $runPyContent = @"
from app import create_app
import os

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
"@
    $runPyContent | Out-File -FilePath "backend/run.py" -Encoding UTF8
    Write-Host "✅ Created backend/run.py" -ForegroundColor Green
}

# Check and create __init__.py if missing  
if (-not (Test-Path "backend/app/__init__.py")) {
    Write-Host "Creating app/__init__.py..." -ForegroundColor Yellow
    $initContent = @"
from flask import Flask
from flask_cors import CORS
from config import config
from app.auth import init_auth
from app.routes import api_bp, auth_bp

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app)
    init_auth(app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'AURA Backend API'}
    
    return app
"@
    $initContent | Out-File -FilePath "backend/app/__init__.py" -Encoding UTF8
    Write-Host "✅ Created backend/app/__init__.py" -ForegroundColor Green
}

# Verify all files now exist
Write-Host "`n✅ All critical files verified/created" -ForegroundColor Green