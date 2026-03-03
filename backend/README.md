# FMCSA Audit Engine - Python Backend

This is the Python backend for the CDLManager Auditing System, designed to process driver logs, fuel receipts, and Bills of Lading for FMCSA compliance analysis using accurate library-based parsing.

## Features

- **File Processing**: Parse PDFs, JPEGs, PNGs, and Excel files
- **FMCSA Compliance**: Apply Hours-of-Service (HOS) rules and other FMCSA regulations
- **Library-Based Analysis**: Extract and normalize driver data using accurate parsing libraries
- **Violation Detection**: Identify HOS violations, form/manner violations, and log falsification
- **Report Generation**: Generate detailed CSV reports with compliance scores
- **RESTful API**: Full API for integration with the Vue.js frontend

## Architecture

```
backend/
├── app.py              # Main Flask application
├── audit_engine.py     # Main audit processing engine
├── file_processor.py   # File parsing and data extraction
├── fmcsa_rules_improved.py  # FMCSA compliance rules engine
├── database.py         # Database models and configuration
├── config.py           # Application configuration
├── init_db.py          # Database initialization script
├── migrate.py          # Database migration script
├── requirements.txt    # Python dependencies
├── DATABASE_SETUP.md   # Database setup guide
└── README.md          # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Tesseract OCR (for image processing)
- PostgreSQL 12 or higher

### Installation

1. **Clone the repository and navigate to backend:**

   ```bash
   cd backend
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR:**

   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`

5. **Set up PostgreSQL Database:**

   ```bash
   # Install PostgreSQL (if not already installed)
   # Windows: Download from https://www.postgresql.org/download/windows/
   # macOS: brew install postgresql
   # Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib

   # Create database and tables
   python init_db.py
   python migrate.py
   ```

6. **Run the application:**
   ```bash
   python start.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check

```
GET /api/health
```

Returns server status and version information.

### Create Audit

```
POST /api/audits
Content-Type: application/json

{
  "driverName": "John Doe",
  "driverType": "long-haul"
}
```

### Upload Files

```
POST /api/audits/{audit_id}/upload
Content-Type: multipart/form-data

files: [file1, file2, ...]
```

### Process Audit

```
POST /api/audits/{audit_id}/process
```

Processes uploaded files and applies FMCSA compliance rules.

### Get All Audits

```
GET /api/audits
```

### Get Specific Audit

```
GET /api/audits/{audit_id}
```

### Download Report

```
GET /api/audits/{audit_id}/report
```

Downloads audit report as CSV file.

### Download Files

```
GET /api/audits/{audit_id}/files
```

Downloads all audit files as ZIP archive.

### Get Statistics

```
GET /api/stats
```

Returns audit statistics and metrics.

## FMCSA Compliance Rules

The system implements the following FMCSA regulations:

### Hours-of-Service (HOS) Violations

- **11-Hour Driving Limit**: Maximum 11 hours of driving after 10 consecutive hours off duty
- **14-Hour On-Duty Limit**: Maximum 14 hours on duty following 10 consecutive hours off duty
- **10-Hour Off-Duty Requirement**: Must have 10 consecutive hours off duty
- **60/70-Hour Rules**: Maximum 60 hours in 7 days or 70 hours in 8 days

### Other Violations

- **Form and Manner**: Missing required fields, improper log completion
- **Log Falsification**: Duplicate entries, impossible time sequences
- **BOL Compliance**: Missing Bill of Lading information
- **Fuel Receipt Analysis**: Cross-reference with duty status

## File Processing

### Supported File Types

- **PDF**: Driver logs, Bills of Lading
- **JPEG/PNG**: Fuel receipts, scanned documents
- **Excel**: Audit summaries, data sheets

### Processing Pipeline

1. **File Upload**: Validate file type and size
2. **Text Extraction**: OCR for images, PDF parsing
3. **Data Normalization**: Standardize extracted data
4. **Compliance Analysis**: Apply FMCSA rules
5. **Report Generation**: Create detailed audit reports

## Driver Types

The system supports different driver classifications:

- **Long Haul**: Beyond 150 air miles from work reporting location
- **Short Haul**: Within 150 air miles with 12-hour return requirement
- **Exemption**: Special certificates or medical exemptions

## Compliance Scoring

The system calculates compliance scores based on:

- **Minor Violations**: 5-point penalty each
- **Major Violations**: 10-point penalty each
- **Critical Violations**: 15-point penalty each

## Error Handling

The API includes comprehensive error handling:

- File validation errors
- Processing failures
- Invalid audit IDs
- Network timeouts

## Development

### Running in Development Mode

```bash
python app.py
```

### Running with Gunicorn (Production)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables

Create a `.env` file for configuration:

```
FLASK_ENV=development
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=104857600
```

## Integration with Frontend

The backend is designed to work seamlessly with the Vue.js frontend:

1. **CORS Enabled**: Allows cross-origin requests from the frontend
2. **JSON Responses**: All endpoints return JSON data
3. **File Upload**: Supports multipart form data for file uploads
4. **Real-time Processing**: Provides processing status updates

## Production Deployment

### AWS Deployment Options

**Option 1: Continuous VM Operation (Recommended)**

- Deploy on EC2 instance
- Run 24/7 for real-time processing
- Higher cost but simpler monitoring

**Option 3: Serverless Container (Alternative)**

- Deploy on AWS Lambda with containerization
- Pay-per-use pricing
- Requires additional setup for containerization

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Testing

### Manual Testing

Use tools like Postman or curl to test endpoints:

```bash
# Health check
curl http://localhost:5000/api/health

# Create audit
curl -X POST http://localhost:5000/api/audits \
  -H "Content-Type: application/json" \
  -d '{"driverName": "Test Driver", "driverType": "long-haul"}'
```

### Unit Testing

```bash
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Install Tesseract OCR and ensure it's in PATH
2. **File upload errors**: Check file size limits and supported formats
3. **Processing failures**: Verify all dependencies are installed
4. **CORS errors**: Ensure CORS is properly configured for your frontend domain

### Logs

The application logs processing steps and errors to help with debugging.

## Support

For technical support or questions about the FMCSA compliance rules implementation, contact the development team.

## License

This project is proprietary software developed for CDLManager.
