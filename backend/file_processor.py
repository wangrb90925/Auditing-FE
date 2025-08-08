import os
import PyPDF2
import pdfplumber
import pandas as pd
from PIL import Image
import pytesseract
import cv2
import numpy as np
from datetime import datetime, timedelta
import re
import json

class FileProcessor:
    def __init__(self):
        self.extracted_data = {
            'driver_logs': [],
            'fuel_receipts': [],
            'bills_of_lading': [],
            'audit_summaries': []
        }
    
    def process_files(self, files):
        """Process all uploaded files and extract relevant data"""
        for file_info in files:
            file_path = file_info['path']
            file_name = file_info['name'].lower()
            
            try:
                if file_path.endswith('.pdf'):
                    self._process_pdf(file_path, file_name)
                elif file_path.endswith(('.jpg', '.jpeg', '.png')):
                    self._process_image(file_path, file_name)
                elif file_path.endswith(('.xlsx', '.xls')):
                    self._process_excel(file_path, file_name)
            except Exception as e:
                print(f"Error processing file {file_name}: {str(e)}")
        
        return self.extracted_data
    
    def _process_pdf(self, file_path, file_name):
        """Process PDF files (driver logs, BOLs)"""
        try:
            # Try pdfplumber first for better text extraction
            with pdfplumber.open(file_path) as pdf:
                text_content = ""
                for page in pdf.pages:
                    text_content += page.extract_text() or ""
            
            # If pdfplumber fails, try PyPDF2
            if not text_content.strip():
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() or ""
            
            # Determine file type and process accordingly
            if 'log' in file_name or 'eld' in file_name:
                self._extract_driver_log_data(text_content, file_name)
            elif 'bol' in file_name or 'lading' in file_name:
                self._extract_bol_data(text_content, file_name)
            else:
                # Generic PDF processing
                self._extract_generic_data(text_content, file_name)
                
        except Exception as e:
            print(f"Error processing PDF {file_name}: {str(e)}")
    
    def _process_image(self, file_path, file_name):
        """Process image files (fuel receipts, scanned documents)"""
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                return
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing techniques
            # 1. Noise reduction
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # 2. Thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 3. OCR extraction
            text_content = pytesseract.image_to_string(thresh)
            
            # Determine file type and process
            if 'fuel' in file_name or 'receipt' in file_name:
                self._extract_fuel_receipt_data(text_content, file_name)
            elif 'bol' in file_name or 'lading' in file_name:
                self._extract_bol_data(text_content, file_name)
            else:
                # Generic image processing
                self._extract_generic_data(text_content, file_name)
                
        except Exception as e:
            print(f"Error processing image {file_name}: {str(e)}")
    
    def _process_excel(self, file_path, file_name):
        """Process Excel files (audit summaries, data sheets)"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Convert to structured data
            excel_data = {
                'filename': file_name,
                'columns': df.columns.tolist(),
                'data': df.to_dict('records'),
                'summary': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'processed_at': datetime.now().isoformat()
                }
            }
            
            if 'audit' in file_name or 'summary' in file_name:
                self.extracted_data['audit_summaries'].append(excel_data)
            else:
                # Generic Excel processing
                self.extracted_data['driver_logs'].append(excel_data)
                
        except Exception as e:
            print(f"Error processing Excel {file_name}: {str(e)}")
    
    def _extract_driver_log_data(self, text_content, file_name):
        """Extract driver log data from text content"""
        try:
            # Parse driver log entries
            log_entries = self._parse_driver_log_entries(text_content)
            
            log_data = {
                'filename': file_name,
                'type': 'driver_log',
                'entries': log_entries,
                'summary': {
                    'total_entries': len(log_entries),
                    'date_range': self._get_date_range(log_entries),
                    'processed_at': datetime.now().isoformat()
                }
            }
            
            self.extracted_data['driver_logs'].append(log_data)
            
        except Exception as e:
            print(f"Error extracting driver log data: {str(e)}")
    
    def _extract_fuel_receipt_data(self, text_content, file_name):
        """Extract fuel receipt data from text content"""
        try:
            # Parse fuel receipt information
            receipt_data = self._parse_fuel_receipt(text_content)
            
            fuel_data = {
                'filename': file_name,
                'type': 'fuel_receipt',
                'data': receipt_data,
                'processed_at': datetime.now().isoformat()
            }
            
            self.extracted_data['fuel_receipts'].append(fuel_data)
            
        except Exception as e:
            print(f"Error extracting fuel receipt data: {str(e)}")
    
    def _extract_bol_data(self, text_content, file_name):
        """Extract Bill of Lading data from text content"""
        try:
            # Parse BOL information
            bol_data = self._parse_bol_data(text_content)
            
            bol_info = {
                'filename': file_name,
                'type': 'bill_of_lading',
                'data': bol_data,
                'processed_at': datetime.now().isoformat()
            }
            
            self.extracted_data['bills_of_lading'].append(bol_info)
            
        except Exception as e:
            print(f"Error extracting BOL data: {str(e)}")
    
    def _extract_generic_data(self, text_content, file_name):
        """Extract generic data from text content"""
        try:
            generic_data = {
                'filename': file_name,
                'type': 'generic',
                'content': text_content,
                'processed_at': datetime.now().isoformat()
            }
            
            self.extracted_data['driver_logs'].append(generic_data)
            
        except Exception as e:
            print(f"Error extracting generic data: {str(e)}")
    
    def _parse_driver_log_entries(self, text_content):
        """Parse driver log entries from text"""
        entries = []
        
        # Split text into lines
        lines = text_content.split('\n')
        
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for date patterns
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', line)
            if date_match:
                if current_entry:
                    entries.append(current_entry)
                current_entry = {
                    'date': date_match.group(1),
                    'duty_status': [],
                    'location': '',
                    'notes': ''
                }
            
            # Look for duty status patterns
            duty_patterns = [
                r'(off duty|on duty|driving|sleeper berth)',
                r'(OFF DUTY|ON DUTY|DRIVING|SLEEPER)'
            ]
            
            for pattern in duty_patterns:
                duty_match = re.search(pattern, line, re.IGNORECASE)
                if duty_match:
                    current_entry['duty_status'].append({
                        'status': duty_match.group(1).lower(),
                        'line': line
                    })
                    break
        
        if current_entry:
            entries.append(current_entry)
        
        return entries
    
    def _parse_fuel_receipt(self, text_content):
        """Parse fuel receipt information"""
        receipt_data = {
            'date': '',
            'time': '',
            'location': '',
            'fuel_amount': '',
            'total_cost': '',
            'duty_status': ''
        }
        
        # Extract date
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text_content)
        if date_match:
            receipt_data['date'] = date_match.group(1)
        
        # Extract time
        time_match = re.search(r'(\d{1,2}:\d{2})', text_content)
        if time_match:
            receipt_data['time'] = time_match.group(1)
        
        # Extract fuel amount
        fuel_match = re.search(r'(\d+\.?\d*)\s*(gallon|gal)', text_content, re.IGNORECASE)
        if fuel_match:
            receipt_data['fuel_amount'] = fuel_match.group(1)
        
        # Extract total cost
        cost_match = re.search(r'\$(\d+\.?\d*)', text_content)
        if cost_match:
            receipt_data['total_cost'] = cost_match.group(1)
        
        return receipt_data
    
    def _parse_bol_data(self, text_content):
        """Parse Bill of Lading information"""
        bol_data = {
            'bol_number': '',
            'date': '',
            'origin': '',
            'destination': '',
            'cargo': '',
            'carrier': ''
        }
        
        # Extract BOL number
        bol_match = re.search(r'(BOL|B/L|Bill of Lading)[\s:]*(\d+)', text_content, re.IGNORECASE)
        if bol_match:
            bol_data['bol_number'] = bol_match.group(2)
        
        # Extract date
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text_content)
        if date_match:
            bol_data['date'] = date_match.group(1)
        
        # Extract origin and destination
        origin_match = re.search(r'from[\s:]*([A-Za-z\s,]+)', text_content, re.IGNORECASE)
        if origin_match:
            bol_data['origin'] = origin_match.group(1).strip()
        
        dest_match = re.search(r'to[\s:]*([A-Za-z\s,]+)', text_content, re.IGNORECASE)
        if dest_match:
            bol_data['destination'] = dest_match.group(1).strip()
        
        return bol_data
    
    def _get_date_range(self, log_entries):
        """Get the date range from log entries"""
        if not log_entries:
            return {}
        
        dates = [entry.get('date', '') for entry in log_entries if entry.get('date')]
        if dates:
            return {
                'start_date': min(dates),
                'end_date': max(dates)
            }
        return {}
    
    def get_processed_data(self):
        """Get the processed data summary"""
        return {
            'total_files_processed': sum(len(data) for data in self.extracted_data.values()),
            'driver_logs_count': len(self.extracted_data['driver_logs']),
            'fuel_receipts_count': len(self.extracted_data['fuel_receipts']),
            'bills_of_lading_count': len(self.extracted_data['bills_of_lading']),
            'audit_summaries_count': len(self.extracted_data['audit_summaries']),
            'data': self.extracted_data
        } 