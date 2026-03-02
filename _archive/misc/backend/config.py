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
