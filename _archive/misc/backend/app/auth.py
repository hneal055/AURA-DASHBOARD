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
