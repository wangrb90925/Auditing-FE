from datetime import datetime, timedelta
import re
from dateutil import parser

class FMCSARules:
    def __init__(self):
        self.violations = []
        self.violation_keys = set()  # Track unique violations to prevent duplicates
        
        # FMCSA HOS Rules
        self.hos_rules = {
            'max_driving_hours': 11,  # Maximum driving hours per day
            'max_on_duty_hours': 14,  # Maximum on-duty hours per day
            'required_off_duty': 10,   # Required consecutive off-duty hours
            'max_60_hour_week': 60,    # Maximum hours in 7 days
            'max_70_hour_week': 70     # Maximum hours in 8 days
        }
    
    def _add_violation(self, violation_data):
        """Add a violation with deduplication logic"""
        # Create a unique key for this violation type and date
        violation_key = f"{violation_data['type']}_{violation_data.get('date', 'unknown')}"
        
        # For certain violation types, also check description to prevent duplicates
        if violation_data['type'] in ['HOS_INVALID_STATUS_TRANSITION', 'FORM_MANNER_MISSING_DUTY_STATUS']:
            # These violations can occur multiple times per day, so use a more specific key
            description_key = violation_data.get('description', '')[:50]  # First 50 chars of description
            violation_key = f"{violation_data['type']}_{violation_data.get('date', 'unknown')}_{description_key}"
        
        # If this is a duplicate violation type for the same date/description, don't add it
        if violation_key in self.violation_keys:
            return
        
        # Add to tracking set and violations list
        self.violation_keys.add(violation_key)
        self.violations.append(violation_data)
    
    def analyze_compliance(self, extracted_data, driver_type):
        """Analyze compliance with FMCSA rules"""
        self.violations = []
        self.violation_keys = set()  # Reset violation tracking
        
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
        
        # Process weekly summaries
        weekly_summaries = extracted_data.get('weekly_summaries', [])
        for summary_data in weekly_summaries:
            self._analyze_weekly_summary_compliance(summary_data)
        
        # Check for log falsification
        if driver_logs:
            self.check_log_falsification(driver_logs[0])
        
        # Check for implausible behavior
        if driver_logs and bills_of_lading:
            self.check_geographic_implausibility(driver_logs[0], bills_of_lading[0] if bills_of_lading else None)
        
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
        
        # Check for multi-day violations (60/70 hour rules)
        self._check_multi_day_compliance(daily_entries, driver_type)
        
        # Check for form and manner violations
        self._check_form_manner_violations(log_data)
        
        # Check for driving while off duty
        self._check_driving_while_off_duty(day_entries)
        
        # Check for missing duty status records
        self._check_missing_duty_status_records(log_data)
    
    def _check_daily_hos_compliance(self, date, entries, driver_type):
        """Check daily HOS compliance with proper time tracking"""
        # Sort entries by time
        sorted_entries = sorted(entries, key=lambda x: x.get('time', '00:00'))
        
        total_driving_hours = 0
        total_on_duty_hours = 0
        off_duty_periods = []
        current_status = None
        status_start_time = None
        
        # Track consecutive hours
        consecutive_on_duty_start = None
        consecutive_off_duty_start = None
        last_duty_status = None
        
        for entry in sorted_entries:
            duty_statuses = entry.get('duty_status', [])
            
            for status_info in duty_statuses:
                status = status_info.get('status', '').lower()
                time_str = entry.get('time', '')
                
                if not time_str:
                    continue
                
                # Check for impossible duty status transitions
                if last_duty_status and not self._is_valid_status_transition(last_duty_status, status):
                    self._add_violation({
                        'date': date,
                        'type': 'HOS_INVALID_STATUS_TRANSITION',
                        'description': f'Invalid duty status transition from {last_duty_status} to {status}',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.8(e)'
                    })
                
                if current_status:
                    # Calculate duration for previous status
                    duration = self._calculate_duration(status_start_time, time_str)
                    
                    if current_status == 'driving':
                        total_driving_hours += duration
                        # Check consecutive on-duty hours
                        if consecutive_on_duty_start:
                            consecutive_on_duty_duration = self._calculate_duration(consecutive_on_duty_start, time_str)
                            if consecutive_on_duty_duration > self.hos_rules['max_on_duty_hours']:
                                self._add_violation({
                                    'date': date,
                                    'type': 'HOS_CONSECUTIVE_ON_DUTY_EXCEEDED',
                                    'description': f'Exceeded 14 consecutive hours on duty: {consecutive_on_duty_duration:.1f} hours',
                                    'severity': 'major',
                                    'penalty': '$2,750',
                                    'section': '395.3(a)(2)'
                                })
                    
                    elif current_status in ['on duty', 'driving']:
                        total_on_duty_hours += duration
                    
                    elif current_status == 'off duty':
                        off_duty_periods.append(duration)
                        # Check if we had 10 consecutive hours off duty
                        if consecutive_off_duty_start:
                            consecutive_off_duty_duration = self._calculate_duration(consecutive_off_duty_start, time_str)
                            if consecutive_off_duty_duration >= self.hos_rules['required_off_duty']:
                                consecutive_on_duty_start = time_str  # Reset consecutive on-duty counter
                
                # Update current status tracking
                if status == 'off duty':
                    if consecutive_off_duty_start is None:
                        consecutive_off_duty_start = time_str
                    consecutive_on_duty_start = None
                elif status in ['on duty', 'driving']:
                    if consecutive_on_duty_start is None:
                        consecutive_on_duty_start = time_str
                    consecutive_off_duty_start = None
                
                current_status = status
                status_start_time = time_str
                last_duty_status = status
        
        # Check driving hours violation
        if total_driving_hours > self.hos_rules['max_driving_hours']:
            self._add_violation({
                'date': date,
                'type': 'HOS_DRIVING_HOURS_EXCEEDED',
                'description': f'Driving hours exceeded 11-hour limit: {total_driving_hours:.1f} hours',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.3(a)(1)'
            })
        
        # Check on-duty hours violation
        if total_on_duty_hours > self.hos_rules['max_on_duty_hours']:
            self._add_violation({
                'date': date,
                'type': 'HOS_ON_DUTY_HOURS_EXCEEDED',
                'description': f'On-duty hours exceeded 14-hour limit: {total_on_duty_hours:.1f} hours',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.3(a)(2)'
            })
        
        # Check required off-duty hours
        if off_duty_periods:
            max_off_duty = max(off_duty_periods)
            if max_off_duty < self.hos_rules['required_off_duty']:
                self._add_violation({
                    'date': date,
                    'type': 'HOS_INSUFFICIENT_OFF_DUTY',
                    'description': f'Insufficient off-duty time: {max_off_duty:.1f} hours (required 10)',
                    'severity': 'major',
                    'penalty': '$2,750',
                    'section': '395.3(a)(1)'
                })
    
    def _is_valid_status_transition(self, from_status, to_status):
        """Check if duty status transition is valid"""
        valid_transitions = {
            'off duty': ['on duty', 'driving'],
            'on duty': ['driving', 'off duty'],
            'driving': ['on duty', 'off duty']
        }
        
        return to_status in valid_transitions.get(from_status, [])
    
    def _check_multi_day_compliance(self, daily_entries, driver_type):
        """Check multi-day HOS compliance (60/70 hour rules)"""
        dates = sorted(daily_entries.keys())
        if len(dates) < 7:
            return
        
        # Check 60-hour rule (7 days)
        for i in range(len(dates) - 6):
            week_dates = dates[i:i+7]
            total_week_hours = 0
            
            for date in week_dates:
                entries = daily_entries[date]
                day_hours = self._calculate_total_day_hours(entries)
                total_week_hours += day_hours
            
            if total_week_hours > self.hos_rules['max_60_hour_week']:
                self._add_violation({
                    'date': week_dates[-1],
                    'type': 'HOS_60_HOUR_RULE_VIOLATION',
                    'description': f'60-hour rule violation: {total_week_hours:.1f} hours in 7 days',
                    'severity': 'major',
                    'penalty': '$2,750',
                    'section': '395.3(b)(1)'
                })
        
        # Check 70-hour rule (8 days)
        if len(dates) >= 8:
            for i in range(len(dates) - 7):
                week_dates = dates[i:i+8]
                total_week_hours = 0
                
                for date in week_dates:
                    entries = daily_entries[date]
                    day_hours = self._calculate_total_day_hours(entries)
                    total_week_hours += day_hours
                
                if total_week_hours > self.hos_rules['max_70_hour_week']:
                    self._add_violation({
                        'date': week_dates[-1],
                        'type': 'HOS_70_HOUR_RULE_VIOLATION',
                        'description': f'70-hour rule violation: {total_week_hours:.1f} hours in 8 days',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.3(b)(2)'
                    })
    
    def _check_missing_duty_status_records(self, log_data):
        """Check for missing duty status records for logged time"""
        entries = log_data.get('entries', [])
        
        for entry in entries:
            duty_statuses = entry.get('duty_status', [])
            time_str = entry.get('time', '')
            
            # Check if time is logged but no duty status is recorded
            if time_str and not duty_statuses:
                self._add_violation({
                    'date': entry.get('date', ''),
                    'type': 'HOS_MISSING_DUTY_STATUS',
                    'description': f'No duty status recorded for logged time: {time_str}',
                    'severity': 'medium',
                    'penalty': '$1,000',
                    'section': '395.8(e)'
                })
            
            # Check for incomplete duty status information
            for status_info in duty_statuses:
                status = status_info.get('status', '')
                if not status:
                    self._add_violation({
                        'date': entry.get('date', ''),
                        'type': 'HOS_INCOMPLETE_DUTY_STATUS',
                        'description': f'Incomplete duty status information at {time_str}',
                        'severity': 'minor',
                        'penalty': '$500',
                        'section': '395.8(e)'
                    })
    
    def _check_form_manner_violations(self, log_data):
        """Check for form and manner violations"""
        entries = log_data.get('entries', [])
        
        for entry in entries:
            # Check for missing required fields
            if not entry.get('date'):
                self._add_violation({
                    'date': '',
                    'type': 'FORM_MANNER_MISSING_DATE',
                    'description': 'Missing date in driver log entry',
                    'severity': 'minor',
                    'penalty': '$1,000',
                    'section': '395.8(e)'
                })
            
            duty_statuses = entry.get('duty_status', [])
            if not duty_statuses:
                self._add_violation({
                    'date': entry.get('date', ''),
                    'type': 'FORM_MANNER_MISSING_DUTY_STATUS',
                    'description': 'Missing duty status in driver log entry',
                    'severity': 'minor',
                    'penalty': '$1,000',
                    'section': '395.8(e)'
                })
            
            # Check for missing duration fields
            if not entry.get('time'):
                self._add_violation({
                    'date': entry.get('date', ''),
                    'type': 'FORM_MANNER_MISSING_TIME',
                    'description': 'Missing time in driver log entry',
                    'severity': 'minor',
                    'penalty': '$1,000',
                    'section': '395.8(e)'
                })
            
            # Check for missing location information
            if not entry.get('location'):
                self._add_violation({
                    'date': entry.get('date', ''),
                    'type': 'FORM_MANNER_MISSING_LOCATION',
                    'description': 'Missing location information in driver log entry',
                    'severity': 'minor',
                    'penalty': '$500',
                    'section': '395.8(e)'
                })
    
    def _check_driving_while_off_duty(self, entries):
        """Check for driving while marked off duty"""
        for entry in entries:
            duty_statuses = entry.get('duty_status', [])
            
            for status_info in duty_statuses:
                status = status_info.get('status', '').lower()
                if status == 'driving':
                    # Check if there's a previous off-duty entry
                    # This is a simplified check - in reality, you'd need to track the sequence
                    pass
    
    def _analyze_fuel_receipt_compliance(self, receipt_data):
        """Analyze fuel receipt compliance"""
        data = receipt_data.get('data', {})
        
        # Check for fueling while off duty
        if data.get('driver_status', '').upper() == 'OFF DUTY':
            self._add_violation({
                'date': data.get('date', ''),
                'type': 'FUEL_WHILE_OFF_DUTY',
                'description': f'Fueling during off-duty hours at {data.get("time", "")}',
                'severity': 'medium',
                'penalty': '$1,000',
                'section': '395.3(a)(1)'
            })
        
        # Check for HOS conflicts in fuel receipts
        if data.get('violation', '').upper() == 'YES':
            self._add_violation({
                'date': data.get('date', ''),
                'type': 'HOS_CONFLICT',
                'description': f'HOS conflict detected in fuel receipt at {data.get("time", "")}',
                'severity': 'medium',
                'penalty': '$1,000',
                'section': '395.3(a)(1)'
            })
        
        # Check for missing fuel receipt information
        if not data.get('fuel_amount') or not data.get('fuel_cost'):
            self._add_violation({
                'date': data.get('date', ''),
                'type': 'FUEL_MISSING_INFORMATION',
                'description': 'Missing fuel amount or cost information',
                'severity': 'minor',
                'penalty': '$500',
                'section': '373.101'
            })
    
    def _analyze_bol_compliance(self, bol_data):
        """Analyze Bill of Lading compliance"""
        data = bol_data.get('data', {})
        
        # Check for missing required BOL information
        if not data.get('bol_number'):
            self._add_violation({
                'date': data.get('date', ''),
                'type': 'BOL_MISSING_NUMBER',
                'description': 'Missing Bill of Lading number',
                'severity': 'minor',
                'penalty': '$500',
                'section': '373.101'
            })
        
        if not data.get('origin') or not data.get('destination'):
            self._add_violation({
                'date': data.get('date', ''),
                'type': 'BOL_MISSING_ROUTE_INFO',
                'description': 'Missing origin or destination information',
                'severity': 'minor',
                'penalty': '$500',
                'section': '373.101'
            })
        
        # Check for missing cargo information
        if not data.get('cargo_description'):
            self._add_violation({
                'date': data.get('date', ''),
                'type': 'BOL_MISSING_CARGO_INFO',
                'description': 'Missing cargo description information',
                'severity': 'minor',
                'penalty': '$500',
                'section': '373.101'
            })
    
    def _analyze_weekly_summary_compliance(self, summary_data):
        """Analyze weekly summary compliance"""
        data = summary_data.get('data', {})
        
        # Check for 60-hour rule violations
        if data.get('cumulative_week_hours', 0) > self.hos_rules['max_60_hour_week']:
            self._add_violation({
                'date': data.get('date', ''),
                'type': 'HOS_60_HOUR_RULE_VIOLATION',
                'description': f'60-hour rule violation: {data.get("cumulative_week_hours", 0):.1f} hours in 7 days',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.3(b)(1)'
            })
        
        # Check for daily driving limit violations
        if data.get('driving_hours', 0) > self.hos_rules['max_driving_hours']:
            self._add_violation({
                'date': data.get('date', ''),
                'type': 'HOS_DAILY_DRIVING_LIMIT',
                'description': f'Daily driving limit exceeded: {data.get("driving_hours", 0):.1f} hours',
                'severity': 'medium',
                'penalty': '$2,750',
                'section': '395.3(a)(1)'
            })
        
        # Check for missing weekly summary information
        if not data.get('total_miles') or not data.get('total_hours'):
            self._add_violation({
                'date': data.get('date', ''),
                'type': 'WEEKLY_SUMMARY_MISSING_INFO',
                'description': 'Missing total miles or hours in weekly summary',
                'severity': 'minor',
                'penalty': '$500',
                'section': '395.8(e)'
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
                
                # Add actual time calculation if available
                if entry.get('duration'):
                    total_hours += entry.get('duration', 0)
        
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
                self._add_violation({
                    'date': entry.get('date', ''),
                    'type': 'LOG_FALSIFICATION_DUPLICATE_TIMES',
                    'description': 'Duplicate time entries detected - possible falsification',
                    'severity': 'critical',
                    'penalty': '$5,000',
                    'section': '395.8(e)'
                })
            
            # Check for impossible duty status sequences
            if len(duty_statuses) > 1:
                for i in range(len(duty_statuses) - 1):
                    current_status = duty_statuses[i].get('status', '').lower()
                    next_status = duty_statuses[i + 1].get('status', '').lower()
                    
                    # Check for impossible transitions (e.g., driving -> off duty without on duty in between)
                    if current_status == 'driving' and next_status == 'off duty':
                        self._add_violation({
                            'date': entry.get('date', ''),
                            'type': 'LOG_FALSIFICATION_IMPOSSIBLE_TRANSITION',
                            'description': 'Impossible duty status transition: driving directly to off duty',
                            'severity': 'critical',
                            'penalty': '$5,000',
                            'section': '395.8(e)'
                        })
            
            # Check for suspicious time patterns
            if len(times) >= 2:
                for i in range(len(times) - 1):
                    time_diff = self._calculate_duration(times[i], times[i + 1])
                    if time_diff < 0.1:  # Less than 6 minutes between entries
                        self._add_violation({
                            'date': entry.get('date', ''),
                            'type': 'LOG_FALSIFICATION_SUSPICIOUS_TIMING',
                            'description': f'Suspicious timing between entries: {time_diff:.2f} hours',
                            'severity': 'major',
                            'penalty': '$2,750',
                            'section': '395.8(e)'
                        })
    
    def check_geographic_implausibility(self, log_data, bol_data):
        """Check for geographically implausible movements"""
        log_entries = log_data.get('entries', [])
        bol_info = bol_data.get('data', {}) if bol_data else {}
        
        # Check for "teleporting" - rapid location changes
        locations = []
        for entry in log_entries:
            location = entry.get('location', '')
            time = entry.get('time', '')
            if location and time:
                locations.append({'location': location, 'time': time})
        
        # Check for rapid location changes (simplified check)
        if len(locations) >= 2:
            for i in range(len(locations) - 1):
                current = locations[i]
                next_loc = locations[i + 1]
                
                # Calculate time difference
                time_diff = self._calculate_duration(current['time'], next_loc['time'])
                
                # If locations are very different and time difference is small, flag as suspicious
                if (current['location'] != next_loc['location'] and 
                    time_diff < 0.5):  # Less than 30 minutes
                    self._add_violation({
                        'date': log_data.get('date', ''),
                        'type': 'GEOGRAPHIC_IMPLAUSIBILITY',
                        'description': f'Rapid location change from {current["location"]} to {next_loc["location"]} in {time_diff:.1f} hours',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.8(e)'
                    })
        
        # Check for location consistency with BOL information
        if bol_info and log_entries:
            bol_origin = bol_info.get('origin', '').lower()
            bol_destination = bol_info.get('destination', '').lower()
            
            log_locations = [entry.get('location', '').lower() for entry in log_entries if entry.get('location')]
            
            # Check if log locations are consistent with BOL route
            if bol_origin and bol_destination:
                if bol_origin not in log_locations and bol_destination not in log_locations:
                    self._add_violation({
                        'date': log_data.get('date', ''),
                        'type': 'GEOGRAPHIC_ROUTE_INCONSISTENCY',
                        'description': f'Log locations inconsistent with BOL route: {bol_origin} to {bol_destination}',
                        'severity': 'medium',
                        'penalty': '$1,000',
                        'section': '395.8(e)'
                    })
    
    def get_violation_summary(self):
        """Get a summary of violations by type and severity"""
        if not self.violations:
            return {}
        
        summary = {
            'total_violations': len(self.violations),
            'by_type': {},
            'by_severity': {},
            'by_date': {}
        }
        
        for violation in self.violations:
            # Count by type
            violation_type = violation.get('type', 'UNKNOWN')
            if violation_type not in summary['by_type']:
                summary['by_type'][violation_type] = 0
            summary['by_type'][violation_type] += 1
            
            # Count by severity
            severity = violation.get('severity', 'unknown')
            if severity not in summary['by_severity']:
                summary['by_severity'][severity] = 0
            summary['by_severity'][severity] += 1
            
            # Count by date
            date = violation.get('date', 'unknown')
            if date not in summary['by_date']:
                summary['by_date'][date] = 0
            summary['by_date'][date] += 1
        
        return summary
    
    def get_consolidated_violations(self):
        """Get violations consolidated by type to reduce repetition"""
        if not self.violations:
            return []
        
        consolidated = {}
        
        for violation in self.violations:
            violation_type = violation.get('type', 'UNKNOWN')
            date = violation.get('date', 'unknown')
            key = f"{violation_type}_{date}"
            
            if key not in consolidated:
                consolidated[key] = {
                    'type': violation_type,
                    'date': date,
                    'description': violation.get('description', ''),
                    'severity': violation.get('severity', ''),
                    'penalty': violation.get('penalty', ''),
                    'section': violation.get('section', ''),
                    'count': 1,
                    'examples': [violation]
                }
            else:
                consolidated[key]['count'] += 1
                consolidated[key]['examples'].append(violation)
        
        # Convert to list and add count information to description
        result = []
        for key, violation_info in consolidated.items():
            if violation_info['count'] > 1:
                violation_info['description'] = f"{violation_info['description']} (Occurred {violation_info['count']} times)"
            
            # Remove examples to keep output clean
            del violation_info['examples']
            result.append(violation_info)
        
        return result 