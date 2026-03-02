# Phase 3.2 - Backend API Setup
Write-Host "🚀 Starting Phase 3.2: Backend API Development" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan

function Write-Status {
    param($Message, $Color = "White")
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
    Write-Host $Message -ForegroundColor $Color
}

# Check if database is running
Write-Status "Checking database status..."
$dbStatus = docker ps -q -f "name=aura-postgres"
if (-not $dbStatus) {
    Write-Status "❌ Database container is not running" "Red"
    Write-Host "💡 Run: .\setup-database.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Status "✅ Database is running" "Green"

# Create backend directory structure
Write-Status "Creating backend API structure..."
$backendDirs = @("backend", "backend/app", "backend/migrations", "backend/tests")
foreach ($dir in $backendDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Status "  Created: $dir" "Gray"
    }
}

# Create Python requirements file
Write-Status "Creating requirements.txt..." "Yellow"
$requirements = @"
Flask==2.3.3
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
Flask-Bcrypt==1.0.1
psycopg2-binary==2.9.7
python-dotenv==1.0.0
gunicorn==21.2.0
pyjwt==2.8.0
requests==2.31.0
"@

$requirements | Out-File -FilePath "backend/requirements.txt" -Encoding UTF8
Write-Status "✅ Created backend/requirements.txt" "Green"

# Create Flask application configuration
Write-Status "Creating Flask configuration..." "Yellow"

# config.py
$configContent = @"
import os
from datetime import timedelta

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aura-super-secret-key-2024'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'aura-jwt-secret-key-2024'
    
    # Database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'aura_dashboard')
    DB_USER = os.environ.get('DB_USER', 'aura_admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'AuraDB2024!')
    
    # JWT Settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Application Settings
    API_VERSION = 'v1'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

class DevelopmentConfig(Config):
    DEBUG = True
    DB_HOST = os.environ.get('DB_HOST', 'localhost')

class ProductionConfig(Config):
    DEBUG = False
    DB_HOST = os.environ.get('DB_HOST', 'aura-postgres')

class TestingConfig(Config):
    TESTING = True
    DB_NAME = 'aura_dashboard_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
"@

$configContent | Out-File -FilePath "backend/config.py" -Encoding UTF8
Write-Status "✅ Created backend/config.py" "Green"

# Create database models
Write-Status "Creating database models..." "Yellow"

$modelsContent = @"
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import jwt
from config import config

bcrypt = Bcrypt()

class Database:
    def __init__(self):
        self.config = config['default']
        self.connection = None
    
    def get_connection(self):
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
        return self.connection
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = None
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

class User:
    def __init__(self, db):
        self.db = db
    
    def find_by_username(self, username):
        query = \"\"\"SELECT id, username, email, password_hash, role, first_name, last_name, 
                   is_active, last_login, created_at, updated_at 
                   FROM users WHERE username = %s\"\"\"
        result = self.db.execute_query(query, (username,))
        return result[0] if result else None
    
    def find_by_id(self, user_id):
        query = \"\"\"SELECT id, username, email, role, first_name, last_name, 
                   is_active, last_login, created_at, updated_at 
                   FROM users WHERE id = %s\"\"\"
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def verify_password(self, password_hash, password):
        return bcrypt.check_password_hash(password_hash, password)
    
    def update_last_login(self, user_id):
        query = \"UPDATE users SET last_login = %s WHERE id = %s\"
        self.db.execute_query(query, (datetime.now(), user_id))
    
    def create_audit_log(self, user_id, action, resource, details=None, ip_address=None, user_agent=None):
        query = \"\"\"INSERT INTO audit_logs (user_id, action, resource, details, ip_address, user_agent) 
                   VALUES (%s, %s, %s, %s, %s, %s)\"\"\"
        self.db.execute_query(query, (user_id, action, resource, details, ip_address, user_agent))

class SystemMetrics:
    def __init__(self, db):
        self.db = db
    
    def add_metric(self, metric_type, metric_value):
        query = \"INSERT INTO system_metrics (metric_type, metric_value) VALUES (%s, %s)\"
        self.db.execute_query(query, (metric_type, metric_value))
    
    def get_recent_metrics(self, metric_type, limit=10):
        query = \"\"\"SELECT metric_type, metric_value, recorded_at 
                   FROM system_metrics 
                   WHERE metric_type = %s 
                   ORDER BY recorded_at DESC 
                   LIMIT %s\"\"\"
        return self.db.execute_query(query, (metric_type, limit))

class Notifications:
    def __init__(self, db):
        self.db = db
    
    def create_notification(self, user_id, title, message, type='info'):
        query = \"\"\"INSERT INTO notifications (user_id, title, message, type) 
                   VALUES (%s, %s, %s, %s)\"\"\"
        self.db.execute_query(query, (user_id, title, message, type))
    
    def get_user_notifications(self, user_id, limit=10):
        query = \"\"\"SELECT id, title, message, type, is_read, created_at 
                   FROM notifications 
                   WHERE user_id = %s 
                   ORDER BY created_at DESC 
                   LIMIT %s\"\"\"
        return self.db.execute_query(query, (user_id, limit))
"@

$modelsContent | Out-File -FilePath "backend/app/models.py" -Encoding UTF8
Write-Status "✅ Created backend/app/models.py" "Green"

# Create authentication module
Write-Status "Creating authentication module..." "Yellow"

$authContent = @"
from flask import jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from app.models import Database, User
from config import config
import datetime

# Initialize extensions
jwt = JWTManager()
db = Database()
user_model = User(db)

def init_auth(app):
    jwt.init_app(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'status': 'error',
            'message': 'Token has expired',
            'error': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'status': 'error',
            'message': 'Invalid token',
            'error': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'status': 'error',
            'message': 'Authorization token is required',
            'error': 'authorization_required'
        }), 401

def login_user(username, password, ip_address=None, user_agent=None):
    try:
        # Find user
        user = user_model.find_by_username(username)
        if not user:
            return {'status': 'error', 'message': 'Invalid credentials'}, 401
        
        # Check if user is active
        if not user['is_active']:
            return {'status': 'error', 'message': 'Account is deactivated'}, 401
        
        # Verify password
        if not user_model.verify_password(user['password_hash'], password):
            return {'status': 'error', 'message': 'Invalid credentials'}, 401
        
        # Update last login
        user_model.update_last_login(user['id'])
        
        # Create audit log
        user_model.create_audit_log(
            user['id'], 
            'login', 
            'auth', 
            'User logged in successfully',
            ip_address,
            user_agent
        )
        
        # Create access token
        access_token = create_access_token(
            identity={
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            },
            expires_delta=datetime.timedelta(hours=24)
        )
        
        return {
            'status': 'success',
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        }, 200
        
    except Exception as e:
        return {'status': 'error', 'message': 'Login failed'}, 500

def get_current_user():
    try:
        current_user = get_jwt_identity()
        user = user_model.find_by_id(current_user['id'])
        if user:
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        return None
    except:
        return None
"@

$authContent | Out-File -FilePath "backend/app/auth.py" -Encoding UTF8
Write-Status "✅ Created backend/app/auth.py" "Green"

# Create API routes
Write-Status "Creating API routes..." "Yellow"

$routesContent = @"
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models import Database, User, SystemMetrics, Notifications
from app.auth import get_current_user, login_user
import psutil
import datetime

# Create blueprints
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Initialize models
db = Database()
user_model = User(db)
metrics_model = SystemMetrics(db)
notifications_model = Notifications(db)

# Authentication routes
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'status': 'error', 'message': 'Username and password required'}), 400
    
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    
    result, status_code = login_user(
        data['username'], 
        data['password'],
        ip_address,
        user_agent
    )
    return jsonify(result), status_code

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    current_user = get_current_user()
    if current_user:
        return jsonify({
            'status': 'success',
            'user': current_user
        }), 200
    return jsonify({'status': 'error', 'message': 'User not found'}), 404

# System routes
@api_bp.route('/system/health', methods=['GET'])
def system_health():
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Store metrics in database
        metrics_model.add_metric('cpu_usage', cpu_percent)
        metrics_model.add_metric('memory_usage', memory.percent)
        metrics_model.add_metric('disk_usage', disk.percent)
        
        return jsonify({
            'status': 'success',
            'data': {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'memory_total': memory.total,
                'disk_usage': disk.percent,
                'disk_free': disk.free,
                'disk_total': disk.total,
                'timestamp': datetime.datetime.now().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get system health'
        }), 500

@api_bp.route('/system/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    try:
        cpu_metrics = metrics_model.get_recent_metrics('cpu_usage', 24)
        memory_metrics = metrics_model.get_recent_metrics('memory_usage', 24)
        
        return jsonify({
            'status': 'success',
            'data': {
                'cpu_metrics': cpu_metrics,
                'memory_metrics': memory_metrics
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get metrics'
        }), 500

# User routes
@api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_current_user()
    if current_user['role'] != 'admin':
        return jsonify({'status': 'error', 'message': 'Insufficient permissions'}), 403
    
    try:
        users = db.execute_query(\"\"\"SELECT id, username, email, role, first_name, last_name, 
                                   is_active, last_login, created_at 
                                   FROM users ORDER BY created_at DESC\"\"\")
        return jsonify({
            'status': 'success',
            'data': users
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get users'
        }), 500

# Dashboard routes
@api_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    try:
        # Get various statistics
        user_count = db.execute_query(\"SELECT COUNT(*) as count FROM users\")[0]['count']
        metrics_count = db.execute_query(\"SELECT COUNT(*) as count FROM system_metrics\")[0]['count']
        audit_count = db.execute_query(\"SELECT COUNT(*) as count FROM audit_logs\")[0]['count']
        
        # Recent activity
        recent_activity = db.execute_query(\"\"\"SELECT action, resource, created_at 
                                            FROM audit_logs 
                                            ORDER BY created_at DESC 
                                            LIMIT 10\"\"\")
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_count': user_count,
                'metrics_count': metrics_count,
                'audit_count': audit_count,
                'recent_activity': recent_activity
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get dashboard stats'
        }), 500
"@

$routesContent | Out-File -FilePath "backend/app/routes.py" -Encoding UTF8
Write-Status "✅ Created backend/app/routes.py" "Green"

# Create main application file
Write-Status "Creating main application file..." "Yellow"

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
Write-Status "✅ Created backend/app/__init__.py" "Green"

# Create run.py
$runContent = @"
from app import create_app
import os

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
"@

$runContent | Out-File -FilePath "backend/run.py" -Encoding UTF8
Write-Status "✅ Created backend/run.py" "Green"

# Create Dockerfile for backend
Write-Status "Creating Dockerfile for backend..." "Yellow"

$dockerfileContent = @"
FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    linux-headers

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser -D -s /bin/sh aura
USER aura

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD [\"gunicorn\", \"-b\", \"0.0.0.0:5000\", \"run:app\", \"--workers\", \"4\", \"--threads\", \"2\"]
"@

$dockerfileContent | Out-File -FilePath "Dockerfile.api" -Encoding UTF8
Write-Status "✅ Created Dockerfile.api" "Green"

Write-Host "`n🎉 Phase 3.2 Backend API Setup Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "📁 Backend structure created successfully" -ForegroundColor White
Write-Host "🐳 Dockerfile.api ready for containerization" -ForegroundColor White
Write-Host "🔐 JWT authentication system implemented" -ForegroundColor White
Write-Host "📊 API endpoints for dashboard and system metrics" -ForegroundColor White
Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Install Python dependencies" -ForegroundColor White
Write-Host "   2. Build and run the backend container" -ForegroundColor White
Write-Host "   3. Test the API endpoints" -ForegroundColor White
Write-Host "   4. Update frontend to use new API" -ForegroundColor White