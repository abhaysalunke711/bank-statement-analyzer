"""
Test the income/expense analyzer and color coding functionality.
"""

import sys
import os
sys.path.append('src')

from income_expense_analyzer import IncomeExpenseAnalyzer
from enhanced_monthly_report_generator import EnhancedMonthlyReportGenerator

def test_income_expense_detection():
    """Test the income/expense detection with sample transactions."""
    print("🧪 Testing Income/Expense Detection")
    print("=" * 50)
    
    analyzer = IncomeExpenseAnalyzer()
    
    # Sample transactions for testing
    test_transactions = [
        {'date': '1/15', 'description': 'DIRECT DEPOSIT PAYROLL', 'amount': '2500.00', 'category': 'Income'},
        {'date': '1/16', 'description': 'WALMART SUPERCENTER #1234', 'amount': '-85.43', 'category': 'Shopping'},
        {'date': '1/17', 'description': 'ATM WITHDRAWAL', 'amount': '-100.00', 'category': 'Banking & Finance'},
        {'date': '1/18', 'description': 'ACH CREDIT REFUND', 'amount': '25.99', 'category': 'Uncategorized'},
        {'date': '1/19', 'description': 'STARBUCKS #5678', 'amount': '-4.75', 'category': 'Food & Dining'},
        {'date': '1/20', 'description': 'INTEREST EARNED', 'amount': '1.25', 'category': 'Banking & Finance'},
        {'date': '1/21', 'description': 'DEBIT PURCHASE AMAZON.COM', 'amount': '-49.99', 'category': 'Shopping'},
        {'date': '1/22', 'description': 'MOBILE DEPOSIT', 'amount': '150.00', 'category': 'Uncategorized'},
    ]
    
    print("🔍 Analyzing sample transactions:")
    print("-" * 50)
    
    classified_transactions = analyzer.classify_transactions(test_transactions)
    
    for i, transaction in enumerate(classified_transactions, 1):
        amount = transaction['amount']
        transaction_type = transaction['transaction_type']
        confidence = transaction['type_confidence']
        reason = transaction['type_reason']
        
        # Color coding for console output
        type_color = "🟢" if transaction_type == 'income' else "🔴"
        confidence_icon = "🎯" if confidence >= 0.8 else "⚠️" if confidence >= 0.6 else "❓"
        
        print(f"{i:2}. {type_color} {transaction_type.upper():7} | {confidence_icon} {confidence:5.1%} | ${amount:>8} | {transaction['description'][:30]}")
        print(f"    📝 Reason: {reason}")
        print()
    
    # Generate summary statistics
    summary = analyzer.get_income_expense_summary(classified_transactions)
    
    print("📊 Summary Statistics:")
    print("-" * 30)
    print(f"💰 Total Income:     ${summary['total_income']:8.2f} ({summary['income_count']} transactions)")
    print(f"💸 Total Expenses:   ${summary['total_expenses']:8.2f} ({summary['expense_count']} transactions)")
    print(f"📈 Net Amount:       ${summary['net_amount']:8.2f}")
    print(f"📊 Average Income:   ${summary['income_avg']:8.2f}")
    print(f"📊 Average Expense:  ${summary['expense_avg']:8.2f}")
    
    return classified_transactions

def test_enhanced_excel_generation():
    """Test the enhanced Excel generation with color coding."""
    print("\n🎨 Testing Enhanced Excel Generation")
    print("=" * 50)
    
    # Use the classified transactions from the previous test
    classified_transactions = test_income_expense_detection()
    
    # Create enhanced Excel report
    generator = EnhancedMonthlyReportGenerator(output_dir='output')
    
    print("📊 Generating colored Excel report...")
    excel_path = generator.create_monthly_excel_report(
        classified_transactions, 
        filename='test_income_expense_colored.xlsx'
    )
    
    if excel_path and os.path.exists(excel_path):
        print(f"✅ Enhanced Excel report created: {excel_path}")
        print("🎨 Features included:")
        print("   • Green color coding for income transactions")
        print("   • Red color coding for expense transactions")
        print("   • Income/expense summary with color highlighting")
        print("   • Transaction type column with confidence levels")
        print("   • Monthly breakdown with net amount color coding")
        
        # Get file size
        file_size = os.path.getsize(excel_path)
        print(f"   • File size: {file_size:,} bytes")
        
        return excel_path
    else:
        print("❌ Failed to create enhanced Excel report")
        return None

def test_color_detection_accuracy():
    """Test the accuracy of income/expense detection."""
    print("\n🎯 Testing Detection Accuracy")
    print("=" * 40)
    
    analyzer = IncomeExpenseAnalyzer()
    
    # Test cases with expected results
    test_cases = [
        # (description, amount, expected_type, min_confidence)
        ('DIRECT DEPOSIT PAYROLL', '2500.00', 'income', 0.8),
        ('SALARY PAYMENT', '3000.00', 'income', 0.8),
        ('ATM WITHDRAWAL', '-100.00', 'expense', 0.8),
        ('DEBIT PURCHASE WALMART', '-50.00', 'expense', 0.8),
        ('ACH CREDIT REFUND', '25.00', 'income', 0.7),
        ('INTEREST EARNED', '1.50', 'income', 0.8),
        ('SERVICE FEE', '-15.00', 'expense', 0.7),
        ('MOBILE DEPOSIT', '200.00', 'income', 0.6),
    ]
    
    correct_predictions = 0
    total_predictions = len(test_cases)
    
    print("Test Case Results:")
    print("-" * 40)
    
    for description, amount, expected_type, min_confidence in test_cases:
        transaction = {'description': description, 'amount': amount}
        result = analyzer.analyze_transaction(transaction)
        
        is_correct = result.type == expected_type
        meets_confidence = result.confidence >= min_confidence
        
        if is_correct:
            correct_predictions += 1
        
        status = "✅" if is_correct and meets_confidence else "⚠️" if is_correct else "❌"
        
        print(f"{status} {description[:25]:25} | Expected: {expected_type:7} | Got: {result.type:7} | Conf: {result.confidence:.1%}")
    
    accuracy = correct_predictions / total_predictions
    print(f"\n🎯 Accuracy: {accuracy:.1%} ({correct_predictions}/{total_predictions})")
    
    if accuracy >= 0.8:
        print("🎉 Excellent accuracy!")
    elif accuracy >= 0.6:
        print("👍 Good accuracy!")
    else:
        print("⚠️  Consider improving detection rules.")

if __name__ == "__main__":
    print("🚀 Starting Income/Expense Analysis Tests")
    print("=" * 60)
    
    # Run all tests
    test_income_expense_detection()
    excel_path = test_enhanced_excel_generation()
    test_color_detection_accuracy()
    
    print("\n🎉 All tests completed!")
    
    if excel_path:
        print(f"\n📋 Next Steps:")
        print(f"1. Open the Excel file: {excel_path}")
        print(f"2. Verify the color coding (green for income, red for expenses)")
        print(f"3. Test the web app with: python app.py")
        print(f"4. Upload PDF files and check the colored tables in browser")
    
    print("\n🌐 Ready to test the enhanced web application!")
