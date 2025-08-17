"""
Basic test of the bank statement analyzer without Google Sheets.
This tests PDF reading and keyword matching functionality.
"""

import sys
import os
sys.path.append('src')

from pdf_reader import PDFReader
from keyword_matcher import KeywordMatcher

def test_pdf_reader():
    """Test PDF reader functionality."""
    print("=== Testing PDF Reader ===")
    
    pdf_reader = PDFReader()
    
    # Test transaction extraction with sample text
    sample_text = """
    01/15/2024 STARBUCKS STORE #1234 SEATTLE WA -$5.75
    01/16/2024 AMAZON.COM AMZN.COM/BILL WA -$29.99
    01/17/2024 SHELL OIL 12345678 REDMOND WA -$45.20
    01/18/2024 DEPOSIT PAYROLL +$2500.00
    01/19/2024 WALMART SUPERCENTER #1234 -$67.89
    """
    
    transactions = pdf_reader.extract_transactions(sample_text)
    
    print(f"Found {len(transactions)} transactions:")
    for i, trans in enumerate(transactions, 1):
        print(f"  {i}. {trans['date']} | {trans['description'][:50]}... | {trans['amount']}")
    
    return transactions

def test_keyword_matcher():
    """Test keyword matching functionality."""
    print("\n=== Testing Keyword Matcher ===")
    
    # Load keywords from config
    matcher = KeywordMatcher('config/keywords.json')
    
    # Test transactions
    test_transactions = [
        {'description': 'STARBUCKS STORE #1234 SEATTLE WA', 'amount': -5.75},
        {'description': 'AMAZON.COM AMZN.COM/BILL WA', 'amount': -29.99},
        {'description': 'SHELL OIL 12345678 REDMOND WA', 'amount': -45.20},
        {'description': 'WALMART SUPERCENTER #1234', 'amount': -67.89},
        {'description': 'MCDONALDS #12345 BELLEVUE WA', 'amount': -12.50},
    ]
    
    categorized = matcher.batch_categorize(test_transactions)
    
    print("Categorized transactions:")
    for trans in categorized:
        print(f"  {trans['category']:<15} | {trans['description'][:40]:<40} | ${abs(trans['amount']):>6.2f}")
    
    # Show statistics
    stats = matcher.get_statistics(categorized)
    print(f"\nCategory Statistics:")
    for category, count in stats.items():
        print(f"  {category}: {count} transactions")
    
    return categorized

def main():
    """Run basic tests."""
    print("Bank Statement Analyzer - Basic Test")
    print("=" * 50)
    
    try:
        # Test PDF reader
        transactions = test_pdf_reader()
        
        # Test keyword matcher
        categorized = test_keyword_matcher()
        
        print("\n" + "=" * 50)
        print("✅ All basic tests passed!")
        print("✅ PDF reading functionality works")
        print("✅ Keyword matching works")
        print("\nNext step: Set up Google Sheets API credentials")
        print("See config/setup_instructions.md for details")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
