#!/usr/bin/env python3
"""
Test script to verify violation detection for sample RODS files
"""

import requests
import json
import os
from pathlib import Path
import time

# API Configuration
API_BASE_URL = "http://localhost:5000/api"
SAMPLE_FILES_DIR = r"D:\Projects\Justin-project\Auditing-FE\frontend\sample"

# Login credentials
USERNAME = "admin"
PASSWORD = "admin123"

def login():
    """Login and get access token"""
    print("Logging in...")
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print(f"[OK] Login successful")
        return token
    else:
        print(f"[ERROR] Login failed: {response.text}")
        return None

def create_audit(token, driver_name, driver_type="long-haul"):
    """Create a new audit"""
    print(f"\nCreating audit for {driver_name}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/audits",
        headers=headers,
        json={
            "driverName": driver_name,
            "driverType": driver_type
        }
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        audit_id = data["id"]
        print(f"[OK] Audit created: {audit_id}")
        return audit_id
    else:
        print(f"[ERROR] Failed to create audit: {response.text}")
        return None

def upload_file(token, audit_id, file_path):
    """Upload a file to an audit"""
    file_name = os.path.basename(file_path)
    print(f"Uploading {file_name}...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(file_path, 'rb') as f:
        files = {'files': (file_name, f, 'application/pdf')}
        response = requests.post(
            f"{API_BASE_URL}/audits/{audit_id}/upload",
            headers=headers,
            files=files
        )
    
    if response.status_code == 200:
        print(f"[OK] File uploaded successfully")
        return True
    else:
        print(f"[ERROR] Failed to upload file: {response.text}")
        return False

def process_audit(token, audit_id):
    """Process an audit to detect violations"""
    print(f"Processing audit...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/audits/{audit_id}/process",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Audit processed successfully")
        return data
    else:
        print(f"[ERROR] Failed to process audit: {response.text}")
        return None

def display_violations(audit_data):
    """Display violation details"""
    violations = audit_data.get("violationsList", [])
    summary = audit_data.get("summary", {})
    
    print(f"\n{'='*80}")
    print(f"AUDIT RESULTS FOR: {audit_data.get('driverName', 'Unknown')}")
    print(f"{'='*80}")
    
    print(f"\nSummary:")
    print(f"   Compliance Score: {summary.get('complianceScore', 0)}%")
    print(f"   Severity: {summary.get('severity', 'unknown')}")
    print(f"   Total Violations: {summary.get('totalViolations', 0)}")
    print(f"   HOS Violations: {summary.get('hosViolations', 0)}")
    print(f"   Form Violations: {summary.get('formViolations', 0)}")
    print(f"   Falsification Violations: {summary.get('falsificationViolations', 0)}")
    
    if violations:
        print(f"\nViolations Detected ({len(violations)}):")
        print(f"{'-'*80}")
        
        for i, violation in enumerate(violations, 1):
            print(f"\n{i}. {violation.get('type', 'Unknown Type')}")
            print(f"   Date: {violation.get('date', 'N/A')}")
            print(f"   Severity: {violation.get('severity', 'N/A')}")
            print(f"   Description: {violation.get('description', 'N/A')}")
            print(f"   Section: {violation.get('section', 'N/A')}")
            print(f"   Penalty: {violation.get('penalty', 'N/A')}")
    else:
        print(f"\n[OK] No violations detected!")
    
    print(f"\n{'='*80}\n")

def test_sample_files():
    """Test violation detection for all sample files"""
    
    # Define sample files to test with expected results
    test_cases = [
        {
            "file": "Richard Woods RODS.pdf",
            "driver_name": "Richard Woods",
            "expected_violations": [
                "HOS_70_HOUR_8_DAY_VIOLATION",
                "FUEL_WITHOUT_ON_DUTY_TIME",
                "PERSONAL_CONVEYANCE_MISUSE"
            ]
        },
        {
            "file": "Gerard Francis Jr Dauphinais RODS.pdf",
            "driver_name": "Gerard Francis Jr Dauphinais",
            "expected_violations": [
                "HOS_14_HOUR_WINDOW_VIOLATION",
                "MISSING_LOCATION_FROM_LOG",
                "DISTANCE_MILEAGE_CHANGE_WITHOUT_DRIVING_TIME"
            ]
        },
        {
            "file": "Kundan Lal RODS 7.15-8.13.pdf",
            "driver_name": "Kundan Lal",
            "expected_violations": [
                "HOS_BREAK_VIOLATION",
                "HOS_DRIVING_HOURS_EXCEEDED",
                "MISSING_LOCATION_FROM_LOG",
                "FUEL_WITHOUT_ON_DUTY_TIME"
            ]
        }
    ]
    
    # Login
    token = login()
    if not token:
        print("[ERROR] Cannot proceed without authentication")
        return
    
    # Test each sample file
    results = []
    
    for test_case in test_cases:
        file_path = os.path.join(SAMPLE_FILES_DIR, test_case["file"])
        
        if not os.path.exists(file_path):
            print(f"[WARNING] File not found: {file_path}")
            continue
        
        # Create audit
        audit_id = create_audit(token, test_case["driver_name"])
        if not audit_id:
            continue
        
        # Upload file
        if not upload_file(token, audit_id, file_path):
            continue
        
        # Wait a moment for file to be ready
        time.sleep(1)
        
        # Process audit
        audit_data = process_audit(token, audit_id)
        if not audit_data:
            continue
        
        # Display results
        display_violations(audit_data)
        
        # Verify expected violations
        violations = audit_data.get("violationsList", [])
        violation_types = [v.get("type") for v in violations]
        
        print(f"Verification for {test_case['driver_name']}:")
        for expected_type in test_case["expected_violations"]:
            if expected_type in violation_types:
                print(f"   [OK] {expected_type} - DETECTED")
            else:
                print(f"   [MISS] {expected_type} - NOT DETECTED")
        
        results.append({
            "driver": test_case["driver_name"],
            "audit_id": audit_id,
            "violations": len(violations),
            "compliance_score": audit_data.get("summary", {}).get("complianceScore", 0)
        })
        
        print(f"\n")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"OVERALL TESTING SUMMARY")
    print(f"{'='*80}")
    
    for result in results:
        print(f"\n{result['driver']}:")
        print(f"   Audit ID: {result['audit_id']}")
        print(f"   Violations: {result['violations']}")
        print(f"   Compliance Score: {result['compliance_score']}%")

if __name__ == "__main__":
    print("="*80)
    print("API VIOLATION DETECTION TEST")
    print("="*80)
    
    test_sample_files()
    
    print("\n[OK] Testing completed!")
