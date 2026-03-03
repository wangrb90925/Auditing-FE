"""
Fuel Receipt Parser

Extracts fuel transaction data from fuel receipt PDFs.
"""

import re
from datetime import datetime
from typing import List, Dict, Optional


class FuelReceiptParser:
    """Parser for extracting fuel receipt data from text content"""
    
    def __init__(self):
        self.fuel_transactions = []
        
    def is_fuel_receipt_document(self, text_content: str) -> bool:
        """
        Detect if the document is a fuel receipt by looking for 'FUEL RECEIPT' text
        
        Args:
            text_content: Extracted text from PDF
            
        Returns:
            bool: True if document contains fuel receipts
        """
        return 'FUEL RECEIPT' in text_content.upper()
    
    def parse_fuel_receipts(self, text_content: str, file_name: str) -> List[Dict]:
        """
        Parse fuel receipt data from text content
        
        Args:
            text_content: Extracted text from fuel receipt PDF
            file_name: Name of the file being processed
            
        Returns:
            List of fuel transaction dictionaries
        """
        print(f"[FUEL_PARSER] Parsing fuel receipts from {file_name}")
        
        fuel_transactions = []
        
        # Split text into individual receipts by "FUEL RECEIPT" marker
        receipt_blocks = re.split(r'FUEL RECEIPT', text_content, flags=re.IGNORECASE)
        
        print(f"[FUEL_PARSER] Found {len(receipt_blocks)} total blocks")
        
        # Process all blocks (including first one if it contains data)
        for i, block in enumerate(receipt_blocks, 0):
            try:
                transaction = self._parse_single_receipt(block, i)
                if transaction:
                    fuel_transactions.append(transaction)
                    print(f"[FUEL_PARSER] ✓ Extracted fuel transaction {i}: {transaction['date']} {transaction['time']} - {transaction['location']}")
            except Exception as e:
                print(f"[FUEL_PARSER] Error parsing receipt block {i}: {e}")
                continue
        
        print(f"[FUEL_PARSER] Successfully extracted {len(fuel_transactions)} fuel transactions")
        self.fuel_transactions = fuel_transactions
        return fuel_transactions
    
    def _parse_single_receipt(self, receipt_text: str, receipt_num: int) -> Optional[Dict]:
        """
        Parse a single fuel receipt block
        
        Args:
            receipt_text: Text content of one fuel receipt
            receipt_num: Receipt number for logging
            
        Returns:
            Dictionary with fuel transaction data or None
        """
        lines = [line.strip() for line in receipt_text.split('\n') if line.strip()]
        
        transaction = {
            'type': 'fuel_receipt',
            'date': None,
            'time': None,
            'datetime_str': None,
            'vehicle': None,
            'volume': None,
            'vendor': None,
            'odometer': None,
            'location': None,
            'total_cost': None,
            'fuel_type': None,
            'jurisdiction': None,
            'reference': None
        }
        
        # Parse receipt data using pattern matching
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for date/time pattern: "September 23, 2025 09:03:00 PM CDT"
            datetime_match = re.search(
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})\s+(\d{1,2}:\d{2}:\d{2})\s+(AM|PM)\s+(\w+)',
                line
            )
            if datetime_match:
                # This is the actual fuel transaction date/time
                transaction['datetime_str'] = datetime_match.group(0)
                transaction['date'] = f"{datetime_match.group(1)} {datetime_match.group(2)}, {datetime_match.group(3)}"
                transaction['time'] = f"{datetime_match.group(4)} {datetime_match.group(5)} {datetime_match.group(6)}"
                
                # Parse to standard format
                try:
                    dt = datetime.strptime(
                        f"{datetime_match.group(1)} {datetime_match.group(2)} {datetime_match.group(3)} {datetime_match.group(4)} {datetime_match.group(5)}",
                        "%B %d %Y %I:%M:%S %p"
                    )
                    transaction['date'] = dt.strftime("%m/%d/%Y")  # Format as MM/DD/YYYY
                    transaction['time'] = f"{datetime_match.group(4)} {datetime_match.group(5)} {datetime_match.group(6)}"
                except:
                    pass
            
            # Vehicle number (after "Vehicle" label)
            if line == 'Vehicle' and i + 1 < len(lines):
                transaction['vehicle'] = lines[i + 1]
            
            # Volume (after "Volume" label)
            if line == 'Volume' and i + 1 < len(lines):
                transaction['volume'] = lines[i + 1]
            
            # Vendor name (after "Vendor Name" label)
            if line == 'Vendor Name' and i + 1 < len(lines):
                transaction['vendor'] = lines[i + 1]
            
            # Odometer (after "Odometer" label)
            if line == 'Odometer' and i + 1 < len(lines):
                transaction['odometer'] = lines[i + 1]
            
            # Location (after "Location" label)
            if line == 'Location' and i + 1 < len(lines):
                transaction['location'] = lines[i + 1]
            
            # Total cost (after "Total Cost" label)
            if line == 'Total Cost' and i + 1 < len(lines):
                transaction['total_cost'] = lines[i + 1]
            
            # Fuel type (after "Fuel Type" label)
            if line == 'Fuel Type' and i + 1 < len(lines):
                transaction['fuel_type'] = lines[i + 1]
            
            # Jurisdiction (after "Jurisdiction" label)
            if line == 'Jurisdiction' and i + 1 < len(lines):
                transaction['jurisdiction'] = lines[i + 1]
            
            # Reference number (after "Reference #" label)
            if line == 'Reference #' and i + 1 < len(lines):
                transaction['reference'] = lines[i + 1]
            
            i += 1
        
        # Only return transaction if we have at least date/time and location
        if transaction['date'] and transaction['time']:
            return transaction
        else:
            print(f"[FUEL_PARSER] ⚠ Receipt {receipt_num} missing required fields (date/time)")
            return None
    
    def get_fuel_transactions(self) -> List[Dict]:
        """Get all parsed fuel transactions"""
        return self.fuel_transactions
    
    def cross_reference_with_logs(self, log_entries: List[Dict], fuel_transactions: List[Dict]) -> List[Dict]:
        """
        Cross-reference fuel transactions with log entries and update remarks
        
        Args:
            log_entries: List of log entry dictionaries from daily log parser
            fuel_transactions: List of fuel transaction dictionaries
            
        Returns:
            Updated log entries with fuel information in remarks
        """
        print(f"[FUEL_CROSS_REF] Cross-referencing {len(fuel_transactions)} fuel transactions with {len(log_entries)} log entries")
        
        updated_count = 0
        
        for fuel in fuel_transactions:
            fuel_date = fuel.get('date')
            fuel_time = fuel.get('time', '').strip()
            fuel_location = fuel.get('location', '')
            
            if not fuel_date or not fuel_time:
                continue
            
            # Parse fuel time to compare (e.g., "09:03:00 PM CDT")
            fuel_time_normalized = self._normalize_time(fuel_time)
            
            # Look for matching log entry by date and time
            for entry in log_entries:
                entry_date = entry.get('date', '')
                entry_start_time = entry.get('start_time', '')
                
                # Normalize entry time for comparison
                entry_time_normalized = self._normalize_time(entry_start_time)
                
                # Check if dates match (try different formats)
                dates_match = self._dates_match(entry_date, fuel_date)
                
                # Check if times are close (within 30 minutes)
                times_close = self._times_close(entry_time_normalized, fuel_time_normalized)
                
                if dates_match and times_close:
                    # Update remarks to include fuel information
                    current_remarks = entry.get('remarks', '')
                    
                    # Only add if "fuel" not already in remarks
                    if 'fuel' not in current_remarks.lower():
                        fuel_info = f"Fuel"
                        if fuel_location:
                            fuel_info += f" at {fuel_location}"
                        if fuel.get('vendor'):
                            fuel_info += f" ({fuel.get('vendor')})"
                        
                        # Append or set remarks
                        if current_remarks:
                            entry['remarks'] = f"{current_remarks}, {fuel_info}"
                        else:
                            entry['remarks'] = fuel_info
                        
                        updated_count += 1
                        print(f"[FUEL_CROSS_REF] ✓ Matched fuel transaction to log entry: {entry_date} {entry_start_time}")
                        break  # Move to next fuel transaction
        
        print(f"[FUEL_CROSS_REF] Updated {updated_count} log entries with fuel information")
        return log_entries
    
    def _normalize_time(self, time_str: str) -> Optional[datetime]:
        """
        Normalize time string to datetime for comparison
        
        Args:
            time_str: Time string in various formats
            
        Returns:
            datetime object or None
        """
        if not time_str:
            return None
        
        # Try different time formats
        time_formats = [
            "%I:%M:%S %p %Z",      # 09:03:00 PM CDT
            "%I:%M:%S %p",         # 09:03:00 PM
            "%H:%M:%S",            # 21:03:00
            "%I:%M %p",            # 09:03 PM
            "%H:%M",               # 21:03
        ]
        
        # Remove timezone abbreviations for parsing
        time_cleaned = re.sub(r'\s+(CDT|CST|EDT|EST|PDT|PST|MDT|MST)\s*$', '', time_str)
        
        for fmt in time_formats:
            try:
                # Use a dummy date for time comparison
                return datetime.strptime(time_cleaned.strip(), fmt)
            except:
                continue
        
        return None
    
    def _dates_match(self, date1: str, date2: str) -> bool:
        """
        Check if two date strings represent the same date
        
        Args:
            date1: First date string (e.g., "9/30" or "09/30/2024")
            date2: Second date string (e.g., "09/30/2024")
            
        Returns:
            bool: True if dates match
        """
        if not date1 or not date2:
            return False
        
        # Try to parse both dates
        try:
            # Extract month and day
            match1 = re.search(r'(\d{1,2})[/-](\d{1,2})', date1)
            match2 = re.search(r'(\d{1,2})[/-](\d{1,2})', date2)
            
            if match1 and match2:
                month1, day1 = int(match1.group(1)), int(match1.group(2))
                month2, day2 = int(match2.group(1)), int(match2.group(2))
                
                return month1 == month2 and day1 == day2
        except:
            pass
        
        return False
    
    def _times_close(self, time1: Optional[datetime], time2: Optional[datetime], 
                     tolerance_minutes: int = 30) -> bool:
        """
        Check if two times are within tolerance of each other
        
        Args:
            time1: First datetime
            time2: Second datetime
            tolerance_minutes: Tolerance in minutes
            
        Returns:
            bool: True if times are close
        """
        if not time1 or not time2:
            return False
        
        # Compare only time components
        diff = abs((time1.hour * 60 + time1.minute) - (time2.hour * 60 + time2.minute))
        
        return diff <= tolerance_minutes

