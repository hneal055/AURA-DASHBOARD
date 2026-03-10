"""
Database Models for Budget Analysis App
SQLAlchemy ORM models for persistent storage
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class BudgetAnalysis(db.Model):
    """
    Main table for storing budget analysis results
    """
    __tablename__ = 'budget_analyses'
    
    # Primary Key
    id = db.Column(db.String(36), primary_key=True)  # UUID
    
    # Basic Info
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Budget Metrics
    total_budget = db.Column(db.Float, nullable=False)
    line_items = db.Column(db.Integer, nullable=False)
    num_departments = db.Column(db.Integer, default=0)
    
    # Risk Assessment
    risk_level = db.Column(db.String(20), default='MODERATE')  # LOW, MODERATE, HIGH, CRITICAL
    risk_score = db.Column(db.Float, default=0.0)
    
    # Data Storage (JSON)
    dataframe_json = db.Column(db.Text, nullable=False)  # Stores DataFrame as JSON
    risk_analysis_json = db.Column(db.Text)  # Risk analysis details
    optimizations_json = db.Column(db.Text)  # Optimization recommendations
    ai_insights_json = db.Column(db.Text)  # Claude AI narrative insights
    
    # Metadata
    analysis_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    # Relationships
    line_items_data = db.relationship('BudgetLineItem', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')
    comparisons = db.relationship('BudgetComparison', 
                                   foreign_keys='BudgetComparison.analysis1_id',
                                   backref='analysis1', 
                                   lazy='dynamic')
    
    def __repr__(self):
        return f'<BudgetAnalysis {self.filename} - ${self.total_budget:,.2f}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'total_budget': self.total_budget,
            'line_items': self.line_items,
            'num_departments': self.num_departments,
            'risk_level': self.risk_level,
            'risk_score': self.risk_score,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'notes': self.notes,
            'tags': self.tags.split(',') if self.tags else []
        }
    
    def get_dataframe_dict(self):
        """Get DataFrame as dictionary"""
        if self.dataframe_json:
            return json.loads(self.dataframe_json)
        return {}
    
    def get_risk_analysis(self):
        """Get risk analysis as dictionary"""
        if self.risk_analysis_json:
            return json.loads(self.risk_analysis_json)
        return {}
    
    def get_optimizations(self):
        """Get optimizations as list"""
        if self.optimizations_json:
            return json.loads(self.optimizations_json)
        return []


class BudgetLineItem(db.Model):
    """
    Individual line items from budget files
    Allows for detailed querying and analysis
    """
    __tablename__ = 'budget_line_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysis_id = db.Column(db.String(36), db.ForeignKey('budget_analyses.id'), nullable=False)
    
    # Line Item Details
    category = db.Column(db.String(100))
    department = db.Column(db.String(100))
    description = db.Column(db.String(500))
    amount = db.Column(db.Float, nullable=False)
    
    # Risk Flags
    risk_category = db.Column(db.String(20))  # LOW, MODERATE, HIGH
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(200))
    
    # Metadata
    line_number = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<LineItem {self.category} - ${self.amount:,.2f}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'department': self.department,
            'description': self.description,
            'amount': self.amount,
            'risk_category': self.risk_category,
            'is_flagged': self.is_flagged,
            'flag_reason': self.flag_reason
        }


class BudgetComparison(db.Model):
    """
    Stores budget comparison results
    """
    __tablename__ = 'budget_comparisons'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # References to two analyses being compared
    analysis1_id = db.Column(db.String(36), db.ForeignKey('budget_analyses.id'), nullable=False)
    analysis2_id = db.Column(db.String(36), db.ForeignKey('budget_analyses.id'), nullable=False)
    
    # Comparison Results (JSON)
    comparison_data_json = db.Column(db.Text, nullable=False)
    
    # Metadata
    comparison_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationship to second analysis
    analysis2 = db.relationship('BudgetAnalysis', foreign_keys=[analysis2_id])
    
    def __repr__(self):
        return f'<Comparison {self.analysis1_id} vs {self.analysis2_id}>'
    
    def get_comparison_data(self):
        """Get comparison results as dictionary"""
        if self.comparison_data_json:
            return json.loads(self.comparison_data_json)
        return {}


class UserActivity(db.Model):
    """
    Track user activity for analytics and debugging
    """
    __tablename__ = 'user_activity'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Activity Details
    action = db.Column(db.String(50), nullable=False)  # upload, analyze, export, compare
    resource_id = db.Column(db.String(36))  # ID of related resource
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Activity {self.action} at {self.timestamp}>'


class AppSettings(db.Model):
    """
    Store application settings and configuration
    """
    __tablename__ = 'app_settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(500))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_db(app):
    """
    Initialize database with Flask app
    
    Usage:
        from database_models import init_db
        init_db(app)
    """
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully")


def get_recent_analyses(limit=10):
    """Get most recent budget analyses"""
    return BudgetAnalysis.query.order_by(
        BudgetAnalysis.upload_date.desc()
    ).limit(limit).all()


def get_analysis_by_id(analysis_id):
    """Get a specific analysis by ID"""
    return BudgetAnalysis.query.get(analysis_id)


def search_analyses(query_text=None, start_date=None, end_date=None, risk_level=None):
    """
    Search for budget analyses with filters
    
    Args:
        query_text: Search in filename
        start_date: Filter by date range (start)
        end_date: Filter by date range (end)
        risk_level: Filter by risk level
    """
    query = BudgetAnalysis.query
    
    if query_text:
        query = query.filter(BudgetAnalysis.filename.contains(query_text))
    
    if start_date:
        query = query.filter(BudgetAnalysis.upload_date >= start_date)
    
    if end_date:
        query = query.filter(BudgetAnalysis.upload_date <= end_date)
    
    if risk_level:
        query = query.filter(BudgetAnalysis.risk_level == risk_level)
    
    return query.order_by(BudgetAnalysis.upload_date.desc()).all()


def get_database_stats():
    """Get database statistics"""
    return {
        'total_analyses': BudgetAnalysis.query.count(),
        'total_line_items': BudgetLineItem.query.count(),
        'total_comparisons': BudgetComparison.query.count(),
        'total_budget_tracked': db.session.query(
            db.func.sum(BudgetAnalysis.total_budget)
        ).scalar() or 0,
        'avg_budget': db.session.query(
            db.func.avg(BudgetAnalysis.total_budget)
        ).scalar() or 0,
        'risk_distribution': db.session.query(
            BudgetAnalysis.risk_level,
            db.func.count(BudgetAnalysis.id)
        ).group_by(BudgetAnalysis.risk_level).all()
    }


def cleanup_old_analyses(days_old=90):
    """Delete analyses older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    old_analyses = BudgetAnalysis.query.filter(
        BudgetAnalysis.upload_date < cutoff_date
    ).all()
    
    count = len(old_analyses)
    for analysis in old_analyses:
        db.session.delete(analysis)
    
    db.session.commit()
    return count


# For backward compatibility
from datetime import timedelta

if __name__ == '__main__':
    print("""
    Database Models Loaded
    ======================
    
    Tables:
    - budget_analyses: Main analysis storage
    - budget_line_items: Individual line items
    - budget_comparisons: Comparison results
    - user_activity: Activity tracking
    - app_settings: Application settings
    
    Helper Functions:
    - init_db(app): Initialize database
    - get_recent_analyses(limit): Get recent analyses
    - get_analysis_by_id(id): Get specific analysis
    - search_analyses(...): Search with filters
    - get_database_stats(): Get statistics
    - cleanup_old_analyses(days): Delete old data
    """)