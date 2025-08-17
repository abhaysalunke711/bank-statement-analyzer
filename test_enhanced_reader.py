"""
Test the enhanced PDF reader with actual bank statements.
"""

import sys
import os
sys.path.append('src')

from enhanced_pdf_reader import EnhancedPDFReader

def test_enhanced_reader():
    """Test the enhanced reader with uploaded PDFs."""
    print("🔍 Testing Enhanced PDF Reader")
    print("=" * 50)
    
    reader = EnhancedPDFReader()
    
    # Look for uploaded PDFs
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print(f"❌ No uploads directory found")
        return
    
    pdf_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"❌ No PDF files found in {uploads_dir}/")
        return
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(uploads_dir, pdf_file)
        print(f"\n📄 Processing: {pdf_file}")
        print("-" * 60)
        
        # Extract text
        text = reader.extract_text_from_pdf(pdf_path)
        if not text:
            print("❌ No text extracted")
            continue
        
        print(f"✅ Extracted {len(text):,} characters")
        
        # Detect bank type
        bank_type = reader.detect_bank_type(text)
        print(f"🏦 Detected bank: {bank_type}")
        
        # Extract transactions
        transactions = reader.extract_transactions(text)
        print(f"📊 Found {len(transactions)} transactions")
        
        if transactions:
            print(f"\n📋 First 5 transactions:")
            for i, trans in enumerate(transactions[:5], 1):
                print(f"   {i}. Date: {trans['date']}")
                print(f"      Description: {trans['description'][:60]}...")
                print(f"      Amount: {trans['amount']}")
                print(f"      Raw: {trans['raw_line'][:80]}...")
                print()
        else:
            print("❌ No transactions found")
            
            # Show some sample lines for debugging
            lines = text.split('\n')
            non_empty = [line.strip() for line in lines if line.strip()]
            
            print(f"\n🔍 Sample lines from PDF (showing lines with numbers):")
            count = 0
            for i, line in enumerate(non_empty):
                if any(char.isdigit() for char in line) and len(line) > 10:
                    print(f"   Line {i+1}: {line[:100]}...")
                    count += 1
                    if count >= 10:
                        break

if __name__ == "__main__":
    test_enhanced_reader()
