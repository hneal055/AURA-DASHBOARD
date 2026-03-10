"""
Flask API Key Authentication Middleware
Add this to your Flask app for API key protection
"""

from functools import wraps
from flask import request, jsonify
import hashlib
import json
import os

def load_api_keys(filename='api_keys.json'):
    """Load API keys from file"""
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return []

def hash_api_key(api_key):
    """Hash an API key"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(provided_key):
    """Verify if an API key is valid"""
    keys = load_api_keys()
    provided_hash = hash_api_key(provided_key)
    
    for key in keys:
        if key['key_hash'] == provided_hash and key.get('active', True):
            return True
    
    return False

def require_api_key(f):
    """
    Decorator to require API key authentication
    
    Usage:
        @app.route('/api/data')
        @require_api_key
        def get_data():
            return jsonify({'data': 'secret'})
    
    API key can be provided in:
    1. Header: X-API-Key: your_key_here
    2. Query parameter: ?api_key=your_key_here
    3. JSON body: {"api_key": "your_key_here"}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Try to get API key from multiple sources
        api_key = None
        
        # 1. Check header (preferred)
        api_key = request.headers.get('X-API-Key')

        # 2. Check JSON body
        if not api_key and request.is_json:
            api_key = request.json.get('api_key')
        
        # Verify API key
        if not api_key:
            return jsonify({
                'error': 'API key required',
                'message': 'Please provide API key in X-API-Key header, api_key query parameter, or JSON body'
            }), 401
        
        if not verify_api_key(api_key):
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or inactive'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_api_key(f):
    """
    Decorator for optional API key authentication
    Provides enhanced access if API key is valid
    
    Usage:
        @app.route('/api/data')
        @optional_api_key
        def get_data():
            if request.is_authenticated:
                return jsonify({'data': 'premium content'})
            else:
                return jsonify({'data': 'free content'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Try to get API key
        api_key = (
            request.headers.get('X-API-Key') or
            request.args.get('api_key') or
            (request.json.get('api_key') if request.is_json else None)
        )
        
        # Set authentication status
        request.is_authenticated = bool(api_key and verify_api_key(api_key))
        
        return f(*args, **kwargs)
    
    return decorated_function

# Rate limiting helpers
def get_rate_limit_key():
    """Get rate limit key (IP address or API key)"""
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"api:{hash_api_key(api_key)[:16]}"
    return f"ip:{request.remote_addr}"

# Example usage
if __name__ == '__main__':
    print("""
    Flask API Key Authentication Middleware
    
    To use in your Flask app:
    
    1. Import the decorators:
       from flask_auth import require_api_key, optional_api_key
    
    2. Protect routes:
       @app.route('/api/secure')
       @require_api_key
       def secure_endpoint():
           return jsonify({'message': 'Authenticated!'})
    
    3. Optional authentication:
       @app.route('/api/data')
       @optional_api_key
       def data_endpoint():
           if request.is_authenticated:
               return jsonify({'premium': True})
           return jsonify({'free': True})
    
    4. Test with curl:
       curl -H "X-API-Key: your_key_here" http://localhost:8080/api/secure
       curl "http://localhost:8080/api/secure?api_key=your_key_here"
    """)