import os
import json
from datetime import datetime
from file_processor import FileProcessor
from fmcsa_rules import FMCSARules

class AuditEngine:
    def __init__(self):
        self.file_processor = FileProcessor()
        self.fmcsa_rules = FMCSARules()
        
    def process_audit(self, files, driver_type, driver_name):
        """
        Main audit processing function
        
        Args:
            files: List of file information dictionaries
            driver_type: Type of driver (long-haul, short-haul, exemption)
            driver_name: Name of the driver
            
        Returns:
            dict: Complete audit results
        """
        try:
            # Step 1: Process and extract data from files
            print(f"Processing {len(files)} files for driver: {driver_name}")
            extracted_data = self.file_processor.process_files(files)
            
            # Step 2: Apply FMCSA compliance rules
            print("Applying FMCSA compliance rules...")
            violations = self.fmcsa_rules.analyze_compliance(extracted_data, driver_type)
            
            # Step 3: Generate audit summary
            audit_summary = self._generate_audit_summary(
                extracted_data, violations, driver_type, driver_name
            )
            
            # Step 4: Calculate compliance score
            compliance_score = self._calculate_compliance_score(violations)
            
            # Step 5: Determine severity level
            severity = self._determine_severity(violations)
            
            # Step 6: Create final audit report
            audit_results = {
                'driver_name': driver_name,
                'driver_type': driver_type,
                'audit_date': datetime.now().isoformat(),
                'files_processed': len(files),
                'extracted_data_summary': self.file_processor.get_processed_data(),
                'violations': violations,
                'violation_summary': self.fmcsa_rules.get_violation_summary(),
                'compliance_score': compliance_score,
                'severity': severity,
                'audit_summary': audit_summary,
                'processing_log': [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'step': 'file_processing',
                        'message': f'Processed {len(files)} files successfully'
                    },
                    {
                        'timestamp': datetime.now().isoformat(),
                        'step': 'compliance_analysis',
                        'message': f'Found {len(violations)} FMCSA violations'
                    },
                    {
                        'timestamp': datetime.now().isoformat(),
                        'step': 'report_generation',
                        'message': f'Generated audit report with {compliance_score}% compliance score'
                    }
                ]
            }
            
            return audit_results
            
        except Exception as e:
            print(f"Error in audit processing: {str(e)}")
            return {
                'error': str(e),
                'driver_name': driver_name,
                'driver_type': driver_type,
                'audit_date': datetime.now().isoformat(),
                'status': 'failed'
            }
    
    def _generate_audit_summary(self, extracted_data, violations, driver_type, driver_name):
        """Generate a human-readable audit summary"""
        summary = {
            'driver_info': {
                'name': driver_name,
                'type': driver_type,
                'audit_period': self._get_audit_period(extracted_data)
            },
            'files_analyzed': {
                'driver_logs': len(extracted_data.get('driver_logs', [])),
                'fuel_receipts': len(extracted_data.get('fuel_receipts', [])),
                'bills_of_lading': len(extracted_data.get('bills_of_lading', [])),
                'audit_summaries': len(extracted_data.get('audit_summaries', []))
            },
            'compliance_analysis': {
                'total_violations': len(violations),
                'hos_violations': len([v for v in violations if 'HOS' in v.get('type', '')]),
                'form_violations': len([v for v in violations if 'FORM' in v.get('type', '').lower()]),
                'falsification_violations': len([v for v in violations if 'FALSIFICATION' in v.get('type', '').lower()]),
                'bol_violations': len([v for v in violations if 'BOL' in v.get('type', '')])
            },
            'key_findings': self._generate_key_findings(violations),
            'recommendations': self._generate_recommendations(violations, driver_type)
        }
        
        return summary
    
    def _get_audit_period(self, extracted_data):
        """Determine the audit period from the data"""
        # This would be extracted from the actual log data
        # For now, return a placeholder
        return {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'duration_days': 31
        }
    
    def _generate_key_findings(self, violations):
        """Generate key findings from violations"""
        findings = []
        
        if not violations:
            findings.append("No FMCSA violations detected during the audit period.")
            return findings
        
        # Group violations by type
        hos_violations = [v for v in violations if 'HOS' in v.get('type', '')]
        form_violations = [v for v in violations if 'FORM' in v.get('type', '').lower()]
        falsification_violations = [v for v in violations if 'FALSIFICATION' in v.get('type', '').lower()]
        
        if hos_violations:
            findings.append(f"Found {len(hos_violations)} Hours-of-Service violations requiring immediate attention.")
        
        if form_violations:
            findings.append(f"Identified {len(form_violations)} form and manner violations in driver logs.")
        
        if falsification_violations:
            findings.append(f"Detected {len(falsification_violations)} potential log falsification issues.")
        
        # Add specific findings for major violations
        major_violations = [v for v in violations if v.get('severity') == 'major']
        if major_violations:
            findings.append(f"Critical: {len(major_violations)} major violations detected with significant penalty exposure.")
        
        return findings
    
    def _generate_recommendations(self, violations, driver_type):
        """Generate recommendations based on violations and driver type"""
        recommendations = []
        
        if not violations:
            recommendations.append("Continue current compliance practices.")
            return recommendations
        
        # HOS-specific recommendations
        hos_violations = [v for v in violations if 'HOS' in v.get('type', '')]
        if hos_violations:
            recommendations.append("Implement stricter Hours-of-Service monitoring and training.")
            recommendations.append("Consider using electronic logging devices (ELDs) for better accuracy.")
        
        # Form and manner recommendations
        form_violations = [v for v in violations if 'FORM' in v.get('type', '').lower()]
        if form_violations:
            recommendations.append("Provide additional training on proper log completion procedures.")
            recommendations.append("Implement log review processes before submission.")
        
        # Driver type specific recommendations
        if driver_type == 'long-haul':
            recommendations.append("Long-haul drivers require special attention to 60/70-hour rules.")
        elif driver_type == 'short-haul':
            recommendations.append("Short-haul drivers should focus on 12-hour return requirements.")
        elif driver_type == 'exemption':
            recommendations.append("Ensure exemption documentation is properly maintained and current.")
        
        # General recommendations
        recommendations.append("Schedule regular compliance training sessions.")
        recommendations.append("Implement pre-trip log review procedures.")
        
        return recommendations
    
    def _calculate_compliance_score(self, violations):
        """Calculate compliance score based on violations"""
        if not violations:
            return 100
        
        # Simple scoring algorithm
        # Each violation reduces score by 5 points
        # Different violation types have different weights
        total_penalty = 0
        
        for violation in violations:
            severity = violation.get('severity', 'minor')
            if severity == 'critical':
                total_penalty += 15
            elif severity == 'major':
                total_penalty += 10
            else:  # minor
                total_penalty += 5
        
        # Calculate score (minimum 0)
        score = max(0, 100 - total_penalty)
        
        return round(score, 1)
    
    def _determine_severity(self, violations):
        """Determine overall severity level of violations"""
        if not violations:
            return 'low'
        
        # Count violations by severity
        critical_count = len([v for v in violations if v.get('severity') == 'critical'])
        major_count = len([v for v in violations if v.get('severity') == 'major'])
        minor_count = len([v for v in violations if v.get('severity') == 'minor'])
        
        # Determine overall severity
        if critical_count > 0:
            return 'critical'
        elif major_count >= 3 or (major_count + critical_count) >= 5:
            return 'high'
        elif major_count > 0 or minor_count >= 5:
            return 'medium'
        else:
            return 'low'
    
    def validate_files(self, files):
        """Validate uploaded files before processing"""
        valid_files = []
        errors = []
        
        for file_info in files:
            file_path = file_info.get('path', '')
            file_name = file_info.get('name', '')
            
            # Check if file exists
            if not os.path.exists(file_path):
                errors.append(f"File not found: {file_name}")
                continue
            
            # Check file size (max 100MB)
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                errors.append(f"File too large: {file_name} ({file_size / 1024 / 1024:.1f}MB)")
                continue
            
            # Check file extension
            allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.xls'}
            file_ext = os.path.splitext(file_name)[1].lower()
            if file_ext not in allowed_extensions:
                errors.append(f"Unsupported file type: {file_name}")
                continue
            
            valid_files.append(file_info)
        
        return {
            'valid_files': valid_files,
            'errors': errors,
            'total_files': len(files),
            'valid_count': len(valid_files)
        }
    
    def get_processing_status(self, audit_id):
        """Get the processing status of an audit"""
        # This would typically query a database
        # For now, return a mock status
        return {
            'audit_id': audit_id,
            'status': 'completed',
            'progress': 100,
            'current_step': 'report_generation',
            'estimated_completion': datetime.now().isoformat()
        } 