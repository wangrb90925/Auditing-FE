from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='auditor')  # 'admin' or 'auditor'
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with audits (for tracking who created which audits)
    audits = db.relationship('Audit', backref='created_by_user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_auditor(self):
        """Check if user is auditor"""
        return self.role == 'auditor'

class Audit(db.Model):
    """Audit model for storing audit information"""
    __tablename__ = 'audits'
    
    id = db.Column(db.String(36), primary_key=True)
    driver_name = db.Column(db.String(255), nullable=False)
    driver_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    violations = db.Column(db.Integer, default=0)
    compliance_score = db.Column(db.Float, default=0.0)
    severity = db.Column(db.String(20), default='low')
    total_violations = db.Column(db.Integer, default=0)
    hos_violations = db.Column(db.Integer, default=0)
    form_violations = db.Column(db.Integer, default=0)
    falsification_violations = db.Column(db.Integer, default=0)
    violations_list = db.Column(db.Text)  # JSON string
    processing_log = db.Column(db.Text)   # JSON string
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Track who created the audit
    
    # Relationship with files
    files = db.relationship('AuditFile', backref='audit', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert audit to dictionary"""
        return {
            'id': self.id,
            'driverName': self.driver_name,
            'driverType': self.driver_type,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'files': [file.to_dict() for file in self.files],
            'violations': self.violations,
            'summary': {
                'complianceScore': self.compliance_score,
                'severity': self.severity,
                'totalViolations': self.total_violations,
                'hosViolations': self.hos_violations,
                'formViolations': self.form_violations,
                'falsificationViolations': self.falsification_violations
            },
            'violationsList': json.loads(self.violations_list) if self.violations_list else [],
            'processingLog': json.loads(self.processing_log) if self.processing_log else []
        }
    
    def update_summary(self, summary_data):
        """Update audit summary from dictionary"""
        self.compliance_score = summary_data.get('complianceScore', 0)
        self.severity = summary_data.get('severity', 'low')
        self.total_violations = summary_data.get('totalViolations', 0)
        self.hos_violations = summary_data.get('hosViolations', 0)
        self.form_violations = summary_data.get('formViolations', 0)
        self.falsification_violations = summary_data.get('falsificationViolations', 0)

class AuditFile(db.Model):
    """Audit file model for storing file information"""
    __tablename__ = 'audit_files'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.String(36), db.ForeignKey('audits.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(500), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert file to dictionary"""
        return {
            'name': self.name,
            'path': self.path,
            'size': self.size
        }

def init_db(app):
    """Initialize database with Flask app"""
    from config import Config
    
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
