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
        query = """SELECT id, username, email, password_hash, role, first_name, last_name, 
                   is_active, last_login, created_at, updated_at 
                   FROM users WHERE username = %s"""
        result = self.db.execute_query(query, (username,))
        return result[0] if result else None
    
    def find_by_id(self, user_id):
        query = """SELECT id, username, email, role, first_name, last_name, 
                   is_active, last_login, created_at, updated_at 
                   FROM users WHERE id = %s"""
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def verify_password(self, password_hash, password):
        return bcrypt.check_password_hash(password_hash, password)
    
    def update_last_login(self, user_id):
        query = "UPDATE users SET last_login = %s WHERE id = %s"
        self.db.execute_query(query, (datetime.now(), user_id))
    
    def create_audit_log(self, user_id, action, resource, details=None, ip_address=None, user_agent=None):
        query = """INSERT INTO audit_logs (user_id, action, resource, details, ip_address, user_agent) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        self.db.execute_query(query, (user_id, action, resource, details, ip_address, user_agent))

class SystemMetrics:
    def __init__(self, db):
        self.db = db
    
    def add_metric(self, metric_type, metric_value):
        query = "INSERT INTO system_metrics (metric_type, metric_value) VALUES (%s, %s)"
        self.db.execute_query(query, (metric_type, metric_value))
    
    def get_recent_metrics(self, metric_type, limit=10):
        query = """SELECT metric_type, metric_value, recorded_at 
                   FROM system_metrics 
                   WHERE metric_type = %s 
                   ORDER BY recorded_at DESC 
                   LIMIT %s"""
        return self.db.execute_query(query, (metric_type, limit))

class Notifications:
    def __init__(self, db):
        self.db = db
    
    def create_notification(self, user_id, title, message, type='info'):
        query = """INSERT INTO notifications (user_id, title, message, type) 
                   VALUES (%s, %s, %s, %s)"""
        self.db.execute_query(query, (user_id, title, message, type))
    
    def get_user_notifications(self, user_id, limit=10):
        query = """SELECT id, title, message, type, is_read, created_at 
                   FROM notifications 
                   WHERE user_id = %s 
                   ORDER BY created_at DESC 
                   LIMIT %s"""
        return self.db.execute_query(query, (user_id, limit))