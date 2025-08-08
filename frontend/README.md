# AI Auditing Agent for CDLManager

A comprehensive AI-powered FMCSA compliance auditing system designed for CDLManager's driver log analysis needs.

## 🎯 Project Overview

This application automates the manual audit process for CDLManager, processing driver logs, fuel receipts, and Bills of Lading to identify FMCSA Hours-of-Service violations and compliance issues.

### Key Features

- **AI-Powered File Processing**: Parse PDFs, JPEGs, PNGs, and Excel files
- **FMCSA Compliance Analysis**: Apply Hours-of-Service rules and regulations
- **Violation Detection**: Identify HOS violations, form/manner violations, and log falsification
- **Report Generation**: Export detailed CSV reports with compliance scores
- **Modern Web Interface**: Responsive Vue.js frontend with professional design
- **RESTful API**: Python Flask backend for scalable processing

## 🏗️ Architecture

```
AI-Auditing-Agent/
├── src/                    # Vue.js Frontend
│   ├── views/             # Application pages
│   ├── components/        # Reusable UI components
│   ├── stores/           # Pinia state management
│   └── assets/           # Icons and static assets
├── backend/               # Python Backend
│   ├── app.py            # Flask application
│   ├── audit_engine.py   # Main audit processing
│   ├── file_processor.py # File parsing and extraction
│   ├── fmcsa_rules.py    # FMCSA compliance rules
│   └── requirements.txt  # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 16+** and npm
- **Python 3.8+** and pip
- **Tesseract OCR** (for image processing)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd AI-aduting-Agent
   ```

2. **Install Frontend Dependencies:**

   ```bash
   npm install
   ```

3. **Install Backend Dependencies:**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR:**
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`

### Running the Application

#### Option 1: Development Mode (Recommended)

1. **Start the Backend:**

   ```bash
   cd backend
   python start.py
   ```

   The backend will be available at `http://localhost:5000`

2. **Start the Frontend:**
   ```bash
   # In a new terminal
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

#### Option 2: Production Mode

1. **Build the Frontend:**

   ```bash
   npm run build
   ```

2. **Start the Backend:**
   ```bash
   cd backend
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## 📋 API Endpoints

### Core Endpoints

| Method | Endpoint                   | Description         |
| ------ | -------------------------- | ------------------- |
| `GET`  | `/api/health`              | Health check        |
| `POST` | `/api/audits`              | Create new audit    |
| `POST` | `/api/audits/{id}/upload`  | Upload files        |
| `POST` | `/api/audits/{id}/process` | Process audit       |
| `GET`  | `/api/audits`              | Get all audits      |
| `GET`  | `/api/audits/{id}`         | Get specific audit  |
| `GET`  | `/api/audits/{id}/report`  | Download CSV report |
| `GET`  | `/api/stats`               | Get statistics      |

### Example Usage

```bash
# Health check
curl http://localhost:5000/api/health

# Create audit
curl -X POST http://localhost:5000/api/audits \
  -H "Content-Type: application/json" \
  -d '{"driverName": "John Doe", "driverType": "long-haul"}'

# Upload files
curl -X POST http://localhost:5000/api/audits/{audit_id}/upload \
  -F "files=@driver_log.pdf" \
  -F "files=@fuel_receipt.jpg"
```

## 🔍 FMCSA Compliance Rules

The system implements comprehensive FMCSA regulations:

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

## 📁 File Processing

### Supported File Types

- **PDF**: Driver logs, Bills of Lading
- **JPEG/PNG**: Fuel receipts, scanned documents
- **Excel**: Audit summaries, data sheets

### Processing Pipeline

1. **File Upload**: Validate file type and size (max 100MB)
2. **Text Extraction**: OCR for images, PDF parsing
3. **Data Normalization**: Standardize extracted data
4. **Compliance Analysis**: Apply FMCSA rules
5. **Report Generation**: Create detailed audit reports

## 👥 User Roles

### Auditor

- Upload driver documents
- Review audit results
- Download compliance reports
- Track audit history

### Admin

- Full access to all features
- System configuration
- User management
- Advanced analytics

## 🎨 Frontend Features

### Modern UI Design

- **LimeWire-inspired Design**: Clean, modern interface with gradients and backdrop blur
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Dark/Light Mode**: Toggle between themes
- **Shadcn-vue Components**: Professional UI components

### Key Pages

- **Dashboard**: Overview of audit activities and compliance metrics
- **Upload**: Drag-and-drop file upload with validation
- **Audit History**: Complete audit history with filtering
- **Audit Details**: Detailed violation analysis and reports

## 🔧 Backend Features

### AI-Powered Processing

- **OCR Technology**: Extract text from images using Tesseract
- **PDF Parsing**: Extract data from driver logs and documents
- **Data Normalization**: Standardize extracted information
- **Pattern Recognition**: Identify duty status, times, and violations

### Compliance Engine

- **FMCSA Rules Engine**: Comprehensive rule implementation
- **Violation Detection**: Automatic identification of compliance issues
- **Scoring Algorithm**: Calculate compliance scores
- **Report Generation**: Detailed CSV exports

## 🚀 Deployment Options

### AWS Deployment (CDLManager Preferred)

**Option 1: Continuous VM Operation**

- Deploy on EC2 instance
- Run 24/7 for real-time processing
- Higher cost but simpler monitoring

**Option 3: Serverless Container**

- Deploy on AWS Lambda with containerization
- Pay-per-use pricing
- Requires additional setup for containerization

### Docker Deployment

```dockerfile
# Frontend
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Backend
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🧪 Testing

### Frontend Testing

```bash
npm run lint          # ESLint checking
npm run test          # Unit tests
npm run test:e2e      # End-to-end tests
```

### Backend Testing

```bash
cd backend
python -m pytest tests/
```

### Manual Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Create and process audit
curl -X POST http://localhost:5000/api/audits \
  -H "Content-Type: application/json" \
  -d '{"driverName": "Test Driver", "driverType": "long-haul"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **Tesseract not found**
   - Install Tesseract OCR and ensure it's in PATH
   - Windows: Download from UB-Mannheim repository

2. **File upload errors**
   - Check file size limits (100MB max)
   - Verify supported file formats
   - Ensure backend is running

3. **CORS errors**
   - Backend CORS is configured for localhost:5173
   - Update CORS settings for production domains

4. **Processing failures**
   - Check Python dependencies are installed
   - Verify file permissions for uploads directory
   - Review backend logs for errors

### Logs

- **Frontend**: Check browser console for errors
- **Backend**: Application logs processing steps and errors

## 📊 Performance

### Scalability

- **File Processing**: Handles 100MB per driver audit
- **Concurrent Processing**: Multiple audits can be processed simultaneously
- **Memory Usage**: Optimized for large file processing
- **Response Time**: Real-time processing with status updates

### Data Volume

- **Monthly Capacity**: 100-200 audits per month
- **Storage**: 10-20 GB monthly data volume
- **Processing Time**: 2-5 minutes per audit

## 🔒 Security

### Data Protection

- **File Validation**: Strict file type and size validation
- **Temporary Storage**: Files processed and cleaned up
- **No Persistent Storage**: Files not stored long-term
- **CORS Protection**: Configured for specific domains

### Authentication

- **Session Management**: Local storage for user sessions
- **Role-based Access**: Auditor and Admin roles
- **API Security**: Input validation and error handling

## 📞 Support

For technical support or questions about FMCSA compliance rules implementation, contact the development team.

## 📄 License

This project is proprietary software developed for CDLManager.

---

**Built with ❤️ for CDLManager's compliance auditing needs**
