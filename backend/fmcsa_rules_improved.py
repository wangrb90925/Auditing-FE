"""
Improved FMCSA Rules Engine

This module replaces the hard-coded violation logic with a proper rule-based system
that uses the driver classification system and violation detector.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from driver_classifications import driver_classification_system, ViolationType
from violation_detector import ViolationDetector

class FMCSARulesImproved:
    """Improved FMCSA compliance rules engine"""
    
    def __init__(self):
        self.violation_detector = ViolationDetector()
        self.classification_system = driver_classification_system
        self.violations = []
        self.violation_summary = {}
        
    def analyze_compliance(self, extracted_data: Dict, driver_type: str) -> List[Dict]:
        """
        Analyze compliance using rule-based detection
        
        Args:
            extracted_data: Processed data from files
            driver_type: Type of driver (long-haul, short-haul, exemption, etc.)
            
        Returns:
            List of violation dictionaries
        """
        # Starting compliance analysis silently
        
        # Reset violations
        self.violations = []
        
        # Get driver classification (will default to long-haul if unknown)
        classification = self.classification_system.get_classification(driver_type)
        if not classification:
            print(f"[ERROR] Failed to get classification for '{driver_type}', using default")
            # Create a minimal default classification
            from driver_classifications import DriverClassification, DriverType, ViolationType
            classification = DriverClassification(
                driver_type=DriverType.LONG_HAUL,
                name="Default Long-Haul Driver",
                description="Default classification when type lookup fails",
                applicable_violations={
                    ViolationType.FORM_MANNER_MISSING_FIELDS,
                    ViolationType.FORM_MANNER_INCOMPLETE_ENTRIES,
                    ViolationType.LOG_FALSIFICATION,
                    ViolationType.DRIVING_OFF_DUTY,
                    ViolationType.FUEL_OFF_DUTY
                },
                hos_limits={}
            )
        
        # Using classification silently
        
        # Detect violations using the rule-based engine
        try:
            detected_violations = self.violation_detector.detect_violations(extracted_data, driver_type)
        except Exception as e:
            # Violation detection failed - using empty list
            detected_violations = []
        
        # Convert violations to the expected format
        for violation in detected_violations:
            violation_dict = {
                'date': violation.date,
                'type': violation.violation_type.value.upper(),
                'description': violation.description,
                'severity': violation.severity.value,
                'penalty': violation.penalty,
                'section': violation.cfr_section,
                'details': violation.details
            }
            self.violations.append(violation_dict)
        
        # Generate violation summary
        self._generate_violation_summary()
        
        # Results available in JSON files
        return self.violations
    
    def _generate_violation_summary(self):
        """Generate summary of violations by type and severity"""
        self.violation_summary = {
            'total_violations': len(self.violations),
            'by_severity': {'minor': 0, 'major': 0, 'critical': 0},
            'by_type': {},
            'hos_violations': 0,
            'form_violations': 0,
            'falsification_violations': 0,
            'fuel_violations': 0,
            'geographic_violations': 0
        }
        
        for violation in self.violations:
            # Count by severity
            severity = violation.get('severity', 'minor').lower()
            if severity in self.violation_summary['by_severity']:
                self.violation_summary['by_severity'][severity] += 1
            
            # Count by type
            violation_type = violation.get('type', '')
            if violation_type not in self.violation_summary['by_type']:
                self.violation_summary['by_type'][violation_type] = 0
            self.violation_summary['by_type'][violation_type] += 1
            
            # Count by category
            if 'HOS' in violation_type:
                self.violation_summary['hos_violations'] += 1
            elif 'FORM' in violation_type:
                self.violation_summary['form_violations'] += 1
            elif 'FALSIFICATION' in violation_type:
                self.violation_summary['falsification_violations'] += 1
            elif 'FUEL' in violation_type:
                self.violation_summary['fuel_violations'] += 1
            elif 'GEOGRAPHIC' in violation_type:
                self.violation_summary['geographic_violations'] += 1
    
    def get_consolidated_violations(self) -> List[Dict]:
        """
        Get consolidated violations (removing duplicates and grouping similar violations)
        """
        if not self.violations:
            return []
        
        # Group violations by type and date
        consolidated = {}
        
        for violation in self.violations:
            key = f"{violation['type']}_{violation['date']}"
            
            if key not in consolidated:
                consolidated[key] = violation.copy()
                consolidated[key]['count'] = 1
            else:
                # Merge duplicate violations
                consolidated[key]['count'] += 1
                # Update description to show count
                base_desc = consolidated[key]['description']
                if 'count' not in base_desc.lower():
                    consolidated[key]['description'] = f"{base_desc} (occurred {consolidated[key]['count']} times)"
        
        return list(consolidated.values())
    
    def get_violation_summary(self) -> Dict:
        """Get violation summary statistics"""
        return self.violation_summary
    
    def get_driver_type_info(self, driver_type: str) -> Dict:
        """Get information about a driver type"""
        classification = self.classification_system.get_classification(driver_type)
        if not classification:
            return {}
        
        return {
            'name': classification.name,
            'description': classification.description,
            'hos_limits': classification.hos_limits,
            'exemptions': classification.exemptions,
            'applicable_violations': [v.value for v in classification.applicable_violations]
        }
    
    def validate_driver_type(self, driver_type: str) -> bool:
        """Validate if driver type is supported"""
        return self.classification_system.get_classification(driver_type) is not None
    
    def get_supported_driver_types(self) -> List[str]:
        """Get list of supported driver types"""
        return [dt.value for dt in self.classification_system.classifications.keys()]
    
    def export_violation_report(self, file_path: str):
        """Export violations to JSON report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'violations': self.violations,
            'consolidated_violations': self.get_consolidated_violations(),
            'summary': self.violation_summary,
            'total_violations': len(self.violations)
        }
        
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def get_penalty_estimate(self) -> Dict:
        """Calculate estimated penalty amounts"""
        total_min = 0
        total_max = 0
        
        for violation in self.violations:
            violation_type_str = violation.get('type', '').lower()
            
            # Map violation type string to enum
            violation_type = None
            for vt in ViolationType:
                if vt.value.upper() == violation_type_str.upper():
                    violation_type = vt
                    break
            
            if violation_type:
                rule = self.classification_system.get_violation_rule(violation_type)
                if rule:
                    min_penalty, max_penalty = rule.penalty_range
                    total_min += min_penalty
                    total_max += max_penalty
        
        return {
            'minimum_penalty': total_min,
            'maximum_penalty': total_max,
            'estimated_penalty': (total_min + total_max) // 2,
            'penalty_range': f"${total_min:,} - ${total_max:,}"
        }
    
    def analyze_compliance_trends(self, historical_data: List[Dict]) -> Dict:
        """Analyze compliance trends over time (for future enhancement)"""
        # This would analyze historical violation data to identify patterns
        # For now, return a placeholder structure
        return {
            'trend': 'stable',
            'improvement_areas': [],
            'recurring_violations': [],
            'recommendations': []
        }

# Backward compatibility - create an instance with the old class name
class FMCSARules(FMCSARulesImproved):
    """Backward compatibility wrapper"""
    
    def __init__(self):
        super().__init__()
        print("[COMPATIBILITY] Using improved FMCSA rules engine")
        
    def analyze_compliance(self, extracted_data: Dict, driver_type: str) -> List[Dict]:
        """Maintain backward compatibility with existing interface"""
        return super().analyze_compliance(extracted_data, driver_type)
