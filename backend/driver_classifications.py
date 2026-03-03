"""
Driver Classification System for FMCSA Compliance Auditing

This module defines different driver types and their applicable rules,
replacing hard-coded logic with configurable classifications.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import json

class DriverType(Enum):
    """Driver classification types"""
    LONG_HAUL = "long-haul"
    SHORT_HAUL = "short-haul" 
    EXEMPTION = "exemption"
    AGRICULTURAL = "agricultural"
    CONSTRUCTION = "construction"
    UTILITY = "utility"

class ViolationType(Enum):
    """FMCSA violation types"""
    HOS_11_HOUR_DRIVING = "hos_11_hour_driving"
    HOS_14_HOUR_WINDOW = "hos_14_hour_window"
    HOS_60_HOUR_7_DAY = "hos_60_hour_7_day"
    HOS_70_HOUR_8_DAY = "hos_70_hour_8_day"
    HOS_10_HOUR_REST = "hos_10_hour_rest"
    HOS_30_MINUTE_BREAK = "hos_30_minute_break"
    FORM_MANNER_MISSING_FIELDS = "form_manner_missing_fields"
    FORM_MANNER_INCOMPLETE_ENTRIES = "form_manner_incomplete_entries"
    FORM_MANNER_ILLEGIBLE = "form_manner_illegible"
    LOG_FALSIFICATION = "log_falsification"
    DISTANCE_CHANGE_WITHOUT_DRIVING_TIME = "distance_change_without_driving_time"
    DRIVING_OFF_DUTY = "driving_off_duty"
    FUEL_OFF_DUTY = "fuel_off_duty"
    PERSONAL_CONVEYANCE_MISUSE = "personal_conveyance_misuse"
    GEOGRAPHIC_IMPLAUSIBLE = "geographic_implausible"
    MISSING_DUTY_STATUS = "missing_duty_status"

class Severity(Enum):
    """Violation severity levels"""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"

@dataclass
class ViolationRule:
    """Defines a specific violation rule"""
    violation_type: ViolationType
    description: str
    severity: Severity
    penalty_range: tuple  # (min, max) penalty amounts
    cfr_section: str
    applicable_driver_types: Set[DriverType]
    threshold_values: Dict[str, float] = None
    
    def __post_init__(self):
        if self.threshold_values is None:
            self.threshold_values = {}

@dataclass
class DriverClassification:
    """Driver classification with applicable rules"""
    driver_type: DriverType
    name: str
    description: str
    applicable_violations: Set[ViolationType]
    hos_limits: Dict[str, float]
    exemptions: List[str] = None
    
    def __post_init__(self):
        if self.exemptions is None:
            self.exemptions = []

class DriverClassificationSystem:
    """Manages driver classifications and violation rules"""
    
    def __init__(self):
        self.classifications = self._initialize_classifications()
        self.violation_rules = self._initialize_violation_rules()
    
    def _initialize_classifications(self) -> Dict[DriverType, DriverClassification]:
        """Initialize driver classifications with their specific rules"""
        
        # Common violation types for most drivers
        common_violations = {
            ViolationType.FORM_MANNER_MISSING_FIELDS,
            ViolationType.FORM_MANNER_INCOMPLETE_ENTRIES,
            ViolationType.FORM_MANNER_ILLEGIBLE,
            ViolationType.LOG_FALSIFICATION,
            ViolationType.DISTANCE_CHANGE_WITHOUT_DRIVING_TIME,
            ViolationType.DRIVING_OFF_DUTY,
            ViolationType.FUEL_OFF_DUTY,
            ViolationType.PERSONAL_CONVEYANCE_MISUSE,
            ViolationType.GEOGRAPHIC_IMPLAUSIBLE,
            ViolationType.MISSING_DUTY_STATUS
        }
        
        # HOS violations for drivers subject to full HOS rules
        full_hos_violations = common_violations | {
            ViolationType.HOS_11_HOUR_DRIVING,
            ViolationType.HOS_14_HOUR_WINDOW,
            ViolationType.HOS_60_HOUR_7_DAY,
            ViolationType.HOS_70_HOUR_8_DAY,
            ViolationType.HOS_10_HOUR_REST,
            ViolationType.HOS_30_MINUTE_BREAK
        }
        
        return {
            DriverType.LONG_HAUL: DriverClassification(
                driver_type=DriverType.LONG_HAUL,
                name="Long-Haul Driver",
                description="Drivers operating beyond 150 air-mile radius",
                applicable_violations=full_hos_violations,
                hos_limits={
                    "max_driving_hours": 11.0,
                    "max_on_duty_hours": 14.0,
                    "min_rest_hours": 10.0,
                    "max_60_7_hours": 60.0,
                    "max_70_8_hours": 70.0,
                    "required_break_minutes": 30.0
                }
            ),
            
            DriverType.SHORT_HAUL: DriverClassification(
                driver_type=DriverType.SHORT_HAUL,
                name="Short-Haul Driver",
                description="Drivers operating within 150 air-mile radius",
                applicable_violations=common_violations | {
                    ViolationType.HOS_11_HOUR_DRIVING,
                    ViolationType.HOS_14_HOUR_WINDOW,
                    ViolationType.HOS_60_HOUR_7_DAY,
                    ViolationType.HOS_70_HOUR_8_DAY
                },
                hos_limits={
                    "max_driving_hours": 11.0,
                    "max_on_duty_hours": 12.0,  # Different for short-haul
                    "min_rest_hours": 10.0,
                    "max_60_7_hours": 60.0,
                    "max_70_8_hours": 70.0,
                    "return_to_base_hours": 12.0  # Must return within 12 hours
                },
                exemptions=["No ELD requirement if within 100 air-mile radius"]
            ),
            
            DriverType.AGRICULTURAL: DriverClassification(
                driver_type=DriverType.AGRICULTURAL,
                name="Agricultural Driver",
                description="Drivers transporting agricultural commodities",
                applicable_violations=common_violations | {
                    ViolationType.HOS_11_HOUR_DRIVING,
                    ViolationType.HOS_14_HOUR_WINDOW
                },
                hos_limits={
                    "max_driving_hours": 11.0,
                    "max_on_duty_hours": 14.0,
                    "seasonal_exemption_radius": 150.0  # miles
                },
                exemptions=[
                    "150 air-mile radius exemption during planting/harvesting",
                    "Relaxed HOS during seasonal operations"
                ]
            ),
            
            DriverType.CONSTRUCTION: DriverClassification(
                driver_type=DriverType.CONSTRUCTION,
                name="Construction Driver",
                description="Drivers in construction operations",
                applicable_violations=common_violations | {
                    ViolationType.HOS_11_HOUR_DRIVING,
                    ViolationType.HOS_14_HOUR_WINDOW,
                    ViolationType.HOS_60_HOUR_7_DAY,
                    ViolationType.HOS_70_HOUR_8_DAY
                },
                hos_limits={
                    "max_driving_hours": 11.0,
                    "max_on_duty_hours": 14.0,
                    "min_rest_hours": 10.0,
                    "max_60_7_hours": 60.0,
                    "max_70_8_hours": 70.0
                },
                exemptions=["Utility service vehicle exemptions may apply"]
            ),
            
            DriverType.EXEMPTION: DriverClassification(
                driver_type=DriverType.EXEMPTION,
                name="Exemption Driver",
                description="Drivers operating under specific exemptions",
                applicable_violations=common_violations,  # Minimal violations
                hos_limits={},  # Varies by exemption type
                exemptions=["Varies by specific exemption granted"]
            )
        }
    
    def _initialize_violation_rules(self) -> Dict[ViolationType, ViolationRule]:
        """Initialize violation rules with penalties and thresholds"""
        
        return {
            ViolationType.HOS_11_HOUR_DRIVING: ViolationRule(
                violation_type=ViolationType.HOS_11_HOUR_DRIVING,
                description="Driving more than 11 hours after 10 consecutive hours off duty",
                severity=Severity.CRITICAL,
                penalty_range=(1100, 2750),
                cfr_section="49 CFR 395.3(a)(1)",
                applicable_driver_types={DriverType.LONG_HAUL, DriverType.SHORT_HAUL, DriverType.AGRICULTURAL, DriverType.CONSTRUCTION},
                threshold_values={"max_hours": 11.0}
            ),
            
            ViolationType.HOS_14_HOUR_WINDOW: ViolationRule(
                violation_type=ViolationType.HOS_14_HOUR_WINDOW,
                description="Driving beyond 14th consecutive hour after coming on duty",
                severity=Severity.CRITICAL,
                penalty_range=(1100, 2750),
                cfr_section="49 CFR 395.3(a)(2)",
                applicable_driver_types={DriverType.LONG_HAUL, DriverType.AGRICULTURAL, DriverType.CONSTRUCTION},
                threshold_values={"max_hours": 14.0}
            ),
            
            ViolationType.HOS_60_HOUR_7_DAY: ViolationRule(
                violation_type=ViolationType.HOS_60_HOUR_7_DAY,
                description="Driving after 60 hours on duty in 7 consecutive days",
                severity=Severity.CRITICAL,
                penalty_range=(1375, 2750),
                cfr_section="49 CFR 395.3(b)(1)",
                applicable_driver_types={DriverType.LONG_HAUL, DriverType.SHORT_HAUL, DriverType.AGRICULTURAL, DriverType.CONSTRUCTION},
                threshold_values={"max_hours": 60.0, "period_days": 7}
            ),
            
            ViolationType.HOS_70_HOUR_8_DAY: ViolationRule(
                violation_type=ViolationType.HOS_70_HOUR_8_DAY,
                description="Driving after 70 hours on duty in 8 consecutive days",
                severity=Severity.CRITICAL,
                penalty_range=(1375, 2750),
                cfr_section="49 CFR 395.3(b)(1)",
                applicable_driver_types={DriverType.LONG_HAUL, DriverType.SHORT_HAUL, DriverType.AGRICULTURAL, DriverType.CONSTRUCTION},
                threshold_values={"max_hours": 70.0, "period_days": 8}
            ),
            
            ViolationType.HOS_10_HOUR_REST: ViolationRule(
                violation_type=ViolationType.HOS_10_HOUR_REST,
                description="Driving without 10 consecutive hours off duty",
                severity=Severity.MAJOR,
                penalty_range=(825, 2200),
                cfr_section="49 CFR 395.3(a)(1)",
                applicable_driver_types={DriverType.LONG_HAUL, DriverType.SHORT_HAUL, DriverType.AGRICULTURAL, DriverType.CONSTRUCTION},
                threshold_values={"min_rest_hours": 10.0}
            ),
            
            ViolationType.HOS_30_MINUTE_BREAK: ViolationRule(
                violation_type=ViolationType.HOS_30_MINUTE_BREAK,
                description="Driving without required 30-minute break",
                severity=Severity.MAJOR,
                penalty_range=(550, 1375),
                cfr_section="49 CFR 395.3(a)(3)(ii)",
                applicable_driver_types={DriverType.LONG_HAUL},
                threshold_values={"required_break_minutes": 30.0, "driving_hours_before_break": 8.0}
            ),
            
            ViolationType.FORM_MANNER_MISSING_FIELDS: ViolationRule(
                violation_type=ViolationType.FORM_MANNER_MISSING_FIELDS,
                description="Missing required fields in driver log",
                severity=Severity.MINOR,
                penalty_range=(275, 825),
                cfr_section="49 CFR 395.8(e)",
                applicable_driver_types=set(DriverType)  # All driver types
            ),
            
            ViolationType.FORM_MANNER_INCOMPLETE_ENTRIES: ViolationRule(
                violation_type=ViolationType.FORM_MANNER_INCOMPLETE_ENTRIES,
                description="Incomplete entries in driver log",
                severity=Severity.MINOR,
                penalty_range=(275, 825),
                cfr_section="49 CFR 395.8(e)",
                applicable_driver_types=set(DriverType)
            ),
            
            ViolationType.LOG_FALSIFICATION: ViolationRule(
                violation_type=ViolationType.LOG_FALSIFICATION,
                description="Falsification of driver log records",
                severity=Severity.CRITICAL,
                penalty_range=(2750, 11000),
                cfr_section="49 CFR 395.8(e)",
                applicable_driver_types=set(DriverType)
            ),
            
            ViolationType.DISTANCE_CHANGE_WITHOUT_DRIVING_TIME: ViolationRule(
                violation_type=ViolationType.DISTANCE_CHANGE_WITHOUT_DRIVING_TIME,
                description="Distance/Mileage change without corresponding driving time",
                severity=Severity.MAJOR,
                penalty_range=(1100, 2750),
                cfr_section="49 CFR 395.8(e)",
                applicable_driver_types=set(DriverType)
            ),
            
            ViolationType.DRIVING_OFF_DUTY: ViolationRule(
                violation_type=ViolationType.DRIVING_OFF_DUTY,
                description="Driving while marked as off duty",
                severity=Severity.MAJOR,
                penalty_range=(1100, 2750),
                cfr_section="49 CFR 395.8(e)",
                applicable_driver_types=set(DriverType)
            ),
            
            ViolationType.FUEL_OFF_DUTY: ViolationRule(
                violation_type=ViolationType.FUEL_OFF_DUTY,
                description="Fuel transaction without corresponding on-duty time",
                severity=Severity.MAJOR,
                penalty_range=(825, 2200),
                cfr_section="49 CFR 395.2",
                applicable_driver_types=set(DriverType)
            ),
            
            ViolationType.PERSONAL_CONVEYANCE_MISUSE: ViolationRule(
                violation_type=ViolationType.PERSONAL_CONVEYANCE_MISUSE,
                description="Misuse of personal conveyance designation",
                severity=Severity.MAJOR,
                penalty_range=(1100, 2750),
                cfr_section="49 CFR 395.8(e)",
                applicable_driver_types=set(DriverType)
            ),
            
            ViolationType.GEOGRAPHIC_IMPLAUSIBLE: ViolationRule(
                violation_type=ViolationType.GEOGRAPHIC_IMPLAUSIBLE,
                description="Geographically implausible movement between locations",
                severity=Severity.MAJOR,
                penalty_range=(825, 2200),
                cfr_section="49 CFR 395.8(e)",
                applicable_driver_types=set(DriverType)
            ),
            
            ViolationType.MISSING_DUTY_STATUS: ViolationRule(
                violation_type=ViolationType.MISSING_DUTY_STATUS,
                description="No record of duty status for logged time",
                severity=Severity.MINOR,
                penalty_range=(275, 825),
                cfr_section="49 CFR 395.8(e)",
                applicable_driver_types=set(DriverType)
            )
        }
    
    def get_classification(self, driver_type: str) -> Optional[DriverClassification]:
        """Get driver classification by type string"""
        try:
            # Normalize the driver type string
            normalized = driver_type.lower().replace('-', '_').replace(' ', '_')
            driver_enum = DriverType(normalized)
            return self.classifications.get(driver_enum)
        except ValueError:
            print(f"[WARNING] Unknown driver type '{driver_type}', available types: {[dt.value for dt in DriverType]}")
            # Return long-haul as default
            return self.classifications.get(DriverType.LONG_HAUL)
    
    def get_applicable_violations(self, driver_type: str) -> Set[ViolationType]:
        """Get applicable violations for a driver type"""
        classification = self.get_classification(driver_type)
        if classification:
            return classification.applicable_violations
        return set()
    
    def get_violation_rule(self, violation_type: ViolationType) -> Optional[ViolationRule]:
        """Get violation rule by type"""
        return self.violation_rules.get(violation_type)
    
    def is_violation_applicable(self, violation_type: ViolationType, driver_type: str) -> bool:
        """Check if a violation type applies to a driver type"""
        applicable_violations = self.get_applicable_violations(driver_type)
        return violation_type in applicable_violations
    
    def get_penalty_range(self, violation_type: ViolationType) -> tuple:
        """Get penalty range for a violation type"""
        rule = self.get_violation_rule(violation_type)
        return rule.penalty_range if rule else (0, 0)
    
    def get_hos_limits(self, driver_type: str) -> Dict[str, float]:
        """Get HOS limits for a driver type"""
        classification = self.get_classification(driver_type)
        return classification.hos_limits if classification else {}
    
    def export_config(self, file_path: str):
        """Export configuration to JSON file"""
        config = {
            'classifications': {},
            'violation_rules': {}
        }
        
        # Export classifications
        for driver_type, classification in self.classifications.items():
            config['classifications'][driver_type.value] = {
                'name': classification.name,
                'description': classification.description,
                'applicable_violations': [v.value for v in classification.applicable_violations],
                'hos_limits': classification.hos_limits,
                'exemptions': classification.exemptions
            }
        
        # Export violation rules
        for violation_type, rule in self.violation_rules.items():
            config['violation_rules'][violation_type.value] = {
                'description': rule.description,
                'severity': rule.severity.value,
                'penalty_range': rule.penalty_range,
                'cfr_section': rule.cfr_section,
                'applicable_driver_types': [dt.value for dt in rule.applicable_driver_types],
                'threshold_values': rule.threshold_values
            }
        
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def import_config(self, file_path: str):
        """Import configuration from JSON file"""
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        # This would rebuild the classifications and rules from the config
        # Implementation would depend on specific requirements
        pass
    
    def get_supported_driver_types(self) -> List[str]:
        """Get list of supported driver types"""
        return [dt.value for dt in self.classifications.keys()]
    
    def get_driver_type_info(self, driver_type: str) -> Dict:
        """Get information about a driver type"""
        classification = self.get_classification(driver_type)
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
        return self.get_classification(driver_type) is not None

# Global instance
driver_classification_system = DriverClassificationSystem()
