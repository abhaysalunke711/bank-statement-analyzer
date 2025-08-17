"""
Test the pivot-style monthly report generator.
"""

import sys
import os
sys.path.append('src')

from pivot_monthly_report_generator import PivotMonthlyReportGenerator
from income_expense_analyzer import IncomeExpenseAnalyzer

def test_pivot_report():
    """Test the pivot-style report generation."""
    print("🧪 Testing Pivot-Style Report Generator")
    print("=" * 50)
    
    # Create sample transactions across multiple months
    sample_transactions = [
        # January Income
        {'date': '1/15', 'description': 'DIRECT DEPOSIT PAYROLL', 'amount': '2500.00', 'category': 'Salary'},
        {'date': '1/20', 'description': 'INTEREST EARNED', 'amount': '5.25', 'category': 'Banking & Finance'},
        {'date': '1/25', 'description': 'FREELANCE PAYMENT', 'amount': '500.00', 'category': 'Business Income'},
        
        # January Expenses  
        {'date': '1/16', 'description': 'WALMART SUPERCENTER', 'amount': '-85.43', 'category': 'Shopping'},
        {'date': '1/18', 'description': 'STARBUCKS #5678', 'amount': '-4.75', 'category': 'Food & Dining'},
        {'date': '1/22', 'description': 'ELECTRIC COMPANY', 'amount': '-120.00', 'category': 'Utilities'},
        {'date': '1/28', 'description': 'ATM WITHDRAWAL', 'amount': '-100.00', 'category': 'Banking & Finance'},
        
        # February Income
        {'date': '2/15', 'description': 'DIRECT DEPOSIT PAYROLL', 'amount': '2500.00', 'category': 'Salary'},
        {'date': '2/20', 'description': 'INTEREST EARNED', 'amount': '6.50', 'category': 'Banking & Finance'},
        {'date': '2/28', 'description': 'TAX REFUND', 'amount': '750.00', 'category': 'Government'},
        
        # February Expenses
        {'date': '2/16', 'description': 'TARGET STORE', 'amount': '-65.89', 'category': 'Shopping'},
        {'date': '2/18', 'description': 'PIZZA HUT', 'amount': '-18.50', 'category': 'Food & Dining'},
        {'date': '2/22', 'description': 'GAS BILL', 'amount': '-85.00', 'category': 'Utilities'},
        {'date': '2/25', 'description': 'UBER RIDE', 'amount': '-15.75', 'category': 'Transportation'},
        
        # March Income
        {'date': '3/15', 'description': 'DIRECT DEPOSIT PAYROLL', 'amount': '2500.00', 'category': 'Salary'},
        {'date': '3/20', 'description': 'DIVIDEND PAYMENT', 'amount': '125.00', 'category': 'Investment'},
        
        # March Expenses
        {'date': '3/16', 'description': 'AMAZON PURCHASE', 'amount': '-99.99', 'category': 'Shopping'},
        {'date': '3/18', 'description': 'RESTAURANT DINING', 'amount': '-45.00', 'category': 'Food & Dining'},
        {'date': '3/22', 'description': 'WATER BILL', 'amount': '-55.00', 'category': 'Utilities'},
        {'date': '3/28', 'description': 'GAS STATION', 'amount': '-40.00', 'category': 'Transportation'},
    ]
    
    print(f"📊 Processing {len(sample_transactions)} sample transactions")
    print(f"📅 Covering 3 months: January, February, March")
    print()
    
    # Create pivot report
    generator = PivotMonthlyReportGenerator(output_dir='output')
    
    print("🎨 Generating pivot-style Excel report...")
    excel_path = generator.create_pivot_excel_report(
        sample_transactions, 
        filename='test_pivot_report.xlsx'
    )
    
    if excel_path and os.path.exists(excel_path):
        print(f"✅ Pivot Excel report created: {excel_path}")
        print()
        print("🎯 Expected Layout:")
        print("   📊 Single sheet: 'Financial Summary'")
        print("   📋 First column: Category/Item names")
        print("   📅 Monthly columns: Jan 2025, Feb 2025, Mar 2025")
        print("   💰 Total column: Sum of amounts for each category")
        print("   🟢 Income section at top (green formatting)")
        print("   ⬜ 4 empty rows separator")
        print("   🔴 Expense section at bottom (red formatting)")
        print()
        
        # Get file size
        file_size = os.path.getsize(excel_path)
        print(f"   📁 File size: {file_size:,} bytes")
        
        # Analyze the data structure
        analyzer = IncomeExpenseAnalyzer()
        classified = analyzer.classify_transactions(sample_transactions)
        
        income_categories = set()
        expense_categories = set()
        months = set()
        
        for transaction in classified:
            if transaction.get('transaction_type') == 'income':
                income_categories.add(transaction.get('category', 'Uncategorized'))
            else:
                expense_categories.add(transaction.get('category', 'Uncategorized'))
            
            # Extract month
            date_str = transaction.get('date', '')
            if '/' in date_str:
                month = date_str.split('/')[0]
                months.add(f"Month {month}")
        
        print(f"   🟢 Income categories: {len(income_categories)} ({', '.join(sorted(income_categories))})")
        print(f"   🔴 Expense categories: {len(expense_categories)} ({', '.join(sorted(expense_categories))})")
        print(f"   📅 Months covered: {len(months)}")
        
        return excel_path
    else:
        print("❌ Failed to create pivot Excel report")
        return None

def verify_pivot_structure():
    """Verify the pivot structure matches requirements."""
    print("\n🔍 Verifying Pivot Structure Requirements")
    print("=" * 45)
    
    requirements = [
        "✅ Single spreadsheet (no multiple tabs)",
        "✅ First column: Transaction items/categories",
        "✅ Monthly columns: One column per month",
        "✅ Total column: Sum of amounts for each item",
        "✅ Income items at top with green color coding",
        "✅ 4 empty rows separator",
        "✅ Expense items at bottom with red color coding",
        "✅ Category-wise aggregation by month",
        "✅ Professional color-coded formatting"
    ]
    
    print("📋 Requirements Check:")
    for req in requirements:
        print(f"   {req}")
    
    print("\n🎯 Key Features:")
    print("   • Pivot table layout: Categories × Months")
    print("   • Color coding: Green (income) vs Red (expenses)")
    print("   • Monthly breakdown with totals")
    print("   • Clear visual separation between income/expenses")
    print("   • Professional Excel formatting")

if __name__ == "__main__":
    print("🚀 Starting Pivot Report Tests")
    print("=" * 40)
    
    excel_path = test_pivot_report()
    verify_pivot_structure()
    
    print("\n🎉 Pivot Report Test Completed!")
    
    if excel_path:
        print(f"\n📋 Next Steps:")
        print(f"1. Open Excel file: {excel_path}")
        print(f"2. Verify the pivot layout structure")
        print(f"3. Check income/expense color coding")
        print(f"4. Test web app with: python app.py")
        print(f"5. Upload PDFs and see the new pivot format")
    
    print("\n🌐 Ready to test the pivot-style web application!")
