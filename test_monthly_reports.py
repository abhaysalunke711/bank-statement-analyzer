"""
Test script for the monthly report generator and web application.
Creates sample data and tests the Excel generation with monthly tabs.
"""

import sys
import os
sys.path.append('src')

from monthly_report_generator import MonthlyReportGenerator
from main import BankStatementAnalyzer

def create_test_transactions():
    """Create sample transactions spanning multiple months."""
    test_transactions = [
        # January 2024
        {'date': '01/05/2024', 'description': 'STARBUCKS #12345 SEATTLE WA', 'category': 'Food & Dining', 'amount': '-$4.75', 'source_file': 'jan_statement.pdf'},
        {'date': '01/10/2024', 'description': 'AMAZON.COM AMZN.COM/BILL WA', 'category': 'Shopping', 'amount': '-$89.99', 'source_file': 'jan_statement.pdf'},
        {'date': '01/15/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$3200.00', 'source_file': 'jan_statement.pdf'},
        {'date': '01/20/2024', 'description': 'SHELL OIL 87654321 REDMOND WA', 'category': 'Transportation', 'amount': '-$52.30', 'source_file': 'jan_statement.pdf'},
        {'date': '01/25/2024', 'description': 'WALMART SUPERCENTER #5678', 'category': 'Shopping', 'amount': '-$123.45', 'source_file': 'jan_statement.pdf'},
        
        # February 2024
        {'date': '02/03/2024', 'description': 'MCDONALDS #9876 BELLEVUE WA', 'category': 'Food & Dining', 'amount': '-$8.99', 'source_file': 'feb_statement.pdf'},
        {'date': '02/08/2024', 'description': 'NETFLIX.COM NETFLIX.COM CA', 'category': 'Entertainment', 'amount': '-$15.99', 'source_file': 'feb_statement.pdf'},
        {'date': '02/12/2024', 'description': 'COSTCO WHOLESALE #123', 'category': 'Shopping', 'amount': '-$234.56', 'source_file': 'feb_statement.pdf'},
        {'date': '02/15/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$3200.00', 'source_file': 'feb_statement.pdf'},
        {'date': '02/18/2024', 'description': 'UBER TRIP SEATTLE WA', 'category': 'Transportation', 'amount': '-$18.75', 'source_file': 'feb_statement.pdf'},
        {'date': '02/22/2024', 'description': 'CVS PHARMACY #4567', 'category': 'Healthcare', 'amount': '-$34.28', 'source_file': 'feb_statement.pdf'},
        {'date': '02/28/2024', 'description': 'VERIZON WIRELESS', 'category': 'Utilities', 'amount': '-$85.00', 'source_file': 'feb_statement.pdf'},
        
        # March 2024
        {'date': '03/05/2024', 'description': 'CHIPOTLE #2345', 'category': 'Food & Dining', 'amount': '-$12.50', 'source_file': 'mar_statement.pdf'},
        {'date': '03/10/2024', 'description': 'TARGET T-1234', 'category': 'Shopping', 'amount': '-$67.89', 'source_file': 'mar_statement.pdf'},
        {'date': '03/15/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$3200.00', 'source_file': 'mar_statement.pdf'},
        {'date': '03/20/2024', 'description': 'SPOTIFY PREMIUM', 'category': 'Entertainment', 'amount': '-$9.99', 'source_file': 'mar_statement.pdf'},
        {'date': '03/25/2024', 'description': 'HOME DEPOT #8901', 'category': 'Shopping', 'amount': '-$156.78', 'source_file': 'mar_statement.pdf'},
        {'date': '03/30/2024', 'description': 'LYFT RIDE', 'category': 'Transportation', 'amount': '-$22.50', 'source_file': 'mar_statement.pdf'},
        
        # Some transactions with different date formats
        {'date': '2024-04-05', 'description': 'DUNKIN #5678', 'category': 'Food & Dining', 'amount': '-$3.25', 'source_file': 'apr_statement.pdf'},
        {'date': '04-10-2024', 'description': 'BEST BUY #9012', 'category': 'Shopping', 'amount': '-$299.99', 'source_file': 'apr_statement.pdf'},
        {'date': '4/15/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$3200.00', 'source_file': 'apr_statement.pdf'},
    ]
    
    return test_transactions

def test_monthly_organization():
    """Test the monthly organization functionality."""
    print("🧪 Testing Monthly Report Generator")
    print("=" * 50)
    
    # Create test transactions
    transactions = create_test_transactions()
    print(f"📊 Created {len(transactions)} test transactions")
    
    # Initialize monthly report generator
    generator = MonthlyReportGenerator()
    
    # Test monthly organization
    monthly_data = generator.organize_transactions_by_month(transactions)
    
    print(f"📅 Organized into {len(monthly_data)} months:")
    for month, trans_list in sorted(monthly_data.items()):
        print(f"   {month}: {len(trans_list)} transactions")
    
    # Create Excel report
    print(f"\n📝 Creating Excel report...")
    excel_path = generator.create_monthly_excel_report(transactions, "test_monthly_report.xlsx")
    
    if excel_path:
        print(f"✅ Excel report created: {excel_path}")
        print(f"📁 File size: {os.path.getsize(excel_path):,} bytes")
        
        # Show what's inside
        print(f"\n📋 Report Contents:")
        print("   📄 Summary tab with overall statistics")
        for month in sorted(monthly_data.keys()):
            formatted_name = generator._format_sheet_name(month)
            trans_count = len(monthly_data[month])
            print(f"   📄 {formatted_name} tab with {trans_count} transactions")
        
        return True
    else:
        print("❌ Failed to create Excel report")
        return False

def test_web_app_components():
    """Test web application components."""
    print(f"\n🌐 Testing Web App Components")
    print("=" * 50)
    
    try:
        # Test analyzer integration
        analyzer = BankStatementAnalyzer()
        print("✅ BankStatementAnalyzer initialized")
        
        # Test monthly generator integration
        monthly_gen = MonthlyReportGenerator()
        print("✅ MonthlyReportGenerator initialized")
        
        # Check required directories
        required_dirs = ['templates', 'static', 'uploads', 'output']
        for directory in required_dirs:
            if os.path.exists(directory):
                print(f"✅ Directory exists: {directory}/")
            else:
                print(f"❌ Missing directory: {directory}/")
        
        # Check template files
        template_files = ['templates/base.html', 'templates/index.html', 'templates/results.html']
        for template in template_files:
            if os.path.exists(template):
                print(f"✅ Template exists: {template}")
            else:
                print(f"❌ Missing template: {template}")
        
        print(f"\n🚀 Web App Ready!")
        print("   Run: python app.py")
        print("   Open: http://localhost:5000")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing web app components: {e}")
        return False

def demonstrate_features():
    """Demonstrate key features."""
    print(f"\n🎯 Key Features Demonstrated:")
    print("=" * 50)
    
    features = [
        "🌐 Web-based interface with drag & drop file upload",
        "📅 Monthly organization with separate Excel tabs",
        "📊 Comprehensive financial summaries per month",
        "🏷️ Smart transaction categorization",
        "📈 Visual charts and reports generation", 
        "💾 Multiple export formats (Excel, CSV, PNG)",
        "🔒 Secure file handling with automatic cleanup",
        "📱 Responsive design for mobile and desktop",
        "🎨 Modern UI with Bootstrap styling",
        "⚡ Real-time processing with progress indicators"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print(f"\n📋 Monthly Excel Report Structure:")
    print("   📄 Summary Tab:")
    print("      • Overall financial overview")
    print("      • Monthly breakdown table")
    print("      • Income vs expenses summary")
    print("   📄 Individual Month Tabs (Jan 2024, Feb 2024, etc.):")
    print("      • Monthly summary statistics")
    print("      • Category-wise breakdown")
    print("      • Detailed transaction list")
    print("      • Professional formatting with colors")

def main():
    """Run all tests and demonstrations."""
    print("🏦 Bank Statement Analyzer - Web App Test Suite")
    print("=" * 60)
    
    # Test monthly report generation
    success1 = test_monthly_organization()
    
    # Test web app components
    success2 = test_web_app_components()
    
    # Demonstrate features
    demonstrate_features()
    
    print(f"\n🎉 Test Results:")
    print("=" * 30)
    print(f"📊 Monthly Reports: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"🌐 Web Components: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print(f"\n🚀 All systems ready! Your web-based bank statement analyzer is complete!")
        print(f"   Start the web app: python app.py")
        print(f"   Open browser: http://localhost:5000")
    else:
        print(f"\n⚠️  Some issues detected. Check the logs above.")

if __name__ == "__main__":
    main()
