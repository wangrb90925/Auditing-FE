# Sample Violation Files for Testing Audit Engine

These sample files are designed to generate realistic compliance scores (NOT 100%) by containing various FMCSA violations.

## 📁 Available Sample Files

### 1. `driver_log_violations.txt`

**Expected Score: 40-50%**

- **HOS Violations**: Exceeds 11-hour driving limit (19.5 hours)
- **On-Duty Violations**: Exceeds 14-hour limit (22 hours)
- **Rest Violations**: Insufficient off-duty time (2 hours vs required 10)

### 2. `form_manner_violations.txt`

**Expected Score: 60-70%**

- **Missing Required Fields**: No dates, incomplete locations
- **Form Violations**: Incomplete duty status information
- **Minor Violations**: Multiple small compliance issues

### 3. `weekly_violations.txt`

**Expected Score: 30-40%**

- **60/70 Hour Rule Violations**: 78.5 hours in 7 days
- **Daily Violations**: Every day exceeds driving limits
- **Cumulative Violations**: Pattern of non-compliance

### 4. `fuel_receipt_violations.txt`

**Expected Score: 70-80%**

- **Timing Violations**: Fueling during off-duty hours
- **HOS Conflicts**: Fuel stops during rest periods
- **Status Falsification**: Potential driver log manipulation

### 5. `bol_violations.txt`

**Expected Score: 50-60%**

- **Medical Certificate**: Expired (2 months ago)
- **HAZMAT Violations**: Missing placards and safety info
- **Documentation Issues**: Incomplete cargo descriptions

### 6. `comprehensive_violations.txt`

**Expected Score: 15-25%**

- **Multiple Violation Types**: HOS, form, fuel, BOL
- **Severe Violations**: 21.5 driving hours, 22 on-duty hours
- **Pattern Violations**: 7 consecutive days of violations

## 🧪 How to Test

### Option 1: Upload via Frontend

1. Go to your frontend upload page
2. Select one or more sample files
3. Enter driver details and submit
4. Check the generated compliance score

### Option 2: Test via API

```bash
# Create an audit
curl -X POST http://localhost:5000/api/audits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"driverName": "Test Driver", "driverType": "long-haul"}'

# Upload sample files
curl -X POST http://localhost:5000/api/audits/{audit_id}/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "files=@sample_violations/driver_log_violations.txt"

# Process the audit
curl -X POST http://localhost:5000/api/audits/{audit_id}/process \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📊 Expected Results

| File                         | Expected Score | Violations | Severity  |
| ---------------------------- | -------------- | ---------- | --------- |
| driver_log_violations.txt    | 40-50%         | 3-4        | Medium    |
| form_manner_violations.txt   | 60-70%         | 5-6        | Low       |
| weekly_violations.txt        | 30-40%         | 4-5        | High      |
| fuel_receipt_violations.txt  | 70-80%         | 2-3        | Medium    |
| bol_violations.txt           | 50-60%         | 3-4        | Medium    |
| comprehensive_violations.txt | 15-25%         | 15+        | Very High |

## 🔧 Customization

You can modify these files to:

- **Increase violations**: Add more driving hours, remove required fields
- **Decrease violations**: Reduce driving hours, add complete information
- **Change violation types**: Focus on specific compliance areas

## ⚠️ Important Notes

- These files are **TEXT FILES** - rename them to `.txt` if needed
- The audit engine expects specific data formats
- Results may vary based on your audit engine implementation
- Use these for **testing purposes only** - not for production

## 🎯 Testing Scenarios

1. **Single Violation Type**: Upload one file type to test specific rules
2. **Multiple Violation Types**: Upload several files to test comprehensive analysis
3. **Violation Severity**: Compare scores across different violation levels
4. **Edge Cases**: Test boundary conditions and unusual scenarios
