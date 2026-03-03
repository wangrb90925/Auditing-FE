"""
Rule-Based Violation Detection Engine

This module implements a comprehensive, configurable violation detection system
that replaces hard-coded logic with rule-based analysis.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import re
from dataclasses import dataclass
from driver_classifications import (
    DriverClassificationSystem, ViolationType, Severity, 
    DriverType, driver_classification_system
)

@dataclass
class LogEntry:
    """Represents a single driver log entry"""
    date: str
    start_time: str
    end_time: str
    duty_status: str
    location: str
    odometer: Optional[float] = None
    hours: Optional[float] = None
    remarks: Optional[str] = None

@dataclass
class FuelTransaction:
    """Represents a fuel transaction"""
    date: str
    time: str
    location: str
    amount: float
    odometer: Optional[float] = None

@dataclass
class Violation:
    """Represents a detected violation"""
    date: str
    violation_type: ViolationType
    description: str
    severity: Severity
    penalty: str
    cfr_section: str
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

class ViolationDetector:
    """Main violation detection engine"""
    
    def __init__(self):
        self.classification_system = driver_classification_system
        self.violations = []
        self.processed_entries = []
        self.fuel_transactions = []
    
    def detect_violations(self, extracted_data: Dict, driver_type: str) -> List[Violation]:
        """
        Main entry point for violation detection
        
        Args:
            extracted_data: Processed data from files
            driver_type: Type of driver (long-haul, short-haul, etc.)
            
        Returns:
            List of detected violations
        """
        self.violations = []
        self.processed_entries = []
        self.fuel_transactions = []
        
        # Debug: Print extracted data summary
        # Silent analysis - results in JSON files only
        
        # Get driver classification
        classification = self.classification_system.get_classification(driver_type)
        if not classification:
            # Default to long-haul if unknown type
            classification = self.classification_system.get_classification("long-haul")
        
        # Process driver logs
        driver_logs = extracted_data.get('driver_logs', [])
        
        # Process driver logs silently
        
        # Process driver logs
        self.processed_entries = self._process_log_entries(driver_logs)
        
        # Process fuel receipts
        fuel_receipts = extracted_data.get('fuel_receipts', [])
        self.fuel_transactions = self._process_fuel_transactions(fuel_receipts)
        
        # Run violation checks based on driver classification
        applicable_violations = classification.applicable_violations
        
        # HOS Violations - CORRECTED: Proper FMCSA HOS implementation
        if ViolationType.HOS_11_HOUR_DRIVING in applicable_violations:
            self._check_11_hour_driving_violations_corrected(classification)
        
        if ViolationType.HOS_14_HOUR_WINDOW in applicable_violations:
            self._check_14_hour_window_violations_corrected(classification)
        
        if ViolationType.HOS_60_HOUR_7_DAY in applicable_violations:
            self._check_60_hour_7_day_violations_corrected(classification)
        
        if ViolationType.HOS_70_HOUR_8_DAY in applicable_violations:
            self._check_70_hour_8_day_violations_corrected(classification)
        
        if ViolationType.HOS_30_MINUTE_BREAK in applicable_violations:
            self._check_30_minute_break_violations_corrected(classification)
        
        # HOS_10_HOUR_REST - REMOVED per user request
        # 
        
        # Form and Manner Violations
        if ViolationType.FORM_MANNER_MISSING_FIELDS in applicable_violations:
            self._check_missing_fields_violations()
        
        if ViolationType.FORM_MANNER_INCOMPLETE_ENTRIES in applicable_violations:
            self._check_incomplete_entries_violations()
        
        # Other Violations
        if ViolationType.LOG_FALSIFICATION in applicable_violations:
            self._check_log_falsification_violations()
        
        if ViolationType.DRIVING_OFF_DUTY in applicable_violations:
            self._check_driving_off_duty_violations()
        
        if ViolationType.FUEL_OFF_DUTY in applicable_violations:
            self._check_fuel_off_duty_violations()
        
        if ViolationType.PERSONAL_CONVEYANCE_MISUSE in applicable_violations:
            self._check_personal_conveyance_violations()
        
        if ViolationType.GEOGRAPHIC_IMPLAUSIBLE in applicable_violations:
            self._check_geographic_implausible_violations()
        
        if ViolationType.MISSING_DUTY_STATUS in applicable_violations:
            self._check_missing_duty_status_violations()
        
        # Enhanced detection for common issues in driver logs (excluding HOS - handled above)
        self._check_comprehensive_violations_non_hos(extracted_data)
        
        # Detection complete - results in JSON files
        return self.violations
    
    def _process_log_entries(self, driver_logs: List[Dict]) -> List[LogEntry]:
        """Process raw driver log data into structured entries - Updated for new library-based format"""
        entries = []
        
        # Process driver log entries silently
        for log_idx, log in enumerate(driver_logs):
            # NEW FORMAT: Check if this is the new library_result format with daily_entries
            if 'library_result' in log and 'daily_entries' in log['library_result']:
                # Process new format from library-based extraction
                daily_entries = log['library_result']['daily_entries']
                
                for day_entry in daily_entries:
                    date = day_entry.get('date', '')
                    day_entries = day_entry.get('entries', [])
                    
                    for entry in day_entries:
                        try:
                            # Extract odometer value (remove "mi" suffix if present)
                            odometer_str = entry.get('odometer', '')
                            odometer_value = None
                            if odometer_str and odometer_str != '-':
                                # Remove "mi" and commas, extract number
                                odometer_clean = re.sub(r'[^\d.]', '', str(odometer_str))
                                odometer_value = self._safe_float(odometer_clean)
                            
                            processed_entry = LogEntry(
                                date=date,
                                start_time=entry.get('start_time', ''),
                                end_time=entry.get('end_time', ''),
                                duty_status=entry.get('duty_status', ''),
                                location=entry.get('location', ''),
                                odometer=odometer_value,
                                hours=self._safe_float(entry.get('duration_hours', 0)),
                                remarks=entry.get('remarks', '')
                            )
                            entries.append(processed_entry)
                            
                        except Exception as e:
                            # Log errors silently to file only
                            continue
            
            # OLD FORMAT: Fallback for old format (for backward compatibility)
            else:
                log_entries = log.get('entries', [])
                
                for entry_idx, entry in enumerate(log_entries):
                    try:
                        # Handle both old and new data formats
                        duty_status = entry.get('duty_status', '')
                        if isinstance(duty_status, list) and duty_status:
                            duty_status = duty_status[0].get('status', '')
                        
                        processed_entry = LogEntry(
                            date=entry.get('date', ''),
                            start_time=entry.get('start_time', entry.get('time', '')),
                            end_time=entry.get('end_time', ''),
                            duty_status=duty_status,
                            location=entry.get('location', ''),
                            odometer=self._safe_float(entry.get('odometer')),
                            hours=self._safe_float(entry.get('duration_hours', entry.get('hours', 0))),
                            remarks=entry.get('remarks', '')
                        )
                        entries.append(processed_entry)
                            
                    except Exception as e:
                        # Log errors silently to file only
                        continue
        
        return entries
    
    def _process_fuel_transactions(self, fuel_receipts: List[Dict]) -> List[FuelTransaction]:
        """Process fuel receipt data into structured transactions"""
        transactions = []
        
        for receipt in fuel_receipts:
            try:
                transaction = FuelTransaction(
                    date=receipt.get('date', ''),
                    time=receipt.get('time', ''),
                    location=receipt.get('location', ''),
                    amount=self._safe_float(receipt.get('amount', 0)),
                    odometer=self._safe_float(receipt.get('odometer'))
                )
                transactions.append(transaction)
            except Exception as e:
                print(f"Error processing fuel transaction: {e}")
                continue
        
        return transactions
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _add_violation(self, violation: Violation):
        """Add a violation to the list"""
        self.violations.append(violation)
    
    def _check_11_hour_driving_violations_corrected(self, classification):
        """
        Check for 11-hour driving limit violations - PROPERLY IMPLEMENTS FMCSA RULE
        
        FMCSA Rule: "A driver may drive up to 11 hours after having taken 10 consecutive hours off duty"
        
        This means we must:
        1. Identify all periods of 10+ consecutive hours off duty
        2. Track driving hours in each DUTY PERIOD (between 10-hour breaks)
        3. Flag violation if any duty period exceeds 11 hours of driving
        """
        max_driving_hours = classification.hos_limits.get('max_driving_hours', 11.0)
        
        # Get all entries sorted chronologically
        all_entries = self._get_chronological_entries()
        if not all_entries:
            return
        
        # Find all 10+ hour break periods
        break_periods = self._find_10_hour_break_periods(all_entries)
        
        # If no 10-hour breaks found, check if driver started with adequate rest
        # For now, we'll analyze duty periods between breaks
        if len(break_periods) == 0:
            # No 10-hour breaks found - check total driving time as fallback
            # (This handles cases where logs don't show the initial 10-hour rest)
            self._check_driving_without_proper_reset(all_entries, max_driving_hours)
            return
        
        # Check driving hours for each duty period (between consecutive 10-hour breaks)
        for i in range(len(break_periods)):
            # Define duty period boundaries
            duty_period_start = break_periods[i]['end_date'], break_periods[i]['end_time']
            
            # Find next break (or end of logs)
            if i + 1 < len(break_periods):
                duty_period_end = break_periods[i + 1]['start_date'], break_periods[i + 1]['start_time']
            else:
                # Last duty period - goes to end of logs
                duty_period_end = all_entries[-1].date, all_entries[-1].end_time if all_entries[-1].end_time else all_entries[-1].start_time
            
            # Count driving hours in this duty period
            driving_hours_in_period = self._calculate_driving_hours_in_period(
                all_entries, duty_period_start, duty_period_end
            )
            
            if driving_hours_in_period > max_driving_hours:
                rule = self.classification_system.get_violation_rule(ViolationType.HOS_11_HOUR_DRIVING)
                if rule:
                    penalty = self._format_penalty(rule.penalty_range)
                    
                    # Format violation date (use start of duty period)
                    violation_date = duty_period_start[0]
                    
                    self._add_violation(Violation(
                        date=violation_date,
                        violation_type=ViolationType.HOS_11_HOUR_DRIVING,
                        description=f"Drove {self._format_hours_readable(driving_hours_in_period)} after 10-hour break, exceeding {max_driving_hours}-hour limit",
                        severity=rule.severity,
                        penalty=penalty,
                        cfr_section=rule.cfr_section,
                        details={
                            'driving_hours_in_period': self._format_hours_readable(driving_hours_in_period),
                            'limit': self._format_hours_readable(max_driving_hours),
                            'duty_period_start': f"{duty_period_start[0]} {duty_period_start[1]}",
                            'duty_period_end': f"{duty_period_end[0]} {duty_period_end[1]}",
                            'break_duration': self._format_hours_readable(break_periods[i]['duration_hours'])
                        }
                    ))
    
    def _check_14_hour_window_violations_corrected(self, classification):
        """Check for 14-hour window violations - CORRECT FMCSA RULE"""
        max_window_hours = classification.hos_limits.get('max_on_duty_hours', 14.0)
        
        # Get all entries sorted chronologically
        all_entries = self._get_chronological_entries()
        if not all_entries:
            return
        
        # Find all 10+ hour break periods
        break_periods = self._find_10_hour_break_periods(all_entries)
        
        # Check elapsed time between breaks
        for i in range(len(break_periods) - 1):
            current_break_end_time = break_periods[i]['end_time']
            current_break_end_date = break_periods[i]['end_date']
            next_break_start_time = break_periods[i + 1]['start_time']
            next_break_start_date = break_periods[i + 1]['start_date']
            
            # Calculate total elapsed time between breaks (including short rests)
            elapsed_hours = self._calculate_elapsed_time_between_breaks(
                current_break_end_date, current_break_end_time,
                next_break_start_date, next_break_start_time
            )
            
            if elapsed_hours and elapsed_hours > max_window_hours:
                rule = self.classification_system.get_violation_rule(ViolationType.HOS_14_HOUR_WINDOW)
                if rule:
                    penalty = self._format_penalty(rule.penalty_range)
                    
                    # Calculate violation hours (excess over 14 hours)
                    violation_hours = round(elapsed_hours - max_window_hours, 2)
                    
                    self._add_violation(Violation(
                        date=next_break_start_date,
                        violation_type=ViolationType.HOS_14_HOUR_WINDOW,
                        description=f"14-hour window violation: {self._format_hours_readable(elapsed_hours)} between 10+ hour breaks (limit: {self._format_hours_readable(max_window_hours)})",
                        severity=rule.severity,
                        penalty=penalty,
                        cfr_section=rule.cfr_section,
                        details={
                            'period_start_time': current_break_end_time,
                            'period_start_date': current_break_end_date,
                            'total_elapsed_hours': self._format_hours_readable(elapsed_hours),
                            'violation_hours': self._format_hours_readable(violation_hours),
                            'limit': self._format_hours_readable(max_window_hours),
                            'previous_break_duration': self._format_hours_readable(break_periods[i]['duration_hours']),
                            'next_break_duration': self._format_hours_readable(break_periods[i + 1]['duration_hours'])
                        }
                    ))
    
    def _check_60_hour_7_day_violations_corrected(self, classification):
        """Check for 60-hour/7-day violations - CORRECTED (one violation per period)"""
        max_hours = classification.hos_limits.get('max_60_7_hours', 60.0)
        
        # Calculate daily totals first
        daily_totals = self._calculate_daily_onduty_hours()
        if not daily_totals:
            return
        
        # Sort dates chronologically instead of as strings
        dates = self._sort_dates_chronologically(list(daily_totals.keys()))
        violations_found = set()  # Track which periods already have violations
        
        for i, end_date in enumerate(dates):
            # Calculate 7-day period ending on this date
            start_index = max(0, i - 6)  # 7 days including end_date
            period_dates = dates[start_index:i+1]
            
            if len(period_dates) >= 7:  # Only check complete 7-day periods
                total_hours = sum(daily_totals[date] for date in period_dates)
                # Round to 2 decimal places to fix floating point precision
                total_hours = round(total_hours, 2)
                
                if total_hours > max_hours:
                    # Create a unique key for this 7-day period
                    period_key = f"{period_dates[0]}_{end_date}"
                    
                    # Only add one violation per 7-day period
                    if period_key not in violations_found:
                        violations_found.add(period_key)
                        
                        rule = self.classification_system.get_violation_rule(ViolationType.HOS_60_HOUR_7_DAY)
                        if rule:
                            penalty = self._format_penalty(rule.penalty_range)
                            
                            # Round daily breakdown values too
                            rounded_daily_breakdown = {date: round(daily_totals[date], 2) for date in period_dates}
                            
                            self._add_violation(Violation(
                                date=end_date,
                                violation_type=ViolationType.HOS_60_HOUR_7_DAY,
                                description=f"60/7 cycle violation: {self._format_hours_readable(total_hours)} in 7-day period ({period_dates[0]} to {end_date})",
                                severity=rule.severity,
                                penalty=penalty,
                                cfr_section=rule.cfr_section,
                                details={
                                    'actual_hours': self._format_hours_readable(total_hours),
                                    'limit': self._format_hours_readable(max_hours),
                                    'period_days': 7,
                                    'period_start': period_dates[0],
                                    'period_end': end_date,
                                    'daily_breakdown': {date: self._format_hours_readable(hours) for date, hours in rounded_daily_breakdown.items()}
                                }
                            ))
    
    def _check_70_hour_8_day_violations_corrected(self, classification):
        """Check for 70-hour/8-day violations - CORRECTED (one violation per period)"""
        max_hours = classification.hos_limits.get('max_70_8_hours', 70.0)
        
        # Calculate daily totals first
        daily_totals = self._calculate_daily_onduty_hours()
        if not daily_totals:
            return
        
        # Sort dates chronologically instead of as strings
        dates = self._sort_dates_chronologically(list(daily_totals.keys()))
        violations_found = set()  # Track which periods already have violations
        
        for i, end_date in enumerate(dates):
            # Calculate 8-day period ending on this date
            start_index = max(0, i - 7)  # 8 days including end_date
            period_dates = dates[start_index:i+1]
            
            if len(period_dates) >= 8:  # Only check complete 8-day periods
                total_hours = sum(daily_totals[date] for date in period_dates)
                # Round to 2 decimal places to fix floating point precision
                total_hours = round(total_hours, 2)
                
                if total_hours > max_hours:
                    # Create a unique key for this 8-day period
                    period_key = f"{period_dates[0]}_{end_date}"
                    
                    # Only add one violation per 8-day period
                    if period_key not in violations_found:
                        violations_found.add(period_key)
                        
                        rule = self.classification_system.get_violation_rule(ViolationType.HOS_70_HOUR_8_DAY)
                        if rule:
                            penalty = self._format_penalty(rule.penalty_range)
                            
                            # Round daily breakdown values too
                            rounded_daily_breakdown = {date: round(daily_totals[date], 2) for date in period_dates}
                            
                            self._add_violation(Violation(
                                date=end_date,
                                violation_type=ViolationType.HOS_70_HOUR_8_DAY,
                                description=f"70/8 cycle violation: {self._format_hours_readable(total_hours)} in 8-day period ({period_dates[0]} to {end_date})",
                                severity=rule.severity,
                                penalty=penalty,
                                cfr_section=rule.cfr_section,
                                details={
                                    'actual_hours': self._format_hours_readable(total_hours),
                                    'limit': self._format_hours_readable(max_hours),
                                    'period_days': 8,
                                    'period_start': period_dates[0],
                                    'period_end': end_date,
                                    'daily_breakdown': {date: self._format_hours_readable(hours) for date, hours in rounded_daily_breakdown.items()}
                                }
                            ))
    
    # HOS_10_HOUR_REST method removed per user request
    
    def _check_missing_fields_violations(self):
        """Check for missing required fields"""
        required_fields = ['date', 'duty_status', 'location']
        
        for entry in self.processed_entries:
            missing_fields = []
            
            for field in required_fields:
                value = getattr(entry, field, None)
                if not value or (isinstance(value, str) and not value.strip()):
                    missing_fields.append(field)
            
            if missing_fields:
                rule = self.classification_system.get_violation_rule(ViolationType.FORM_MANNER_MISSING_FIELDS)
                penalty = self._format_penalty(rule.penalty_range)
                
                self._add_violation(Violation(
                    date=entry.date or 'Unknown',
                    violation_type=ViolationType.FORM_MANNER_MISSING_FIELDS,
                    description=f"Missing required fields: {', '.join(missing_fields)}",
                    severity=rule.severity,
                    penalty=penalty,
                    cfr_section=rule.cfr_section,
                    details={'missing_fields': missing_fields}
                ))
    
    def _check_fuel_off_duty_violations(self):
        """Check for fuel activity with incorrect duty status - CORRECTED"""
        # Check all log entries for fuel-related remarks
        for entry in self.processed_entries:
            duty_status = entry.duty_status.lower() if entry.duty_status else ''
            remarks = entry.remarks.lower() if entry.remarks else ''
            location = entry.location.lower() if entry.location else ''
            
            if 'fuel' in remarks:
                if 'off_duty' in duty_status:
                    rule = self.classification_system.get_violation_rule(ViolationType.FUEL_OFF_DUTY)
                    if rule:
                        penalty = self._format_penalty(rule.penalty_range)
                        
                        self._add_violation(Violation(
                            date=entry.date,
                            violation_type=ViolationType.FUEL_OFF_DUTY,
                            description=f"Fuel activity with incorrect duty status '{entry.duty_status}' - should be 'on_duty'",
                            severity=rule.severity,
                            penalty=penalty,
                            cfr_section=rule.cfr_section,
                            details={
                                'actual_duty_status': entry.duty_status,
                                'required_duty_status': 'on_duty',
                                'fuel_indicator': remarks or location,
                                'time': entry.start_time,
                                'location': entry.location
                            }
                        ))
    
    # Helper methods
    def _group_entries_by_date(self) -> Dict[str, List[LogEntry]]:
        """Group log entries by date"""
        entries_by_date = {}
        for entry in self.processed_entries:
            date = entry.date
            if date not in entries_by_date:
                entries_by_date[date] = []
            entries_by_date[date].append(entry)
        return entries_by_date
    
    def _calculate_driving_hours(self, entries: List[LogEntry]) -> float:
        """Calculate total driving hours for a set of entries"""
        driving_hours = 0
        for entry in entries:
            if entry.duty_status and 'driving' in entry.duty_status.lower():
                hours = entry.hours or 0
                driving_hours += hours
                # Adding driving hours silently
        
        # Total driving hours calculated
        return driving_hours
    
    def _calculate_on_duty_hours(self, entries: List[LogEntry]) -> float:
        """Calculate total on-duty hours for a set of entries"""
        on_duty_hours = 0
        for entry in entries:
            if entry.duty_status and 'off' not in entry.duty_status.lower() and 'sleeper' not in entry.duty_status.lower():
                hours = entry.hours or 0
                on_duty_hours += hours
                # Adding on-duty hours silently
        
        # Total on-duty hours calculated
        return on_duty_hours
    
    def _calculate_duty_window_hours(self, entries: List[LogEntry]) -> float:
        """Calculate the duty window (first on-duty to last activity)"""
        if not entries:
            return 0
        
        # This is a simplified calculation
        # In practice, you'd need to parse actual times
        return sum(entry.hours or 0 for entry in entries)
    
    def _calculate_rest_period(self, prev_entries: List[LogEntry], curr_entries: List[LogEntry]) -> float:
        """Calculate rest period between consecutive days"""
        # This is a simplified calculation
        # In practice, you'd need to analyze the actual off-duty periods
        return 10.0  # Placeholder
    
    # _has_corresponding_duty_time method removed - no longer needed with corrected fuel logic
    
    def _format_penalty(self, penalty_range: Tuple[int, int]) -> str:
        """Format penalty range as string"""
        min_penalty, max_penalty = penalty_range
        if min_penalty == max_penalty:
            return f"${min_penalty:,}"
        else:
            return f"${min_penalty:,} - ${max_penalty:,}"
    
    def _format_hours_readable(self, decimal_hours: float) -> str:
        if decimal_hours is None or decimal_hours == 0:
            return "0h 0m"
        
        # Extract hours, minutes, seconds
        total_seconds = int(decimal_hours * 3600)  # Convert to total seconds
        
        hours = total_seconds // 3600
        remaining_seconds = total_seconds % 3600
        minutes = remaining_seconds // 60
        
        return f"{hours}h {minutes}m"
    
    def _get_chronological_entries(self) -> List[LogEntry]:
        """Get all entries sorted chronologically across all days"""
        all_entries = []
        
        # Convert processed entries to datetime-sortable format
        for entry in self.processed_entries:
            if entry.date and entry.start_time:
                try:
                    start_datetime = self._parse_datetime(entry.date, entry.start_time)
                    all_entries.append((start_datetime, entry))
                except:
                    # If datetime parsing fails, still include the entry with a default time
                    from datetime import datetime
                    default_datetime = datetime(2025, 1, 1, 0, 0, 0)
                    all_entries.append((default_datetime, entry))
        
        # Sort by datetime and return just the entries
        all_entries.sort(key=lambda x: x[0])
        return [entry for _, entry in all_entries]
    
    def _calculate_daily_onduty_hours(self) -> Dict[str, float]:
        """Calculate total on-duty hours per day (driving + on-duty-not-driving)"""
        daily_totals = {}
        
        entries_by_date = self._group_entries_by_date()
        
        for date, entries in entries_by_date.items():
            total_hours = 0
            for entry in entries:
                duty_status = entry.duty_status.lower() if entry.duty_status else ''
                hours = entry.hours or 0
                
                # Count driving and on-duty hours (exclude off-duty and sleeper berth)
                if ('driving' in duty_status or 
                    ('on' in duty_status and 'off' not in duty_status)):
                    total_hours += hours
            
            # Round to 2 decimal places to fix floating point precision
            daily_totals[date] = round(total_hours, 2)
        
        return daily_totals
    
    def _calculate_daily_driving_hours(self) -> Dict[str, float]:
        """Calculate total driving hours per day"""
        daily_totals = {}
        
        entries_by_date = self._group_entries_by_date()
        
        for date, entries in entries_by_date.items():
            total_hours = 0
            for entry in entries:
                duty_status = entry.duty_status.lower() if entry.duty_status else ''
                hours = entry.hours or 0
                
                # Count only driving hours
                if 'driving' in duty_status:
                    total_hours += hours
            
            # Round to 2 decimal places to fix floating point precision
            daily_totals[date] = round(total_hours, 2)
        
        return daily_totals
    
    def _calculate_driving_hours_in_period(self, all_entries: List[LogEntry], 
                                          period_start: Tuple[str, str], 
                                          period_end: Tuple[str, str]) -> float:
        """
        Calculate total driving hours within a specific duty period
        
        Args:
            all_entries: All log entries in chronological order
            period_start: (date, time) tuple marking start of duty period
            period_end: (date, time) tuple marking end of duty period
            
        Returns:
            Total driving hours in the period
        """
        total_driving_hours = 0.0
        start_date, start_time = period_start
        end_date, end_time = period_end
        
        # Parse start and end datetimes
        start_dt = self._parse_datetime_with_date(start_date, start_time)
        end_dt = self._parse_datetime_with_date(end_date, end_time)
        
        if not start_dt or not end_dt:
            return 0.0
        
        # Count driving hours for entries within this period
        for entry in all_entries:
            entry_dt = self._parse_datetime_with_date(entry.date, entry.start_time)
            
            if entry_dt and start_dt <= entry_dt < end_dt:
                duty_status = entry.duty_status.lower() if entry.duty_status else ''
                hours = entry.hours or 0
                
                # Count only driving hours
                if 'driving' in duty_status:
                    total_driving_hours += hours
        
        return round(total_driving_hours, 2)
    
    def _check_driving_without_proper_reset(self, all_entries: List[LogEntry], max_driving_hours: float):
        """
        Fallback check when no 10-hour breaks are found in the logs
        
        This handles edge cases where:
        - Logs don't include the initial 10-hour rest
        - Driver hasn't taken any 10-hour breaks during logged period
        """
        # Group by calendar day as fallback
        daily_driving = {}
        
        for entry in all_entries:
            duty_status = entry.duty_status.lower() if entry.duty_status else ''
            hours = entry.hours or 0
            
            if 'driving' in duty_status:
                date = entry.date
                if date not in daily_driving:
                    daily_driving[date] = 0.0
                daily_driving[date] += hours
        
        # Check each day
        for date, total_hours in daily_driving.items():
            total_hours = round(total_hours, 2)
            
            if total_hours > max_driving_hours:
                rule = self.classification_system.get_violation_rule(ViolationType.HOS_11_HOUR_DRIVING)
                if rule:
                    penalty = self._format_penalty(rule.penalty_range)
                    
                    self._add_violation(Violation(
                        date=date,
                        violation_type=ViolationType.HOS_11_HOUR_DRIVING,
                        description=f"Drove {self._format_hours_readable(total_hours)} without proper 10-hour reset, exceeding {max_driving_hours}-hour limit",
                        severity=rule.severity,
                        penalty=penalty,
                        cfr_section=rule.cfr_section,
                        details={
                            'driving_hours': self._format_hours_readable(total_hours),
                            'limit': self._format_hours_readable(max_driving_hours),
                            'note': 'No 10-hour break found in logs'
                        }
                    ))
    
    def _sort_dates_chronologically(self, dates: List[str]) -> List[str]:
        """Sort dates chronologically instead of as strings"""
        def parse_date_for_sorting(date_str: str):
            """Parse date string like '4/15' into sortable tuple (month, day)"""
            try:
                if '/' in date_str:
                    parts = date_str.split('/')
                    if len(parts) == 2:
                        month = int(parts[0])
                        day = int(parts[1])
                        # Assume current year for sorting purposes
                        year = 2025
                        return (year, month, day)
                    elif len(parts) == 3:
                        month = int(parts[0])
                        day = int(parts[1])
                        year = int(parts[2])
                        # Handle 2-digit years
                        if year < 100:
                            year += 2000
                        return (year, month, day)
                
                # Fallback: try to extract numbers
                import re
                numbers = re.findall(r'\d+', date_str)
                if len(numbers) >= 2:
                    month = int(numbers[0])
                    day = int(numbers[1])
                    year = int(numbers[2]) if len(numbers) > 2 else 2025
                    if year < 100:
                        year += 2000
                    return (year, month, day)
                
                # Last resort: return a default that will sort to end
                return (9999, 12, 31)
                
            except (ValueError, IndexError):
                # If parsing fails, return a default that will sort to end
                return (9999, 12, 31)
        
        # Sort dates using the parsed date tuples
        return sorted(dates, key=parse_date_for_sorting)
    
    def _find_10_hour_break_periods(self, all_entries: List[LogEntry]) -> List[Dict]:
        """Find all periods of 10+ consecutive hours of break (off_duty, sleeper, personal_conveyance)"""
        break_periods = []
        current_break_start = None
        current_break_hours = 0
        current_break_entries = []
        
        for entry in all_entries:
            duty_status = entry.duty_status.lower() if entry.duty_status else ''
            hours = entry.hours or 0
            
            # Check if this is a break activity
            is_break = any(status in duty_status for status in ['off_duty', 'sleeper', 'personal_conveyance'])
            
            if is_break:
                # Continue or start break period
                if current_break_start is None:
                    current_break_start = entry
                    current_break_hours = 0
                    current_break_entries = []
                
                current_break_hours += hours
                current_break_entries.append(entry)
                
                # If we've accumulated 10+ hours of break, record this period
                if current_break_hours >= 10.0:
                    # Find the actual end time (last entry in this break sequence)
                    last_entry = current_break_entries[-1]
                    
                    break_periods.append({
                        'start_time': current_break_start.start_time,
                        'start_date': current_break_start.date,
                        'end_time': last_entry.end_time if last_entry.end_time else last_entry.start_time,
                        'end_date': last_entry.date,
                        'duration_hours': round(current_break_hours, 2),
                        'entries': current_break_entries.copy()
                    })
            else:
                # Work activity - reset break tracking
                current_break_start = None
                current_break_hours = 0
                current_break_entries = []
        
        return break_periods
    
    def _calculate_elapsed_time_between_breaks(self, start_date: str, start_time: str, 
                                             end_date: str, end_time: str) -> Optional[float]:
        """Calculate total elapsed time between two break periods (including dates)"""
        try:
            # Parse start datetime
            start_dt = self._parse_datetime_with_date(start_date, start_time)
            # Parse end datetime  
            end_dt = self._parse_datetime_with_date(end_date, end_time)
            
            if start_dt and end_dt:
                # Calculate time difference in hours
                time_diff = end_dt - start_dt
                elapsed_hours = time_diff.total_seconds() / 3600
                return round(elapsed_hours, 2)
            
        except Exception as e:
            print(f"[DEBUG] Error calculating elapsed time: {e}")
            
        return None
    
    def _parse_datetime_with_date(self, date_str: str, time_str: str):
        """Parse date and time into complete datetime object"""
        try:
            from datetime import datetime
            import re
            
            # Parse date from "4/15" format
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 2:
                    month = int(parts[0])
                    day = int(parts[1])
                    year = 2025  # Assume current year
                elif len(parts) == 3:
                    month = int(parts[0])
                    day = int(parts[1])
                    year = int(parts[2])
                    if year < 100:
                        year += 2000
                else:
                    return None
            else:
                return None
            
            # Parse time from "1:17:23 PM EDT" format
            time_match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)', time_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                second = int(time_match.group(3))
                ampm = time_match.group(4)
                
                # Convert to 24-hour format
                if ampm == 'PM' and hour != 12:
                    hour += 12
                elif ampm == 'AM' and hour == 12:
                    hour = 0
                
                return datetime(year, month, day, hour, minute, second)
            
            return None
            
        except Exception as e:
            print(f"[DEBUG] Error parsing datetime: {e}")
            return None
    
    def _parse_time_for_comparison(self, time_str: str):
        """Parse time string for chronological comparison"""
        from datetime import datetime
        import re
        
        # Handle formats like "1:17:23 PM EDT"
        time_match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)', time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            second = int(time_match.group(3))
            ampm = time_match.group(4)
            
            # Convert to 24-hour format
            if ampm == 'PM' and hour != 12:
                hour += 12
            elif ampm == 'AM' and hour == 12:
                hour = 0
            
            # Return as comparable datetime (using fixed date for comparison)
            return datetime(2025, 1, 1, hour, minute, second)
        
        # Fallback
        return datetime(2025, 1, 1, 0, 0, 0)
    
    # Placeholder methods for other violation checks
    def _check_incomplete_entries_violations(self):
        """Check for incomplete entries"""
        for entry in self.processed_entries:
            incomplete_fields = []
            
            # Check for incomplete time information
            if not entry.start_time or not entry.end_time:
                incomplete_fields.append('time_period')
            
            # REMOVED: Location check (handled by _check_missing_fields_violations to avoid duplicates)
            # if not entry.location or len(entry.location.strip()) < 3:
            #     incomplete_fields.append('location')
            
            # DISABLED: Duration field check (can be enabled later if needed)
            # if (entry.duty_status and entry.duty_status.lower() in ['driving', 'on_duty'] and 
            #     (not entry.hours or entry.hours <= 0)):
            #     incomplete_fields.append('duration')
            
            if incomplete_fields:
                rule = self.classification_system.get_violation_rule(ViolationType.FORM_MANNER_INCOMPLETE_ENTRIES)
                if rule:
                    penalty = self._format_penalty(rule.penalty_range)
                    
                    self._add_violation(Violation(
                        date=entry.date,
                        violation_type=ViolationType.FORM_MANNER_INCOMPLETE_ENTRIES,
                        description=f"Incomplete entry fields: {', '.join(incomplete_fields)}",
                        severity=rule.severity,
                        penalty=penalty,
                        cfr_section=rule.cfr_section,
                        details={'incomplete_fields': incomplete_fields, 'entry_time': entry.start_time}
                    ))
    
    def _check_log_falsification_violations(self):
        """Check for log falsification with proper date/time handling"""
        # Use the enhanced method that processes chronological entries across days
        # This properly handles day transitions and detects real impossibilities
        self._check_falsification_with_proper_datetime_analysis()

    def _check_driving_off_duty_violations(self):
        """Check for driving while off duty - corrected logic"""
        # Check each off-duty entry against the NEXT entry to see if location changed
        for i, entry in enumerate(self.processed_entries):
            if entry.duty_status and any(status in entry.duty_status.lower() for status in ['duty', 'sleeper', 'personal']):
                # Get the next entry to compare locations
                if i + 1 < len(self.processed_entries):
                    next_entry = self.processed_entries[i + 1]
                    
                    # Check if location changed from current off-duty position to next position
                    current_location = entry.location.strip() if entry.location else ''
                    next_location = next_entry.location.strip() 
                    if next_entry.location:
                        next_location = next_location
                    else:
                        if i + 2 < len(self.processed_entries):
                            next_location = self.processed_entries[i + 2].location.strip() if self.processed_entries[i + 2].location else ''
                        else:
                            next_location = ''
                    
                    # If locations are different and both exist, driver moved while off duty
                    if (current_location and next_location and 
                        current_location != next_location):
                        
                        # Skip if this is a legitimate break with explicit break remarks
                        remarks = (entry.remarks or '').lower()
                        if 'break' in remarks or 'rest' in remarks or 'meal' in remarks:
                            continue  # Skip legitimate breaks
                        
                        rule = self.classification_system.get_violation_rule(ViolationType.DRIVING_OFF_DUTY)
                        if rule:
                            penalty = self._format_penalty(rule.penalty_range)
                            if 'personal' in entry.duty_status.lower():
                                violation_type=ViolationType.PERSONAL_CONVEYANCE_MISUSE
                            elif 'off' in entry.duty_status.lower():
                                violation_type=ViolationType.DRIVING_OFF_DUTY
                            else:
                                violation_type=ViolationType.DISTANCE_CHANGE_WITHOUT_DRIVING_TIME
                            
                            self._add_violation(Violation(
                                date=entry.date,
                                violation_type=violation_type,
                                description=f"Location changed while marked {entry.duty_status}: {current_location} → {next_location}",
                                severity=rule.severity,
                                penalty=penalty,
                                cfr_section=rule.cfr_section,
                                details={
                                    'current_location': current_location,
                                    'next_location': next_location,
                                    'hours': entry.hours,
                                    'remarks': entry.remarks,
                                    'next_entry_time': next_entry.start_time
                                }
                            ))
    
    def _check_personal_conveyance_violations(self):
        """Check for personal conveyance misuse"""
        pass
    
    def _check_geographic_implausible_violations(self):
        """Check for geographically implausible movements using proper datetime analysis"""
        # Get all entries chronologically across all days
        all_entries = []
        
        # Convert processed entries to datetime-sortable format
        for entry in self.processed_entries:
            if entry.date and entry.start_time and entry.location:
                try:
                    start_datetime = self._parse_datetime(entry.date, entry.start_time)
                    all_entries.append({
                        'date': entry.date,
                        'start_time': entry.start_time,
                        'end_time': entry.end_time,
                        'start_datetime': start_datetime,
                        'odometer': entry.odometer,
                        'location': entry.location,
                        'duty_status': entry.duty_status,
                        'hours': entry.hours,
                        'entry_obj': entry
                    })
                except:
                    continue
        
        if len(all_entries) < 2:
            return
        
        # Sort by actual datetime
        all_entries.sort(key=lambda x: x['start_datetime'])
        
        # Check for implausible movements
        for i in range(1, len(all_entries)):
            prev_entry = all_entries[i-1]
            curr_entry = all_entries[i]
            
            if (prev_entry['location'] and curr_entry['location'] and 
                prev_entry['location'] != curr_entry['location']):
                
                # Check for implausible movement
                if self._is_movement_implausible_with_time(prev_entry, curr_entry):
                    rule = self.classification_system.get_violation_rule(ViolationType.GEOGRAPHIC_IMPLAUSIBLE)
                    if rule:
                        penalty = self._format_penalty(rule.penalty_range)
                        
                        # Calculate time difference
                        time_diff = curr_entry['start_datetime'] - prev_entry['start_datetime']
                        time_diff_hours = time_diff.total_seconds() / 3600
                        
                        self._add_violation(Violation(
                            date=curr_entry['date'],
                            violation_type=ViolationType.GEOGRAPHIC_IMPLAUSIBLE,
                            description=f"Implausible movement from {prev_entry['location']} to {curr_entry['location']} in {time_diff_hours:.1f} hours",
                            severity=rule.severity,
                            penalty=penalty,
                            cfr_section=rule.cfr_section,
                            details={
                                'from_location': prev_entry['location'],
                                'to_location': curr_entry['location'],
                                'from_time': prev_entry['start_time'],
                                'to_time': curr_entry['start_time'],
                                'time_difference_hours': time_diff_hours,
                                'from_date': prev_entry['date'],
                                'to_date': curr_entry['date']
                            }
                        ))
    
    def _is_movement_implausible_with_time(self, prev_entry: Dict, curr_entry: Dict) -> bool:
        """Check if movement between entries is geographically implausible with proper time analysis"""
        try:
            
            # Calculate time difference
            time_diff = curr_entry['start_datetime'] - prev_entry['start_datetime']
            time_diff_hours = time_diff.total_seconds() / 3600

            if prev_entry['odometer'] and curr_entry['odometer'] and time_diff_hours > 0:
                prev_distance = int(re.sub(r"[^\d]", "", prev_entry['odometer'])) 
                curr_distance = int(re.sub(r"[^\d]", "", curr_entry['odometer'])) 
            
            if prev_distance and curr_distance:
                distance_change = abs(curr_distance - prev_distance)
                
                # If distance change is more than 500 miles in less than 8 hours, implausible
                if distance_change / time_diff_hours > 100:
                    return True
            
            return False
            
        except Exception as e:
            return False
    
    def _check_missing_duty_status_violations(self):
        """Check for missing duty status records"""
        for entry in self.processed_entries:
            if not entry.duty_status or entry.duty_status.strip() == '':
                rule = self.classification_system.get_violation_rule(ViolationType.MISSING_DUTY_STATUS)
                penalty = self._format_penalty(rule.penalty_range)
                
                self._add_violation(Violation(
                    date=entry.date,
                    violation_type=ViolationType.MISSING_DUTY_STATUS,
                    description=f"Missing duty status record for {entry.date}",
                    severity=rule.severity,
                    penalty=penalty,
                    cfr_section=rule.cfr_section,
                    details={'location': entry.location}
                ))
    
    def _check_comprehensive_violations_non_hos(self, extracted_data: Dict):
        """Enhanced violation detection based on extracted data patterns - EXCLUDING HOS (handled separately)"""
        
        # Check for fuel-related violations in driver logs
        self._check_fuel_violations_in_logs(extracted_data)
        
        # Check for form and manner violations
        self._check_form_violations_in_logs(extracted_data)
        
        # NOTE: HOS violations are now handled by the corrected methods above
    
    def _check_fuel_violations_in_logs(self, extracted_data: Dict):
        """Check for fuel-related violations within driver log data - DISABLED (handled by main method)"""
        # This method is now disabled to avoid duplicate fuel violation detection
        # All fuel violations are handled by _check_fuel_off_duty_violations() method
        pass
    
    def _check_form_violations_in_logs(self, extracted_data: Dict):
        """Check for form and manner violations in driver logs"""
        driver_logs = extracted_data.get('driver_logs', [])
        
        for log in driver_logs:
            entries = log.get('entries', [])
            
            for entry in entries:
                missing_fields = []
                
                # Check required fields
                if not entry.get('date'):
                    missing_fields.append('date')
                if not entry.get('duty_status'):
                    missing_fields.append('duty_status')
                if not entry.get('location'):
                    missing_fields.append('location')
                
                if missing_fields:
                    rule = self.classification_system.get_violation_rule(ViolationType.FORM_MANNER_MISSING_FIELDS)
                    if rule:
                        penalty = self._format_penalty(rule.penalty_range)
                        
                        self._add_violation(Violation(
                            date=entry.get('date', 'Unknown'),
                            violation_type=ViolationType.FORM_MANNER_MISSING_FIELDS,
                            description=f"Missing required fields: {', '.join(missing_fields)}",
                            severity=rule.severity,
                            penalty=penalty,
                            cfr_section=rule.cfr_section,
                            details={'missing_fields': missing_fields}
                        ))
    
    # OLD METHOD REMOVED - HOS violations now handled by corrected methods above
    
    def _check_30_minute_break_violations_corrected(self, classification):
        """Check for 30-minute break requirement - CORRECTED to find ALL violations"""
        # Get all entries sorted chronologically
        all_entries = self._get_chronological_entries()
        if not all_entries:
            return
        
        # Track consecutive driving periods and break accumulation
        consecutive_driving_hours = 0
        driving_start_entry = None
        violations_found = []  # Track violations to avoid duplicates
        
        # Track consecutive non-driving time for break accumulation
        consecutive_break_hours = 0
        
        for entry in all_entries:
            duty_status = entry.duty_status.lower() if entry.duty_status else ''
            hours = entry.hours or 0
            
            if 'driving' in duty_status:
                # Reset break accumulation when we start driving
                consecutive_break_hours = 0
                
                # Continue or start driving period
                if consecutive_driving_hours == 0:
                    driving_start_entry = entry
                consecutive_driving_hours += hours
                
                # Check if we've driven 8+ hours without a 30-minute break
                if consecutive_driving_hours >= 8.0:
                    # Create unique violation key to avoid duplicates
                    violation_key = f"{driving_start_entry.date}_{driving_start_entry.start_time}_{entry.date}_{entry.start_time}"
                    
                    if violation_key not in violations_found:
                        violations_found.append(violation_key)
                        
                        rule = self.classification_system.get_violation_rule(ViolationType.HOS_30_MINUTE_BREAK)
                        if rule:
                            penalty = self._format_penalty(rule.penalty_range)
                            
                            self._add_violation(Violation(
                                date=entry.date,
                                violation_type=ViolationType.HOS_30_MINUTE_BREAK,
                                description=f"Missing 30-minute break after {self._format_hours_readable(consecutive_driving_hours)} of consecutive driving",
                                severity=rule.severity,
                                penalty=penalty,
                                cfr_section=rule.cfr_section,
                                details={
                                    'consecutive_driving_hours': self._format_hours_readable(consecutive_driving_hours),
                                    'required_break_minutes': "30min",
                                    'driving_start_date': driving_start_entry.date,
                                    'driving_start_time': driving_start_entry.start_time,
                                    'violation_date': entry.date,
                                    'violation_time': entry.start_time
                                }
                            ))
            else:
                consecutive_break_hours += hours
                if consecutive_break_hours >= 0.5:  # 30 minutes = 0.5 hours
                    # Reset consecutive driving after accumulated 30+ minute break
                    consecutive_driving_hours = 0
                    driving_start_entry = None
    
    def _check_falsification_with_proper_datetime_analysis(self):
        """Check for log falsification using proper date/time analysis"""
        # Get all entries chronologically across all days
        all_entries = []
        
        # Convert processed entries to datetime-sortable format
        for entry in self.processed_entries:
            if entry.date and entry.start_time and entry.end_time:
                try:
                    # Create full datetime objects for proper comparison
                    start_datetime = self._parse_datetime(entry.date, entry.start_time)
                    end_datetime = self._parse_datetime(entry.date, entry.end_time)
                    
                    # Handle day transitions (end time might be next day)
                    if end_datetime < start_datetime:
                        # Add one day to end_datetime
                        from datetime import timedelta
                        end_datetime += timedelta(days=1)
                    
                    all_entries.append({
                        'date': entry.date,
                        'start_time': entry.start_time,
                        'end_time': entry.end_time,
                        'start_datetime': start_datetime,
                        'end_datetime': end_datetime,
                        'duty_status': entry.duty_status,
                        'location': entry.location,
                        'entry_obj': entry
                    })
                except Exception as e:
                    # Skip entries with parsing errors
                    continue
        
        if not all_entries:
            return
        
        # Sort by actual datetime
        all_entries.sort(key=lambda x: x['start_datetime'])
        
        # Check for real impossibilities
        for i in range(1, len(all_entries)):
            prev_entry = all_entries[i-1]
            curr_entry = all_entries[i]
            
            # Check for overlapping times (previous entry ends after current entry starts)
            if prev_entry['end_datetime'] > curr_entry['start_datetime']:
                # Calculate overlap duration
                overlap_seconds = (prev_entry['end_datetime'] - curr_entry['start_datetime']).total_seconds()
                
                # Only flag significant overlaps (more than 1 minute) to avoid minor ELD timing issues
                if overlap_seconds > 60:  # More than 1 minute overlap
                    rule = self.classification_system.get_violation_rule(ViolationType.LOG_FALSIFICATION)
                    if rule:
                        penalty = self._format_penalty(rule.penalty_range)
                        overlap_minutes = overlap_seconds / 60
                        
                        self._add_violation(Violation(
                            date=curr_entry['date'],
                            violation_type=ViolationType.LOG_FALSIFICATION,
                            description=f"Overlapping log entries: {overlap_minutes:.1f} minute overlap between {prev_entry['end_time']} and {curr_entry['start_time']}",
                            severity=rule.severity,
                            penalty=penalty,
                            cfr_section=rule.cfr_section,
                            details={
                                'prev_end': prev_entry['end_time'],
                                'curr_start': curr_entry['start_time'],
                                'overlap_minutes': overlap_minutes,
                                'prev_date': prev_entry['date'],
                                'curr_date': curr_entry['date']
                            }
                        ))
            
            # Check for exact duplicate entries (but exclude legitimate all-day periods)
            if self._is_exact_duplicate_entry(prev_entry, curr_entry):
                # Check if this is a legitimate all-day sleeper berth or off-duty period
                if not self._is_legitimate_all_day_period(prev_entry, curr_entry):
                    rule = self.classification_system.get_violation_rule(ViolationType.LOG_FALSIFICATION)
                    if rule:
                        penalty = self._format_penalty(rule.penalty_range)
                        
                        self._add_violation(Violation(
                            date=curr_entry['date'],
                            violation_type=ViolationType.LOG_FALSIFICATION,
                            description=f"Duplicate log entry: {curr_entry['start_time']} {curr_entry['duty_status']} at {curr_entry['location']}",
                            severity=rule.severity,
                            penalty=penalty,
                            cfr_section=rule.cfr_section,
                            details={
                                'duplicate_time': curr_entry['start_time'],
                                'duplicate_status': curr_entry['duty_status'],
                                'duplicate_location': curr_entry['location']
                            }
                        ))
    
    def _parse_datetime(self, date: str, time: str):
        """Parse date and time into datetime object"""
        try:
            from datetime import datetime
            import re
            
            # Parse date from "8/14" format
            if '/' in date:
                parts = date.split('/')
                if len(parts) == 2:
                    month = int(parts[0])
                    day = int(parts[1])
                    year = 2025  # Assume current year
                else:
                    month, day, year = 8, 1, 2025
            else:
                month, day, year = 8, 1, 2025
            
            # Parse time from "1:17:23 PM EDT" format
            time_match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)', time)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                second = int(time_match.group(3))
                ampm = time_match.group(4)
                
                # Convert to 24-hour format
                if ampm == 'PM' and hour != 12:
                    hour += 12
                elif ampm == 'AM' and hour == 12:
                    hour = 0
                
                return datetime(year, month, day, hour, minute, second)
            
            # Fallback
            return datetime(year, month, day, 0, 0, 0)
            
        except Exception as e:
            # Fallback to a default datetime
            from datetime import datetime
            return datetime(2025, 8, 1, 0, 0, 0)
    
    def _is_exact_duplicate_entry(self, prev_entry: Dict, curr_entry: Dict) -> bool:
        """Check for exact duplicate entries"""
        return (prev_entry['start_time'] == curr_entry['start_time'] and
                prev_entry['end_time'] == curr_entry['end_time'] and
                prev_entry['duty_status'] == curr_entry['duty_status'] and
                prev_entry['location'] == curr_entry['location'])
    
    def _is_legitimate_all_day_period(self, prev_entry: Dict, curr_entry: Dict) -> bool:
        """Check if duplicate entries represent legitimate all-day sleeper berth or off-duty periods"""
        try:
            # Check if both entries are 12:00:00 AM (start and end of day)
            is_midnight_start = '12:00:00 AM' in prev_entry['start_time']
            is_midnight_end = '12:00:00 AM' in curr_entry['end_time']
            
            # Check if duty status is sleeper berth or off duty
            duty_status = prev_entry['duty_status'].lower()
            is_rest_status = duty_status in ['sleeper_berth', 'off_duty']
            
            # Check if this spans across consecutive days
            prev_date = prev_entry['date']
            curr_date = curr_entry['date']
            
            # Parse dates to check if they're consecutive
            if '/' in prev_date and '/' in curr_date:
                try:
                    prev_parts = prev_date.split('/')
                    curr_parts = curr_date.split('/')
                    
                    if len(prev_parts) == 2 and len(curr_parts) == 2:
                        prev_month, prev_day = int(prev_parts[0]), int(prev_parts[1])
                        curr_month, curr_day = int(curr_parts[0]), int(curr_parts[1])
                        
                        # Check if consecutive days (same month, day+1) or (month+1, day 1)
                        is_consecutive = (
                            (prev_month == curr_month and curr_day == prev_day + 1) or
                            (curr_month == prev_month + 1 and prev_day >= 28 and curr_day == 1)
                        )
                        
                        # If it's midnight-to-midnight, rest status, and consecutive days, it's legitimate
                        if is_midnight_start and is_midnight_end and is_rest_status and is_consecutive:
                            return True
                except:
                    pass
            
            # Also check for same-day all-day periods (12:00 AM to 12:00 AM same day)
            if (is_midnight_start and is_midnight_end and is_rest_status and 
                prev_date == curr_date):
                return True
            
            return False
            
        except Exception as e:
            return False
    
    # OLD METHOD REMOVED - Replaced by corrected HOS violation methods above
    
    def _find_off_duty_period(self, entries: List[Dict], start_index: int) -> Tuple[Optional[int], Optional[int]]:
        """Find a continuous off-duty period starting from start_index"""
        if start_index >= len(entries):
            return None, None
        
        # Check if current entry is off-duty
        current_entry = entries[start_index]
        duty_status = current_entry.get('duty_status', '').lower()
        
        if duty_status not in ['off_duty', 'sleeper_berth']:
            return None, None
        
        # Find the end of the off-duty period
        off_duty_start = start_index
        off_duty_end = start_index
        
        for i in range(start_index + 1, len(entries)):
            entry = entries[i]
            status = entry.get('duty_status', '').lower()
            
            if status in ['off_duty', 'sleeper_berth']:
                off_duty_end = i
            else:
                break  # End of off-duty period
        
        return off_duty_start, off_duty_end
    
    def _analyze_duty_cycle(self, entries: List[Dict], cycle_start: int, prev_off_duty_hours: float):
        """Analyze a single duty cycle for HOS violations"""
        if cycle_start >= len(entries):
            return
        
        # Track the duty cycle
        cycle_driving_hours = 0
        cycle_on_duty_hours = 0
        cycle_start_time = entries[cycle_start].get('start_time', '')
        cycle_date = entries[cycle_start].get('date', '')
        
        # Find the end of this duty cycle (until next 10+ hour off-duty period)
        cycle_entries = []
        i = cycle_start
        
        while i < len(entries):
            entry = entries[i]
            duty_status = entry.get('duty_status', '').lower()
            duration_hours = entry.get('duration_hours', 0)
            
            cycle_entries.append(entry)
            
            # Count driving hours
            if 'driving' in duty_status:
                cycle_driving_hours += duration_hours
            
            # Count on-duty hours (driving + on_duty_not_driving)
            if duty_status in ['driving', 'on_duty_not_driving', 'on_duty']:
                cycle_on_duty_hours += duration_hours
            
            # Check if we've reached another significant off-duty period
            if duty_status in ['off_duty', 'sleeper_berth'] and duration_hours >= 10.0:
                break  # End of duty cycle
            
            i += 1
        
        # Calculate the total time span of the duty cycle
        if cycle_entries:
            cycle_end_time = cycle_entries[-1].get('end_time', '')
            total_cycle_hours = self._calculate_time_span(cycle_start_time, cycle_end_time, cycle_date)
            
            # Check 11-hour driving violation
            if cycle_driving_hours > 11.0:
                rule = self.classification_system.get_violation_rule(ViolationType.HOS_11_HOUR_DRIVING)
                if rule:
                    penalty = self._format_penalty(rule.penalty_range)
                    self._add_violation(Violation(
                        date=cycle_date,
                        violation_type=ViolationType.HOS_11_HOUR_DRIVING,
                        description=f"Driving {cycle_driving_hours:.2f} hours exceeds 11-hour limit after {prev_off_duty_hours:.1f} hours off duty",
                        severity=rule.severity,
                        penalty=penalty,
                        cfr_section=rule.cfr_section,
                        details={
                            'actual_driving_hours': cycle_driving_hours, 
                            'limit': 11.0,
                            'previous_off_duty_hours': prev_off_duty_hours,
                            'cycle_start_time': cycle_start_time
                        }
                    ))
            
            # Check 14-hour window violation (driving beyond 14th consecutive hour)
            if total_cycle_hours > 14.0 and cycle_driving_hours > 0:
                # Check if there was any driving after the 14th hour
                driving_after_14th_hour = self._check_driving_after_14th_hour(cycle_entries, cycle_start_time)
                
                if driving_after_14th_hour:
                    rule = self.classification_system.get_violation_rule(ViolationType.HOS_14_HOUR_WINDOW)
                    if rule:
                        penalty = self._format_penalty(rule.penalty_range)
                        self._add_violation(Violation(
                            date=cycle_date,
                            violation_type=ViolationType.HOS_14_HOUR_WINDOW,
                            description=f"Driving beyond 14th consecutive hour (cycle span: {total_cycle_hours:.2f} hours)",
                            severity=rule.severity,
                            penalty=penalty,
                            cfr_section=rule.cfr_section,
                            details={
                                'cycle_span_hours': total_cycle_hours,
                                'limit': 14.0,
                                'previous_off_duty_hours': prev_off_duty_hours,
                                'cycle_start_time': cycle_start_time,
                                'driving_hours_in_cycle': cycle_driving_hours
                            }
                        ))
    
    def _calculate_time_difference(self, start_entry: Dict, end_entry: Dict) -> float:
        """Calculate time difference between two entries in hours"""
        try:
            # Sum up all the duration_hours between start and end entries
            total_hours = 0
            start_time = start_entry.get('start_time', '')
            end_time = end_entry.get('end_time', '')
            
            # For continuous off-duty periods, sum the duration_hours
            total_hours = start_entry.get('duration_hours', 0) + end_entry.get('duration_hours', 0)
            
            return total_hours
        except:
            return 0.0
    
    def _calculate_time_span(self, start_time: str, end_time: str, date: str) -> float:
        """Calculate the time span of a duty cycle in hours"""
        try:
            # Parse time strings like "6:28:22 AM CDT" and "7:14:47 PM CDT"
            from datetime import datetime
            import re
            
            # Extract time parts (simplified parsing)
            start_match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)', start_time)
            end_match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)', end_time)
            
            if start_match and end_match:
                # Convert to 24-hour format
                start_hour = int(start_match.group(1))
                start_min = int(start_match.group(2))
                start_sec = int(start_match.group(3))
                start_ampm = start_match.group(4)
                
                end_hour = int(end_match.group(1))
                end_min = int(end_match.group(2))
                end_sec = int(end_match.group(3))
                end_ampm = end_match.group(4)
                
                # Convert to 24-hour format
                if start_ampm == 'PM' and start_hour != 12:
                    start_hour += 12
                elif start_ampm == 'AM' and start_hour == 12:
                    start_hour = 0
                    
                if end_ampm == 'PM' and end_hour != 12:
                    end_hour += 12
                elif end_ampm == 'AM' and end_hour == 12:
                    end_hour = 0
                
                # Calculate time difference
                start_total_minutes = start_hour * 60 + start_min + start_sec / 60
                end_total_minutes = end_hour * 60 + end_min + end_sec / 60
                
                # Handle day transition
                if end_total_minutes < start_total_minutes:
                    end_total_minutes += 24 * 60  # Add 24 hours
                
                time_diff_hours = (end_total_minutes - start_total_minutes) / 60
                return time_diff_hours
            
            return 0.0
        except:
            return 0.0
    
    def _check_driving_after_14th_hour(self, cycle_entries: List[Dict], cycle_start_time: str) -> bool:
        """Check if there was any driving after the 14th consecutive hour"""
        try:
            # Track cumulative time from cycle start
            cumulative_hours = 0
            
            for entry in cycle_entries:
                duration_hours = entry.get('duration_hours', 0)
                duty_status = entry.get('duty_status', '').lower()
                
                # If we're past 14 hours and this is driving, it's a violation
                if cumulative_hours > 14.0 and 'driving' in duty_status:
                    return True
                
                cumulative_hours += duration_hours
            
            return False
        except:
            return False
