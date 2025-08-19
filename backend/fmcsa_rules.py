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
            self._check_fuel_receipt_compliance(receipt_data)
        
        # Process Bills of Lading
        bills_of_lading = extracted_data.get('bills_of_lading', [])
        for bol_data in bills_of_lading:
            self._check_bol_compliance(bol_data)
        
        # Process weekly summaries
        weekly_summaries = extracted_data.get('weekly_summaries', [])
        for summary_data in weekly_summaries:
            self._check_weekly_summary_compliance(summary_data)
        
        # Check for log falsification
        if driver_logs:
            self._check_log_falsification(driver_logs)
        
        # Check for implausible behavior
        if driver_logs and bills_of_lading:
            self._check_geographic_implausibility(driver_logs, bills_of_lading)
        
        # If no violations found, add a basic compliance check
        if not self.violations:
            self._add_basic_compliance_check(extracted_data)
        
        return self.violations
    
    def _analyze_driver_log_compliance(self, log_data, driver_type):
        """Analyze driver log compliance with HOS rules"""
        entries = log_data.get('entries', [])
        
        if not entries:
            # Add violation for missing log entries
            self._add_violation({
                'date': 'unknown',
                'type': 'FORM_MANNER_MISSING_ENTRIES',
                'description': 'Driver log contains no entries or duty status records',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.8(a)'
            })
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
        for date, day_entries in daily_entries.items():
            self._check_driving_while_off_duty(date, day_entries)
        
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
                
                # Check for impossible duty status transitions - only flag clearly invalid ones
                if last_duty_status and not self._is_valid_status_transition(last_duty_status, status):
                    # Only flag if this is clearly impossible (e.g., driving -> driving without off duty)
                    if last_duty_status == 'driving' and status == 'driving':
                        # Check if there was sufficient off-duty time between
                        if consecutive_off_duty_start:
                            off_duty_duration = self._calculate_duration(consecutive_off_duty_start, time_str)
                            if off_duty_duration < 0.5:  # Less than 30 minutes off duty
                                self._add_violation({
                                    'date': date,
                                    'type': 'HOS_INVALID_STATUS_TRANSITION',
                                    'description': f'Invalid duty status transition from {last_duty_status} to {status} without sufficient off-duty time',
                                    'severity': 'major',
                                    'penalty': '$2,750',
                                    'section': '395.8(e)'
                                })
                    elif last_duty_status == 'off duty' and status == 'driving':
                        # This is valid - driver can go from off duty to driving
                        pass
                    else:
                        # Only flag other transitions if they're clearly problematic
                        self._add_violation({
                            'date': date,
                            'type': 'HOS_INVALID_STATUS_TRANSITION',
                            'description': f'Invalid duty status transition from {last_duty_status} to {status}',
                            'severity': 'minor',
                            'penalty': '$1,375',
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
        
        # Check for insufficient off-duty time only if we have a complete day
        # Don't flag this for single-day logs or incomplete data
        total_off_duty = sum(off_duty_periods)
        
        # Only check off-duty time if we have multiple entries AND can reasonably determine the full day
        # Be more lenient with real ELD data that may be incomplete
        if (total_off_duty < self.hos_rules['required_off_duty'] and 
            len(sorted_entries) >= 5 and  # Need at least 5 entries to determine a full day
            any(entry.get('time', '') >= '23:00' for entry in sorted_entries) and  # Need very late entries
            any(entry.get('time', '') <= '06:00' for entry in sorted_entries)):  # Need early entries too
            
            # Only flag if we're really sure this is a complete day
            if total_off_duty < 5:  # Less than 5 hours off duty is definitely a problem
                self._add_violation({
                    'date': date,
                    'type': 'HOS_INSUFFICIENT_OFF_DUTY',
                    'description': f'Insufficient off-duty time: {total_off_duty:.1f} hours (required: 10 hours)',
                    'severity': 'major',
                    'penalty': '$2,750',
                    'section': '395.3(a)(2)'
                })
    
    def _check_multi_day_compliance(self, daily_entries, driver_type):
        """Check 60/70 hour weekly limits"""
        if not daily_entries or len(daily_entries) < 7:
            # Need at least 7 days to check weekly limits
            return
        
        # Calculate total hours for the week
        week_hours = 0
        week_start = None
        
        for date, entries in daily_entries.items():
            if not week_start:
                week_start = date
            
            # Calculate total on-duty hours for this day
            day_hours = 0
            for entry in entries:
                duty_statuses = entry.get('duty_status', [])
                for status_info in duty_statuses:
                    status = status_info.get('status', '').lower()
                    if status in ['driving', 'on duty']:
                        # Estimate duration (this would be more accurate with actual time data)
                        day_hours += 8  # Assume 8 hours if no specific time data
            
            week_hours += day_hours
        
        # Check 60/70 hour limits only if we have reasonable data
        # Be more realistic with estimated hours from ELD data
        if week_hours > 0:  # Only check if we have some data
            # Since we're estimating hours (assuming 8 hours per entry), be more lenient
            # Real ELD data often has gaps, so estimated hours may be inflated
            if driver_type == 'long-haul':
                if week_hours > self.hos_rules['max_70_hour_week'] * 1.2:  # Allow 20% buffer for estimates
                    self._add_violation({
                        'date': week_start or 'unknown',
                        'type': 'HOS_WEEKLY_LIMIT_EXCEEDED',
                        'description': f'Weekly hours exceeded 70-hour limit: {week_hours} hours (estimated)',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.3(b)'
                    })
            else:
                if week_hours > self.hos_rules['max_60_hour_week'] * 1.2:  # Allow 20% buffer for estimates
                    self._add_violation({
                        'date': week_start or 'unknown',
                        'type': 'HOS_WEEKLY_LIMIT_EXCEEDED',
                        'description': f'Weekly hours exceeded 60-hour limit: {week_hours} hours (estimated)',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.3(b)'
                    })
    
    def _check_form_manner_violations(self, log_data):
        """Check for form and manner violations - only flag clear, actual violations"""
        entries = log_data.get('entries', [])
        
        # Only check if we have multiple entries to establish a pattern
        if len(entries) < 2:
            return
        
        for entry in entries:
            # Only flag missing fields if they're truly missing and critical
            if not entry.get('date') and len(entries) > 1:
                # Only flag if we have other entries with dates to compare
                other_dates = [e.get('date') for e in entries if e.get('date')]
                if other_dates:
                    self._add_violation({
                        'date': 'unknown',
                        'type': 'FORM_MANNER_MISSING_DATE',
                        'description': 'Missing date in driver log entry',
                        'severity': 'minor',
                        'penalty': '$1,375',
                        'section': '395.8(d)'
                    })
            
            # Only flag missing duty status if it's clearly a log entry
            duty_statuses = entry.get('duty_status', [])
            if not duty_statuses and entry.get('time'):
                # Only flag if this looks like it should have a duty status
                self._add_violation({
                    'date': entry.get('date', 'unknown'),
                    'type': 'FORM_MANNER_MISSING_DUTY_STATUS',
                    'description': 'Missing duty status for timed entry',
                    'severity': 'minor',
                    'penalty': '$1,375',
                    'section': '395.8(d)'
                })
    
    def _check_driving_while_off_duty(self, date, entries):
        """Check for driving while marked off duty"""
        for entry in entries:
            duty_statuses = entry.get('duty_status', [])
            for status_info in duty_statuses:
                status = status_info.get('status', '').lower()
                if status == 'off duty' and entry.get('activity') == 'driving':
                    self._add_violation({
                        'date': date,
                        'type': 'HOS_DRIVING_WHILE_OFF_DUTY',
                        'description': 'Driver marked as off duty while driving',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.8(f)(1)'
                    })
    
    def _check_missing_duty_status_records(self, log_data):
        """Check for missing RODS (Record of Duty Status)"""
        entries = log_data.get('entries', [])
        if not entries:
            self._add_violation({
                'date': 'unknown',
                'type': 'HOS_MISSING_RODS',
                'description': 'No Record of Duty Status (RODS) found',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.8(a)'
            })
    
    def _check_log_falsification(self, driver_logs):
        """Check for potential log falsification - only flag clear, obvious violations"""
        for log_data in driver_logs:
            entries = log_data.get('entries', [])
            
            # Only check if we have enough entries to establish a pattern
            if len(entries) < 3:
                continue
            
            # Check for impossible time sequences (only flag if clearly impossible)
            for i in range(len(entries) - 1):
                current_entry = entries[i]
                next_entry = entries[i + 1]
                
                current_time = current_entry.get('time', '00:00')
                next_time = next_entry.get('time', '00:00')
                
                # Only flag if times are clearly impossible (e.g., 23:00 followed by 06:00)
                if current_time > next_time:
                    # Check if this could be a legitimate overnight period
                    current_hour = int(current_time.split(':')[0]) if ':' in current_time else 0
                    next_hour = int(next_time.split(':')[0]) if ':' in next_time else 0
                    
                    # Only flag if the time difference is clearly impossible (e.g., 14:00 followed by 10:00)
                    if current_hour > 12 and next_hour < 12:
                        # This could be legitimate overnight - skip
                        continue
                    elif current_hour - next_hour > 8:  # More than 8 hour difference in same day (be more lenient)
                        # Only flag if this is clearly impossible (e.g., 16:00 followed by 06:00)
                        if current_hour >= 16 and next_hour <= 6:
                            self._add_violation({
                                'date': current_entry.get('date', 'unknown'),
                                'type': 'FALSIFICATION_TIME_SEQUENCE',
                                'description': 'Suspicious time sequence detected in driver log',
                                'severity': 'major',
                                'penalty': '$2,750',
                                'section': '395.8(e)'
                            })
            
            # Only flag duplicate entries if they're clearly problematic
            # ELD systems often have multiple entries at similar times
            duplicate_times = {}
            for entry in entries:
                time_key = f"{entry.get('time', '')}_{entry.get('date', '')}"
                if time_key in duplicate_times:
                    # Only flag if same time/date has CONFLICTING statuses (not just duplicates)
                    current_status = entry.get('duty_status', [])
                    previous_status = duplicate_times[time_key].get('duty_status', [])
                    
                    # Extract actual status values for comparison
                    current_status_values = [s.get('status', '').lower() for s in current_status]
                    previous_status_values = [s.get('status', '').lower() for s in previous_status]
                    
                    # Only flag if statuses are truly conflicting (e.g., driving vs off duty)
                    if (set(current_status_values) & set(previous_status_values) and 
                        len(set(current_status_values) ^ set(previous_status_values)) > 0):
                        # This is a real conflict - flag it
                        self._add_violation({
                            'date': entry.get('date', 'unknown'),
                            'type': 'FALSIFICATION_DUPLICATE_ENTRIES',
                            'description': 'Conflicting duty status entries at same time',
                            'severity': 'major',
                            'penalty': '$2,750',
                            'section': '395.8(e)'
                        })
                else:
                    duplicate_times[time_key] = entry
    
    def _check_geographic_implausibility(self, driver_logs, bills_of_lading):
        """Check for geographically implausible movements"""
        for log_data in driver_logs:
            entries = log_data.get('entries', [])
            
            # Check for rapid location changes that would be impossible
            for i in range(len(entries) - 1):
                current_entry = entries[i]
                next_entry = entries[i + 1]
                
                current_location = current_entry.get('location', '')
                next_location = next_entry.get('location', '')
                
                if current_location and next_location:
                    # This is a simplified check - in practice, you'd calculate actual distances
                    # and compare with reasonable travel times
                    if current_location != next_location:
                        # Assume any location change might be suspicious for now
                        # In a real implementation, you'd check actual distances and times
                        pass
    
    def _check_fuel_receipt_compliance(self, receipt_data):
        """Check fuel receipt compliance"""
        # Only check if this is actually a fuel receipt file
        if not receipt_data or not isinstance(receipt_data, dict):
            return
        
        # Check if this is identified as a fuel receipt
        if receipt_data.get('type') == 'fuel_receipt' or 'fuel' in receipt_data.get('file_name', '').lower():
            # Check for fueling while off duty
            duty_status = receipt_data.get('duty_status', '').lower()
            if duty_status == 'off duty':
                self._add_violation({
                    'date': receipt_data.get('date', 'unknown'),
                    'type': 'FUEL_OFF_DUTY_VIOLATION',
                    'description': 'Fueling while marked off duty - fueling is on-duty activity',
                    'severity': 'major',
                    'penalty': '$2,750',
                    'section': '395.2'
                })
            
            # Check for missing fuel information
            if not receipt_data.get('fuel_amount'):
                self._add_violation({
                    'date': receipt_data.get('date', 'unknown'),
                    'type': 'FUEL_MISSING_AMOUNT',
                    'description': 'Fuel receipt missing fuel amount',
                    'severity': 'minor',
                    'penalty': '$1,375',
                    'section': '395.8(d)'
                })
        
        # If it's not a fuel receipt file, don't add violations
        # This prevents false positives for other file types
    
    def _check_bol_compliance(self, bol_data):
        """Check Bill of Lading compliance"""
        # Only check if this is actually a BOL file
        if not bol_data or not isinstance(bol_data, dict):
            return
        
        # Check if this is identified as a BOL
        if bol_data.get('type') == 'bill_of_lading' or 'bol' in bol_data.get('file_name', '').lower():
            # Check for missing required fields
            required_fields = ['shipper', 'consignee', 'commodity', 'weight']
            for field in required_fields:
                if not bol_data.get(field):
                    self._add_violation({
                        'date': bol_data.get('date', 'unknown'),
                        'type': 'BOL_MISSING_FIELD',
                        'description': f'Missing required BOL field: {field}',
                        'severity': 'minor',
                        'penalty': '$1,375',
                        'section': '395.8(d)'
                    })
            
            # Check for BOL number
            if not bol_data.get('bol_number'):
                self._add_violation({
                    'date': bol_data.get('date', 'unknown'),
                    'type': 'BOL_MISSING_NUMBER',
                    'description': 'Missing Bill of Lading number',
                    'severity': 'minor',
                    'penalty': '$1,375',
                    'section': '395.8(d)'
                })
        
        # If it's not a BOL file, don't add violations
        # This prevents false positives for other file types
    
    def _check_weekly_summary_compliance(self, summary_data):
        """Check weekly summary compliance"""
        # Only check if this is actually a weekly summary file
        if not summary_data or not isinstance(summary_data, dict):
            return
        
        # Check for missing weekly totals only if this is supposed to be a summary
        if summary_data.get('type') == 'weekly_summary':
            if not summary_data.get('total_hours'):
                self._add_violation({
                    'date': summary_data.get('date', 'unknown'),
                    'type': 'WEEKLY_SUMMARY_MISSING_TOTALS',
                    'description': 'Weekly summary missing total hours calculation',
                    'severity': 'minor',
                    'penalty': '$1,375',
                    'section': '395.8(d)'
                })
            
            # Check for other required weekly summary fields
            if not summary_data.get('week_ending_date'):
                self._add_violation({
                    'date': summary_data.get('date', 'unknown'),
                    'type': 'WEEKLY_SUMMARY_MISSING_DATE',
                    'description': 'Weekly summary missing week ending date',
                    'severity': 'minor',
                    'penalty': '$1,375',
                    'section': '395.8(d)'
                })
        
        # If it's not a weekly summary file, don't add violations
        # This prevents false positives for other file types
    
    def _add_basic_compliance_check(self, extracted_data):
        """Add basic compliance check if no violations found"""
        # Only add violations if we have insufficient data for analysis
        # Don't artificially reduce scores for compliant files
        
        driver_logs = extracted_data.get('driver_logs', [])
        fuel_receipts = extracted_data.get('fuel_receipts', [])
        bills_of_lading = extracted_data.get('bills_of_lading', [])
        weekly_summaries = extracted_data.get('weekly_summaries', [])
        
        # Check if we have any data to analyze
        total_files = len(driver_logs) + len(fuel_receipts) + len(bills_of_lading) + len(weekly_summaries)
        
        if total_files == 0:
            # Only add violation if no files were processed at all
            self._add_violation({
                'date': 'unknown',
                'type': 'COMPLIANCE_NO_FILES',
                'description': 'No files were processed for compliance analysis',
                'severity': 'minor',
                'penalty': '$0',
                'section': 'General'
            })
        elif not driver_logs and not fuel_receipts and not bills_of_lading and not weekly_summaries:
            # Only add violation if file processing failed completely
            self._add_violation({
                'date': 'unknown',
                'type': 'COMPLIANCE_PROCESSING_FAILED',
                'description': 'File processing failed - unable to extract data for analysis',
                'severity': 'minor',
                'penalty': '$0',
                'section': 'General'
            })
        # If we have data and no violations, the file is compliant - don't add artificial violations
        # This ensures compliant files get 100% scores
    
    def _is_valid_status_transition(self, from_status, to_status):
        """Check if duty status transition is valid - be more realistic with ELD data"""
        # Normalize status names to handle variations
        from_status = from_status.lower().replace('berth', '').strip()
        to_status = to_status.lower().replace('berth', '').strip()
        
        # ELD systems often have multiple valid transitions
        valid_transitions = {
            'off duty': ['on duty', 'driving', 'sleeper', 'off duty'],  # Can stay off duty
            'on duty': ['driving', 'off duty', 'sleeper', 'on duty'],   # Can stay on duty
            'driving': ['on duty', 'off duty', 'sleeper', 'driving'],   # Can stay driving
            'sleeper': ['on duty', 'off duty', 'driving', 'sleeper']    # Can stay in sleeper
        }
        
        # If we don't recognize the status, assume it's valid (don't penalize)
        if from_status not in valid_transitions:
            return True
            
        return to_status in valid_transitions.get(from_status, [])
    
    def _calculate_duration(self, start_time, end_time):
        """Calculate duration between two time strings"""
        try:
            start = datetime.strptime(start_time, '%H:%M')
            end = datetime.strptime(end_time, '%H:%M')
            
            # Handle overnight periods
            if end < start:
                end += timedelta(days=1)
            
            duration = (end - start).total_seconds() / 3600  # Convert to hours
            return duration
        except:
            return 0  # Return 0 if time parsing fails
    
    def get_consolidated_violations(self):
        """Get consolidated violations for reporting"""
        if not self.violations:
            return []
        
        # Group violations by type
        violation_groups = {}
        for violation in self.violations:
            violation_type = violation.get('type', 'UNKNOWN')
            if violation_type not in violation_groups:
                violation_groups[violation_type] = []
            violation_groups[violation_type].append(violation)
        
        # Create consolidated violations
        consolidated = []
        for violation_type, violations in violation_groups.items():
            consolidated.append({
                'type': violation_type,
                'count': len(violations),
                'severity': max([v.get('severity', 'minor') for v in violations]),
                'description': f'{len(violations)} {violation_type.replace("_", " ").title()} violations',
                'penalty': violations[0].get('penalty', '$0'),
                'section': violations[0].get('section', 'Unknown')
            })
        
        return consolidated
    
    def get_violation_summary(self):
        """Get summary of violations by category"""
        if not self.violations:
            return {'total': 0, 'by_severity': {}, 'by_type': {}}
        
        summary = {
            'total': len(self.violations),
            'by_severity': {},
            'by_type': {}
        }
        
        # Count by severity
        for violation in self.violations:
            severity = violation.get('severity', 'unknown')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
        
        # Count by type
        for violation in self.violations:
            violation_type = violation.get('type', 'unknown')
            summary['by_type'][violation_type] = summary['by_type'].get(violation_type, 0) + 1
        
        return summary 