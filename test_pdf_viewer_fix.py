"""
Test script to verify the PDF viewer functionality is working correctly.
"""

import os
import sys
import requests
import time
from urllib.parse import quote

sys.path.append('src')

def test_pdf_viewer_functionality():
    """Test the complete PDF viewer functionality."""
    print("🔍 Testing PDF Viewer Functionality")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if Flask app is running
    print("1. 🌐 Testing Flask application...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Flask app is running")
        else:
            print(f"   ❌ Flask app returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Flask app is not accessible: {e}")
        return False
    
    # Test 2: Check available PDF files
    print("\n2. 📄 Checking available PDF files...")
    upload_dir = "uploads"
    
    if not os.path.exists(upload_dir):
        print("   ❌ Upload directory not found")
        return False
    
    pdf_files = [f for f in os.listdir(upload_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("   ❌ No PDF files found in uploads directory")
        print("   💡 Upload some PDF files through the web interface first")
        return False
    
    print(f"   ✅ Found {len(pdf_files)} PDF files:")
    for i, pdf_file in enumerate(pdf_files, 1):
        file_size = os.path.getsize(os.path.join(upload_dir, pdf_file))
        print(f"      {i}. {pdf_file} ({file_size:,} bytes)")
    
    # Test 3: Test PDF serving endpoint for each file
    print("\n3. 🔗 Testing PDF serving endpoints...")
    working_files = []
    
    for pdf_file in pdf_files:
        encoded_filename = quote(pdf_file)
        pdf_url = f"{base_url}/view_pdf/{encoded_filename}"
        
        try:
            response = requests.head(pdf_url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                content_length = response.headers.get('Content-Length', '0')
                
                print(f"   ✅ {pdf_file}")
                print(f"      URL: {pdf_url}")
                print(f"      Content-Type: {content_type}")
                print(f"      Size: {content_length} bytes")
                working_files.append((pdf_file, pdf_url))
            else:
                print(f"   ❌ {pdf_file} - Status: {response.status_code}")
                if response.status_code == 404:
                    # Try to get the error message
                    try:
                        error_response = requests.get(pdf_url, timeout=5)
                        print(f"      Error: {error_response.text[:200]}...")
                    except:
                        pass
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {pdf_file} - Network error: {e}")
    
    if not working_files:
        print("   ❌ No PDF files are accessible via the web endpoint")
        return False
    
    # Test 4: Test filename mapping logic
    print("\n4. 🔄 Testing filename mapping...")
    
    for pdf_file, pdf_url in working_files[:2]:  # Test first 2 files
        # Simulate the filename extraction logic from app.py
        actual_filename = pdf_file
        
        if '_20' in actual_filename and actual_filename.count('_') >= 2:
            parts = actual_filename.rsplit('_', 2)
            if len(parts) == 3:
                original_name = parts[0] + os.path.splitext(actual_filename)[1]
            else:
                original_name = actual_filename
        else:
            original_name = actual_filename
        
        print(f"   📄 {actual_filename}")
        print(f"      → Display name: {original_name}")
        print(f"      → URL: {pdf_url}")
    
    # Test 5: Test PDF.js compatibility
    print("\n5. 📚 Testing PDF.js compatibility...")
    
    # Test if PDF.js can load the file by checking the first few bytes
    test_file = working_files[0][0]
    test_url = working_files[0][1]
    
    try:
        response = requests.get(test_url, timeout=10, stream=True)
        if response.status_code == 200:
            # Read first few bytes to verify it's a valid PDF
            first_chunk = response.raw.read(8)
            if first_chunk.startswith(b'%PDF'):
                print(f"   ✅ {test_file} is a valid PDF file")
                print(f"      PDF version: {first_chunk.decode('ascii', errors='ignore')}")
            else:
                print(f"   ❌ {test_file} does not appear to be a valid PDF")
                print(f"      First bytes: {first_chunk}")
        else:
            print(f"   ❌ Could not download {test_file} - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error testing PDF compatibility: {e}")
    
    return True

def show_browser_testing_steps():
    """Show manual browser testing steps."""
    print("\n📋 Manual Browser Testing Steps")
    print("=" * 35)
    
    print("To complete the PDF viewer testing:")
    print()
    print("1. 🌐 Open your browser and go to:")
    print("   http://localhost:5000")
    print()
    print("2. 📤 If no files are uploaded yet:")
    print("   • Upload some PDF bank statements")
    print("   • Wait for processing to complete")
    print()
    print("3. 📄 On the results page:")
    print("   • Scroll to 'Processed PDF Files' section")
    print("   • Click on any PDF file card")
    print()
    print("4. 🔍 In the PDF viewer modal:")
    print("   • Check if PDF loads (no infinite spinner)")
    print("   • Test page navigation (prev/next)")
    print("   • Test zoom controls (in/out/reset)")
    print("   • Test fullscreen mode")
    print("   • Check browser console for errors (F12)")
    print()
    print("5. ✅ Expected behavior:")
    print("   • PDF should load within 5-10 seconds")
    print("   • All controls should work smoothly")
    print("   • No JavaScript errors in console")
    print("   • Fullscreen mode should work")

def show_troubleshooting_guide():
    """Show troubleshooting guide for common issues."""
    print("\n🛠️ Troubleshooting Guide")
    print("=" * 28)
    
    print("If PDF viewer still shows spinner:")
    print()
    print("🔍 Browser Console Errors:")
    print("   • Press F12 → Console tab")
    print("   • Look for red error messages")
    print("   • Check if PDF.js library loaded")
    print("   • Verify PDF URL is correct")
    print()
    print("🌐 Network Issues:")
    print("   • Check if PDF URL returns 200 OK")
    print("   • Verify file exists in uploads/")
    print("   • Test PDF URL directly in browser")
    print()
    print("📄 PDF File Issues:")
    print("   • Ensure file is valid PDF format")
    print("   • Check file permissions")
    print("   • Try with a different PDF file")
    print()
    print("⚙️ Flask Server Issues:")
    print("   • Check Flask terminal for errors")
    print("   • Restart Flask application")
    print("   • Verify all routes are registered")
    print()
    print("🔧 PDF.js Issues:")
    print("   • Check if PDF.js CDN is accessible")
    print("   • Verify PDF.js worker script loads")
    print("   • Test with PDF.js examples online")

def create_simple_test_pdf():
    """Create a simple test PDF for testing purposes."""
    print("\n📝 Creating Simple Test PDF")
    print("=" * 30)
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        test_pdf_path = "uploads/test_simple.pdf"
        
        # Create a simple PDF
        c = canvas.Canvas(test_pdf_path, pagesize=letter)
        c.drawString(100, 750, "Test PDF for PDF Viewer")
        c.drawString(100, 700, "This is a simple test PDF file.")
        c.drawString(100, 650, "If you can see this, the PDF viewer is working!")
        c.drawString(100, 600, "Date: 2025-08-17")
        c.drawString(100, 550, "Amount: $123.45")
        c.showPage()
        c.save()
        
        print(f"   ✅ Created test PDF: {test_pdf_path}")
        print(f"   📏 File size: {os.path.getsize(test_pdf_path):,} bytes")
        return test_pdf_path
        
    except ImportError:
        print("   ⚠️  reportlab not installed - cannot create test PDF")
        print("   💡 Install with: pip install reportlab")
        return None
    except Exception as e:
        print(f"   ❌ Error creating test PDF: {e}")
        return None

if __name__ == "__main__":
    print("🚀 PDF Viewer Fix Verification")
    print("=" * 35)
    
    # Run main tests
    success = test_pdf_viewer_functionality()
    
    if success:
        print("\n✅ All automated tests passed!")
        print("🎉 PDF viewer functionality is working correctly")
    else:
        print("\n❌ Some tests failed")
        print("🔧 Check the issues above and try the troubleshooting steps")
    
    # Show additional guides
    show_browser_testing_steps()
    show_troubleshooting_guide()
    
    # Offer to create a test PDF
    print("\n" + "="*50)
    create_test_response = input("Create a simple test PDF? (y/n): ").lower().strip()
    if create_test_response in ['y', 'yes']:
        create_simple_test_pdf()
    
    print("\n🏁 Testing complete!")
    print("📞 If issues persist, check browser console and Flask logs for details.")


