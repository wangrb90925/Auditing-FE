"""
Daily Log Parser - For simple Driver's Daily Log PDFs

This module parses the simple Driver's Daily Log format (table-based).
Example: Alfred Wilson's log with columns: No., Status, Start (CDT), Duration, Location, Engine, Odo, CMV, Notes
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Any


class DailyLogParser:
    """Parser for simple Driver's Daily Log format"""
    
    def __init__(self):
        self.parsed_data = []
    
    def parse_daily_log(self, text_content: str, file_name: str, fuel_transactions: List[Dict] = None) -> Dict[str, Any]:
        """
        Parse Daily Log data directly from text content
        
        Args:
            text_content: Clean text from PDF
            file_name: Name of the file
            fuel_transactions: Optional list of fuel transactions to cross-reference
            
        Returns:
            Dict with structured driver log data matching Samsara format
        """
        print(f"[DAILY_LOG_PARSER] Starting parse for: {file_name}")
        
        # Extract driver information (same for all dates)
        driver_info = self._extract_driver_info(text_content)
        print(f"[DAILY_LOG_PARSER] Driver: {driver_info.get('driver_name')}")
        
        # Split by dates and extract entries for each date
        daily_entries = self._extract_entries_by_date(text_content)
        print(f"[DAILY_LOG_PARSER] Found {len(daily_entries)} date(s) with entries")
        
        # Cross-reference with fuel transactions if provided
        if fuel_transactions:
            print(f"[DAILY_LOG_PARSER] Cross-referencing with {len(fuel_transactions)} fuel transactions")
            daily_entries = self._merge_fuel_data(daily_entries, fuel_transactions)
        
        # Calculate totals
        totals = self._calculate_totals(daily_entries)
        
        # Get date range from daily entries
        date_range = self._get_date_range(daily_entries)
        
        result = {
            'file_name': file_name,
            'extraction_method': 'daily_log_direct',
            'extracted_at': datetime.now().isoformat(),
            'driver_name': driver_info.get('driver_name', 'Unknown'),
            'driver_id': driver_info.get('driver_id', ''),
            'carrier_name': driver_info.get('carrier_name', ''),
            'vehicle': driver_info.get('vehicle', ''),
            'start_date': date_range[0],
            'end_date': date_range[1],
            'daily_entries': daily_entries,
            'total_driving_hours': totals['driving_hours'],
            'total_on_duty_hours': totals['on_duty_hours'],
            'total_off_duty_hours': totals['off_duty_hours'],
            'violations': [],
            'violation_types': []
        }
        
        return result
    
    def _extract_log_date(self, text_content: str) -> str:
        """Extract log date (e.g., 'September 30, 2025')"""
        # Pattern: Log Date: September 30, 2025
        date_match = re.search(r'Log Date:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})', text_content)
        if date_match:
            return date_match.group(1).strip()
        return ''
    
    def _normalize_log_date(self, date_str: str) -> str:
        """Convert 'September 30, 2025' to '9/30' format"""
        month_map = {
            'january': '1', 'february': '2', 'march': '3', 'april': '4',
            'may': '5', 'june': '6', 'july': '7', 'august': '8',
            'september': '9', 'october': '10', 'november': '11', 'december': '12'
        }
        
        match = re.search(r'([A-Za-z]+)\s+(\d{1,2})', date_str)
        if match:
            month_name = match.group(1).lower()
            day = match.group(2)
            if month_name in month_map:
                return f"{month_map[month_name]}/{day}"
        
        return date_str
    
    def _get_date_range(self, daily_entries: List[Dict]) -> tuple:
        """Get start and end dates from daily entries"""
        if not daily_entries:
            return ('', '')
        
        dates = [entry['date'] for entry in daily_entries if entry.get('date')]
        if not dates:
            return ('', '')
        
        # For simple comparison, use the first and last (assuming chronological order)
        return (dates[0], dates[-1])
    
    def _extract_driver_info(self, text_content: str) -> Dict[str, str]:
        """Extract driver and vehicle information"""
        info = {}
        
        # Extract driver name (e.g., "Driver\nWilson, Alfred")
        driver_match = re.search(r'Driver[\s\n]+([A-Za-z]+,\s*[A-Za-z]+)', text_content)
        if driver_match:
            # Reverse from "Wilson, Alfred" to "Alfred Wilson"
            name_parts = driver_match.group(1).split(',')
            if len(name_parts) == 2:
                info['driver_name'] = f"{name_parts[1].strip()} {name_parts[0].strip()}"
            else:
                info['driver_name'] = driver_match.group(1).strip()
        
        # Extract driver license
        license_match = re.search(r'Driver License[\s\n]+([^\n]+)', text_content)
        if license_match:
            info['driver_id'] = license_match.group(1).strip()
        
        # Extract carrier
        carrier_match = re.search(r'Carrier and DOT#[\s\n]+([^\n]+)', text_content)
        if carrier_match:
            info['carrier_name'] = carrier_match.group(1).strip()
        
        # Extract Fleet ID (vehicle)
        fleet_match = re.search(r'Fleet ID[\s\n]+([^\n]+)', text_content)
        if fleet_match:
            info['vehicle'] = fleet_match.group(1).strip()
        
        return info
    
    def _extract_entries_by_date(self, text_content: str) -> List[Dict]:
        """
        Split content by log dates and extract entries for each date
        Returns list of {'date': str, 'entries': List[Dict]}
        """
        daily_entries = []
        
        # Find all "Log Date:" occurrences with their dates
        log_date_pattern = r'Log Date:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})'
        date_matches = list(re.finditer(log_date_pattern, text_content))
        
        if not date_matches:
            print("[DAILY_LOG_PARSER] No 'Log Date:' found, treating entire content as single date")
            # Fall back to extracting all entries as one date
            log_date = self._extract_log_date(text_content)
            entries = self._extract_table_entries(text_content, None)
            
            # Filter to keep only real duty status entries
            filtered_entries = self._filter_duty_status_only(entries)
            
            if filtered_entries:
                return [{
                    'date': self._normalize_log_date(log_date) if log_date else 'Unknown',
                    'entries': filtered_entries
                }]
            return []
        
        print(f"[DAILY_LOG_PARSER] Found {len(date_matches)} log date(s)")
        
        # Process each date section
        for i, match in enumerate(date_matches):
            log_date = match.group(1)
            normalized_date = self._normalize_log_date(log_date)
            print(f"[DAILY_LOG_PARSER] Processing date: {log_date} -> {normalized_date}")
            
            # Get the text for this date section
            # From current match to next match (or end of file)
            start_pos = match.end()
            if i + 1 < len(date_matches):
                end_pos = date_matches[i + 1].start()
            else:
                end_pos = len(text_content)
            
            date_section = text_content[start_pos:end_pos]
            
            # Extract entries for this date
            entries = self._extract_table_entries(date_section, log_date)
            
            # Filter to keep only real duty status entries (exclude system/diagnostic events)
            filtered_entries = self._filter_duty_status_only(entries)
            
            if filtered_entries:
                daily_entries.append({
                    'date': normalized_date,
                    'entries': filtered_entries
                })
                print(f"[DAILY_LOG_PARSER] Date {normalized_date}: {len(filtered_entries)} duty status entries (filtered from {len(entries)} total)")
            else:
                print(f"[DAILY_LOG_PARSER] Date {normalized_date}: No duty status entries found")
        
        return daily_entries
    
    def _filter_duty_status_only(self, entries: List[Dict]) -> List[Dict]:
        """
        Filter entries to keep only real duty statuses (exclude system/diagnostic events)
        
        Keep: driving, on_duty, off_duty, sleeper_berth, personal_conveyance
        Exclude: data_diagnostic, engine_power_up, engine_shutdown, cert, 
                 intermediate_location, yard_move, eld_malfunction, etc.
        """
        valid_statuses = {'driving', 'on_duty', 'off_duty', 'sleeper_berth', 'personal_conveyance'}
        
        filtered = []
        for entry in entries:
            duty_status = entry.get('duty_status', '')
            if duty_status in valid_statuses:
                filtered.append(entry)
            else:
                print(f"[DAILY_LOG_PARSER] Filtered out: {duty_status} at {entry.get('start_time', 'unknown')}")
        
        # Recalculate end times after filtering (since we removed intermediate entries)
        filtered = self._calculate_end_times(filtered)
        
        return filtered
    
    def _extract_table_entries(self, text_content: str, log_date: str = None) -> List[Dict]:
        """Extract entries from the table by splitting on row numbers"""
        entries = []
        
        # Find the table section - look for the header row
        table_match = re.search(r'No\.\s*Status\s*Start.*?Duration.*?Location', text_content, re.DOTALL)
        if not table_match:
            print("[DAILY_LOG_PARSER] Could not find table header")
            return entries
        
        # Get text after the table header
        table_start = table_match.end()
        
        # Find where the table ends (before "Unidentified events" section)
        unidentified_match = re.search(r'Unidentified\s+events?', text_content[table_start:], re.IGNORECASE)
        if unidentified_match:
            table_end = table_start + unidentified_match.start()
            print(f"[DAILY_LOG_PARSER] Stopping at 'Unidentified events' section (position {table_end})")
        else:
            table_end = len(text_content)
        
        table_text = text_content[table_start:table_end]
        
        # Split by row numbers (lines that start with a digit followed by whitespace/newline)
        # Pattern: start of line or after newline, followed by digit(s), then whitespace
        row_pattern = r'(?:^|\n)(\d+)\s*\n'
        rows = re.split(row_pattern, table_text)
        
        # The split creates: ['', '1', 'content1', '2', 'content2', ...]
        # So we process in pairs: row_number, row_content
        for i in range(1, len(rows), 2):
            if i + 1 < len(rows):
                row_num = rows[i]
                row_content = rows[i + 1]
                
                # Stop if we've gone past the table (e.g., reached a new section)
                row_content_upper = row_content.upper()
                if any(marker in row_content_upper for marker in [
                    'CERTIFICATION', 'PAGE ', 'UNIDENTIFIED', 
                    'DRIVER SIGNATURE', 'REMARKS'
                ]):
                    print(f"[DAILY_LOG_PARSER] Stopping at end-of-table marker in row {row_num}")
                    break
                
                # Parse this row
                entry = self._parse_table_row(row_num, row_content)
                if entry and entry.get('start_time'):
                    entries.append(entry)
                    print(f"[DAILY_LOG_PARSER] Row {row_num}: {entry.get('duty_status')} at {entry.get('start_time')}")
        
        # Don't calculate end times here - will be done after filtering
        return entries
    
    def _parse_table_row(self, row_num: str, row_content: str) -> Dict:
        """Parse a single table row"""
        entry = {}
        
        # Clean up the content - normalize whitespace
        row_content = row_content.strip()
        lines = [line.strip() for line in row_content.split('\n') if line.strip()]
        
        if not lines:
            return {}
        
        # First line usually contains: Status
        # Look for status keywords
        status_line = '\n'.join(lines[:3])  # Check first few lines for status
        duty_status = self._extract_status(status_line)
        if not duty_status:
            # Skip non-duty-status rows (like Data Diagnostic, Engine Power Up, etc.)
            # But still try to process them
            duty_status = self._extract_any_status(status_line)
            if not duty_status:
                return {}
        
        entry['duty_status'] = duty_status
        
        # Find start time (pattern: 12:00:00 AM or 1:04:45 PM)
        time_match = re.search(r'(\d{1,2}:\d{2}:\d{2})\s*(AM|PM)', row_content)
        if time_match:
            entry['start_time'] = f"{time_match.group(1)} {time_match.group(2)} CDT"
        else:
            return {}  # Skip entries without valid time
        
        # Extract duration - multiple possible formats:
        # - "10 hr 37 min 37 sec" (hours, minutes, seconds)
        # - "12 min 33 sec" (minutes and seconds only)
        # - "46 sec" (seconds only)
        # - "2 hr" (hours only)
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Try to extract hours
        hour_match = re.search(r'(\d+)\s*hr', row_content, re.IGNORECASE)
        if hour_match:
            hours = int(hour_match.group(1))
        
        # Try to extract minutes
        min_match = re.search(r'(\d+)\s*min', row_content, re.IGNORECASE)
        if min_match:
            minutes = int(min_match.group(1))
        
        # Try to extract seconds (can be on new line like "37\nsec")
        sec_match = re.search(r'(\d+)\s*[\n\s]*sec', row_content, re.IGNORECASE)
        if sec_match:
            seconds = int(sec_match.group(1))
        
        # Build duration string
        if hours > 0 or minutes > 0 or seconds > 0:
            duration_parts = []
            if hours > 0:
                duration_parts.append(f"{hours}h")
            if minutes > 0:
                duration_parts.append(f"{minutes}m")
            if seconds > 0:
                duration_parts.append(f"{seconds}s")
            
            entry['duration'] = ' '.join(duration_parts)
            entry['duration_hours'] = round(hours + minutes/60 + seconds/3600, 2)
        else:
            entry['duration'] = ''
            entry['duration_hours'] = 0.0
        
        # Extract location - multiple possible formats:
        # 1. "8.2 mi NE of Ville \nPlatte, LA" or "2.7 mi NW of\nPlaquemine, LA"
        # 2. "Tulsa, OK" or "Broken Arrow, \nOK"
        # 3. "Lafayette, LA" (simple city, state)
        
        # First try distance-based location (most specific)
        location_match = re.search(r'(\d+\.?\d*)\s*mi\s+([NSEW]+)\s+(?:of\s+)?(.+?),\s*([A-Z]{2})', row_content, re.DOTALL)
        if location_match:
            # Distance-based location
            distance = location_match.group(1)
            direction = location_match.group(2)
            city = location_match.group(3).replace('\n', ' ').strip()
            state = location_match.group(4)
            entry['location'] = f"{distance} mi {direction} of {city}, {state}"
        else:
            # Try city, state format - but exclude duty status keywords
            # Find ALL potential city, state matches
            # Note: Removed \b at end to handle cases like "TX37048" (no space before number)
            city_matches = list(re.finditer(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s*\n?\s*([A-Z]{2})(?![a-z])', row_content))
            
            # Filter out duty status keywords
            duty_keywords = ['Driving', 'Driver', 'Sleeper', 'Personal', 'Conveyance', 'On', 'Duty', 'Off', 'Data', 'Diagnostic', 'Engine', 'Int', 'Location']
            duty_phrases = ['On Duty', 'Off Duty', 'Data Diagnostic', 'Int Location', 'Personal Conveyance']
            
            for match in city_matches:
                city = match.group(1)
                state = match.group(2)
                
                # Skip if city is a duty status keyword or phrase
                if city in duty_keywords or city in duty_phrases:
                    continue
                
                # Also skip if city is composed entirely of duty keywords
                city_words = city.split()
                if all(word in duty_keywords for word in city_words):
                    continue
                
                # Skip if state looks like it's part of another word (like "ELD")
                # Only skip if followed by a lowercase letter (not digit, space, or uppercase)
                end_pos = match.end()
                if end_pos < len(row_content):
                    next_char = row_content[end_pos]
                    # Skip only if next char is a lowercase letter (like "D" in "ELD" -> skip "EL")
                    if next_char.islower():
                        continue
                
                # This is likely a real location
                entry['location'] = f"{city}, {state}"
                break
            else:
                # No valid location found
                entry['location'] = ''
        
        # Extract CMV/vehicle (3-digit number like "006")
        cmv_match = re.search(r'\b(\d{3})\b', row_content)
        if cmv_match:
            entry['vehicle'] = cmv_match.group(1)
        else:
            entry['vehicle'] = ''
        
        # Extract odometer (pattern: "866,687 (508)" or "870,286")
        odo_match = re.search(r'(\d{1,3},\d{3}(?:,\d{3})?)\s*(?:\([\d,]+\))?', row_content)
        if odo_match:
            entry['odometer'] = odo_match.group(1)
        else:
            entry['odometer'] = ''
        
        # Extract notes/remarks from remaining text
        entry['remarks'] = self._extract_remarks(row_content)
        entry['raw_line'] = row_content
        entry['end_time'] = ''  # Will be calculated later
        
        return entry
    
    def _extract_status(self, text: str) -> str:
        """Extract duty status from text"""
        # Main duty statuses we care about for HOS
        text_upper = text.upper()
        
        # Check in order of specificity
        if 'DRIVING' in text_upper:
            return 'driving'
        elif 'ON DUTY' in text_upper:
            return 'on_duty'
        elif 'OFF DUTY' in text_upper:
            return 'off_duty'
        elif 'SLEEPER' in text_upper or 'SLEEPER BERTH' in text_upper:
            return 'sleeper_berth'
        
        return ''
    
    def _extract_any_status(self, text: str) -> str:
        """Extract any status including non-duty statuses"""
        text_upper = text.upper()
        
        # Try to extract main duty statuses first
        duty_status = self._extract_status(text)
        if duty_status:
            return duty_status
        
        # Check for other statuses (these won't count for HOS but we should record them)
        if 'DATA' in text_upper and 'DIAGNOSTIC' in text_upper:
            return 'data_diagnostic'
        elif 'ENGINE' in text_upper and 'POWER' in text_upper:
            return 'engine_power_up'
        elif 'ENGINE' in text_upper and 'SHUTDOWN' in text_upper:
            return 'engine_shutdown'
        elif 'ELD' in text_upper and 'MALFUNCTION' in text_upper:
            return 'eld_malfunction'
        elif 'INT LOCATION' in text_upper or 'INTERMEDIATE LOCATION' in text_upper:
            return 'intermediate_location'
        elif 'CERT' in text_upper:
            return 'certification'
        elif 'YM STARTED' in text_upper or 'YARD MOVE' in text_upper:
            return 'yard_move'
        
        return ''
    
    def _extract_remarks(self, text: str) -> str:
        """Extract notes/remarks from row text"""
        remarks = []
        text_upper = text.upper()
        
        # Common remarks
        remark_keywords = [
            'POST-TRIP INSPECTION', 'PRE-TRIP INSPECTION', 'LOADING', 'UNLOADING',
            'BREAK', 'FUEL', 'TYING DOWN LOAD', 'LOAD', 'OFF DUTY', 'SLEEP',
            'MEAL', 'REST', 'MAINTENANCE'
        ]
        
        for keyword in remark_keywords:
            if keyword in text_upper:
                # Get the original case version
                match = re.search(re.escape(keyword.title()), text, re.IGNORECASE)
                if match:
                    remarks.append(match.group(0))
        
        return ', '.join(set(remarks))  # Remove duplicates
    
    def _calculate_end_times(self, entries: List[Dict]) -> List[Dict]:
        """Calculate end times based on next entry's start time"""
        for i in range(len(entries)):
            if i + 1 < len(entries):
                # End time is the next entry's start time
                entries[i]['end_time'] = entries[i + 1]['start_time']
            else:
                # Last entry - calculate from duration or use end of day
                if entries[i].get('duration_hours', 0) > 0:
                    end_time = self._add_duration_to_time(
                        entries[i]['start_time'],
                        entries[i]['duration_hours']
                    )
                    entries[i]['end_time'] = end_time
                else:
                    # Default to end of day
                    entries[i]['end_time'] = '11:59:59 PM CDT'
        
        return entries
    
    def _add_duration_to_time(self, time_str: str, duration_hours: float) -> str:
        """Add duration to a time string"""
        try:
            # Parse time (format: "12:00:00 AM CDT")
            time_parts = time_str.split()
            if len(time_parts) >= 2:
                time_only = f"{time_parts[0]} {time_parts[1]}"
                timezone = time_parts[2] if len(time_parts) > 2 else 'CDT'
                
                # Parse the time
                dt = datetime.strptime(time_only, '%I:%M:%S %p')
                
                # Add duration
                dt += timedelta(hours=duration_hours)
                
                # Format back
                return f"{dt.strftime('%I:%M:%S %p')} {timezone}"
        except Exception as e:
            print(f"[DAILY_LOG_PARSER] Error calculating end time: {e}")
        
        return time_str
    
    def _calculate_totals(self, daily_entries: List[Dict]) -> Dict[str, float]:
        """Calculate total hours by duty status"""
        totals = {
            'driving_hours': 0.0,
            'on_duty_hours': 0.0,
            'off_duty_hours': 0.0,
            'sleeper_hours': 0.0
        }
        
        for day in daily_entries:
            for entry in day.get('entries', []):
                duration_hours = entry.get('duration_hours', 0.0)
                status = entry.get('duty_status', '')
                
                if status == 'driving':
                    totals['driving_hours'] += duration_hours
                    totals['on_duty_hours'] += duration_hours  # Driving is also on-duty
                elif status == 'on_duty':
                    totals['on_duty_hours'] += duration_hours
                elif status == 'off_duty':
                    totals['off_duty_hours'] += duration_hours
                elif status == 'sleeper_berth':
                    totals['sleeper_hours'] += duration_hours
        
        return totals
    
    def _merge_fuel_data(self, daily_entries: List[Dict], fuel_transactions: List[Dict]) -> List[Dict]:
        """
        Cross-reference fuel transactions with log entries and update remarks
        
        Args:
            daily_entries: List of daily entry dictionaries (date + entries list)
            fuel_transactions: List of fuel transaction dictionaries
            
        Returns:
            Updated daily_entries with fuel information in remarks
        """
        updated_count = 0
        
        # Flatten all entries for easier processing
        all_log_entries = []
        for day in daily_entries:
            for entry in day.get('entries', []):
                entry['_parent_date'] = day.get('date')  # Track which date this belongs to
                all_log_entries.append(entry)
        
        # Cross-reference each fuel transaction
        for fuel in fuel_transactions:
            fuel_date = fuel.get('date', '')  # Format: MM/DD/YYYY
            fuel_time = fuel.get('time', '').strip()  # Format: HH:MM:SS AM/PM CDT
            fuel_location = fuel.get('location', '')
            fuel_vendor = fuel.get('vendor', '')
            
            if not fuel_date or not fuel_time:
                continue
            
            # Normalize fuel time for comparison
            fuel_time_normalized = self._normalize_time_for_comparison(fuel_time)
            
            # Look for matching log entry
            for entry in all_log_entries:
                entry_date = entry.get('_parent_date', '')  # Format: 9/30
                entry_start_time = entry.get('start_time', '')  # Format: 12:34:06 PM CDT
                entry_end_time = entry.get('end_time', '')  # Format: 12:52:13 PM CDT
                entry_duration_hours = entry.get('duration_hours', 0)
                
                # Check if dates match
                dates_match = self._dates_match_for_merge(entry_date, fuel_date)
                
                if not dates_match:
                    continue
                
                # Check if fuel time falls WITHIN the log entry's time range (start to end)
                fuel_in_range = self._fuel_time_in_entry_range(
                    fuel_time_normalized, 
                    entry_start_time, 
                    entry_end_time,
                    entry_duration_hours
                )
                
                if fuel_in_range:
                    # Update remarks to include fuel information
                    current_remarks = entry.get('remarks', '')
                    
                    # Only add if "fuel" not already in remarks
                    if 'fuel' not in current_remarks.lower():
                        fuel_info = f"Fuel"
                        if fuel_location:
                            fuel_info += f" at {fuel_location}"
                        if fuel_vendor:
                            fuel_info += f" ({fuel_vendor})"
                        
                        # Append or set remarks
                        if current_remarks and current_remarks.strip():
                            entry['remarks'] = f"{current_remarks}, {fuel_info}"
                        else:
                            entry['remarks'] = fuel_info
                        
                        updated_count += 1
                        print(f"[FUEL_MERGE] ✓ Matched fuel transaction {fuel_date} {fuel_time} to log entry {entry_date} {entry_start_time}-{entry_end_time}")
                        print(f"[FUEL_MERGE]   Updated remarks: {entry['remarks']}")
                        break  # Move to next fuel transaction
        
        print(f"[FUEL_MERGE] Updated {updated_count} log entries with fuel information")
        
        # Clean up temporary parent_date field
        for entry in all_log_entries:
            entry.pop('_parent_date', None)
        
        return daily_entries
    
    def _normalize_time_for_comparison(self, time_str: str) -> tuple:
        """
        Normalize time string to (hour, minute) tuple for comparison
        
        Args:
            time_str: Time string (e.g., "12:34:06 PM CDT" or "09:03:00 PM CDT")
            
        Returns:
            Tuple of (hour_24, minute) or None
        """
        if not time_str:
            return None
        
        # Remove timezone abbreviations
        time_cleaned = re.sub(r'\s+(CDT|CST|EDT|EST|PDT|PST|MDT|MST)\s*$', '', time_str).strip()
        
        # Try to match time pattern: HH:MM:SS AM/PM
        match = re.search(r'(\d{1,2}):(\d{2})(?::\d{2})?\s*(AM|PM)', time_cleaned, re.IGNORECASE)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            am_pm = match.group(3).upper()
            
            # Convert to 24-hour format
            if am_pm == 'PM' and hour != 12:
                hour += 12
            elif am_pm == 'AM' and hour == 12:
                hour = 0
            
            return (hour, minute)
        
        return None
    
    def _dates_match_for_merge(self, date1: str, date2: str) -> bool:
        """
        Check if two date strings represent the same date
        
        Args:
            date1: First date (e.g., "9/30")
            date2: Second date (e.g., "09/30/2024")
            
        Returns:
            bool: True if dates match
        """
        if not date1 or not date2:
            return False
        
        # Extract month and day from both
        match1 = re.search(r'(\d{1,2})[/-](\d{1,2})', date1)
        match2 = re.search(r'(\d{1,2})[/-](\d{1,2})', date2)
        
        if match1 and match2:
            month1, day1 = int(match1.group(1)), int(match1.group(2))
            month2, day2 = int(match2.group(1)), int(match2.group(2))
            
            return month1 == month2 and day1 == day2
        
        return False
    
    def _times_close_for_merge(self, time1: tuple, time2: tuple, tolerance_minutes: int = 30) -> bool:
        """
        Check if two times are within tolerance
        
        Args:
            time1: Tuple of (hour, minute)
            time2: Tuple of (hour, minute)
            tolerance_minutes: Tolerance in minutes
            
        Returns:
            bool: True if times are close
        """
        if not time1 or not time2:
            return False
        
        # Calculate difference in minutes
        minutes1 = time1[0] * 60 + time1[1]
        minutes2 = time2[0] * 60 + time2[1]
        diff = abs(minutes1 - minutes2)
        
        return diff <= tolerance_minutes
    
    def _fuel_time_in_entry_range(self, fuel_time: tuple, entry_start_time: str, 
                                    entry_end_time: str, entry_duration_hours: float) -> bool:
        """
        Check if fuel time falls within the log entry's time range (start to end)
        
        Args:
            fuel_time: Tuple of (hour, minute) for fuel transaction
            entry_start_time: Entry start time string (e.g., "08:00:00 AM CDT")
            entry_end_time: Entry end time string (e.g., "10:15:00 AM CDT")
            entry_duration_hours: Duration in hours (e.g., 2.25)
            
        Returns:
            bool: True if fuel time falls within entry's time range
        """
        if not fuel_time:
            return False
        
        # Normalize entry start and end times
        start_time = self._normalize_time_for_comparison(entry_start_time)
        end_time = self._normalize_time_for_comparison(entry_end_time)
        
        # If we have end_time, check if fuel time is between start and end
        if end_time and start_time:
            fuel_minutes = fuel_time[0] * 60 + fuel_time[1]
            start_minutes = start_time[0] * 60 + start_time[1]
            end_minutes = end_time[0] * 60 + end_time[1]
            
            # Handle cases where end time crosses midnight (e.g., 11:00 PM to 2:00 AM)
            if end_minutes < start_minutes:
                # Crosses midnight
                return fuel_minutes >= start_minutes or fuel_minutes <= end_minutes
            else:
                # Normal case: check if fuel time is between start and end
                is_in_range = start_minutes <= fuel_minutes <= end_minutes
                
                if is_in_range:
                    print(f"[TIME_MATCH] ✓ Fuel time {fuel_time[0]:02d}:{fuel_time[1]:02d} is WITHIN entry range {start_time[0]:02d}:{start_time[1]:02d} - {end_time[0]:02d}:{end_time[1]:02d}")
                
                return is_in_range
        
        # Fallback: if no end_time, calculate it from start_time + duration
        if start_time and entry_duration_hours > 0:
            fuel_minutes = fuel_time[0] * 60 + fuel_time[1]
            start_minutes = start_time[0] * 60 + start_time[1]
            
            # Calculate end time in minutes
            duration_minutes = int(entry_duration_hours * 60)
            end_minutes = start_minutes + duration_minutes
            
            # Handle 24-hour wrap
            if end_minutes >= 1440:  # 24 hours = 1440 minutes
                end_minutes = end_minutes % 1440
                # Crosses midnight
                return fuel_minutes >= start_minutes or fuel_minutes <= end_minutes
            else:
                is_in_range = start_minutes <= fuel_minutes <= end_minutes
                
                if is_in_range:
                    print(f"[TIME_MATCH] ✓ Fuel time {fuel_time[0]:02d}:{fuel_time[1]:02d} is WITHIN calculated range {start_time[0]:02d}:{start_time[1]:02d} - {end_minutes//60:02d}:{end_minutes%60:02d}")
                
                return is_in_range
        
        # Last resort: use proximity check (within 30 minutes of start)
        print(f"[TIME_MATCH] Fallback: Using proximity check")
        return self._times_close_for_merge(fuel_time, start_time, tolerance_minutes=30)
