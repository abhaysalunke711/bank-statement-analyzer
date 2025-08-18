"""
Debug script to help identify and fix PDF viewer issues.
"""

import os
import sys
sys.path.append('src')

def debug_pdf_files():
    """Debug PDF file locations and naming."""
    print("🔍 PDF Viewer Debug Information")
    print("=" * 40)
    
    # Check directories
    upload_dir = "uploads"
    output_dir = "output"
    
    print(f"📁 Checking directories:")
    print(f"   Upload directory exists: {os.path.exists(upload_dir)}")
    print(f"   Output directory exists: {os.path.exists(output_dir)}")
    print()
    
    # List files in upload directory
    if os.path.exists(upload_dir):
        upload_files = os.listdir(upload_dir)
        print(f"📄 Files in upload directory ({len(upload_files)} files):")
        for i, file in enumerate(upload_files, 1):
            file_path = os.path.join(upload_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   {i}. {file} ({file_size:,} bytes)")
        print()
    else:
        print("❌ Upload directory not found")
        print()
    
    # List files in output directory
    if os.path.exists(output_dir):
        output_files = os.listdir(output_dir)
        print(f"📊 Files in output directory ({len(output_files)} files):")
        for i, file in enumerate(output_files, 1):
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   {i}. {file} ({file_size:,} bytes)")
        print()
    else:
        print("❌ Output directory not found")
        print()

def test_pdf_serving():
    """Test PDF serving functionality."""
    print("🌐 Testing PDF Serving")
    print("=" * 25)
    
    upload_dir = "uploads"
    
    if not os.path.exists(upload_dir):
        print("❌ No upload directory found")
        return
    
    pdf_files = [f for f in os.listdir(upload_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in upload directory")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF files:")
    for i, pdf_file in enumerate(pdf_files, 1):
        file_path = os.path.join(upload_dir, pdf_file)
        file_size = os.path.getsize(file_path)
        
        print(f"\n{i}. {pdf_file}")
        print(f"   📁 Path: {file_path}")
        print(f"   📏 Size: {file_size:,} bytes")
        print(f"   🔗 URL: /view_pdf/{pdf_file}")
        print(f"   ✅ Readable: {os.access(file_path, os.R_OK)}")
        
        # Check if it's a valid PDF
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                is_pdf = header.startswith(b'%PDF')
                print(f"   📄 Valid PDF: {is_pdf}")
                if not is_pdf:
                    print(f"   ⚠️  File header: {header}")
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")

def show_filename_mapping():
    """Show how filenames are mapped."""
    print("\n🔄 Filename Mapping Analysis")
    print("=" * 35)
    
    upload_dir = "uploads"
    
    if not os.path.exists(upload_dir):
        print("❌ No upload directory found")
        return
    
    pdf_files = [f for f in os.listdir(upload_dir) if f.endswith('.pdf')]
    
    print("📝 Filename mapping (actual → display):")
    for pdf_file in pdf_files:
        # Simulate the filename extraction logic from app.py
        actual_filename = pdf_file
        
        if '_20' in actual_filename:  # Contains timestamp
            parts = actual_filename.split('_')
            if len(parts) >= 3:
                original_name = '_'.join(parts[:-1]) + os.path.splitext(actual_filename)[1]
                original_name = original_name.replace('_' + parts[-1].split('.')[0], '')
            else:
                original_name = actual_filename
        else:
            original_name = actual_filename
        
        print(f"   {actual_filename} → {original_name}")

def show_troubleshooting_steps():
    """Show troubleshooting steps."""
    print("\n🛠️ Troubleshooting Steps")
    print("=" * 30)
    
    print("1. 🔍 Check Browser Console:")
    print("   • Open browser dev tools (F12)")
    print("   • Go to Console tab")
    print("   • Look for JavaScript errors")
    print("   • Check PDF URL being requested")
    print()
    
    print("2. 🌐 Test PDF URL Directly:")
    print("   • Copy PDF URL from console")
    print("   • Open in new browser tab")
    print("   • Check if PDF loads directly")
    print()
    
    print("3. 📄 Verify PDF Files:")
    print("   • Check if PDF files exist in uploads/")
    print("   • Verify file permissions")
    print("   • Test with a simple PDF file")
    print()
    
    print("4. 🔧 Flask Server Logs:")
    print("   • Check terminal running python app.py")
    print("   • Look for PDF serving logs")
    print("   • Check for any error messages")
    print()
    
    print("5. 🧪 Test with Sample PDF:")
    print("   • Create a simple PDF file")
    print("   • Upload through the web interface")
    print("   • Try to view it")

def create_test_instructions():
    """Create step-by-step test instructions."""
    print("\n📋 Testing Instructions")
    print("=" * 25)
    
    print("To test the PDF viewer fix:")
    print()
    print("1. 🚀 Start the application:")
    print("   python app.py")
    print()
    print("2. 🌐 Open browser:")
    print("   http://localhost:5000")
    print()
    print("3. 📤 Upload PDF files:")
    print("   • Use the file upload interface")
    print("   • Upload bank statement PDFs")
    print()
    print("4. 🔍 Check results page:")
    print("   • Look for 'Processed PDF Files' section")
    print("   • Verify file names are displayed correctly")
    print()
    print("5. 📄 Test PDF viewer:")
    print("   • Click on any PDF file card")
    print("   • Check browser console for errors")
    print("   • Verify PDF loads and displays")
    print()
    print("6. 🐛 If issues persist:")
    print("   • Check browser console (F12)")
    print("   • Check Flask server logs")
    print("   • Run this debug script again")

if __name__ == "__main__":
    debug_pdf_files()
    test_pdf_serving()
    show_filename_mapping()
    show_troubleshooting_steps()
    create_test_instructions()
    
    print("\n✅ Debug analysis complete!")
    print("🔧 Use the information above to troubleshoot PDF viewer issues.")
    print("📞 Check browser console and Flask logs for more details.")


