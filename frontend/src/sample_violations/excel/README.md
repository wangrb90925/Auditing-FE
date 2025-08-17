# Sample Violation Files for Testing Audit Engine

These sample files are designed to generate realistic compliance scores (NOT 100%) by containing various FMCSA violations. The files come in multiple formats to test your audit engine's ability to process different file types.

## 📁 Available Sample Files

### 📄 PDF Files (Text-based violations)

**Best for testing text extraction and parsing**

#### 1. `driver_log_violations.pdf`

**Expected Score: 40-50%**

- **HOS Violations**: Exceeds 11-hour driving limit (19.5 hours)
- **On-Duty Violations**: Exceeds 14-hour limit (22 hours)
- **Rest Violations**: Insufficient off-duty time (2 hours vs required 10)

#### 2. `form_manner_violations.pdf`

**Expected Score: 60-70%**

- **Missing Required Fields**: No dates, incomplete locations
- **Form Violations**: Incomplete duty status information
- **Minor Violations**: Multiple small compliance issues

#### 3. `weekly_violations.pdf`

**Expected Score: 30-40%**

- **60/70 Hour Rule Violations**: 78.5 hours in 7 days
- **Daily Violations**: Every day exceeds driving limits
- **Cumulative Violations**: Pattern of non-compliance

#### 4. `fuel_receipt_violations.pdf`

**Expected Score: 70-80%**

- **Timing Violations**: Fueling during off-duty hours
- **HOS Conflicts**: Fuel stops during rest periods
- **Status Falsification**: Potential driver log manipulation

#### 5. `bol_violations.pdf`

**Expected Score: 50-60%**

- **Medical Certificate**: Expired (2 months ago)
- **HAZMAT Violations**: Missing placards and safety info
- **Documentation Issues**: Incomplete cargo descriptions

#### 6. `comprehensive_violations.pdf`

**Expected Score: 15-25%**

- **Multiple Violation Types**: HOS, form, fuel, BOL
- **Severe Violations**: 21.5 driving hours, 22 on-duty hours
- **Pattern Violations**: 7 consecutive days of violations

### 🖼️ PNG Files (Image-based violations)

**Best for testing OCR and image processing**

#### 1. `driver_log_violations.png`

**Expected Score: 40-50%**

- **HOS Driving Hours Violation**: Exceeds 11-hour limit by 8.5 hours
- **HOS On-Duty Hours Violation**: Exceeds 14-hour limit by 8 hours
- **Insufficient Rest Period**: Only 2 hours vs required 10 hours

#### 2. `fuel_receipt_violations.png`

**Expected Score: 70-80%**

- **Fuel Timing Violation**: Fueling at 02:30 AM while OFF DUTY
- **HOS Conflict**: Multiple fuel stops during rest periods

#### 3. `weekly_summary_violations.png`

**Expected Score: 30-40%**

- **60-Hour Rule Violation**: 78.5 hours in 7 days
- **Daily Driving Limit Violations**: 7 consecutive days of violations

### 📊 Excel Files (Structured data violations)

**Best for testing spreadsheet processing and data analysis**

#### 1. `driver_log_violations.xlsx`

**Expected Score: 40-50%**

- **Sheet 1: Driver_Log**: 24-hour detailed log with violation flags
- **Sheet 2: Violations**: Summary of HOS violations with penalties

#### 2. `fuel_receipt_violations.xlsx`

**Expected Score: 70-80%**

- **Sheet 1: Fuel_Receipts**: Fuel transactions with timing violations
- **Sheet 2: Violations**: Summary of fuel-related HOS conflicts

#### 3. `weekly_summary_violations.xlsx`

**Expected Score: 30-40%**

- **Sheet 1: Weekly_Summary**: 7-day summary with cumulative hours
- **Sheet 2: Violations**: Weekly rule violations and penalties

## 🧪 How to Test

### Option 1: Upload via Frontend

1. Go to your frontend upload page
2. Select one or more sample files (mix different formats)
3. Enter driver details and submit
4. Check the generated compliance score

### Option 2: Test via API

```bash
# Create an audit
curl -X POST http://localhost:5000/api/audits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"driverName": "Test Driver", "driverType": "long-haul"}'

# Upload sample files (mix different formats)
curl -X POST http://localhost:5000/api/audits/{audit_id}/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "files=@sample_violations/driver_log_violations.pdf" \
  -F "files=@sample_violations/fuel_receipt_violations.png" \
  -F "files=@sample_violations/weekly_summary_violations.xlsx"

# Process the audit
curl -X POST http://localhost:5000/api/audits/{audit_id}/process \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📊 Expected Results by File Type

| File Type | File Name                      | Expected Score | Violations | Severity  |
| --------- | ------------------------------ | -------------- | ---------- | --------- |
| **PDF**   | driver_log_violations.pdf      | 40-50%         | 3-4        | Medium    |
| **PDF**   | form_manner_violations.pdf     | 60-70%         | 5-6        | Low       |
| **PDF**   | weekly_violations.pdf          | 30-40%         | 4-5        | High      |
| **PDF**   | fuel_receipt_violations.pdf    | 70-80%         | 2-3        | Medium    |
| **PDF**   | bol_violations.pdf             | 50-60%         | 3-4        | Medium    |
| **PDF**   | comprehensive_violations.pdf   | 15-25%         | 15+        | Very High |
| **PNG**   | driver_log_violations.png      | 40-50%         | 3          | Medium    |
| **PNG**   | fuel_receipt_violations.png    | 70-80%         | 2          | Medium    |
| **PNG**   | weekly_summary_violations.png  | 30-40%         | 2          | High      |
| **Excel** | driver_log_violations.xlsx     | 40-50%         | 3          | Medium    |
| **Excel** | fuel_receipt_violations.xlsx   | 70-80%         | 2          | Medium    |
| **Excel** | weekly_summary_violations.xlsx | 30-40%         | 2          | High      |

## 🎯 Testing Scenarios

### 1. **Single File Type Testing**

- Upload only PDFs to test text extraction
- Upload only PNGs to test OCR capabilities
- Upload only Excel files to test spreadsheet processing

### 2. **Mixed File Type Testing**

- Upload combination of PDF + PNG + Excel
- Test audit engine's ability to process multiple formats
- Verify consistent violation detection across formats

### 3. **Violation Severity Testing**

- Start with high-score files (70-80%) to verify basic functionality
- Progress to medium-score files (40-60%) to test violation detection
- End with low-score files (15-40%) to test comprehensive analysis

### 4. **Format-Specific Testing**

- **PDFs**: Test text parsing, table extraction, and violation identification
- **PNGs**: Test OCR accuracy and image-to-text conversion
- **Excel**: Test structured data analysis and violation calculation

## 🔧 Customization

You can modify these files to:

- **Increase violations**: Add more driving hours, remove required fields
- **Decrease violations**: Reduce driving hours, add complete information
- **Change violation types**: Focus on specific compliance areas
- **Adjust file formats**: Convert between PDF, PNG, and Excel

## ⚠️ Important Notes

- **PDF files** contain structured text that should be easily parsed
- **PNG files** require OCR processing and may have varying accuracy
- **Excel files** contain structured data that should be directly readable
- Results may vary based on your audit engine implementation
- Use these for **testing purposes only** - not for production

## 🚀 Getting Started

1. **Choose your test scenario** from the options above
2. **Upload files** via frontend or API
3. **Monitor processing** and check for errors
4. **Verify results** match expected compliance scores
5. **Test edge cases** with different file combinations

## 📈 Performance Expectations

- **PDF Processing**: Fastest, most reliable text extraction
- **PNG Processing**: Medium speed, depends on OCR quality
- **Excel Processing**: Fast, structured data extraction
- **Mixed Files**: May take longer due to format switching

Your audit engine should now be able to process all these file types and generate realistic compliance scores that are NOT 100%! 🎯
