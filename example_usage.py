"""
Example usage script for Bank Statement Analyzer.
Demonstrates how to use the analyzer programmatically.
"""

import os
import sys

# Add src to path
sys.path.append('src')

from main import BankStatementAnalyzer

def example_basic_usage():
    """Basic usage example - process all PDFs in data directory."""
    print("=== Basic Usage Example ===")
    
    # Initialize analyzer
    analyzer = BankStatementAnalyzer()
    
    # Run analysis on all PDFs in data directory
    results = analyzer.run_analysis()
    
    print(f"Processed {results['total_transactions']} transactions")
    print(f"Found {results['categories_found']} categories")
    
    if results['sheet_url']:
        print(f"Google Sheet created: {results['sheet_url']}")
    
    if results['csv_path']:
        print(f"CSV backup saved: {results['csv_path']}")

def example_specific_files():
    """Example processing specific PDF files."""
    print("\n=== Specific Files Example ===")
    
    # List of specific PDF files to process
    pdf_files = [
        'data/bank_statement_jan_2024.pdf',
        'data/bank_statement_feb_2024.pdf'
    ]
    
    # Check if files exist (for demo purposes)
    existing_files = [f for f in pdf_files if os.path.exists(f)]
    
    if not existing_files:
        print("No example PDF files found. Please add PDF files to the data/ directory.")
        return
    
    analyzer = BankStatementAnalyzer()
    
    # Process only specific files
    results = analyzer.run_analysis(
        pdf_files=existing_files,
        sheet_title="January-February 2024 Analysis"
    )
    
    print(f"Processed {results['total_transactions']} transactions from {len(existing_files)} files")

def example_custom_keywords():
    """Example with custom keyword configuration."""
    print("\n=== Custom Keywords Example ===")
    
    analyzer = BankStatementAnalyzer()
    
    # Set custom keywords programmatically
    custom_keywords = {
        "Coffee Shops": {
            "exact": ["starbucks", "dunkin", "coffee bean", "peets"],
            "fuzzy": ["coffee", "espresso", "latte"],
            "regex": [".*coffee.*", ".*cafe.*"]
        },
        "Online Shopping": {
            "exact": ["amazon", "ebay", "etsy", "shopify"],
            "fuzzy": ["online", "e-commerce"],
            "regex": [".*amazon.*", ".*shop.*"]
        },
        "Subscriptions": {
            "exact": ["netflix", "spotify", "hulu", "disney+", "apple music"],
            "fuzzy": ["subscription", "monthly", "streaming"],
            "regex": [".*subscription.*", ".*monthly.*"]
        }
    }
    
    analyzer.keyword_matcher.set_keywords(custom_keywords)
    
    # Run analysis with custom keywords
    results = analyzer.run_analysis(sheet_title="Custom Categories Analysis")
    
    print(f"Used custom keywords for {results['categories_found']} categories")

def example_csv_only():
    """Example that only creates CSV output (no Google Sheets)."""
    print("\n=== CSV Only Example ===")
    
    # Create analyzer without Google Sheets credentials
    analyzer = BankStatementAnalyzer()
    analyzer.sheets_client = None  # Disable Google Sheets
    
    results = analyzer.run_analysis(
        sheet_title="CSV Only Analysis",
        export_csv=True
    )
    
    if results['csv_path']:
        print(f"CSV file created: {results['csv_path']}")
        print("You can open this file in Excel or any spreadsheet application")

def main():
    """Run all examples."""
    print("Bank Statement Analyzer - Example Usage")
    print("=" * 50)
    
    # Check if data directory exists
    if not os.path.exists('data'):
        print("Creating data directory...")
        os.makedirs('data')
        print("Please add PDF bank statements to the 'data' directory and run again.")
        return
    
    # Check for PDF files
    pdf_files = [f for f in os.listdir('data') if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("No PDF files found in data directory.")
        print("Please add PDF bank statements to the 'data' directory and run again.")
        return
    
    print(f"Found {len(pdf_files)} PDF files in data directory:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    
    # Run examples
    try:
        example_basic_usage()
        example_specific_files()
        example_custom_keywords()
        example_csv_only()
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Check the logs in the output directory for more details.")
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("Check the 'output' directory for generated files and logs.")

if __name__ == "__main__":
    main()
