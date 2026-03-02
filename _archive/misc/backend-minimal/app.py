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
