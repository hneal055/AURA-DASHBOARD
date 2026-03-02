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
