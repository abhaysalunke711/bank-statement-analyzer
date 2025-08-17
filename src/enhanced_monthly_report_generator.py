"""
Enhanced Monthly Report Generator with Income/Expense Color Coding.
Creates Excel files with green for income and red for expenses.
"""

import os
import logging
import pandas as pd
import xlsxwriter
from datetime import datetime
from typing import List, Dict, Tuple
import re
from collections import defaultdict

from income_expense_analyzer import IncomeExpenseAnalyzer

class EnhancedMonthlyReportGenerator:
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.income_expense_analyzer = IncomeExpenseAnalyzer()
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def organize_transactions_by_month(self, transactions: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Organize transactions by month-year.
        
        Args:
            transactions: List of categorized transactions
            
        Returns:
            Dictionary with month-year as keys and transaction lists as values
        """
        monthly_data = defaultdict(list)
        
        for transaction in transactions:
            date_str = transaction.get('date', '')
            month_year = self._extract_month_year(date_str)
            
            if month_year:
                monthly_data[month_year].append(transaction)
            else:
                # If date parsing fails, put in 'Unknown' category
                monthly_data['Unknown'].append(transaction)
        
        return dict(monthly_data)
    
    def _extract_month_year(self, date_str: str) -> str:
        """Extract month-year from date string."""
        if not date_str:
            return None
        
        try:
            # Handle Chase format MM/DD (assume current year or extract from filename)
            if re.match(r'^\d{1,2}/\d{1,2}$', date_str):
                # For MM/DD format, assume 2025 (or extract from context)
                date_str += '/2025'
            
            # Try various date formats
            date_formats = [
                '%m/%d/%Y',    # 01/15/2024
                '%m-%d-%Y',    # 01-15-2024
                '%Y-%m-%d',    # 2024-01-15
                '%d/%m/%Y',    # 15/01/2024
                '%d-%m-%Y',    # 15-01-2024
                '%m/%d/%y',    # 01/15/24
                '%m-%d-%y',    # 01-15-24
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt)
                    return parsed_date.strftime('%Y-%m')  # Format: 2024-01
                except ValueError:
                    continue
            
            # Try regex extraction for embedded dates
            date_patterns = [
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',  # MM/DD/YY or MM-DD-YY
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        if len(groups[2]) == 2:  # Two-digit year
                            year = int('20' + groups[2]) if int(groups[2]) < 50 else int('19' + groups[2])
                        else:
                            year = int(groups[2])
                        
                        # Assume first pattern is MM/DD/YYYY
                        if len(groups[0]) <= 2 and int(groups[0]) <= 12:
                            month = int(groups[0])
                        else:
                            month = int(groups[1])
                        
                        return f"{year:04d}-{month:02d}"
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not parse date '{date_str}': {e}")
            return None
    
    def create_monthly_excel_report(self, transactions: List[Dict], filename: str = None) -> str:
        """
        Create an Excel file with separate tabs for each month and color coding for income/expenses.
        
        Args:
            transactions: List of categorized transactions
            filename: Custom filename for the Excel file
            
        Returns:
            Path to created Excel file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monthly_bank_analysis_colored_{timestamp}.xlsx"
        
        excel_path = os.path.join(self.output_dir, filename)
        
        try:
            # Classify transactions as income or expenses
            self.logger.info("Analyzing transactions for income/expense classification...")
            classified_transactions = self.income_expense_analyzer.classify_transactions(transactions)
            
            # Organize transactions by month
            monthly_data = self.organize_transactions_by_month(classified_transactions)
            
            if not monthly_data:
                self.logger.warning("No monthly data to process")
                return ""
            
            # Create Excel workbook
            workbook = xlsxwriter.Workbook(excel_path)
            
            # Define color-coded formats
            formats = self._create_color_formats(workbook)
            
            # Create summary sheet first
            self._create_summary_sheet(workbook, monthly_data, formats)
            
            # Create a sheet for each month
            sorted_months = sorted(monthly_data.keys(), key=lambda x: x if x != 'Unknown' else 'ZZZZ')
            
            for month_year in sorted_months:
                month_transactions = monthly_data[month_year]
                sheet_name = self._format_sheet_name(month_year)
                
                self._create_month_sheet(
                    workbook, sheet_name, month_transactions, formats
                )
            
            workbook.close()
            
            self.logger.info(f"Enhanced Excel report with color coding created: {excel_path}")
            self.logger.info(f"Created {len(monthly_data)} monthly tabs with income/expense analysis")
            
            return excel_path
            
        except Exception as e:
            self.logger.error(f"Error creating enhanced Excel report: {e}")
            return ""
    
    def _create_color_formats(self, workbook) -> Dict:
        """Create all formatting styles including color coding."""
        formats = {}
        
        # Header formats
        formats['header'] = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        
        formats['summary_header'] = workbook.add_format({
            'bold': True,
            'bg_color': '#70AD47',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        
        # Income formats (Green theme)
        formats['income_amount'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#E2EFDA',  # Light green background
            'font_color': '#0D5016',  # Dark green text
            'border': 1,
            'bold': True
        })
        
        formats['income_text'] = workbook.add_format({
            'bg_color': '#E2EFDA',  # Light green background
            'font_color': '#0D5016',  # Dark green text
            'border': 1,
            'text_wrap': True
        })
        
        formats['income_category'] = workbook.add_format({
            'bg_color': '#70AD47',  # Green background
            'font_color': 'white',
            'border': 1,
            'bold': True,
            'align': 'center'
        })
        
        # Expense formats (Red theme)
        formats['expense_amount'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#FCE4D6',  # Light red background
            'font_color': '#C5504B',  # Dark red text
            'border': 1,
            'bold': True
        })
        
        formats['expense_text'] = workbook.add_format({
            'bg_color': '#FCE4D6',  # Light red background
            'font_color': '#C5504B',  # Dark red text
            'border': 1,
            'text_wrap': True
        })
        
        formats['expense_category'] = workbook.add_format({
            'bg_color': '#C5504B',  # Red background
            'font_color': 'white',
            'border': 1,
            'bold': True,
            'align': 'center'
        })
        
        # Neutral formats
        formats['neutral_amount'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1
        })
        
        formats['neutral_text'] = workbook.add_format({
            'border': 1,
            'text_wrap': True
        })
        
        # Special summary formats
        formats['total_income'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#70AD47',
            'font_color': 'white',
            'border': 1,
            'bold': True
        })
        
        formats['total_expense'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#C5504B',
            'font_color': 'white',
            'border': 1,
            'bold': True
        })
        
        formats['net_positive'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#70AD47',
            'font_color': 'white',
            'border': 1,
            'bold': True
        })
        
        formats['net_negative'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#C5504B',
            'font_color': 'white',
            'border': 1,
            'bold': True
        })
        
        return formats
    
    def _format_sheet_name(self, month_year: str) -> str:
        """Format month-year for sheet name."""
        if month_year == 'Unknown':
            return 'Unknown Dates'
        
        try:
            year, month = month_year.split('-')
            month_names = [
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
            ]
            month_name = month_names[int(month) - 1]
            return f"{month_name} {year}"
        except:
            return month_year
    
    def _create_summary_sheet(self, workbook, monthly_data, formats):
        """Create summary sheet with overall statistics and color coding."""
        worksheet = workbook.add_worksheet('Summary')
        
        # Title
        worksheet.write(0, 0, 'Bank Statement Analysis Summary', formats['header'])
        worksheet.merge_range(0, 0, 0, 5, 'Bank Statement Analysis Summary', formats['header'])
        
        row = 2
        
        # Overall statistics with income/expense analysis
        all_transactions = [t for transactions in monthly_data.values() for t in transactions]
        summary_stats = self.income_expense_analyzer.get_income_expense_summary(all_transactions)
        
        # Write overall summary
        worksheet.write(row, 0, 'Overall Financial Summary', formats['summary_header'])
        worksheet.merge_range(row, 0, row, 1, 'Overall Financial Summary', formats['summary_header'])
        row += 1
        
        # Financial summary data with color coding
        financial_data = [
            ('Total Transactions', len(all_transactions), 'neutral_text', 'neutral_text'),
            ('Total Income', summary_stats['total_income'], 'neutral_text', 'total_income'),
            ('Total Expenses', summary_stats['total_expenses'], 'neutral_text', 'total_expense'),
            ('Net Amount', summary_stats['net_amount'], 'neutral_text', 
             'net_positive' if summary_stats['net_amount'] >= 0 else 'net_negative'),
            ('Income Transactions', summary_stats['income_count'], 'neutral_text', 'income_text'),
            ('Expense Transactions', summary_stats['expense_count'], 'neutral_text', 'expense_text'),
            ('Average Income', summary_stats['income_avg'], 'neutral_text', 'income_amount'),
            ('Average Expense', summary_stats['expense_avg'], 'neutral_text', 'expense_amount')
        ]
        
        for label, value, label_format, value_format in financial_data:
            worksheet.write(row, 0, label, formats[label_format])
            if isinstance(value, (int, float)) and any(word in label for word in ['Amount', 'Income', 'Expense']):
                worksheet.write(row, 1, value, formats[value_format])
            else:
                worksheet.write(row, 1, value, formats[value_format])
            row += 1
        
        row += 2
        
        # Monthly breakdown with color coding
        worksheet.write(row, 0, 'Monthly Income & Expense Breakdown', formats['summary_header'])
        worksheet.merge_range(row, 0, row, 5, 'Monthly Income & Expense Breakdown', formats['summary_header'])
        row += 1
        
        # Headers
        headers = ['Month', 'Transactions', 'Income', 'Expenses', 'Net Amount', 'Classification']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, formats['header'])
        row += 1
        
        # Monthly data with color coding
        sorted_months = sorted([k for k in monthly_data.keys() if k != 'Unknown'])
        if 'Unknown' in monthly_data:
            sorted_months.append('Unknown')
        
        for month_year in sorted_months:
            month_transactions = monthly_data[month_year]
            month_stats = self.income_expense_analyzer.get_income_expense_summary(month_transactions)
            
            display_name = self._format_sheet_name(month_year)
            net_amount = month_stats['net_amount']
            
            # Determine row coloring based on net amount
            if net_amount > 0:
                classification = "Positive"
                net_format = formats['net_positive']
                row_theme = 'income'
            else:
                classification = "Negative" 
                net_format = formats['net_negative']
                row_theme = 'expense'
            
            worksheet.write(row, 0, display_name, formats['neutral_text'])
            worksheet.write(row, 1, len(month_transactions), formats['neutral_text'])
            worksheet.write(row, 2, month_stats['total_income'], formats['income_amount'])
            worksheet.write(row, 3, month_stats['total_expenses'], formats['expense_amount'])
            worksheet.write(row, 4, net_amount, net_format)
            worksheet.write(row, 5, classification, formats[f'{row_theme}_category'])
            row += 1
        
        # Auto-adjust column widths
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 5, 15)
        
        # Add legend
        row += 2
        worksheet.write(row, 0, 'Color Legend:', formats['header'])
        row += 1
        worksheet.write(row, 0, 'Income (Green)', formats['income_category'])
        worksheet.write(row, 1, 'Money coming in', formats['income_text'])
        row += 1
        worksheet.write(row, 0, 'Expense (Red)', formats['expense_category'])
        worksheet.write(row, 1, 'Money going out', formats['expense_text'])
    
    def _create_month_sheet(self, workbook, sheet_name, transactions, formats):
        """Create a sheet for a specific month with color coding."""
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Title
        worksheet.write(0, 0, f'{sheet_name} Analysis', formats['header'])
        worksheet.merge_range(0, 0, 0, 6, f'{sheet_name} Analysis', formats['header'])
        
        row = 2
        
        # Monthly summary with income/expense breakdown
        month_stats = self.income_expense_analyzer.get_income_expense_summary(transactions)
        
        worksheet.write(row, 0, 'Monthly Financial Summary', formats['summary_header'])
        worksheet.merge_range(row, 0, row, 1, 'Monthly Financial Summary', formats['summary_header'])
        row += 1
        
        monthly_summary = [
            ('Total Transactions', len(transactions), 'neutral_text', 'neutral_text'),
            ('Income Transactions', month_stats['income_count'], 'neutral_text', 'income_text'),
            ('Expense Transactions', month_stats['expense_count'], 'neutral_text', 'expense_text'),
            ('Total Income', month_stats['total_income'], 'neutral_text', 'total_income'),
            ('Total Expenses', month_stats['total_expenses'], 'neutral_text', 'total_expense'),
            ('Net Amount', month_stats['net_amount'], 'neutral_text', 
             'net_positive' if month_stats['net_amount'] >= 0 else 'net_negative'),
        ]
        
        for label, value, label_format, value_format in monthly_summary:
            worksheet.write(row, 0, label, formats[label_format])
            if isinstance(value, (int, float)) and any(word in label for word in ['Amount', 'Income', 'Expense']):
                worksheet.write(row, 1, value, formats[value_format])
            else:
                worksheet.write(row, 1, value, formats[value_format])
            row += 1
        
        row += 2
        
        # Detailed transactions with color coding
        worksheet.write(row, 0, 'Detailed Transactions (Color Coded)', formats['summary_header'])
        worksheet.merge_range(row, 0, row, 6, 'Detailed Transactions (Color Coded)', formats['summary_header'])
        row += 1
        
        # Transaction headers
        trans_headers = ['Date', 'Description', 'Category', 'Amount', 'Type', 'Confidence', 'Source File']
        for col, header in enumerate(trans_headers):
            worksheet.write(row, col, header, formats['header'])
        row += 1
        
        # Transaction data with color coding
        # Sort by type first (income first), then by amount
        sorted_transactions = sorted(transactions, 
            key=lambda x: (x.get('transaction_type', 'expense'), -abs(self._clean_amount(x.get('amount', 0)))))
        
        for transaction in sorted_transactions:
            transaction_type = transaction.get('transaction_type', 'expense')
            amount = self._clean_amount(transaction.get('amount', 0))
            confidence = transaction.get('type_confidence', 0.0)
            
            # Choose formats based on transaction type
            if transaction_type == 'income':
                text_format = formats['income_text']
                amount_format = formats['income_amount']
                category_format = formats['income_category']
            else:
                text_format = formats['expense_text']
                amount_format = formats['expense_amount']
                category_format = formats['expense_category']
            
            worksheet.write(row, 0, transaction.get('date', ''), text_format)
            worksheet.write(row, 1, transaction.get('description', ''), text_format)
            worksheet.write(row, 2, transaction.get('category', ''), text_format)
            worksheet.write(row, 3, amount, amount_format)
            worksheet.write(row, 4, transaction_type.title(), category_format)
            worksheet.write(row, 5, f"{confidence:.1%}", text_format)
            worksheet.write(row, 6, transaction.get('source_file', ''), text_format)
            row += 1
        
        # Auto-adjust column widths
        worksheet.set_column(0, 0, 12)  # Date
        worksheet.set_column(1, 1, 40)  # Description
        worksheet.set_column(2, 2, 15)  # Category
        worksheet.set_column(3, 3, 12)  # Amount
        worksheet.set_column(4, 4, 10)  # Type
        worksheet.set_column(5, 5, 12)  # Confidence
        worksheet.set_column(6, 6, 20)  # Source File
    
    def _clean_amount(self, amount_str) -> float:
        """Convert amount string to float."""
        try:
            if isinstance(amount_str, (int, float)):
                return float(amount_str)
            
            # Remove currency symbols and commas
            cleaned = str(amount_str).replace('$', '').replace(',', '').strip()
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            # Handle + prefix
            if cleaned.startswith('+'):
                cleaned = cleaned[1:]
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
