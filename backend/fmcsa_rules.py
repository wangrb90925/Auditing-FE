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
            'max_70_hour_week': 70,    # Maximum hours in 8 days
            'required_break_time': 0.5,  # 30-minute break required after 8 hours driving
            'max_14_hour_window': 14,   # 14-hour window from first on-duty time
            'max_70_hour_8_days': 70    # 70 hours in 8 consecutive days
        }
        
        # Track fuel transactions for cross-referencing
        self.fuel_transactions = []
        self.driver_logs_data = []
    

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
        self.fuel_transactions = []
        self.driver_logs_data = []
        
        # Store data for cross-referencing
        driver_logs = extracted_data.get('driver_logs', [])
        fuel_receipts = extracted_data.get('fuel_receipts', [])
        bills_of_lading = extracted_data.get('bills_of_lading', [])
        raw_text_blobs = [a for a in extracted_data.get('audit_summaries', []) if a.get('type') == 'raw_text']
        weekly_summaries = extracted_data.get('weekly_summaries', [])
        
        # Store driver logs for cross-referencing
        for log_data in driver_logs:
            if log_data.get('type') == 'driver_log':
                self.driver_logs_data.append(log_data)
        
        # Store fuel transactions for cross-referencing
        for receipt_data in fuel_receipts:
            if receipt_data.get('type') == 'fuel_receipt' or 'fuel' in receipt_data.get('file_name', '').lower():
                self.fuel_transactions.append(receipt_data)
        
        # Process driver logs
        for log_data in driver_logs:
            if log_data.get('type') == 'driver_log':
                self._analyze_driver_log_compliance(log_data, driver_type)
        
        # Process fuel receipts
        for receipt_data in fuel_receipts:
            self._check_fuel_receipt_compliance(receipt_data)
        
        # Process Bills of Lading
        for bol_data in bills_of_lading:
            self._check_bol_compliance(bol_data)
        
        # Process weekly summaries
        for summary_data in weekly_summaries:
            self._check_weekly_summary_compliance(summary_data)
        
        # Cross-reference fuel transactions with driver logs
        self._check_fuel_transaction_compliance()
        
        # Check for log falsification
        if driver_logs:
            self._check_log_falsification(driver_logs)
        
        # Check for implausible behavior
        if driver_logs and bills_of_lading:
            self._check_geographic_implausibility(driver_logs, bills_of_lading)
        
        # Check for missing location violations
        self._check_missing_location_violations()
        
        # Check for PC misuse violations
        self._check_pc_misuse_violations()
        
        # Check for distance/mileage violations
        self._check_distance_mileage_violations()
        
        # Heuristic raw-text scans for additional violations
        if raw_text_blobs:
            self._scan_raw_text_for_pc(raw_text_blobs)
            self._scan_raw_text_for_missing_locations(raw_text_blobs)
            self._scan_raw_text_for_fuel_without_on_duty(raw_text_blobs)
            self._scan_raw_text_for_hos_patterns(raw_text_blobs)

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
        first_on_duty_time = None  # Track first on-duty time for 14-hour window
        driving_sessions = []  # Track driving sessions for break violations
        current_driving_session = None

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
                        
                        # Track driving session for break violations
                        if current_driving_session is None:
                            current_driving_session = {'start': status_start_time, 'total_hours': 0}
                        current_driving_session['total_hours'] += duration
                        
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
                        
                        # Track first on-duty time for 14-hour window
                        if first_on_duty_time is None:
                            first_on_duty_time = status_start_time
                    
                    elif current_status == 'off duty':
                        off_duty_periods.append(duration)
                        
                        # End current driving session if exists
                        if current_driving_session:
                            driving_sessions.append(current_driving_session)
                            current_driving_session = None
                        
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
        
        # Check driving hours violation (only when we have sufficient evidence for a full day)
        sufficient_entries = len(sorted_entries) >= 5
        has_early = any(e.get('time','') <= '06:00' for e in sorted_entries)
        has_late = any(e.get('time','') >= '18:00' for e in sorted_entries)
        if total_driving_hours > self.hos_rules['max_driving_hours'] and (sufficient_entries or (has_early and has_late)):

            self._add_violation({
                'date': date,
                'type': 'HOS_DRIVING_HOURS_EXCEEDED',
                'description': f'Driving hours exceeded 11-hour limit: {total_driving_hours:.1f} hours',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.3(a)(1)'
            })
        
        # Check on-duty hours violation (only when we have sufficient evidence for a full day)
        if total_on_duty_hours > self.hos_rules['max_on_duty_hours'] and (sufficient_entries or (has_early and has_late)):

            self._add_violation({
                'date': date,
                'type': 'HOS_ON_DUTY_HOURS_EXCEEDED',
                'description': f'On-duty hours exceeded 14-hour limit: {total_on_duty_hours:.1f} hours',
                'severity': 'major',
                'penalty': '$2,750',
                'section': '395.3(a)(2)'
            })
        
        # Add final driving session if exists
        if current_driving_session:
            driving_sessions.append(current_driving_session)
        
        # Check for 30-minute break violations
        self._check_break_violations(date, driving_sessions)
        
        # Check for 14-hour window violations
        self._check_14_hour_window_violation(date, first_on_duty_time, sorted_entries)
        
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
        """Check 60/70 hour weekly limits and 70/8 cycle rule"""
        if not daily_entries or len(daily_entries) < 7:
            # Need at least 7 days to check weekly limits
            return
        
        # Sort dates to ensure proper order
        sorted_dates = sorted(daily_entries.keys())
        
        # Calculate total hours for the week
        week_hours = 0
        week_start = sorted_dates[0] if sorted_dates else None
        
        for date in sorted_dates:
            entries = daily_entries[date]

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
        if week_hours > 0:  # Only check if we have some data
            if driver_type == 'long-haul':
                if week_hours > self.hos_rules['max_70_hour_week']:
                    self._add_violation({
                        'date': week_start or 'unknown',
                        'type': 'HOS_WEEKLY_LIMIT_EXCEEDED',
                        'description': f'Weekly hours exceeded 70-hour limit: {week_hours} hours (estimated)',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.3(b)'
                    })
            else:
                if week_hours > self.hos_rules['max_60_hour_week']:
                    self._add_violation({
                        'date': week_start or 'unknown',
                        'type': 'HOS_WEEKLY_LIMIT_EXCEEDED',
                        'description': f'Weekly hours exceeded 60-hour limit: {week_hours} hours (estimated)',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.3(b)'
                    })
        
        # Check 70/8 cycle rule (70 hours in any 8 consecutive days)
        if len(sorted_dates) >= 8:
            for i in range(len(sorted_dates) - 7):  # Check every 8-day window
                eight_day_hours = 0
                for j in range(i, i + 8):
                    if j < len(sorted_dates):
                        date = sorted_dates[j]
                        entries = daily_entries[date]
                        
                        # Calculate hours for this day
                        day_hours = 0
                        for entry in entries:
                            duty_statuses = entry.get('duty_status', [])
                            for status_info in duty_statuses:
                                status = status_info.get('status', '').lower()
                                if status in ['driving', 'on duty']:
                                    day_hours += 8  # Estimate
                        
                        eight_day_hours += day_hours
                
                if eight_day_hours > self.hos_rules['max_70_hour_8_days']:
                    self._add_violation({
                        'date': sorted_dates[i] if i < len(sorted_dates) else 'unknown',
                        'type': 'HOS_70_8_CYCLE_VIOLATION',
                        'description': f'70/8 cycle rule violated: {eight_day_hours} hours in 8 consecutive days',
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

            duty_status = (receipt_data.get('duty_status') or '').lower()
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

    # --- Heuristic raw text scanners ---
    def _scan_raw_text_for_pc(self, raw_text_blobs):
        for blob in raw_text_blobs:
            text = (blob.get('content') or '').lower()
            # Look for PC markers on lines that also show speed/miles/driving context
            for line in text.split('\n'):
                l = line.lower()
                if (' pc ' in f" {l} " or 'personal conveyance' in l) and ('drive' in l or 'driving' in l or 'mi' in l or 'mph' in l):
                    self._add_violation({
                        'date': self._extract_any_date(l) or 'unknown',
                        'type': 'PC_MISUSE_VIOLATION',
                        'description': 'Misuse of Personal Conveyance (PC) detected in log remarks',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.2'
                    })

    def _scan_raw_text_for_missing_locations(self, raw_text_blobs):
        # If logs show headers for location columns but many lines lack city/state, flag per date
        for blob in raw_text_blobs:
            text = blob.get('content') or ''
            lines = [ln for ln in text.split('\n') if ln.strip()]
            missing_by_date = {}
            for ln in lines:
                date = self._extract_any_date(ln)
                if not date:
                    continue
                # Heuristic: if a line looks like a status/time line but lacks a comma (city, ST)
                if re.search(r'\b(OFF|ON|DRIVING|SLEEPER|OFF DUTY|ON DUTY)\b', ln, re.I) and ',' not in ln and self._is_valid_date_string(date):
                    missing_by_date[date] = True
            for date in missing_by_date.keys():
                self._add_violation({
                    'date': date,
                    'type': 'FORM_MANNER_MISSING_LOCATION',
                    'description': f'Missing location in driver log on {date}',
                    'severity': 'minor',
                    'penalty': '$1,375',
                    'section': '395.8(d)'
                })

    def _scan_raw_text_for_fuel_without_on_duty(self, raw_text_blobs):
        # Very simple: detect lines that say Fuel or Receipt with amounts but nearby OFF/PC
        for blob in raw_text_blobs:
            text = blob.get('content') or ''
            lines = [ln for ln in text.split('\n') if ln.strip()]
            for i, ln in enumerate(lines):
                if re.search(r'\b(fuel|receipt|diesel|gallon|gal)\b', ln, re.I):
                    date = self._extract_any_date(ln) or self._extract_any_date(' '.join(lines[max(0, i-2):i+3]))
                    window = ' '.join(lines[max(0, i-3):i+4]).lower()
                    if 'off duty' in window or ' pc ' in f" {window} ":
                        self._add_violation({
                            'date': date or 'unknown',
                            'type': 'FUEL_WITHOUT_ON_DUTY_TIME',
                            'description': 'Fuel transaction without corresponding on-duty time',
                            'severity': 'major',
                            'penalty': '$2,750',
                            'section': '395.2'
                        })

    def _scan_raw_text_for_hos_patterns(self, raw_text_blobs):
        # Detect textual mentions of long continuous driving and missing breaks
        for blob in raw_text_blobs:
            text = (blob.get('content') or '').lower()
            # Look for patterns like "driving 11:30" or total driving > 11 mentioned
            if re.search(r'driving\s*(1[12]:\d\d|1[2-9]\.\d|1[2-9] hours?)', text):
                self._add_violation({
                    'date': self._extract_any_date(text) or 'unknown',
                    'type': 'HOS_DRIVING_HOURS_EXCEEDED',
                    'description': 'Text indicates driving duration beyond 11 hours',
                    'severity': 'major',
                    'penalty': '$2,750',
                    'section': '395.3(a)(1)'
                })
            # Break mention
            if re.search(r'(no\s*30\s*min|miss(ing)?\s*30\s*min|no break)', text):
                self._add_violation({
                    'date': self._extract_any_date(text) or 'unknown',
                    'type': 'HOS_BREAK_VIOLATION',
                    'description': 'Text indicates missing 30-minute break after 8 hours driving',
                    'severity': 'major',
                    'penalty': '$2,750',
                    'section': '395.3(a)(3)'
                })

    def _extract_any_date(self, text):
        try:
            # Numeric formats MM/DD(/YY|YYYY) or MM-DD(-YY|YYYY)
            m = re.search(r'(\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{1,2}-\d{1,2}-\d{2,4}\b|\b\d{1,2}/\d{1,2}\b|\b\d{1,2}-\d{1,2}\b)', text)
            if m:
                return m.group(1)
            # Month name formats (avoid generic words like OFF)
            month_names = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)'
            m = re.search(rf'\b{month_names}\s+\d{{1,2}}\b', text, re.I)
            if m:
                return m.group(0)
        except Exception:
            return None
        return None

    def _is_valid_date_string(self, s: str) -> bool:
        # accept numeric formats or real month names only
        if re.match(r'^\d{1,2}/\d{1,2}(/\d{2,4})?$', s):
            return True
        if re.match(r'^\d{1,2}-\d{1,2}(-\d{2,4})?$', s):
            return True
        months = 'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December'
        if re.match(rf'^(?:{months})\s+\d{{1,2}}$', s, re.I):
            return True
        return False
    
    def _check_break_violations(self, date, driving_sessions):
        """Check for 30-minute break violations after 8 hours of driving"""
        for session in driving_sessions:
            if session['total_hours'] >= 8:  # 8 hours of driving requires 30-minute break
                # Check if there was a break of at least 30 minutes
                # This would need to be cross-referenced with off-duty periods
                # For now, we'll flag if driving session is longer than 8 hours without break
                if session['total_hours'] > 8.5:  # Allow some buffer
                    self._add_violation({
                        'date': date,
                        'type': 'HOS_BREAK_VIOLATION',
                        'description': f'30-minute break required after 8 hours driving: {session["total_hours"]:.1f} hours without break',
                        'severity': 'major',
                        'penalty': '$2,750',
                        'section': '395.3(a)(3)'
                    })
    
    def _check_14_hour_window_violation(self, date, first_on_duty_time, entries):
        """Check for 14-hour window violations"""
        if not first_on_duty_time or not entries:
            return
        
        # Find the last on-duty or driving time
        last_on_duty_time = None
        for entry in reversed(entries):
            duty_statuses = entry.get('duty_status', [])
            for status_info in duty_statuses:
                status = status_info.get('status', '').lower()
                if status in ['on duty', 'driving']:
                    last_on_duty_time = entry.get('time', '')
                    break
            if last_on_duty_time:
                break
        
        if last_on_duty_time:
            window_duration = self._calculate_duration(first_on_duty_time, last_on_duty_time)
            if window_duration > self.hos_rules['max_14_hour_window']:
                self._add_violation({
                    'date': date,
                    'type': 'HOS_14_HOUR_WINDOW_VIOLATION',
                    'description': f'14-hour window exceeded: {window_duration:.1f} hours from first on-duty time',
                    'severity': 'major',
                    'penalty': '$2,750',
                    'section': '395.3(a)(2)'
                })
    
    def _check_fuel_transaction_compliance(self):
        """Check fuel transactions against driver logs for compliance"""
        for fuel_transaction in self.fuel_transactions:
            fuel_date = fuel_transaction.get('date', '')
            fuel_time = fuel_transaction.get('time', '')
            
            if not fuel_date or not fuel_time:
                continue
            
            # Find corresponding driver log entry
            found_on_duty_time = False
            for log_data in self.driver_logs_data:
                entries = log_data.get('entries', [])
                for entry in entries:
                    entry_date = entry.get('date', '')
                    if entry_date == fuel_date:
                        duty_statuses = entry.get('duty_status', [])
                        for status_info in duty_statuses:
                            status = status_info.get('status', '').lower()
                            if status in ['on duty', 'driving']:
                                found_on_duty_time = True
                                break
                        if found_on_duty_time:
                            break
                if found_on_duty_time:
                    break
            
            if not found_on_duty_time:
                self._add_violation({
                    'date': fuel_date,
                    'type': 'FUEL_WITHOUT_ON_DUTY_TIME',
                    'description': f'Fuel transaction without corresponding on-duty time on {fuel_date}',
                    'severity': 'major',
                    'penalty': '$2,750',
                    'section': '395.2'
                })
    
    def _check_missing_location_violations(self):
        """Check for missing location information in driver logs"""
        for log_data in self.driver_logs_data:
            entries = log_data.get('entries', [])
            for entry in entries:
                date = entry.get('date', '')
                location = entry.get('location', '')
                
                # Check if location is missing or empty
                if not location or location.strip() == '' or location.lower() in ['', 'n/a', 'none', 'unknown']:
                    self._add_violation({
                        'date': date,
                        'type': 'FORM_MANNER_MISSING_LOCATION',
                        'description': f'Missing location information in driver log on {date}',
                        'severity': 'minor',
                        'penalty': '$1,375',
                        'section': '395.8(d)'
                    })
    
    def _check_pc_misuse_violations(self):
        """Check for Personal Conveyance (PC) misuse violations"""
        for log_data in self.driver_logs_data:
            entries = log_data.get('entries', [])
            for entry in entries:
                duty_statuses = entry.get('duty_status', [])
                for status_info in duty_statuses:
                    status = status_info.get('status', '').lower()
                    remarks = status_info.get('remarks', '').lower()
                    
                    # Check for PC misuse patterns
                    if 'pc' in remarks or 'personal conveyance' in remarks:
                        # Check if PC is being used inappropriately
                        if 'driving' in status and 'pc' in remarks:
                            # PC should not be used while driving for commercial purposes
                            self._add_violation({
                                'date': entry.get('date', ''),
                                'type': 'PC_MISUSE_VIOLATION',
                                'description': f'Misuse of Personal Conveyance (PC) on {entry.get("date", "")}',
                        'severity': 'major',
                        'penalty': '$2,750',
                                'section': '395.2'
                            })
    
    def _check_distance_mileage_violations(self):
        """Check for distance/mileage changes without corresponding driving time"""
        for log_data in self.driver_logs_data:
            entries = log_data.get('entries', [])
            for i, entry in enumerate(entries):
                current_miles = entry.get('miles', 0)
                current_driving_time = 0
                
                # Calculate driving time for this entry
                duty_statuses = entry.get('duty_status', [])
                for status_info in duty_statuses:
                    status = status_info.get('status', '').lower()
                    if status == 'driving':
                        # Estimate driving time (this would be more accurate with actual time data)
                        current_driving_time += 1  # Assume 1 hour per driving entry
                
                # Check if there's a significant mileage change without driving time
                if i > 0:
                    prev_entry = entries[i-1]
                    prev_miles = prev_entry.get('miles', 0)
                    mileage_change = current_miles - prev_miles
                    
                    if mileage_change > 0 and current_driving_time == 0:
                        self._add_violation({
                            'date': entry.get('date', ''),
                            'type': 'DISTANCE_MILEAGE_VIOLATION',
                            'description': f'Distance/mileage change without corresponding driving time: +{mileage_change} miles',
                            'severity': 'major',
                            'penalty': '$2,750',
                            'section': '395.8(d)'
                        })