"""
Main script for Bank Statement Analyzer.
Orchestrates PDF reading, keyword matching, and Google Sheets creation.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import List, Dict

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_pdf_reader import EnhancedPDFReader
from keyword_matcher import KeywordMatcher
from google_sheets_client import GoogleSheetsClient
from report_generator import ReportGenerator

class BankStatementAnalyzer:
    def __init__(self, config_dir: str = 'config', data_dir: str = 'data', output_dir: str = 'output'):
        self.config_dir = config_dir
        self.data_dir = data_dir
        self.output_dir = output_dir
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.pdf_reader = EnhancedPDFReader()
        self.keyword_matcher = KeywordMatcher()
        self.sheets_client = None
        self.report_generator = ReportGenerator(output_dir)
        
        # Load configuration
        self._load_configuration()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configure logging
        log_file = os.path.join(self.output_dir, f'analyzer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Bank Statement Analyzer initialized")
    
    def _load_configuration(self):
        """Load configuration files."""
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load keywords
        keywords_path = os.path.join(self.config_dir, 'keywords.json')
        if os.path.exists(keywords_path):
            self.keyword_matcher.load_keywords(keywords_path)
        else:
            self.logger.warning(f"Keywords file not found: {keywords_path}")
            self.logger.info("Creating default keywords template...")
            self.keyword_matcher.export_keywords_template(keywords_path)
            self.keyword_matcher.load_keywords(keywords_path)
        
        # Initialize Google Sheets client
        credentials_path = os.path.join(self.config_dir, 'credentials.json')
        service_account_path = os.path.join(self.config_dir, 'service_account.json')
        
        if os.path.exists(service_account_path):
            self.sheets_client = GoogleSheetsClient(service_account_path=service_account_path)
        elif os.path.exists(credentials_path):
            self.sheets_client = GoogleSheetsClient(credentials_path=credentials_path)
        else:
            self.logger.warning("No Google Sheets credentials found")
            self.logger.info(f"Please place credentials.json or service_account.json in {self.config_dir}")
    
    def process_pdf_files(self, pdf_files: List[str] = None) -> List[Dict]:
        """
        Process PDF files and extract transactions.
        
        Args:
            pdf_files: List of specific PDF files to process, or None for all PDFs in data directory
            
        Returns:
            List of all transactions from processed files
        """
        all_transactions = []
        
        if pdf_files:
            # Process specific files
            for pdf_file in pdf_files:
                if not os.path.exists(pdf_file):
                    self.logger.error(f"File not found: {pdf_file}")
                    continue
                
                self.logger.info(f"Processing: {pdf_file}")
                text = self.pdf_reader.extract_text_from_pdf(pdf_file)
                
                if text:
                    transactions = self.pdf_reader.extract_transactions(text)
                    
                    # Add source file information
                    for transaction in transactions:
                        transaction['source_file'] = os.path.basename(pdf_file)
                    
                    all_transactions.extend(transactions)
                    self.logger.info(f"Extracted {len(transactions)} transactions from {pdf_file}")
                else:
                    self.logger.warning(f"No text extracted from {pdf_file}")
        else:
            # Process all PDFs in data directory
            if not os.path.exists(self.data_dir):
                self.logger.error(f"Data directory not found: {self.data_dir}")
                return []
            
            pdf_texts = self.pdf_reader.process_multiple_pdfs(self.data_dir)
            
            for filename, text in pdf_texts.items():
                transactions = self.pdf_reader.extract_transactions(text)
                
                # Add source file information
                for transaction in transactions:
                    transaction['source_file'] = filename
                
                all_transactions.extend(transactions)
                self.logger.info(f"Extracted {len(transactions)} transactions from {filename}")
        
        return all_transactions
    
    def categorize_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """
        Categorize transactions using keyword matching.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of categorized transactions
        """
        self.logger.info(f"Categorizing {len(transactions)} transactions")
        
        categorized = self.keyword_matcher.batch_categorize(transactions)
        
        # Log statistics
        stats = self.keyword_matcher.get_statistics(categorized)
        self.logger.info("Categorization statistics:")
        for category, count in stats.items():
            self.logger.info(f"  {category}: {count} transactions")
        
        return categorized
    
    def create_google_sheet(self, transactions: List[Dict], title: str = None) -> str:
        """
        Create Google Sheet with transaction data.
        
        Args:
            transactions: List of categorized transactions
            title: Custom title for the spreadsheet
            
        Returns:
            Spreadsheet URL if successful, empty string otherwise
        """
        if not self.sheets_client:
            self.logger.error("Google Sheets client not initialized")
            return ""
        
        if not title:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title = f"Bank Statement Analysis - {timestamp}"
        
        spreadsheet_id = self.sheets_client.create_bank_statement_sheet(transactions, title)
        
        if spreadsheet_id:
            url = self.sheets_client.get_spreadsheet_url(spreadsheet_id)
            self.logger.info(f"Google Sheet created: {url}")
            return url
        else:
            self.logger.error("Failed to create Google Sheet")
            return ""
    
    def export_to_csv(self, transactions: List[Dict], filename: str = None) -> str:
        """
        Export transactions to CSV file as backup.
        
        Args:
            transactions: List of categorized transactions
            filename: Custom filename for the CSV
            
        Returns:
            Path to created CSV file
        """
        import csv
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bank_statement_analysis_{timestamp}.csv"
        
        csv_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['date', 'description', 'category', 'amount', 'source_file']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for transaction in transactions:
                    writer.writerow({
                        'date': transaction.get('date', ''),
                        'description': transaction.get('description', ''),
                        'category': transaction.get('category', 'Uncategorized'),
                        'amount': transaction.get('amount', 0),
                        'source_file': transaction.get('source_file', '')
                    })
            
            self.logger.info(f"CSV export created: {csv_path}")
            return csv_path
            
        except Exception as e:
            self.logger.error(f"Error creating CSV export: {e}")
            return ""
    
    def run_analysis(self, pdf_files: List[str] = None, sheet_title: str = None, 
                    export_csv: bool = True, create_reports: bool = True) -> Dict[str, str]:
        """
        Run complete bank statement analysis.
        
        Args:
            pdf_files: Specific PDF files to process
            sheet_title: Custom title for Google Sheet
            export_csv: Whether to export CSV backup
            create_reports: Whether to create category summaries and charts
            
        Returns:
            Dictionary with results (sheet_url, csv_path, etc.)
        """
        results = {
            'sheet_url': '',
            'csv_path': '',
            'total_transactions': 0,
            'categories_found': 0,
            'report_files': {}
        }
        
        try:
            # Step 1: Process PDFs
            self.logger.info("Starting PDF processing...")
            transactions = self.process_pdf_files(pdf_files)
            
            if not transactions:
                self.logger.warning("No transactions found in PDF files")
                return results
            
            results['total_transactions'] = len(transactions)
            
            # Step 2: Categorize transactions
            self.logger.info("Starting transaction categorization...")
            categorized_transactions = self.categorize_transactions(transactions)
            
            # Count unique categories
            categories = set(t.get('category', 'Uncategorized') for t in categorized_transactions)
            results['categories_found'] = len(categories)
            
            # Step 3: Create Google Sheet
            if self.sheets_client:
                self.logger.info("Creating Google Sheet...")
                sheet_url = self.create_google_sheet(categorized_transactions, sheet_title)
                results['sheet_url'] = sheet_url
            else:
                self.logger.warning("Skipping Google Sheet creation (no credentials)")
            
            # Step 4: Create comprehensive reports
            if create_reports:
                self.logger.info("Creating comprehensive reports...")
                analysis = self.report_generator.analyze_transactions(categorized_transactions)
                report_files = self.report_generator.create_comprehensive_report(analysis)
                results['report_files'] = report_files
                
                # Log analysis summary
                overall = analysis.get('overall', {})
                self.logger.info(f"Financial Summary:")
                self.logger.info(f"  Total Income: ${overall.get('total_income', 0):.2f}")
                self.logger.info(f"  Total Expenses: ${overall.get('total_expenses', 0):.2f}")
                self.logger.info(f"  Net Amount: ${overall.get('net_amount', 0):.2f}")
            
            # Step 5: Export basic CSV backup
            if export_csv:
                self.logger.info("Creating basic CSV backup...")
                csv_path = self.export_to_csv(categorized_transactions)
                results['csv_path'] = csv_path
            
            self.logger.info("Analysis completed successfully!")
            self.logger.info(f"Processed {results['total_transactions']} transactions")
            self.logger.info(f"Found {results['categories_found']} categories")
            
            if results['sheet_url']:
                self.logger.info(f"Google Sheet: {results['sheet_url']}")
            
            if results['csv_path']:
                self.logger.info(f"CSV backup: {results['csv_path']}")
            
            # Log report files
            for report_type, file_path in results['report_files'].items():
                self.logger.info(f"{report_type}: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}", exc_info=True)
        
        return results

def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(description='Bank Statement Analyzer')
    parser.add_argument('--pdf-files', nargs='+', help='Specific PDF files to process')
    parser.add_argument('--data-dir', default='data', help='Directory containing PDF files')
    parser.add_argument('--config-dir', default='config', help='Configuration directory')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    parser.add_argument('--sheet-title', help='Custom title for Google Sheet')
    parser.add_argument('--no-csv', action='store_true', help='Skip CSV export')
    parser.add_argument('--no-reports', action='store_true', help='Skip comprehensive reports and charts')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = BankStatementAnalyzer(
        config_dir=args.config_dir,
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )
    
    # Run analysis
    results = analyzer.run_analysis(
        pdf_files=args.pdf_files,
        sheet_title=args.sheet_title,
        export_csv=not args.no_csv,
        create_reports=not args.no_reports
    )
    
    # Print results
    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)
    print(f"Total transactions: {results['total_transactions']}")
    print(f"Categories found: {results['categories_found']}")
    
    if results['sheet_url']:
        print(f"Google Sheet: {results['sheet_url']}")
    
    if results['csv_path']:
        print(f"CSV backup: {results['csv_path']}")
    
    # Print report files
    if results['report_files']:
        print("\nGenerated Reports:")
        for report_type, file_path in results['report_files'].items():
            report_name = report_type.replace('_', ' ').title()
            print(f"  {report_name}: {file_path}")
    
    print("="*50)

if __name__ == "__main__":
    main()
