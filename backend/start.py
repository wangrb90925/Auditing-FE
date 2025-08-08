#!/usr/bin/env python3
"""
Startup script for the AI Audit Engine backend
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        ('flask', 'flask'),
        ('flask-cors', 'flask_cors'),
        ('PyPDF2', 'PyPDF2'),
        ('pdfplumber', 'pdfplumber'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('Pillow', 'PIL'),
        ('opencv-python', 'cv2'),
        ('pytesseract', 'pytesseract')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    print("✅ All required packages are installed")

def check_tesseract():
    """Check if Tesseract OCR is available"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is available")
    except Exception as e:
        print("⚠️  Warning: Tesseract OCR not found")
        print("   Image processing (JPEG/PNG) may not work properly")
        print("   Install Tesseract:")
        print("   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   - macOS: brew install tesseract")
        print("   - Ubuntu/Debian: sudo apt-get install tesseract-ocr")

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def start_server():
    """Start the Flask development server"""
    print("\n🚀 Starting AI Audit Engine Backend...")
    print("📍 Server will be available at: http://localhost:5000")
    print("📋 API Documentation: http://localhost:5000/api/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        from app import app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🔍 AI Audit Engine Backend - Startup Check")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Run checks
    check_python_version()
    check_dependencies()
    check_tesseract()
    create_directories()
    
    print("\n" + "=" * 50)
    print("✅ All checks passed!")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 