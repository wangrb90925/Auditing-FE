from datetime import datetime, timedelta
import re
from dateutil import parser

class FMCSARules:
    def __init__(self):
        self.violations = []
        
        # FMCSA HOS Rules
        self.hos_rules = {
            'max_driving_hours': 11,  # Maximum driving hours per day
            'max_on_duty_hours': 14,  # Maximum on-duty hours per day
            'required_off_duty': 10,   # Required consecutive off-duty hours
            'max_60_hour_week': 60,    # Maximum hours in 7 days
            'max_70_hour_week': 70     # Maximum hours in 8 days
        }
    
    def analyze_compliance(self, extracted_data, driver_type):
        """Analyze compliance with FMCSA rules"""
        self.violations = []
        
        # Process driver logs
        driver_logs = extracted_data.get('driver_logs', [])
        for log_data in driver_logs:
            if log_data.get('type') == 'driver_log':
                self._analyze_driver_log_compliance(log_data, driver_type)
        
        # Process fuel receipts
        fuel_receipts = extracted_data.get('fuel_receipts', [])
        for receipt_data in fuel_receipts:
            self._analyze_fuel_receipt_compliance(receipt_data)
        
        # Process Bills of Lading
        bills_of_lading = extracted_data.get('bills_of_lading', [])
        for bol_data in bills_of_lading:
            self._analyze_bol_compliance(bol_data)
        
        return self.violations
    
    def _analyze_driver_log_compliance(self, log_data, driver_type):
        """Analyze driver log compliance with HOS rules"""
        entries = log_data.get('entries', [])
        
        if not entries:
            return
        
        # Group entries by date
        daily_entries = {}
        for entry in entries:
            date = entry.get('date', '')
            if date:
                if date not in daily_entries:
                    daily_entries[date] = []
                daily_entries[date].append(entry)
        
        # Analyze each day for violations
        for date, day_entries in daily_entries.items():
            self._check_daily_hos_compliance(date, day_entries, driver_type)
        
        # Check for multi-day violations
        self._check_multi_day_compliance(daily_entries, driver_type)
        
        # Check for form and manner violations
        self._check_form_manner_violations(log_data)
    
    def _check_daily_hos_compliance(self, date, entries, driver_type):
        """Check daily HOS compliance"""
        total_driving_hours = 0
        total_on_duty_hours = 0
        off_duty_periods = []
        current_status = None
        status_start_time = None
        
        for entry in entries:
            duty_statuses = entry.get('duty_status', [])
            
            for status_info in duty_statuses:
                status = status_info.get('status', '').lower()
                line = status_info.get('line', '')
                
                # Extract time from line
                time_match = re.search(r'(\d{1,2}:\d{2})', line)
                if time_match:
                    time_str = time_match.group(1)
                    
                    if current_status:
                        # Calculate duration for previous status
                        duration = self._calculate_duration(status_start_time, time_str)
                        
                        if current_status == 'driving':
                            total_driving_hours += duration
                        elif current_status in ['on duty', 'driving']:
                            total_on_duty_hours += duration
                        elif current_status == 'off duty':
                            off_duty_periods.append(duration)
                    
                    current_status = status
                    status_start_time = time_str
        
        # Check driving hours violation
        if total_driving_hours > self.hos_rules['max_driving_hours']:
            self.violations.append({
                'date': date,
                'type': 'HOS_DRIVING_HOURS_EXCEEDED',
                'description': f'Driving hours exceeded 11-hour limit: {total_driving_hours} hours',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.3(a)(1)'
            })
        
        # Check on-duty hours violation
        if total_on_duty_hours > self.hos_rules['max_on_duty_hours']:
            self.violations.append({
                'date': date,
                'type': 'HOS_ON_DUTY_HOURS_EXCEEDED',
                'description': f'On-duty hours exceeded 14-hour limit: {total_on_duty_hours} hours',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.3(a)(2)'
            })
        
        # Check required off-duty hours
        if off_duty_periods:
            max_off_duty = max(off_duty_periods)
            if max_off_duty < self.hos_rules['required_off_duty']:
                self.violations.append({
                    'date': date,
                    'type': 'HOS_INSUFFICIENT_OFF_DUTY',
                    'description': f'Insufficient off-duty time: {max_off_duty} hours (required 10)',
                    'severity': 'major',
                    'penalty': '$2,750',
                    'section': '395.3(a)(1)'
                })
    
    def _check_multi_day_compliance(self, daily_entries, driver_type):
        """Check multi-day HOS compliance (60/70 hour rules)"""
        # This is a simplified implementation
        # In a real system, you'd need to track hours across multiple days
        
        total_week_hours = 0
        dates = sorted(daily_entries.keys())[:7]  # Last 7 days
        
        for date in dates:
            entries = daily_entries[date]
            day_hours = self._calculate_total_day_hours(entries)
            total_week_hours += day_hours
        
        # Check 60-hour rule
        if total_week_hours > self.hos_rules['max_60_hour_week']:
            self.violations.append({
                'date': dates[-1] if dates else '',
                'type': 'HOS_60_HOUR_RULE_VIOLATION',
                'description': f'60-hour rule violation: {total_week_hours} hours in 7 days',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.3(b)(1)'
            })
    
    def _check_form_manner_violations(self, log_data):
        """Check for form and manner violations"""
        entries = log_data.get('entries', [])
        
        for entry in entries:
            # Check for missing required fields
            if not entry.get('date'):
                self.violations.append({
                    'date': '',
                    'type': 'FORM_MANNER_MISSING_DATE',
                    'description': 'Missing date in driver log entry',
                    'severity': 'minor',
                    'penalty': '$1,000',
                    'section': '395.8(e)'
                })
            
            duty_statuses = entry.get('duty_status', [])
            if not duty_statuses:
                self.violations.append({
                    'date': entry.get('date', ''),
                    'type': 'FORM_MANNER_MISSING_DUTY_STATUS',
                    'description': 'Missing duty status in driver log entry',
                    'severity': 'minor',
                    'penalty': '$1,000',
                    'section': '395.8(e)'
                })
    
    def _analyze_fuel_receipt_compliance(self, receipt_data):
        """Analyze fuel receipt compliance"""
        data = receipt_data.get('data', {})
        
        # Check for fueling while off duty
        # This would require cross-referencing with driver logs
        # For now, we'll add a placeholder check
        
        if data.get('time') and data.get('date'):
            # In a real implementation, you'd check if the driver was marked off duty
            # at the time of fueling
            pass
    
    def _analyze_bol_compliance(self, bol_data):
        """Analyze Bill of Lading compliance"""
        data = bol_data.get('data', {})
        
        # Check for missing required BOL information
        if not data.get('bol_number'):
            self.violations.append({
                'date': data.get('date', ''),
                'type': 'BOL_MISSING_NUMBER',
                'description': 'Missing Bill of Lading number',
                'severity': 'minor',
                'penalty': '$500',
                'section': '373.101'
            })
        
        if not data.get('origin') or not data.get('destination'):
            self.violations.append({
                'date': data.get('date', ''),
                'type': 'BOL_MISSING_ROUTE_INFO',
                'description': 'Missing origin or destination information',
                'severity': 'minor',
                'penalty': '$500',
                'section': '373.101'
            })
    
    def _calculate_duration(self, start_time, end_time):
        """Calculate duration between two time strings"""
        try:
            start = parser.parse(start_time)
            end = parser.parse(end_time)
            
            # Handle overnight periods
            if end < start:
                end += timedelta(days=1)
            
            duration = (end - start).total_seconds() / 3600  # Convert to hours
            return round(duration, 2)
        except:
            return 0
    
    def _calculate_total_day_hours(self, entries):
        """Calculate total hours for a day"""
        total_hours = 0
        
        for entry in entries:
            duty_statuses = entry.get('duty_status', [])
            for status_info in duty_statuses:
                # Simplified calculation - in reality, you'd need proper time tracking
                total_hours += 1  # Placeholder
        
        return total_hours
    
    def check_log_falsification(self, log_data):
        """Check for potential log falsification"""
        entries = log_data.get('entries', [])
        
        for entry in entries:
            duty_statuses = entry.get('duty_status', [])
            
            # Check for impossible time sequences
            times = []
            for status_info in duty_statuses:
                line = status_info.get('line', '')
                time_match = re.search(r'(\d{1,2}:\d{2})', line)
                if time_match:
                    times.append(time_match.group(1))
            
            # Check for duplicate times
            if len(times) != len(set(times)):
                self.violations.append({
                    'date': entry.get('date', ''),
                    'type': 'LOG_FALSIFICATION_DUPLICATE_TIMES',
                    'description': 'Duplicate time entries detected - possible falsification',
                    'severity': 'critical',
                    'penalty': '$5,000',
                    'section': '395.8(e)'
                })
    
    def check_geographic_implausibility(self, log_data, bol_data):
        """Check for geographically implausible movements"""
        # This would require geocoding and distance calculations
        # For now, we'll add a placeholder
        
        log_entries = log_data.get('entries', [])
        bol_info = bol_data.get('data', {}) if bol_data else {}
        
        # In a real implementation, you'd:
        # 1. Extract locations from logs and BOLs
        # 2. Calculate distances and travel times
        # 3. Check if movements are physically possible
        
        pass
    
    def get_violation_summary(self):
        """Get a summary of violations by type"""
        summary = {
            'total_violations': len(self.violations),
            'hos_violations': len([v for v in self.violations if 'HOS' in v.get('type', '')]),
            'form_violations': len([v for v in self.violations if 'FORM' in v.get('type', '')]),
            'falsification_violations': len([v for v in self.violations if 'FALSIFICATION' in v.get('type', '')]),
            'bol_violations': len([v for v in self.violations if 'BOL' in v.get('type', '')]),
            'by_severity': {
                'minor': len([v for v in self.violations if v.get('severity') == 'minor']),
                'major': len([v for v in self.violations if v.get('severity') == 'major']),
                'critical': len([v for v in self.violations if v.get('severity') == 'critical'])
            }
        }
        
        return summary 