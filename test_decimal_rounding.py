"""
Test decimal rounding functionality across all report generators.
"""

import sys
import os
sys.path.append('src')

from pivot_monthly_report_generator import PivotMonthlyReportGenerator
from income_expense_analyzer import IncomeExpenseAnalyzer
from excel_viewer import ExcelViewer

def test_decimal_rounding():
    """Test that all amounts are properly rounded to 2 decimal places."""
    print("🧪 Testing Decimal Rounding")
    print("=" * 40)
    
    # Create sample transactions with various decimal precision
    sample_transactions = [
        # Transactions with irregular decimal places
        {'date': '1/15', 'description': 'SALARY PAYMENT', 'amount': '2500.123456', 'category': 'Salary'},
        {'date': '1/16', 'description': 'GROCERY STORE', 'amount': '-85.4321', 'category': 'Shopping'},
        {'date': '1/17', 'description': 'INTEREST EARNED', 'amount': '5.789012', 'category': 'Banking & Finance'},
        {'date': '1/18', 'description': 'COFFEE SHOP', 'amount': '-4.9876', 'category': 'Food & Dining'},
        {'date': '1/19', 'description': 'FREELANCE PAYMENT', 'amount': '500.555555', 'category': 'Business Income'},
        {'date': '1/20', 'description': 'ATM FEE', 'amount': '-2.5', 'category': 'Banking & Finance'},
        
        # February transactions
        {'date': '2/15', 'description': 'SALARY PAYMENT', 'amount': '2500.987654', 'category': 'Salary'},
        {'date': '2/16', 'description': 'RESTAURANT', 'amount': '-25.333333', 'category': 'Food & Dining'},
        {'date': '2/17', 'description': 'DIVIDEND', 'amount': '75.111111', 'category': 'Investment'},
        {'date': '2/18', 'description': 'GAS STATION', 'amount': '-40.666666', 'category': 'Transportation'},
    ]
    
    print(f"📊 Processing {len(sample_transactions)} transactions with irregular decimals")
    print("🔍 Checking decimal precision in all calculations...")
    print()
    
    # Test income/expense analyzer rounding
    analyzer = IncomeExpenseAnalyzer()
    classified_transactions = analyzer.classify_transactions(sample_transactions)
    summary = analyzer.get_income_expense_summary(classified_transactions)
    
    print("💰 Income/Expense Summary (should all be 2 decimals):")
    print(f"   Total Income: ${summary['total_income']}")
    print(f"   Total Expenses: ${summary['total_expenses']}")
    print(f"   Net Amount: ${summary['net_amount']}")
    print(f"   Average Income: ${summary['income_avg']}")
    print(f"   Average Expense: ${summary['expense_avg']}")
    
    # Check if all values have at most 2 decimal places
    def check_decimal_places(value, name):
        if isinstance(value, (int, float)):
            decimal_places = len(str(value).split('.')[-1]) if '.' in str(value) else 0
            if decimal_places <= 2:
                print(f"   ✅ {name}: {decimal_places} decimal places")
                return True
            else:
                print(f"   ❌ {name}: {decimal_places} decimal places (should be ≤ 2)")
                return False
        return True
    
    print("\n🔍 Decimal Places Validation:")
    all_valid = True
    all_valid &= check_decimal_places(summary['total_income'], 'Total Income')
    all_valid &= check_decimal_places(summary['total_expenses'], 'Total Expenses')
    all_valid &= check_decimal_places(summary['net_amount'], 'Net Amount')
    all_valid &= check_decimal_places(summary['income_avg'], 'Average Income')
    all_valid &= check_decimal_places(summary['expense_avg'], 'Average Expense')
    
    # Test pivot report generator
    print("\n📊 Testing Pivot Report Generator...")
    generator = PivotMonthlyReportGenerator(output_dir='output')
    excel_path = generator.create_pivot_excel_report(
        classified_transactions, 
        filename='test_decimal_rounding.xlsx'
    )
    
    if excel_path and os.path.exists(excel_path):
        print(f"✅ Pivot Excel report created: {excel_path}")
        
        # Read the Excel file and check the values
        viewer = ExcelViewer()
        excel_data = viewer.read_excel_file(excel_path)
        
        if excel_data and excel_data.get('sheets'):
            sheet_data = list(excel_data['sheets'].values())[0]
            print(f"\n📋 Checking Excel Sheet Values:")
            
            # Look for monetary values in the sheet
            monetary_values = []
            for row in sheet_data['rows']:
                for cell in row:
                    cell_str = str(cell)
                    if '$' in cell_str or (cell_str.replace('.', '').replace('-', '').isdigit() and '.' in cell_str):
                        try:
                            # Extract numeric value
                            numeric_value = float(cell_str.replace('$', '').replace(',', '').strip())
                            if numeric_value != 0:  # Skip zero values
                                monetary_values.append((cell_str, numeric_value))
                        except (ValueError, TypeError):
                            pass
            
            print(f"   Found {len(monetary_values)} monetary values in Excel sheet")
            
            # Check first few values for decimal precision
            for i, (original, value) in enumerate(monetary_values[:10]):
                decimal_places = len(str(value).split('.')[-1]) if '.' in str(value) else 0
                status = "✅" if decimal_places <= 2 else "❌"
                print(f"   {status} {original} ({decimal_places} decimal places)")
                if decimal_places > 2:
                    all_valid = False
        
        # Get file size
        file_size = os.path.getsize(excel_path)
        print(f"   📁 File size: {file_size:,} bytes")
    else:
        print("❌ Failed to create pivot Excel report")
        all_valid = False
    
    print(f"\n🎯 Overall Validation Result:")
    if all_valid:
        print("✅ All decimal values are properly rounded to 2 decimal places!")
    else:
        print("❌ Some values have more than 2 decimal places - needs fixing")
    
    return all_valid

def demonstrate_before_after():
    """Show before and after examples of decimal rounding."""
    print("\n📝 Before/After Decimal Rounding Examples:")
    print("=" * 50)
    
    test_values = [
        2500.123456,
        85.4321,
        5.789012,
        4.9876,
        500.555555,
        2.5,
        25.333333,
        75.111111,
        40.666666
    ]
    
    print("Original Value    →    Rounded Value")
    print("-" * 35)
    for value in test_values:
        rounded = round(value, 2)
        print(f"${value:<12} →    ${rounded}")

if __name__ == "__main__":
    print("🚀 Starting Decimal Rounding Tests")
    print("=" * 50)
    
    result = test_decimal_rounding()
    demonstrate_before_after()
    
    print("\n🎉 Decimal Rounding Test Completed!")
    
    if result:
        print("✅ All systems properly round decimals to 2 places")
        print("💰 Financial calculations are now precise and consistent")
    else:
        print("⚠️  Some systems need decimal rounding fixes")
    
    print("\n🌐 Ready to test with properly rounded decimals!")
