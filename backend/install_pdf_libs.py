#!/usr/bin/env python3
"""
Install additional PDF processing libraries for better encoding handling
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install PDF processing libraries"""
    print("🔧 Installing enhanced PDF processing libraries...")
    print("=" * 50)
    
    # Libraries to install
    libraries = [
        "pymupdf",           # Better encoding handling
        "pdfminer.six",      # Robust text extraction
        "camelot-py[cv]"     # Table extraction
    ]
    
    success_count = 0
    
    for lib in libraries:
        if install_package(lib):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"Installation complete: {success_count}/{len(libraries)} libraries installed")
    
    if success_count == len(libraries):
        print("🎉 All libraries installed successfully!")
        print("\nThese libraries will help with:")
        print("- PyMuPDF: Better encoding and font handling")
        print("- pdfminer: Robust text extraction from complex PDFs")
        print("- Camelot: Table extraction from structured PDFs")
    else:
        print("⚠️  Some libraries failed to install")
        print("Try running: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
