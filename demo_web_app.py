"""
Complete demonstration of the Bank Statement Analyzer Web Application.
Shows all features including monthly organization and Excel tab generation.
"""

import os
import sys
import time
sys.path.append('src')

from monthly_report_generator import MonthlyReportGenerator

def create_demo_data():
    """Create comprehensive demo data spanning multiple months."""
    demo_transactions = [
        # January 2024 - Heavy spending month
        {'date': '01/01/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$4500.00', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/02/2024', 'description': 'RENT PAYMENT PROPERTY MGMT', 'category': 'Home & Garden', 'amount': '-$1200.00', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/03/2024', 'description': 'STARBUCKS #12345 SEATTLE WA', 'category': 'Food & Dining', 'amount': '-$5.75', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/05/2024', 'description': 'AMAZON.COM AMZN.COM/BILL WA', 'category': 'Shopping', 'amount': '-$127.99', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/08/2024', 'description': 'SHELL OIL 87654321 REDMOND WA', 'category': 'Transportation', 'amount': '-$65.20', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/10/2024', 'description': 'WHOLE FOODS MARKET #456', 'category': 'Food & Dining', 'amount': '-$89.45', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/12/2024', 'description': 'NETFLIX.COM NETFLIX.COM CA', 'category': 'Entertainment', 'amount': '-$15.99', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/15/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$4500.00', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/18/2024', 'description': 'VERIZON WIRELESS PAYMENT', 'category': 'Utilities', 'amount': '-$95.00', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/22/2024', 'description': 'COSTCO WHOLESALE #123', 'category': 'Shopping', 'amount': '-$234.56', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/25/2024', 'description': 'UBER TRIP SEATTLE WA', 'category': 'Transportation', 'amount': '-$23.75', 'source_file': 'jan_2024_statement.pdf'},
        {'date': '01/28/2024', 'description': 'MCDONALDS #9876 BELLEVUE WA', 'category': 'Food & Dining', 'amount': '-$12.99', 'source_file': 'jan_2024_statement.pdf'},
        
        # February 2024 - Moderate spending
        {'date': '02/01/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$4500.00', 'source_file': 'feb_2024_statement.pdf'},
        {'date': '02/02/2024', 'description': 'RENT PAYMENT PROPERTY MGMT', 'category': 'Home & Garden', 'amount': '-$1200.00', 'source_file': 'feb_2024_statement.pdf'},
        {'date': '02/05/2024', 'description': 'TARGET T-1234 REDMOND WA', 'category': 'Shopping', 'amount': '-$67.89', 'source_file': 'feb_2024_statement.pdf'},
        {'date': '02/08/2024', 'description': 'CHIPOTLE #2345 SEATTLE WA', 'category': 'Food & Dining', 'amount': '-$14.50', 'source_file': 'feb_2024_statement.pdf'},
        {'date': '02/12/2024', 'description': 'CVS PHARMACY #4567', 'category': 'Healthcare', 'amount': '-$34.28', 'source_file': 'feb_2024_statement.pdf'},
        {'date': '02/15/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$4500.00', 'source_file': 'feb_2024_statement.pdf'},
        {'date': '02/18/2024', 'description': 'SPOTIFY PREMIUM SUBSCRIPTION', 'category': 'Entertainment', 'amount': '-$9.99', 'source_file': 'feb_2024_statement.pdf'},
        {'date': '02/22/2024', 'description': 'HOME DEPOT #8901', 'category': 'Shopping', 'amount': '-$156.78', 'source_file': 'feb_2024_statement.pdf'},
        {'date': '02/25/2024', 'description': 'LYFT RIDE SEATTLE WA', 'category': 'Transportation', 'amount': '-$18.50', 'source_file': 'feb_2024_statement.pdf'},
        {'date': '02/28/2024', 'description': 'DUNKIN #5678 BELLEVUE WA', 'category': 'Food & Dining', 'amount': '-$4.25', 'source_file': 'feb_2024_statement.pdf'},
        
        # March 2024 - Light spending month
        {'date': '03/01/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$4500.00', 'source_file': 'mar_2024_statement.pdf'},
        {'date': '03/02/2024', 'description': 'RENT PAYMENT PROPERTY MGMT', 'category': 'Home & Garden', 'amount': '-$1200.00', 'source_file': 'mar_2024_statement.pdf'},
        {'date': '03/08/2024', 'description': 'WALMART SUPERCENTER #5678', 'category': 'Shopping', 'amount': '-$45.67', 'source_file': 'mar_2024_statement.pdf'},
        {'date': '03/12/2024', 'description': 'PANERA BREAD #789', 'category': 'Food & Dining', 'amount': '-$11.99', 'source_file': 'mar_2024_statement.pdf'},
        {'date': '03/15/2024', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$4500.00', 'source_file': 'mar_2024_statement.pdf'},
        {'date': '03/20/2024', 'description': 'BEST BUY #9012', 'category': 'Shopping', 'amount': '-$299.99', 'source_file': 'mar_2024_statement.pdf'},
        {'date': '03/25/2024', 'description': 'ELECTRIC COMPANY PAYMENT', 'category': 'Utilities', 'amount': '-$125.00', 'source_file': 'mar_2024_statement.pdf'},
        
        # April 2024 - Different date formats
        {'date': '2024-04-01', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$4500.00', 'source_file': 'apr_2024_statement.pdf'},
        {'date': '04-02-2024', 'description': 'RENT PAYMENT PROPERTY MGMT', 'category': 'Home & Garden', 'amount': '-$1200.00', 'source_file': 'apr_2024_statement.pdf'},
        {'date': '4/8/2024', 'description': 'TRADER JOES #123', 'category': 'Food & Dining', 'amount': '-$67.89', 'source_file': 'apr_2024_statement.pdf'},
        {'date': '04/15/24', 'description': 'DEPOSIT PAYROLL', 'category': 'Banking & Finance', 'amount': '+$4500.00', 'source_file': 'apr_2024_statement.pdf'},
        {'date': '4-20-2024', 'description': 'HULU STREAMING SERVICE', 'category': 'Entertainment', 'amount': '-$12.99', 'source_file': 'apr_2024_statement.pdf'},
    ]
    
    return demo_transactions

def demonstrate_monthly_excel_generation():
    """Demonstrate the complete monthly Excel generation process."""
    print("🏦 Bank Statement Analyzer - Complete Web App Demo")
    print("=" * 60)
    
    # Create demo data
    print("📊 Creating comprehensive demo data...")
    transactions = create_demo_data()
    print(f"   ✅ Generated {len(transactions)} transactions across 4 months")
    
    # Initialize monthly generator
    generator = MonthlyReportGenerator()
    
    # Organize by month
    print(f"\n📅 Organizing transactions by month...")
    monthly_data = generator.organize_transactions_by_month(transactions)
    
    total_income = 0
    total_expenses = 0
    
    for month, month_transactions in sorted(monthly_data.items()):
        month_income = sum(generator._clean_amount(t.get('amount', 0)) for t in month_transactions if generator._clean_amount(t.get('amount', 0)) > 0)
        month_expenses = abs(sum(generator._clean_amount(t.get('amount', 0)) for t in month_transactions if generator._clean_amount(t.get('amount', 0)) < 0))
        
        total_income += month_income
        total_expenses += month_expenses
        
        formatted_month = generator._format_sheet_name(month)
        print(f"   📋 {formatted_month:<12} | {len(month_transactions):2d} transactions | Income: ${month_income:>8,.2f} | Expenses: ${month_expenses:>8,.2f}")
    
    print(f"\n💰 Overall Summary:")
    print(f"   📈 Total Income:  ${total_income:>10,.2f}")
    print(f"   📉 Total Expenses: ${total_expenses:>10,.2f}")
    print(f"   💵 Net Amount:    ${total_income - total_expenses:>10,.2f}")
    
    # Create Excel file
    print(f"\n📝 Creating Excel file with monthly tabs...")
    excel_path = generator.create_monthly_excel_report(transactions, "demo_monthly_analysis.xlsx")
    
    if excel_path and os.path.exists(excel_path):
        file_size = os.path.getsize(excel_path)
        print(f"   ✅ Excel file created: {excel_path}")
        print(f"   📁 File size: {file_size:,} bytes")
        
        print(f"\n📋 Excel File Structure:")
        print(f"   📄 Summary Tab:")
        print(f"      • Overall financial statistics")
        print(f"      • Monthly breakdown table")
        print(f"      • Income vs expenses comparison")
        
        for month in sorted(monthly_data.keys()):
            formatted_name = generator._format_sheet_name(month)
            trans_count = len(monthly_data[month])
            print(f"   📄 {formatted_name} Tab:")
            print(f"      • Monthly summary ({trans_count} transactions)")
            print(f"      • Category breakdown with totals")
            print(f"      • Detailed transaction list")
            print(f"      • Professional formatting with colors")
        
        return excel_path
    else:
        print(f"   ❌ Failed to create Excel file")
        return None

def show_web_app_features():
    """Show web application features."""
    print(f"\n🌐 Web Application Features:")
    print("=" * 40)
    
    features = [
        "🖱️  Drag & drop PDF upload interface",
        "📱 Responsive design for all devices", 
        "⚡ Real-time progress indicators",
        "🔒 Secure file handling with auto-cleanup",
        "📊 Instant analysis and categorization",
        "📅 Monthly Excel tabs generation",
        "📈 Visual charts and comprehensive reports",
        "💾 Multiple download formats (Excel, CSV, PNG)",
        "🎨 Modern Bootstrap UI with animations",
        "🔧 Configurable transaction categories"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print(f"\n🚀 How to Use the Web App:")
    print("=" * 30)
    print("1. 🌐 Start: Double-click 'start_web_app.bat' or run 'python app.py'")
    print("2. 📁 Upload: Drag & drop your PDF bank statements")
    print("3. ⏳ Process: Watch real-time analysis progress")
    print("4. 📊 Download: Get your Excel file with monthly tabs")
    print("5. 📈 Analyze: Open Excel to explore your organized financial data")
    
    print(f"\n📋 What Makes This Special:")
    print("=" * 35)
    print("✨ Each statement month gets its own Excel tab")
    print("✨ Professional formatting with colors and summaries")
    print("✨ Smart categorization with 10+ built-in categories")
    print("✨ Web-based - no command line knowledge needed")
    print("✨ Handles multiple PDF files simultaneously")
    print("✨ Automatic date parsing from various formats")

def main():
    """Run the complete demonstration."""
    # Generate the demo Excel file
    excel_path = demonstrate_monthly_excel_generation()
    
    # Show web app features
    show_web_app_features()
    
    print(f"\n🎯 Demo Results:")
    print("=" * 25)
    if excel_path:
        print(f"✅ Demo Excel file: {excel_path}")
        print(f"✅ Web app components: Ready")
        print(f"✅ Monthly tabs: Working")
        print(f"✅ Financial summaries: Generated")
    
    print(f"\n🎉 Your Bank Statement Analyzer Web App is Complete!")
    print("=" * 55)
    print("🌟 Key Achievement: Monthly Excel tabs with organized financial data")
    print("🌟 Ready to process your real bank statements via web browser")
    print("🌟 Transform messy PDFs into organized monthly financial reports")
    
    print(f"\n🚀 Next Steps:")
    print("1. Run: start_web_app.bat (Windows) or python app.py")
    print("2. Open: http://localhost:5000 in your browser")
    print("3. Upload: Your PDF bank statements")
    print("4. Download: Organized Excel files with monthly tabs")
    print("5. Enjoy: Professional financial analysis at your fingertips!")

if __name__ == "__main__":
    main()
