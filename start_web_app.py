"""
Startup script for the Bank Statement Analyzer Web Application.
Provides easy launch with system checks and helpful information.
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'flask', 'werkzeug', 'xlsxwriter', 'matplotlib', 
        'seaborn', 'pandas', 'PyPDF2', 'pdfplumber'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def check_directories():
    """Ensure all required directories exist."""
    directories = ['templates', 'static', 'uploads', 'output', 'config', 'src']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}/")
        else:
            print(f"✅ Directory exists: {directory}/")

def open_browser_delayed():
    """Open browser after a delay to ensure server is running."""
    time.sleep(2)
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Opened web browser")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please manually open: http://localhost:5000")

def display_welcome():
    """Display welcome message and instructions."""
    print("🏦 Bank Statement Analyzer - Web Application")
    print("=" * 60)
    print("🎯 Features:")
    print("   • Upload multiple PDF bank statements")
    print("   • Automatic transaction categorization")
    print("   • Monthly organization with separate Excel tabs")
    print("   • Visual charts and comprehensive reports")
    print("   • Drag & drop interface with progress tracking")
    print()
    print("📋 What you'll get:")
    print("   • Excel file with monthly tabs (Jan 2024, Feb 2024, etc.)")
    print("   • Summary tab with overall financial statistics")
    print("   • Category breakdowns and detailed transaction lists")
    print("   • CSV backups and visual charts")
    print()

def main():
    """Main startup function."""
    display_welcome()
    
    print("🔧 System Check:")
    print("-" * 30)
    
    # Check dependencies
    missing_packages = check_dependencies()
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print(f"   Run: pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All dependencies installed")
    
    # Check directories
    check_directories()
    
    # Check key files
    key_files = ['app.py', 'src/main.py', 'templates/index.html']
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            return False
    
    print("\n🚀 Starting Web Application...")
    print("-" * 40)
    print("📍 Server: http://localhost:5000")
    print("📁 Upload folder: uploads/")
    print("📊 Output folder: output/")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 40)
    
    # Schedule browser opening
    Timer(2.0, open_browser_delayed).start()
    
    # Start the Flask app
    try:
        # Import and run the Flask app
        sys.path.append('.')
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("Thank you for using Bank Statement Analyzer!")
        
    except Exception as e:
        print(f"\n❌ Error starting web application: {e}")
        print("Please check the error logs and try again.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Failed to start the application")
        print("Please check the requirements and try again.")
        sys.exit(1)
