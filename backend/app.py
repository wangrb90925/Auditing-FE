from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.utils import secure_filename
from audit_engine import AuditEngine
from file_processor import FileProcessor
from fmcsa_rules import FMCSARules
import tempfile
import zipfile

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'xls'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize components
audit_engine = AuditEngine()
file_processor = FileProcessor()
fmcsa_rules = FMCSARules()

# In-memory storage for audits (in production, use a database)
audits = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/audits', methods=['POST'])
def create_audit():
    """Create a new audit"""
    try:
        data = request.get_json()
        
        audit_id = str(uuid.uuid4())
        audit_data = {
            'id': audit_id,
            'driverName': data.get('driverName', ''),
            'driverType': data.get('driverType', ''),
            'status': 'pending',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat(),
            'files': [],
            'violations': 0,
            'summary': {
                'complianceScore': 0,
                'severity': 'low',
                'totalViolations': 0,
                'hosViolations': 0,
                'formViolations': 0,
                'falsificationViolations': 0
            },
            'violationsList': [],
            'processingLog': []
        }
        
        audits[audit_id] = audit_data
        
        return jsonify(audit_data), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>/upload', methods=['POST'])
def upload_files(audit_id):
    """Upload files for an audit"""
    try:
        if audit_id not in audits:
            return jsonify({'error': 'Audit not found'}), 404
        
        audit = audits[audit_id]
        
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{audit_id}_{filename}")
                file.save(file_path)
                uploaded_files.append({
                    'name': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path)
                })
        
        audit['files'] = uploaded_files
        audit['updatedAt'] = datetime.now().isoformat()
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} files',
            'files': uploaded_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>/process', methods=['POST'])
def process_audit(audit_id):
    """Process the audit with AI engine"""
    try:
        if audit_id not in audits:
            return jsonify({'error': 'Audit not found'}), 404
        
        audit = audits[audit_id]
        
        if not audit['files']:
            return jsonify({'error': 'No files uploaded for processing'}), 400
        
        # Update status to processing
        audit['status'] = 'processing'
        audit['updatedAt'] = datetime.now().isoformat()
        audit['processingLog'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'info',
            'message': 'Starting FMCSA compliance analysis'
        })
        
        # Process files
        extracted_data = file_processor.process_files(audit['files'])
        
        audit['processingLog'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'info',
            'message': f'Extracted data from {len(audit["files"])} files'
        })
        
        # Apply FMCSA rules
        violations = fmcsa_rules.analyze_compliance(extracted_data, audit['driverType'])
        
        audit['processingLog'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'info',
            'message': f'Found {len(violations)} FMCSA violations'
        })
        
        # Calculate compliance score
        total_violations = len(violations)
        compliance_score = max(0, 100 - (total_violations * 5))  # Simple scoring
        
        # Determine severity
        if total_violations == 0:
            severity = 'low'
        elif total_violations <= 5:
            severity = 'medium'
        else:
            severity = 'high'
        
        # Update audit with results
        audit['violations'] = total_violations
        audit['violationsList'] = violations
        audit['summary'] = {
            'complianceScore': compliance_score,
            'severity': severity,
            'totalViolations': total_violations,
            'hosViolations': len([v for v in violations if 'HOS' in v.get('type', '')]),
            'formViolations': len([v for v in violations if 'form' in v.get('type', '').lower()]),
            'falsificationViolations': len([v for v in violations if 'falsification' in v.get('type', '').lower()])
        }
        audit['status'] = 'completed'
        audit['updatedAt'] = datetime.now().isoformat()
        
        audit['processingLog'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'success',
            'message': f'Audit completed with {compliance_score}% compliance score'
        })
        
        return jsonify(audit)
        
    except Exception as e:
        if audit_id in audits:
            audits[audit_id]['status'] = 'failed'
            audits[audit_id]['processingLog'].append({
                'timestamp': datetime.now().isoformat(),
                'type': 'warning',
                'message': f'Processing failed: {str(e)}'
            })
        
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits', methods=['GET'])
def get_audits():
    """Get all audits"""
    try:
        return jsonify(list(audits.values()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>', methods=['GET'])
def get_audit(audit_id):
    """Get specific audit"""
    try:
        if audit_id not in audits:
            return jsonify({'error': 'Audit not found'}), 404
        
        return jsonify(audits[audit_id])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audits/<audit_id>/report', methods=['GET'])
def download_report(audit_id):
    """Download audit report as CSV"""
    try:
        if audit_id not in audits:
            return jsonify({'error': 'Audit not found'}), 404
        
        audit = audits[audit_id]
        
        if audit['status'] != 'completed':
            return jsonify({'error': 'Audit not completed'}), 400
        
        # Create CSV report
        report_data = []
        
        # Add audit summary
        report_data.append(['FMCSA Compliance Audit Report'])
        report_data.append(['Driver Name', audit['driverName']])
        report_data.append(['Driver Type', audit['driverType']])
        report_data.append(['Audit Date', audit['createdAt']])
        report_data.append(['Compliance Score', f"{audit['summary']['complianceScore']}%"])
        report_data.append(['Total Violations', audit['violations']])
        report_data.append(['Severity', audit['summary']['severity']])
        report_data.append([])
        
        # Add violation details
        if audit['violationsList']:
            report_data.append(['Violation Details'])
            report_data.append(['Date', 'Type', 'Description', 'Severity', 'Penalty'])
            
            for violation in audit['violationsList']:
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
def download_files(audit_id):
    """Download all audit files as ZIP"""
    try:
        if audit_id not in audits:
            return jsonify({'error': 'Audit not found'}), 404
        
        audit = audits[audit_id]
        
        if not audit['files']:
            return jsonify({'error': 'No files found'}), 404
        
        # Create temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
            for file_info in audit['files']:
                if os.path.exists(file_info['path']):
                    zipf.write(file_info['path'], file_info['name'])
        
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name=f"audit_files_{audit_id}.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get audit statistics"""
    try:
        total_audits = len(audits)
        completed_audits = len([a for a in audits.values() if a['status'] == 'completed'])
        pending_audits = len([a for a in audits.values() if a['status'] == 'pending'])
        processing_audits = len([a for a in audits.values() if a['status'] == 'processing'])
        
        total_violations = sum(a['violations'] for a in audits.values())
        
        return jsonify({
            'totalAudits': total_audits,
            'completedAudits': completed_audits,
            'pendingAudits': pending_audits,
            'processingAudits': processing_audits,
            'totalViolations': total_violations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False) 