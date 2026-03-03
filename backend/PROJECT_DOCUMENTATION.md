# FMCSA Auditing System - Improved Architecture

## 🎯 **Project Overview**

This is a **driver violation detection system** for FMCSA (Federal Motor Carrier Safety Administration) compliance auditing. The system analyzes driver logs, fuel receipts, and other documents to detect Hours-of-Service (HOS) violations and other compliance issues.

### **Key Improvements Made:**
- ✅ **Removed all hard-coded violations** for specific drivers
- ✅ **Implemented rule-based violation detection** system
- ✅ **Added configurable driver classifications** (long-haul, short-haul, exemptions)
- ✅ **Created proper penalty calculation** based on CFR regulations
- ✅ **Enhanced audit engine** with comprehensive analysis
- ✅ **Updated violation detection** to use accurate library-based data instead of AI
- ✅ **Improved data processing** with precise timing and duration calculations
- ✅ **Removed AI dependencies** - now uses pure library-based parsing for better accuracy

---

## 🏗️ **System Architecture**

### **Core Components:**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API      │    │   PostgreSQL    │
│   (React/Vue)   │◄──►│   (app.py)       │◄──►│   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Audit Engine   │
                    │  (audit_engine)  │
                    └──────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
         ┌──────────────────┐  ┌─────────────────┐
         │  File Processor  │  │  FMCSA Rules    │
         │ (file_processor) │  │ (fmcsa_rules)   │
         └──────────────────┘  └─────────────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         ▼                           ▼
              ┌─────────────────────┐    ┌──────────────────┐
              │ Driver              │    │ Violation        │
              │ Classifications     │    │ Detector         │
              │ (driver_class...)   │    │ (violation_det.) │
              └─────────────────────┘    └──────────────────┘
```

---

## 📋 **Violation Detection Logic**

### **1. Driver Classifications**

The system supports different driver types with specific rules:

#### **Long-Haul Drivers**
- **Description:** Drivers operating beyond 150 air-mile radius
- **HOS Limits:**
  - Max driving: 11 hours
  - Max on-duty: 14 hours
  - Min rest: 10 hours
  - 60/70 hour limits: 60 hours in 7 days OR 70 hours in 8 days
  - Required break: 30 minutes after 8 hours driving

#### **Short-Haul Drivers**
- **Description:** Drivers within 150 air-mile radius
- **HOS Limits:**
  - Max driving: 11 hours
  - Max on-duty: 12 hours (different from long-haul)
  - Must return to base within 12 hours
  - 60/70 hour limits apply
  - **Exemption:** No ELD requirement if within 100 air-mile radius

#### **Agricultural Drivers**
- **Description:** Transporting agricultural commodities
- **Special Rules:**
  - 150 air-mile radius exemption during planting/harvesting
  - Relaxed HOS during seasonal operations
  - Limited HOS violations apply

#### **Construction/Utility Drivers**
- **Description:** Construction and utility operations
- **Rules:** Similar to long-haul with potential utility vehicle exemptions

#### **Exemption Drivers**
- **Description:** Operating under specific FMCSA exemptions
- **Rules:** Minimal violations, varies by exemption type

### **2. Violation Types Detected**

#### **Hours-of-Service (HOS) Violations:**
1. **11-Hour Driving Limit** - `HOS_11_HOUR_DRIVING`
   - Penalty: $1,100 - $2,750
   - CFR: 49 CFR 395.3(a)(1)

2. **14-Hour Window** - `HOS_14_HOUR_WINDOW`
   - Penalty: $1,100 - $2,750
   - CFR: 49 CFR 395.3(a)(2)

3. **60/70 Hour Limits** - `HOS_60_HOUR_7_DAY` / `HOS_70_HOUR_8_DAY`
   - Penalty: $1,375 - $2,750
   - CFR: 49 CFR 395.3(b)(1)

4. **10-Hour Rest** - `HOS_10_HOUR_REST`
   - Penalty: $825 - $2,200
   - CFR: 49 CFR 395.3(a)(1)

5. **30-Minute Break** - `HOS_30_MINUTE_BREAK`
   - Penalty: $550 - $1,375
   - CFR: 49 CFR 395.3(a)(3)(ii)

#### **Form and Manner Violations:**
6. **Missing Fields** - `FORM_MANNER_MISSING_FIELDS`
   - Penalty: $275 - $825
   - CFR: 49 CFR 395.8(e)

7. **Incomplete Entries** - `FORM_MANNER_INCOMPLETE_ENTRIES`
   - Penalty: $275 - $825
   - CFR: 49 CFR 395.8(e)

#### **Other Violations:**
8. **Log Falsification** - `LOG_FALSIFICATION`
   - Penalty: $2,750 - $11,000
   - CFR: 49 CFR 395.8(e)

9. **Driving Off Duty** - `DRIVING_OFF_DUTY`
   - Penalty: $1,100 - $2,750
   - CFR: 49 CFR 395.8(e)

10. **Fuel Off Duty** - `FUEL_OFF_DUTY`
    - Penalty: $825 - $2,200
    - CFR: 49 CFR 395.2

11. **Personal Conveyance Misuse** - `PERSONAL_CONVEYANCE_MISUSE`
    - Penalty: $1,100 - $2,750
    - CFR: 49 CFR 395.8(e)

12. **Geographic Implausible** - `GEOGRAPHIC_IMPLAUSIBLE`
    - Penalty: $825 - $2,200
    - CFR: 49 CFR 395.8(e)

---

## 🔄 **Audit Processing Flow**

### **Step 1: File Upload & Validation**
```python
# Files are uploaded via /api/audits/{audit_id}/upload
# Supported formats: PDF, Excel, Images (JPG, PNG)
# Max file size: 100MB per file
```

### **Step 2: File Processing**
```python
# FileProcessor extracts data from:
# - Driver logs (duty status, hours, locations)
# - Fuel receipts (date, time, location, amount)
# - Bills of lading (shipment information)
# - Audit summaries (text analysis)
```

### **Step 3: Driver Classification**
```python
# System determines applicable rules based on driver_type:
classification = driver_classification_system.get_classification(driver_type)
applicable_violations = classification.applicable_violations
hos_limits = classification.hos_limits
```

### **Step 4: Violation Detection**
```python
# ViolationDetector runs rule-based analysis:
violations = violation_detector.detect_violations(extracted_data, driver_type)

# Each violation includes:
# - Date of occurrence
# - Violation type (enum)
# - Description
# - Severity (minor/major/critical)
# - Penalty range
# - CFR section reference
```

### **Step 5: Compliance Scoring**
```python
# Compliance score calculation:
def calculate_compliance_score(violations):
    total_penalty = 0
    for violation in violations:
        base_penalty = get_base_penalty(violation.severity)
        type_penalty = get_type_penalty(violation.type)
        total_penalty += base_penalty + type_penalty
    
    return max(0, 100 - total_penalty)
```

### **Step 6: Report Generation**
```python
# Final audit report includes:
# - Violation list (detailed)
# - Consolidated violations (grouped)
# - Compliance score
# - Severity assessment
# - Penalty estimates
# - Recommendations
```

---

## 🛠️ **Configuration System**

### **Driver Classifications Configuration**
The system uses `driver_classifications.py` to define:
- Driver types and their rules
- HOS limits per driver type
- Applicable violation types
- Exemptions and special conditions

### **Violation Rules Configuration**
Each violation type is defined with:
- Description and severity
- Penalty ranges (min/max)
- CFR section references
- Applicable driver types
- Threshold values

### **Extensibility**
New driver types or violation rules can be added by:
1. Adding to the `DriverType` enum
2. Creating a `DriverClassification` instance
3. Defining `ViolationRule` instances
4. Implementing detection logic in `ViolationDetector`

---

## 🔧 **API Endpoints**

### **Driver Type Management**
- `GET /api/driver-types` - List all supported driver types
- `GET /api/driver-types/{type}/validate` - Validate a driver type

### **Audit Management**
- `POST /api/audits` - Create new audit
- `POST /api/audits/{id}/upload` - Upload files
- `POST /api/audits/{id}/process` - Process audit
- `GET /api/audits/{id}` - Get audit results
- `GET /api/audits/{id}/report` - Download CSV report

### **System Information**
- `GET /api/health` - System health and version info
- `GET /api/stats` - Audit statistics

---

## 🚀 **Running the Project**

### **Prerequisites:**
1. **PostgreSQL** installed and running
2. **Python 3.8+** with virtual environment
3. **Required packages** from requirements.txt

### **Setup Steps:**
```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python init_db.py

# 4. Start the application
python start.py
```

### **Environment Variables:**
Create a `.env` file with:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=audit_db
DB_USER=postgres
DB_PASSWORD=password
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key  # Optional
```

---

## 📊 **Testing the System**

### **Sample Driver Types:**
- `long-haul` - Full HOS rules apply
- `short-haul` - Modified 12-hour rule
- `agricultural` - Seasonal exemptions
- `construction` - Standard rules with utility exemptions
- `exemption` - Minimal rules, varies by exemption

### **Expected Behavior:**
1. **No Hard-coded Violations** - System only detects actual rule violations
2. **Driver-Specific Rules** - Different rules apply based on driver type
3. **Configurable Penalties** - Penalties based on CFR regulations
4. **Comprehensive Analysis** - All violation types checked systematically

---

## 🔍 **Troubleshooting**

### **Common Issues:**
1. **"Unknown driver type"** - Use supported types: long-haul, short-haul, etc.
2. **"No violations detected"** - Check if files contain actual violation data
3. **"Processing failed"** - Verify file formats and content structure

### **Debug Mode:**
Enable debug logging by setting `FLASK_DEBUG=1` in environment variables.

---

## 📈 **Future Enhancements**

### **Planned Features:**
1. **Machine Learning** - Pattern recognition for complex violations
2. **Real-time Monitoring** - Live violation detection
3. **Custom Rules** - User-defined violation rules
4. **Advanced Analytics** - Trend analysis and predictive insights
5. **Integration APIs** - Connect with ELD systems and fleet management

### **Scalability:**
- **Microservices** - Split components into separate services
- **Message Queues** - Asynchronous processing for large files
- **Caching** - Redis for improved performance
- **Load Balancing** - Handle multiple concurrent audits

---

## 📝 **Code Quality**

### **Best Practices Implemented:**
- ✅ **Separation of Concerns** - Each module has a specific responsibility
- ✅ **Configuration Management** - No hard-coded values
- ✅ **Error Handling** - Comprehensive exception handling
- ✅ **Type Hints** - Python type annotations for better code clarity
- ✅ **Documentation** - Comprehensive docstrings and comments
- ✅ **Extensibility** - Easy to add new driver types and violations

### **Testing Strategy:**
- **Unit Tests** - Test individual violation detection methods
- **Integration Tests** - Test complete audit processing flow
- **API Tests** - Verify all endpoints work correctly
- **Performance Tests** - Ensure system handles large files efficiently

---

*This documentation reflects the improved system architecture that replaces hard-coded logic with a flexible, rule-based approach for FMCSA compliance auditing.*
