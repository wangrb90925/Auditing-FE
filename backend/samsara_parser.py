"""
Direct Samsara ELD Data Parser

This module directly parses Samsara ELD data without relying on AI,
since we have perfect structured data from the PDF extraction.
"""

import re
from datetime import datetime
from typing import Dict, List, Any

class SamsaraParser:
    """Direct parser for Samsara ELD data"""
    
    def __init__(self):
        self.parsed_data = []
    
    def parse_samsara_data(self, text_content: str, file_name: str) -> Dict[str, Any]:
        """
        Parse Samsara ELD data directly from text content
        
        Args:
            text_content: Clean text from PDF
            file_name: Name of the file
            
        Returns:
            Dict with structured driver log data
        """
        # Silent parsing - output only to JSON files
        
        # Extract driver information
        driver_info = self._extract_driver_info(text_content)
        
        # Extract daily entries with complete data
        daily_entries = self._extract_daily_entries(text_content)
        
        # Calculate totals
        totals = self._calculate_totals(daily_entries)
        
        result = {
            'file_name': file_name,
            'extraction_method': 'samsara_direct',
            'extracted_at': datetime.now().isoformat(),
            'driver_name': driver_info.get('driver_name', 'Unknown'),
            'driver_id': driver_info.get('driver_id', ''),
            'carrier_name': driver_info.get('carrier_name', ''),
            'vehicle': driver_info.get('vehicle', ''),
            'start_date': self._get_date_range(daily_entries)[0],
            'end_date': self._get_date_range(daily_entries)[1],
            'daily_entries': daily_entries,
            'total_driving_hours': totals['driving_hours'],
            'total_on_duty_hours': totals['on_duty_hours'],
            'total_off_duty_hours': totals['off_duty_hours'],
            'violations': [],
            'violation_types': []
        }
        
        # Results will be available in JSON files
        
        return result
    
    def _extract_driver_info(self, text_content: str) -> Dict[str, str]:
        """Extract driver and vehicle information"""
        info = {}
        
        # Extract driver name
        driver_match = re.search(r'Driver:\s*([^(]+)', text_content)
        if driver_match:
            info['driver_name'] = driver_match.group(1).strip()
        
        # Extract carrier name
        carrier_match = re.search(r'Carrier Name:\s*([^\n]+)', text_content)
        if carrier_match:
            info['carrier_name'] = carrier_match.group(1).strip()
        
        # Extract vehicle
        vehicle_match = re.search(r'Vehicles:\s*([^\n]+)', text_content)
        if vehicle_match:
            info['vehicle'] = vehicle_match.group(1).strip()
        
        # Extract driver license
        license_match = re.search(r'Driver License:\s*([^\n]+)', text_content)
        if license_match:
            info['driver_id'] = license_match.group(1).strip()
        
        return info
    
    def _extract_daily_entries(self, text_content: str) -> List[Dict]:
        """Extract daily entries with complete time, duration, and status data"""
        daily_entries = []
        
        # Split by date headers to process each day
        date_sections = re.split(r'\n(?=[A-Z][a-z]{2}, [A-Z][a-z]{2} \d{1,2})', text_content)
        
        for section in date_sections:
            if not section.strip():
                continue
            
            # Extract date from section header
            date_match = re.search(r'([A-Z][a-z]{2}, [A-Z][a-z]{2} \d{1,2})', section)
            if not date_match:
                continue
            
            date_str = date_match.group(1)
            # Processing date silently
            
            # Extract entries for this date
            entries = self._extract_entries_for_date(section, date_str)
            
            if entries:
                daily_entries.append({
                    'date': self._normalize_date(date_str),
                    'entries': entries
                })
                # Entries found for date
        
        return daily_entries
    
    def _extract_entries_for_date(self, section: str, date_str: str) -> List[Dict]:
        """Extract individual entries for a specific date"""
        entries = []
        
        # UNIVERSAL APPROACH: Handle both EDT and CDT time zones, different vehicle formats
        # Pattern supports: EDT, CDT, kENWORTH, numeric vehicles, missing odometers
        time_pattern = r'(\d{1,2}:\d{2}:\d{2})\s+(AM|PM)\s+(EDT|CDT)\s*-\s*(\d{1,2}:\d{2}:\d{2})\s+(AM|PM)\s+(EDT|CDT)\s+(\d+h?\s*\d*m?\s*\d*s?)\s+(DRIVING|ON DUTY|OFF DUTY|SLEEPER BERTH|PERSONAL CONVEYANCE)(?:\([^)]*\))?'
        
        # Find all time matches with their positions
        time_matches = []
        for match in re.finditer(time_pattern, section, re.IGNORECASE):
            time_matches.append({
                'match': match,
                'start_pos': match.start(),
                'end_pos': match.end(),
                'start_time': f"{match.group(1)} {match.group(2)} {match.group(3)}",  # Include timezone
                'end_time': f"{match.group(4)} {match.group(5)} {match.group(6)}",    # Include timezone
                'duration': match.group(7).strip(),
                'status': match.group(8).strip()
            })
        
        print(f"[DEBUG_SECTION] Found {len(time_matches)} time entries for {date_str}")
        
        # Process each time match and get text until next match
        for i, time_info in enumerate(time_matches):
            # Get text from end of current match to start of next match (or end of section)
            start_pos = time_info['end_pos']
            if i + 1 < len(time_matches):
                end_pos = time_matches[i + 1]['start_pos']
            else:
                # FIXED: For the last entry, look ahead to find more complete text
                # Find the next date section or end of meaningful content
                remaining_section = section[start_pos:]
                
                # Look for next date header or end markers
                next_date_match = re.search(r'\n[A-Z][a-z]{2}, [A-Z][a-z]{2} \d{1,2}', remaining_section)
                url_match = re.search(r'https://cloud\.samsara\.com', remaining_section)
                
                if next_date_match:
                    end_pos = start_pos + next_date_match.start()
                elif url_match:
                    end_pos = start_pos + url_match.start()
                else:
                    # Use the full remaining section
                    end_pos = len(section)
                
                print(f"[DEBUG_LAST_ENTRY] Last entry - using text until position {end_pos}")
            
            # Extract the complete text for this entry
            remaining_text = section[start_pos:end_pos].strip()
            
            # Clean up \n symbols and extra whitespace
            remaining_text = remaining_text.replace('\n', ' ').replace('\t', ' ')
            # Remove multiple spaces
            remaining_text = re.sub(r'\s+', ' ', remaining_text).strip()
            
            print(f"[DEBUG_ENTRY] Entry {i+1}:")
            print(f"[DEBUG_ENTRY] - Time: {time_info['start_time']} - {time_info['end_time']}")
            print(f"[DEBUG_ENTRY] - Duration: {time_info['duration']}")
            print(f"[DEBUG_ENTRY] - Status: {time_info['status']}")
            print(f"[DEBUG_ENTRY] - Position: {start_pos} to {end_pos}")
            print(f"[DEBUG_ENTRY] - Cleaned remaining text: '{remaining_text}'")
            
            # Parse remaining text - EXTRACT LOCATION FIRST (from back), then odometer
            location = self._extract_location_from_remaining(remaining_text)
            vehicle = self._extract_vehicle_from_remaining(remaining_text)
            odometer = self._extract_odometer_from_remaining(remaining_text, location)  # Pass location to avoid conflict
            remarks = self._extract_remarks_from_remaining(remaining_text)
            
            # Convert duration to hours
            duration_hours = self._parse_duration_to_hours(time_info['duration'])
            
            entry = {
                'start_time': time_info['start_time'],
                'end_time': time_info['end_time'],
                'duration': time_info['duration'],
                'duration_hours': duration_hours,
                'duty_status': self._normalize_status(time_info['status']),
                'vehicle': vehicle,
                'odometer': odometer,
                'location': location,
                'remarks': remarks,
                'raw_line': section[time_info['match'].start():end_pos].strip()  # Complete entry text
            }
            
            entries.append(entry)
            print(f"[DEBUG_ENTRY] Added entry with location: '{location}'")
        
        return entries
    
    def _parse_duration_to_hours(self, duration_str: str) -> float:
        """Parse duration string to decimal hours"""
        if not duration_str:
            return 0.0
        
        total_hours = 0.0
        
        # Extract hours
        hour_match = re.search(r'(\d+)h', duration_str)
        if hour_match:
            total_hours += int(hour_match.group(1))
        
        # Extract minutes
        min_match = re.search(r'(\d+)m', duration_str)
        if min_match:
            total_hours += int(min_match.group(1)) / 60.0
        
        # Extract seconds
        sec_match = re.search(r'(\d+)s', duration_str)
        if sec_match:
            total_hours += int(sec_match.group(1)) / 3600.0
        
        return round(total_hours, 2)
    
    def _normalize_status(self, status: str) -> str:
        """Normalize duty status"""
        status = status.upper()
        if 'DRIVING' in status:
            return 'driving'
        elif 'ON DUTY' in status:
            return 'on_duty'
        elif 'OFF DUTY' in status:
            return 'off_duty'
        elif 'SLEEPER' in status:
            return 'sleeper_berth'
        elif 'PERSONAL CONVEYANCE' in status:
            return 'personal_conveyance'
        else:
            return status.lower()
    
    def _extract_vehicle_from_remaining(self, text: str) -> str:
        """Extract vehicle from remaining text (handles multiple formats)"""
        print(f"[DEBUG_VEHICLE] Parsing text: '{text}'")
        
        # Format 1: kENWORTH 15 (Tedd's format)
        vehicle_match = re.search(r'kENWORTH\s*\d*', text)
        if vehicle_match:
            vehicle = vehicle_match.group(0).strip()
            print(f"[DEBUG_VEHICLE] Found kENWORTH: '{vehicle}'")
            return vehicle
        
        # Format 2: Just vehicle number (David/Adrian format) - "1014" or "971"
        # Look for standalone numbers that are likely vehicle IDs
        vehicle_match = re.search(r'\b(\d{3,4})\b', text)
        if vehicle_match:
            vehicle = vehicle_match.group(1)
            print(f"[DEBUG_VEHICLE] Found numeric vehicle: '{vehicle}'")
            return vehicle
        
        print(f"[DEBUG_VEHICLE] No vehicle found")
        return ""
    
    def _extract_odometer_from_remaining(self, text: str, location: str = "") -> str:
        """Extract odometer from remaining text (handles multiple formats)"""
        print(f"[DEBUG_ODOMETER] Parsing text: '{text}'")
        print(f"[DEBUG_ODOMETER] Known location: '{location}'")
        
        # Handle missing odometer case (Adrian's format with "-")
        if text.strip() == "-" or "- -" in text:
            print(f"[DEBUG_ODOMETER] Found missing odometer marker")
            return "-"
        
        # Pattern 1: Large odometer reading - "363,226 mi" (5-6 digits with comma)
        odometer_match = re.search(r'([\d,]{5,}\s*mi)', text)
        if odometer_match:
            odometer = odometer_match.group(1).strip()
            print(f"[DEBUG_ODOMETER] Pattern 1 (large number) match: '{odometer}'")
            return odometer
        
        # Pattern 2: Medium odometer reading - "110,916 mi" (4-6 digits)
        odometer_match = re.search(r'([\d,]{4,}\s*mi)', text)
        if odometer_match:
            odometer = odometer_match.group(1).strip()
            # Skip if this is part of the location
            if location and odometer in location:
                print(f"[DEBUG_ODOMETER] Skipping '{odometer}' (part of location)")
            else:
                print(f"[DEBUG_ODOMETER] Pattern 2 (medium number) match: '{odometer}'")
                return odometer
        
        # Pattern 3: Any number + mi that's NOT part of the location
        all_mi_matches = re.findall(r'([\d,]+\.?\d*\s*mi)', text)
        for mi_match in all_mi_matches:
            # Skip if this mi pattern is part of the location
            if location and mi_match in location:
                print(f"[DEBUG_ODOMETER] Skipping '{mi_match}' (part of location)")
                continue
            
            # Check if it looks like an odometer (3+ digits)
            number_part = re.search(r'([\d,]+)', mi_match)
            if number_part:
                number = number_part.group(1).replace(',', '')
                if len(number) >= 3:  # Odometer should be 3+ digits
                    print(f"[DEBUG_ODOMETER] Pattern 3 (any valid) match: '{mi_match}'")
                    return mi_match
        
        print(f"[DEBUG_ODOMETER] No odometer match found")
        return ""
    
    def _extract_location_from_remaining(self, text: str) -> str:
        """Extract location from remaining text"""
        print(f"[DEBUG_LOCATION] Parsing text: '{text}'")
        
        # Pattern 1: Distance-based location "3.8 mi ESE Middletown, OH"
        location_match = re.search(r'(\d+\.\d+\s+mi\s+[NSEW]{1,3}\s+[A-Za-z\s,]+)', text)
        if location_match:
            location = location_match.group(1).strip()
            print(f"[DEBUG_LOCATION] Found distance-based location: '{location}'")
            return location
        
        # Pattern 2: Simple city, state format "Lafayette, LA" or "Broken Arrow, OK"
        # Match city name (one or more capitalized words) followed by comma and 2-letter state code
        # Note: (?![a-z]) allows digits after state code (handles "TX37048" without space)
        city_match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})(?![a-z])', text)
        if city_match:
            city = city_match.group(1)
            state = city_match.group(2)
            
            # Filter out duty status keywords that might match the pattern
            duty_keywords = ['Driving', 'Driver', 'Sleeper', 'Personal', 'Conveyance', 'On', 'Duty', 'Off', 'Data', 'Diagnostic', 'Engine', 'Int', 'Location']
            duty_phrases = ['On Duty', 'Off Duty', 'Data Diagnostic', 'Int Location', 'Personal Conveyance']
            
            # Skip if city is a duty status keyword or phrase
            if city in duty_keywords or city in duty_phrases:
                print(f"[DEBUG_LOCATION] Skipping duty status keyword: '{city}'")
            else:
                # Also skip if city is composed entirely of duty keywords
                city_words = city.split()
                if all(word in duty_keywords for word in city_words):
                    print(f"[DEBUG_LOCATION] Skipping duty phrase composed of keywords: '{city}'")
                else:
                    location = f"{city}, {state}"
                    print(f"[DEBUG_LOCATION] Found simple city/state location: '{location}'")
                    return location
        
        print(f"[DEBUG_LOCATION] No location match found")
        return ""
    
    def _extract_remarks_from_remaining(self, text: str) -> str:
        """Extract remarks from remaining text"""
        remarks = []
        if 'Pre-Trip' in text:
            remarks.append('Pre-Trip Inspection')
        if 'Loading' in text:
            remarks.append('Loading')
        if 'Unloading' in text:
            remarks.append('Unloading')
        if 'Break' in text:
            remarks.append('Break')
        if 'ELD' in text:
            remarks.append('ELD')
        if 'Sleep' in text:
            remarks.append('Sleep')
        if 'Fuel' in text:
            remarks.append('Fuel')
        if 'Agriculture' in text:
            remarks.append('Agriculture Exempt')
        return ', '.join(remarks)
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date format"""
        # Convert "Thu, Aug 14" to "8/14" format
        month_map = {
            'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4',
            'May': '5', 'Jun': '6', 'Jul': '7', 'Aug': '8',
            'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        
        match = re.search(r'([A-Z][a-z]{2})\s+(\d{1,2})', date_str)
        if match:
            month_abbr = match.group(1)
            day = match.group(2)
            if month_abbr in month_map:
                return f"{month_map[month_abbr]}/{day}"
        
        return date_str
    
    def _get_date_range(self, daily_entries: List[Dict]) -> tuple:
        """Get start and end dates from daily entries"""
        if not daily_entries:
            return ('', '')
        
        dates = [entry['date'] for entry in daily_entries]
        return (min(dates), max(dates))
    
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
