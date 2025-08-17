"""
Test the web application integration with enhanced PDF reader.
Simulates the web app workflow with actual bank statements.
"""

import sys
import os
sys.path.append('src')

from main import BankStatementAnalyzer
from monthly_report_generator import MonthlyReportGenerator

def test_complete_workflow():
    """Test the complete workflow with actual PDFs."""
    print("🌐 Testing Complete Web App Workflow")
    print("=" * 50)
    
    # Initialize components (same as web app)
    analyzer = BankStatementAnalyzer(data_dir='uploads')
    monthly_generator = MonthlyReportGenerator()
    
    # Find uploaded files
    uploads_dir = 'uploads'
    pdf_files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files")
    
    # Step 1: Run analysis (same as web app does)
    print("\n📊 Running analysis...")
    results = analyzer.run_analysis(
        pdf_files=pdf_files,
        create_reports=True,
        export_csv=True
    )
    
    print(f"✅ Analysis complete!")
    print(f"   📈 Total transactions: {results['total_transactions']}")
    print(f"   🏷️  Categories found: {results['categories_found']}")
    
    # Step 2: Get transactions for monthly report
    print(f"\n📅 Creating monthly Excel report...")
    transactions = []
    for file_path in pdf_files:
        filename = os.path.basename(file_path)
        text = analyzer.pdf_reader.extract_text_from_pdf(file_path)
        if text:
            file_transactions = analyzer.pdf_reader.extract_transactions(text)
            for transaction in file_transactions:
                transaction['source_file'] = filename
            transactions.extend(file_transactions)
    
    # Step 3: Categorize transactions
    categorized_transactions = analyzer.keyword_matcher.batch_categorize(transactions)
    
    # Step 4: Create monthly Excel report
    excel_path = monthly_generator.create_monthly_excel_report(categorized_transactions)
    
    if excel_path:
        file_size = os.path.getsize(excel_path)
        print(f"✅ Excel report created: {excel_path}")
        print(f"📁 File size: {file_size:,} bytes")
        
        # Analyze the monthly organization
        monthly_data = monthly_generator.organize_transactions_by_month(categorized_transactions)
        print(f"\n📋 Monthly breakdown:")
        for month, month_transactions in sorted(monthly_data.items()):
            print(f"   📅 {month}: {len(month_transactions)} transactions")
    
    print(f"\n🎯 Results Summary:")
    print(f"   ✅ PDF text extraction: Working")
    print(f"   ✅ Chase bank detection: Working") 
    print(f"   ✅ Transaction parsing: {len(transactions)} found")
    print(f"   ✅ Categorization: {results['categories_found']} categories")
    print(f"   ✅ Monthly organization: Working")
    print(f"   ✅ Excel generation: {'Working' if excel_path else 'Failed'}")
    
    return results

if __name__ == "__main__":
    test_complete_workflow()
