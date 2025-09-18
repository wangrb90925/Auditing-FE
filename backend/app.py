from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import uuid
import json
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.utils import secure_filename
from audit_engine import AuditEngine
from file_processor import FileProcessor
from fmcsa_rules import FMCSARules
from database import db, Audit, AuditFile, User, init_db
from auth import (
    create_user, authenticate_user, get_user_by_id, get_all_users, 
    update_user, change_user_role, create_default_admin, change_user_password,
    admin_required, auditor_required
)
import tempfile
import zipfile

app = Flask(__name__)
CORS(app)

# Configuration
from config import Config

app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['JWT_SECRET_KEY'] = Config.SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize JWT
jwt = JWTManager(app)

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db(app)

# Create default admin user if no users exist
with app.app_context():
    create_default_admin()

# Initialize components
audit_engine = AuditEngine()
file_processor = FileProcessor()
fmcsa_rules = FMCSARules()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create user
        user, error = create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'auditor')  # Default to auditor
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        # Authenticate user
        user, error = authenticate_user(data['username'], data['password'])
        
        if error:
            return jsonify({'error': error}), 401
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = get_user_by_id(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Update user
        user, error = update_user(current_user_id, **data)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Get user and verify current password
        user = get_user_by_id(int(current_user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin endpoints
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        users = get_all_users()
        return jsonify([user.to_dict() for user in users])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required
def change_role(user_id):
    """Change user role (admin only)"""
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'error': 'Role is required'}), 400
        
        user, error = change_user_role(user_id, new_role)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/audits', methods=['POST'])
@jwt_required()
@auditor_required
def create_audit():
    """Create a new audit"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        if not data.get('driverName'):
            return jsonify({'error': 'Driver name is required'}), 400
        if not data.get('driverType'):
            return jsonify({'error': 'Driver type is required'}), 400
        
        audit_id = str(uuid.uuid4())
        print(f"Generated audit ID: {audit_id}")  # Debug logging
        
        # Create new audit in database
        try:
            user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID format'}), 400
            
        audit = Audit(
            id=audit_id,
            driver_name=data.get('driverName', ''),
            driver_type=data.get('driverType', ''),
            status='pending',
            violations_list=json.dumps([]),
            processing_log=json.dumps([]),
            created_by=user_id
        )
        
        db.session.add(audit)
        db.session.commit()
        
        print(f"Audit created successfully with ID: {audit.id}")  # Debug logging
        return jsonify(audit.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating audit: {str(e)}")  # Debug logging
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>/upload', methods=['POST'])
@jwt_required()
@auditor_required
def upload_files(audit_id):
    """Upload files for an audit"""
    try:
        # Validate audit_id
        if not audit_id or audit_id == 'undefined' or audit_id == 'null':
            return jsonify({'error': 'Invalid audit ID'}), 400
        
        print(f"Uploading files for audit ID: {audit_id}")  # Debug logging
        
        # Get audit from database
        audit = Audit.query.get(audit_id)
        if not audit:
            return jsonify({'error': 'Audit not found'}), 404
        
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{audit_id}_{filename}")
                file.save(file_path)
                
                # Save file info to database
                audit_file = AuditFile(
                    audit_id=audit_id,
                    name=filename,
                    path=file_path,
                    size=os.path.getsize(file_path)
                )
                db.session.add(audit_file)
                uploaded_files.append({
                    'name': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path)
                })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} files',
            'files': uploaded_files
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>/process', methods=['POST'])
@jwt_required()
@auditor_required
def process_audit(audit_id):
    """Process the audit with AI engine"""
    try:
        # Validate audit_id
        if not audit_id or audit_id == 'undefined' or audit_id == 'null':
            return jsonify({'error': 'Invalid audit ID'}), 400
        
        print(f"Processing audit ID: {audit_id}")  # Debug logging
        
        # Get audit from database
        audit = Audit.query.get(audit_id)
        if not audit:
            return jsonify({'error': 'Audit not found'}), 404
        
        if not audit.files:
            return jsonify({'error': 'No files uploaded for processing'}), 400
        
        # Update status to processing
        audit.status = 'processing'
        processing_log = json.loads(audit.processing_log) if audit.processing_log else []
        processing_log.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'info',
            'message': 'Starting FMCSA compliance analysis'
        })
        audit.processing_log = json.dumps(processing_log)
        db.session.commit()
        
        # Convert files to expected format
        files_data = [{'name': f.name, 'path': f.path, 'size': f.size} for f in audit.files]
        
        # Use a fresh audit engine instance for comprehensive analysis
        fresh_audit_engine = AuditEngine()
        print(f"🔍 Processing audit with {len(files_data)} files")
        audit_results = fresh_audit_engine.process_audit(files_data, audit.driver_type, audit.driver_name or 'Unknown Driver')
        print(f"🔍 Audit results: compliance_score={audit_results.get('compliance_score')}, violations={len(audit_results.get('violations', []))}")
        
        if 'error' in audit_results:
            raise Exception(audit_results['error'])
        
        # Extract results from audit engine
        violations = audit_results.get('violations', [])
        consolidated_violations = audit_results.get('consolidated_violations', [])
        compliance_score = audit_results.get('compliance_score', 100)
        severity = audit_results.get('severity', 'low')
        violation_summary = audit_results.get('violation_summary', {})
        
        processing_log.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'info',
            'message': f'Extracted data from {len(files_data)} files'
        })
        
        processing_log.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'info',
            'message': f'Found {len(violations)} FMCSA violations'
        })
        
        # Update audit with comprehensive results
        audit.violations = len(violations)
        audit.violations_list = json.dumps(violations)
        audit.compliance_score = compliance_score
        audit.severity = severity
        audit.total_violations = len(violations)
        
        # Count specific violation types
        audit.hos_violations = len([v for v in violations if 'HOS' in v.get('type', '')])
        audit.form_violations = len([v for v in violations if 'FORM' in v.get('type', '').upper()])
        audit.falsification_violations = len([v for v in violations if 'FALSIFICATION' in v.get('type', '').upper()])
        
        # Add additional violation counts
        audit.bol_violations = len([v for v in violations if 'BOL' in v.get('type', '')])
        audit.fuel_violations = len([v for v in violations if 'FUEL' in v.get('type', '')])
        audit.geographic_violations = len([v for v in violations if 'GEOGRAPHIC' in v.get('type', '')])
        
        audit.status = 'completed'
        
        processing_log.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'success',
            'message': f'Audit completed with {compliance_score}% compliance score and {len(violations)} violations'
        })
        audit.processing_log = json.dumps(processing_log)
        
        db.session.commit()
        
        return jsonify(audit.to_dict())
        
    except Exception as e:
        # Update audit status to failed
        if audit:
            audit.status = 'failed'
            processing_log = json.loads(audit.processing_log) if audit.processing_log else []
            processing_log.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'warning',
                'message': f'Processing failed: {str(e)}'
            })
            audit.processing_log = json.dumps(processing_log)
            db.session.commit()
        
        print(f"Error processing audit {audit_id}: {str(e)}")
        return jsonify({'error': f'Failed to process audit: {str(e)}'}), 500

@app.route('/api/audits', methods=['GET'])
@jwt_required()
@auditor_required
def get_audits():
    """Get all audits"""
    try:
        audits_list = Audit.query.all()
        return jsonify([audit.to_dict() for audit in audits_list])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>', methods=['GET'])
@jwt_required()
@auditor_required
def get_audit(audit_id):
    """Get specific audit"""
    try:
        # Validate audit_id
        if not audit_id or audit_id == 'undefined' or audit_id == 'null':
            return jsonify({'error': 'Invalid audit ID'}), 400
        
        print(f"Getting audit ID: {audit_id}")  # Debug logging
        
        audit = Audit.query.get(audit_id)
        if not audit:
            return jsonify({'error': 'Audit not found'}), 404
        
        return jsonify(audit.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>', methods=['DELETE'])
@jwt_required()
@auditor_required
def delete_audit(audit_id):
    """Delete specific audit"""
    try:
        # Validate audit_id
        if not audit_id or audit_id == 'undefined' or audit_id == 'null':
            return jsonify({'error': 'Invalid audit ID'}), 400
        
        print(f"Deleting audit ID: {audit_id}")  # Debug logging
        
        audit = Audit.query.get(audit_id)
        if not audit:
            return jsonify({'error': 'Audit not found'}), 404
        
        # Delete associated files from storage
        for file_info in audit.files:
            if os.path.exists(file_info.path):
                os.remove(file_info.path)
        
        # Delete from database
        db.session.delete(audit)
        db.session.commit()
        
        return jsonify({'message': 'Audit deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>/report', methods=['GET'])
@jwt_required()
@auditor_required
def download_report(audit_id):
    """Download audit report as CSV"""
    try:
        # Validate audit_id
        if not audit_id or audit_id == 'undefined' or audit_id == 'null':
            return jsonify({'error': 'Invalid audit ID'}), 400
        
        print(f"Downloading report for audit ID: {audit_id}")  # Debug logging
        
        audit = Audit.query.get(audit_id)
        if not audit:
            return jsonify({'error': 'Audit not found'}), 404
        
        if audit.status != 'completed':
            return jsonify({'error': 'Audit not completed'}), 400
        
        # Create CSV report
        report_data = []
        
        # Add audit summary
        report_data.append(['FMCSA Compliance Audit Report'])
        report_data.append(['Driver Name', audit.driver_name])
        report_data.append(['Driver Type', audit.driver_type])
        report_data.append(['Audit Date', audit.created_at.isoformat() if audit.created_at else ''])
        report_data.append(['Compliance Score', f"{audit.compliance_score}%"])
        report_data.append(['Total Violations', audit.violations])
        report_data.append(['Severity', audit.severity])
        report_data.append([])
        
        # Add violation details
        violations_list = json.loads(audit.violations_list) if audit.violations_list else []
        if violations_list:
            report_data.append(['Violation Details'])
            report_data.append(['Date', 'Type', 'Description', 'Severity', 'Penalty'])
            
            for violation in violations_list:
                report_data.append([
                    violation.get('date', ''),
                    violation.get('type', ''),
                    violation.get('description', ''),
                    violation.get('severity', ''),
                    violation.get('penalty', '')
                ])
        
        # Create temporary CSV file
        df = pd.DataFrame(report_data)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        df.to_csv(temp_file.name, index=False, header=False)
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f"fmcsa_audit_{audit_id}.csv",
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>/files', methods=['GET'])
@jwt_required()
@auditor_required
def download_files(audit_id):
    """Download all audit files as ZIP"""
    try:
        # Validate audit_id
        if not audit_id or audit_id == 'undefined' or audit_id == 'null':
            return jsonify({'error': 'Invalid audit ID'}), 400
        
        print(f"Downloading files for audit ID: {audit_id}")  # Debug logging
        
        audit = Audit.query.get(audit_id)
        if not audit:
            return jsonify({'error': 'Audit not found'}), 404
        
        if not audit.files:
            return jsonify({'error': 'No files found'}), 404
        
        # Create temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
            for file_info in audit.files:
                if os.path.exists(file_info.path):
                    zipf.write(file_info.path, file_info.name)
        
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name=f"audit_files_{audit_id}.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
@jwt_required()
@auditor_required
def get_stats():
    """Get audit statistics"""
    try:
        total_audits = Audit.query.count()
        completed_audits = Audit.query.filter_by(status='completed').count()
        pending_audits = Audit.query.filter_by(status='pending').count()
        processing_audits = Audit.query.filter_by(status='processing').count()
        
        total_violations = db.session.query(db.func.sum(Audit.violations)).scalar() or 0
        
        return jsonify({
            'totalAudits': total_audits,
            'completedAudits': completed_audits,
            'pendingAudits': pending_audits,
            'processingAudits': processing_audits,
            'totalViolations': total_violations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin-only endpoints
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    try:
        users = get_all_users()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['admin', 'auditor']:
            return jsonify({'error': 'Invalid role. Must be admin or auditor'}), 400
        
        user, error = change_user_role(user_id, new_role)
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': f'User role updated to {new_role}',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/toggle-status', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = not user.is_active
        db.session.commit()
        
        action = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'message': f'User {action} successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/system-stats', methods=['GET'])
@jwt_required()
@admin_required
def get_system_stats():
    """Get system statistics (admin only)"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_audits = Audit.query.count()
        
        # Mock system health (in real app, this would check actual system metrics)
        system_health = 95
        
        return jsonify({
            'totalUsers': total_users,
            'activeUsers': active_users,
            'totalAudits': total_audits,
            'systemHealth': system_health
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/system-logs', methods=['GET'])
@jwt_required()
@admin_required
def get_system_logs():
    """Get system logs (admin only)"""
    try:
        # Mock system logs (in real app, this would fetch from actual log files)
        logs = [
            {
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'message': 'System running normally'
            },
            {
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'level': 'INFO',
                'message': 'Database backup completed'
            }
        ]
        
        return jsonify(logs)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Enable auto-reload when AUTO_RELOAD=1 (or FLASK_DEBUG=1)
    auto_reload = os.getenv('AUTO_RELOAD', '0') == '1' or os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(
        debug=auto_reload,
        host='127.0.0.1',
        port=5000,
        use_reloader=auto_reload
    ) 