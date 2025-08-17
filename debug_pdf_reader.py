"""
Debug script to analyze PDF extraction issues.
This will help identify why real bank statements aren't extracting transactions.
"""

import sys
import os
import re
sys.path.append('src')

from pdf_reader import PDFReader

def analyze_pdf_content(pdf_path: str):
    """Analyze PDF content in detail to debug extraction issues."""
    print(f"🔍 Analyzing PDF: {os.path.basename(pdf_path)}")
    print("=" * 60)
    
    reader = PDFReader()
    
    # Try both extraction methods
    print("📄 Testing PDF text extraction methods:")
    print("-" * 40)
    
    # Method 1: pdfplumber
    try:
        text_plumber = reader._extract_with_pdfplumber(pdf_path)
        print(f"✅ pdfplumber: Extracted {len(text_plumber)} characters")
        if text_plumber:
            print(f"   First 200 chars: {repr(text_plumber[:200])}")
        else:
            print("   ❌ No text extracted with pdfplumber")
    except Exception as e:
        print(f"   ❌ pdfplumber failed: {e}")
        text_plumber = ""
    
    # Method 2: PyPDF2
    try:
        text_pypdf2 = reader._extract_with_pypdf2(pdf_path)
        print(f"✅ PyPDF2: Extracted {len(text_pypdf2)} characters")
        if text_pypdf2:
            print(f"   First 200 chars: {repr(text_pypdf2[:200])}")
        else:
            print("   ❌ No text extracted with PyPDF2")
    except Exception as e:
        print(f"   ❌ PyPDF2 failed: {e}")
        text_pypdf2 = ""
    
    # Choose the better extraction
    text = text_plumber if len(text_plumber) > len(text_pypdf2) else text_pypdf2
    
    if not text:
        print("\n❌ PROBLEM: No text could be extracted from this PDF!")
        print("   Possible causes:")
        print("   • PDF contains scanned images instead of text")
        print("   • PDF is password protected")
        print("   • PDF uses unsupported encoding")
        print("   • PDF is corrupted")
        print("\n💡 Solutions:")
        print("   • Try OCR software to convert scanned PDFs to text")
        print("   • Check if PDF opens normally in a PDF viewer")
        print("   • Try a different PDF from your bank")
        return False
    
    print(f"\n📝 Successfully extracted {len(text)} characters")
    
    # Analyze the text structure
    print("\n🔍 Analyzing text structure:")
    print("-" * 30)
    
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    print(f"   Total lines: {len(lines)}")
    print(f"   Non-empty lines: {len(non_empty_lines)}")
    
    # Show first few lines
    print(f"\n📋 First 10 non-empty lines:")
    for i, line in enumerate(non_empty_lines[:10], 1):
        print(f"   {i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
    
    # Test transaction pattern matching
    print(f"\n🎯 Testing transaction pattern matching:")
    print("-" * 40)
    
    # Current patterns
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
    amount_pattern = r'[-+]?\$?\d{1,3}(?:,\d{3})*\.?\d{0,2}'
    
    date_matches = []
    amount_matches = []
    potential_transactions = []
    
    for i, line in enumerate(non_empty_lines):
        dates = re.findall(date_pattern, line)
        amounts = re.findall(amount_pattern, line)
        
        if dates:
            date_matches.extend([(i+1, date) for date in dates])
        if amounts:
            amount_matches.extend([(i+1, amount) for amount in amounts])
        if dates and amounts:
            potential_transactions.append((i+1, line, dates, amounts))
    
    print(f"   Date pattern matches: {len(date_matches)}")
    if date_matches:
        print(f"   First 5 date matches:")
        for line_num, date in date_matches[:5]:
            print(f"      Line {line_num}: {date}")
    
    print(f"   Amount pattern matches: {len(amount_matches)}")
    if amount_matches:
        print(f"   First 5 amount matches:")
        for line_num, amount in amount_matches[:5]:
            print(f"      Line {line_num}: {amount}")
    
    print(f"   Potential transactions (lines with both date and amount): {len(potential_transactions)}")
    if potential_transactions:
        print(f"   First 3 potential transactions:")
        for line_num, line, dates, amounts in potential_transactions[:3]:
            print(f"      Line {line_num}: {line[:60]}...")
            print(f"         Dates: {dates}, Amounts: {amounts}")
    else:
        print("   ❌ No lines found with both date and amount patterns!")
        
        # Let's try to understand the format better
        print(f"\n🔧 Trying to understand the bank statement format:")
        print("-" * 50)
        
        # Look for common bank statement keywords
        keywords = ['date', 'description', 'amount', 'balance', 'transaction', 'debit', 'credit']
        for keyword in keywords:
            matches = [line for line in non_empty_lines if keyword.lower() in line.lower()]
            if matches:
                print(f"   Lines containing '{keyword}': {len(matches)}")
                if len(matches) <= 3:
                    for line in matches:
                        print(f"      {line[:80]}...")
        
        # Try alternative date patterns
        print(f"\n🔍 Trying alternative date patterns:")
        alt_date_patterns = [
            (r'\b\d{4}-\d{2}-\d{2}\b', 'YYYY-MM-DD'),
            (r'\b\d{2}/\d{2}/\d{4}\b', 'MM/DD/YYYY'),
            (r'\b\d{2}-\d{2}-\d{4}\b', 'MM-DD-YYYY'),
            (r'\b\d{1,2}\s+\w{3}\s+\d{4}\b', 'DD MMM YYYY'),
            (r'\w{3}\s+\d{1,2},?\s+\d{4}', 'MMM DD, YYYY')
        ]
        
        for pattern, description in alt_date_patterns:
            matches = []
            for line in non_empty_lines:
                found = re.findall(pattern, line)
                if found:
                    matches.extend(found)
            if matches:
                print(f"   {description} pattern: {len(matches)} matches")
                print(f"      Examples: {matches[:3]}")
        
        # Try alternative amount patterns
        print(f"\n💰 Trying alternative amount patterns:")
        alt_amount_patterns = [
            (r'\$\d+\.\d{2}', 'Dollar amounts'),
            (r'\d+\.\d{2}', 'Decimal numbers'),
            (r'\(\d+\.\d{2}\)', 'Parentheses amounts'),
            (r'\d{1,3}(?:,\d{3})*\.\d{2}', 'Comma-separated amounts')
        ]
        
        for pattern, description in alt_amount_patterns:
            matches = []
            for line in non_empty_lines:
                found = re.findall(pattern, line)
                if found:
                    matches.extend(found)
            if matches:
                print(f"   {description}: {len(matches)} matches")
                print(f"      Examples: {matches[:5]}")
    
    return len(potential_transactions) > 0

def suggest_improvements(pdf_path: str):
    """Suggest improvements based on the analysis."""
    print(f"\n💡 Suggestions for improving transaction extraction:")
    print("=" * 55)
    
    print("1. 🔧 Custom Pattern Development:")
    print("   • Analyze the specific format your bank uses")
    print("   • Create custom regex patterns for your bank's layout")
    print("   • Consider table-based extraction for structured data")
    
    print("\n2. 📊 Enhanced Parsing:")
    print("   • Look for table structures in the PDF")
    print("   • Use column-based extraction")
    print("   • Handle multi-line transactions")
    
    print("\n3. 🏦 Bank-Specific Handlers:")
    print("   • Different banks have different formats")
    print("   • May need bank-specific parsing logic")
    print("   • Consider header/footer detection")
    
    print("\n4. 🔍 OCR Fallback:")
    print("   • If PDF is image-based, use OCR")
    print("   • Install pytesseract for OCR capability")
    print("   • Convert images to text before processing")

def main():
    """Main debug function."""
    print("🔍 Bank Statement PDF Debug Tool")
    print("=" * 50)
    
    # Look for uploaded PDFs
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        pdf_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"❌ No PDF files found in {uploads_dir}/")
            print("   Please upload some bank statement PDFs through the web interface first.")
            return
        
        print(f"📁 Found {len(pdf_files)} PDF files in {uploads_dir}/:")
        for i, filename in enumerate(pdf_files, 1):
            print(f"   {i}. {filename}")
        
        # Analyze each PDF
        for pdf_file in pdf_files:
            pdf_path = os.path.join(uploads_dir, pdf_file)
            print(f"\n" + "="*80)
            success = analyze_pdf_content(pdf_path)
            
            if not success:
                suggest_improvements(pdf_path)
                
    else:
        print(f"❌ Uploads directory not found: {uploads_dir}")
        print("   Please run the web app and upload some PDFs first.")

if __name__ == "__main__":
    main()
