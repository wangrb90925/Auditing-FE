#!/usr/bin/env python3
"""
Create sample PNG images and Excel files with violation data for audit engine testing
"""

import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime, timedelta

def create_violation_png(filename, content_type, violations):
    """Create a PNG image with violation data"""
    
    # Create image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw title
    title = f"{content_type.upper()} - COMPLIANCE VIOLATIONS"
    draw.text((50, 30), title, fill='darkred', font=font_large)
    
    # Draw violation details
    y_position = 80
    for violation in violations:
        # Violation type
        draw.text((50, y_position), f"• {violation['type']}", fill='darkred', font=font_medium)
        y_position += 30
        
        # Violation description
        draw.text((70, y_position), violation['description'], fill='black', font=font_small)
        y_position += 25
        
        # Violation details
        if 'details' in violation:
            for detail in violation['details']:
                draw.text((90, y_position), f"- {detail}", fill='darkblue', font=font_small)
                y_position += 20
        
        y_position += 15
    
    # Draw footer
    footer = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Expected Score: {violations[0].get('expected_score', 'N/A')}"
    draw.text((50, height - 40), footer, fill='gray', font=font_small)
    
    # Save image
    image.save(filename)
    print(f"✅ Created PNG: {filename}")

def create_violation_excel(filename, content_type, violations):
    """Create an Excel file with violation data"""
    
    # Create DataFrames for different sheets
    sheets = {}
    
    if content_type == "driver_log":
        # Driver log data with violations
        log_data = []
        for i in range(24):
            hour = f"{i:02d}:00"
            if 6 <= i <= 20:
                status = "DRIVING" if i % 2 == 0 else "ON DUTY"
                location = "Highway" if i % 2 == 0 else "Rest Area"
                remarks = "Violation: Exceeds driving limit" if i > 11 else "Normal operation"
            else:
                status = "OFF DUTY"
                location = "Rest Area"
                remarks = "Insufficient rest period"
            
            log_data.append({
                'Date': '2024-08-17',
                'Time': hour,
                'Duty_Status': status,
                'Location': location,
                'Remarks': remarks,
                'Violation_Flag': 'YES' if i > 11 or (i < 6 and i > 0) else 'NO'
            })
        
        sheets['Driver_Log'] = pd.DataFrame(log_data)
        
        # Violations summary
        violations_summary = [
            {'Violation_Type': 'HOS_DRIVING_HOURS_EXCEEDED', 'Description': 'Exceeds 11-hour limit', 'Hours': 19.5, 'Penalty': '$2,750'},
            {'Violation_Type': 'HOS_ON_DUTY_HOURS_EXCEEDED', 'Description': 'Exceeds 14-hour limit', 'Hours': 22.0, 'Penalty': '$2,750'},
            {'Violation_Type': 'HOS_INSUFFICIENT_OFF_DUTY', 'Description': 'Insufficient rest period', 'Hours': 2.0, 'Penalty': '$2,750'}
        ]
        sheets['Violations'] = pd.DataFrame(violations_summary)
        
    elif content_type == "fuel_receipt":
        # Fuel receipt data with timing violations
        fuel_data = [
            {'Date': '2024-08-17', 'Time': '02:30 AM', 'Location': 'Flying J Truck Stop', 'Driver_Status': 'OFF DUTY', 'Violation': 'YES'},
            {'Date': '2024-08-17', 'Time': '08:00 AM', 'Location': 'Rest Area', 'Driver_Status': 'ON DUTY', 'Violation': 'NO'},
            {'Date': '2024-08-17', 'Time': '23:00 PM', 'Location': 'Truck Stop', 'Driver_Status': 'ON DUTY', 'Violation': 'YES'}
        ]
        sheets['Fuel_Receipts'] = pd.DataFrame(fuel_data)
        
        # Violations summary
        violations_summary = [
            {'Violation_Type': 'FUEL_TIMING_VIOLATION', 'Description': 'Fueling during off-duty hours', 'Count': 2, 'Penalty': '$1,000'},
            {'Violation_Type': 'HOS_CONFLICT', 'Description': 'Fuel stops during rest periods', 'Count': 1, 'Penalty': '$1,000'}
        ]
        sheets['Violations'] = pd.DataFrame(violations_summary)
        
    elif content_type == "weekly_summary":
        # Weekly summary with cumulative violations
        weekly_data = []
        for i, day in enumerate(['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
            driving_hours = 11.5 if i % 2 == 0 else 11.0
            on_duty_hours = 14.0
            off_duty_hours = 10.0
            
            weekly_data.append({
                'Day': day,
                'Date': date,
                'Driving_Hours': driving_hours,
                'On_Duty_Hours': on_duty_hours,
                'Off_Duty_Hours': off_duty_hours,
                'Violations': 'YES' if driving_hours > 11 else 'NO',
                'Cumulative_Week_Hours': (i + 1) * driving_hours
            })
        
        sheets['Weekly_Summary'] = pd.DataFrame(weekly_data)
        
        # Violations summary
        violations_summary = [
            {'Violation_Type': '60_HOUR_RULE_VIOLATION', 'Description': 'Exceeds 60 hours in 7 days', 'Total_Hours': 78.5, 'Penalty': '$2,750'},
            {'Violation_Type': 'DAILY_DRIVING_LIMIT', 'Description': 'Daily driving hours exceeded', 'Days_Affected': 7, 'Penalty': '$19,250'}
        ]
        sheets['Violations'] = pd.DataFrame(violations_summary)
    
    # Save to Excel
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Created Excel: {filename}")

def main():
    """Create sample PNG and Excel files with violations"""
    
    # Create sample_violations directory if it doesn't exist
    sample_dir = "sample_violations"
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
    
    print("🔄 Creating sample PNG and Excel files with violations...")
    
    # Sample violations data
    violations_data = {
        "driver_log": [
            {
                'type': 'HOS Driving Hours Violation',
                'description': 'Driver exceeded 11-hour driving limit',
                'details': ['Total driving hours: 19.5', 'Limit: 11 hours', 'Excess: 8.5 hours'],
                'expected_score': '40-50%'
            },
            {
                'type': 'HOS On-Duty Hours Violation',
                'description': 'Driver exceeded 14-hour on-duty limit',
                'details': ['Total on-duty hours: 22', 'Limit: 14 hours', 'Excess: 8 hours'],
                'expected_score': '40-50%'
            },
            {
                'type': 'Insufficient Rest Period',
                'description': 'Driver did not get required 10-hour rest',
                'details': ['Actual rest: 2 hours', 'Required: 10 hours', 'Deficit: 8 hours'],
                'expected_score': '40-50%'
            }
        ],
        "fuel_receipt": [
            {
                'type': 'Fuel Timing Violation',
                'description': 'Fueling during off-duty hours',
                'details': ['Fuel time: 02:30 AM', 'Driver status: OFF DUTY', 'HOS violation'],
                'expected_score': '70-80%'
            },
            {
                'type': 'HOS Conflict',
                'description': 'Fuel stops during rest periods',
                'details': ['Multiple fuel stops', 'Interrupted rest periods', 'Potential falsification'],
                'expected_score': '70-80%'
            }
        ],
        "weekly_summary": [
            {
                'type': '60-Hour Rule Violation',
                'description': 'Exceeded 60-hour weekly limit',
                'details': ['7-day total: 78.5 hours', 'Limit: 60 hours', 'Excess: 18.5 hours'],
                'expected_score': '30-40%'
            },
            {
                'type': 'Daily Driving Limit Violations',
                'description': 'Every day exceeded driving limits',
                'details': ['7 consecutive days', 'Pattern of non-compliance', 'Cumulative violations'],
                'expected_score': '30-40%'
            }
        ]
    }
    
    # Create PNG files
    for content_type, violations in violations_data.items():
        png_filename = os.path.join(sample_dir, f"{content_type}_violations.png")
        create_violation_png(png_filename, content_type, violations)
    
    # Create Excel files
    for content_type, violations in violations_data.items():
        excel_filename = os.path.join(sample_dir, f"{content_type}_violations.xlsx")
        create_violation_excel(excel_filename, content_type, violations)
    
    print("\n🎯 Sample file creation completed!")
    print("📁 Check the 'sample_violations' directory for:")
    print("   • PNG files with violation data")
    print("   • Excel files with structured violation data")
    print("📋 You can now upload these files to test your audit engine")

if __name__ == "__main__":
    main()
