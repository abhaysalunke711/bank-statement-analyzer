"""
Monthly report generator for creating Excel files with separate tabs for each month.
Organizes bank statement analysis by month with comprehensive summaries.
"""

import os
import logging
import pandas as pd
import xlsxwriter
from datetime import datetime
from typing import List, Dict, Tuple
import re
from collections import defaultdict

class MonthlyReportGenerator:
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
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
        Create an Excel file with separate tabs for each month.
        
        Args:
            transactions: List of categorized transactions
            filename: Custom filename for the Excel file
            
        Returns:
            Path to created Excel file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monthly_bank_analysis_{timestamp}.xlsx"
        
        excel_path = os.path.join(self.output_dir, filename)
        
        try:
            # Organize transactions by month
            monthly_data = self.organize_transactions_by_month(transactions)
            
            if not monthly_data:
                self.logger.warning("No monthly data to process")
                return ""
            
            # Create Excel workbook
            workbook = xlsxwriter.Workbook(excel_path)
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })
            
            currency_format = workbook.add_format({
                'num_format': '$#,##0.00',
                'border': 1
            })
            
            text_format = workbook.add_format({
                'border': 1,
                'text_wrap': True
            })
            
            summary_header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#70AD47',
                'font_color': 'white',
                'border': 1
            })
            
            # Create summary sheet first
            self._create_summary_sheet(workbook, monthly_data, header_format, currency_format, text_format)
            
            # Create a sheet for each month
            sorted_months = sorted(monthly_data.keys(), key=lambda x: x if x != 'Unknown' else 'ZZZZ')
            
            for month_year in sorted_months:
                month_transactions = monthly_data[month_year]
                sheet_name = self._format_sheet_name(month_year)
                
                self._create_month_sheet(
                    workbook, sheet_name, month_transactions, 
                    header_format, currency_format, text_format, summary_header_format
                )
            
            workbook.close()
            
            self.logger.info(f"Monthly Excel report created: {excel_path}")
            self.logger.info(f"Created {len(monthly_data)} monthly tabs")
            
            return excel_path
            
        except Exception as e:
            self.logger.error(f"Error creating monthly Excel report: {e}")
            return ""
    
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
    
    def _create_summary_sheet(self, workbook, monthly_data, header_format, currency_format, text_format):
        """Create summary sheet with overall statistics."""
        worksheet = workbook.add_worksheet('Summary')
        
        # Title
        worksheet.write(0, 0, 'Bank Statement Analysis Summary', header_format)
        worksheet.merge_range(0, 0, 0, 5, 'Bank Statement Analysis Summary', header_format)
        
        row = 2
        
        # Overall statistics
        total_transactions = sum(len(transactions) for transactions in monthly_data.values())
        all_transactions = [t for transactions in monthly_data.values() for t in transactions]
        
        total_income = sum(self._clean_amount(t.get('amount', 0)) for t in all_transactions if self._clean_amount(t.get('amount', 0)) > 0)
        total_expenses = abs(sum(self._clean_amount(t.get('amount', 0)) for t in all_transactions if self._clean_amount(t.get('amount', 0)) < 0))
        net_amount = total_income - total_expenses
        
        # Write overall summary
        worksheet.write(row, 0, 'Overall Summary', header_format)
        worksheet.merge_range(row, 0, row, 1, 'Overall Summary', header_format)
        row += 1
        
        summary_data = [
            ['Total Transactions', total_transactions],
            ['Total Income', total_income],
            ['Total Expenses', total_expenses],
            ['Net Amount', net_amount],
            ['Number of Months', len([k for k in monthly_data.keys() if k != 'Unknown'])]
        ]
        
        for label, value in summary_data:
            worksheet.write(row, 0, label, text_format)
            if isinstance(value, (int, float)) and 'Amount' in label or 'Income' in label or 'Expenses' in label:
                worksheet.write(row, 1, value, currency_format)
            else:
                worksheet.write(row, 1, value, text_format)
            row += 1
        
        row += 2
        
        # Monthly breakdown
        worksheet.write(row, 0, 'Monthly Breakdown', header_format)
        worksheet.merge_range(row, 0, row, 4, 'Monthly Breakdown', header_format)
        row += 1
        
        # Headers
        headers = ['Month', 'Transactions', 'Income', 'Expenses', 'Net Amount']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        row += 1
        
        # Monthly data
        sorted_months = sorted([k for k in monthly_data.keys() if k != 'Unknown'])
        if 'Unknown' in monthly_data:
            sorted_months.append('Unknown')
        
        for month_year in sorted_months:
            month_transactions = monthly_data[month_year]
            month_income = sum(self._clean_amount(t.get('amount', 0)) for t in month_transactions if self._clean_amount(t.get('amount', 0)) > 0)
            month_expenses = abs(sum(self._clean_amount(t.get('amount', 0)) for t in month_transactions if self._clean_amount(t.get('amount', 0)) < 0))
            month_net = month_income - month_expenses
            
            display_name = self._format_sheet_name(month_year)
            
            worksheet.write(row, 0, display_name, text_format)
            worksheet.write(row, 1, len(month_transactions), text_format)
            worksheet.write(row, 2, month_income, currency_format)
            worksheet.write(row, 3, month_expenses, currency_format)
            worksheet.write(row, 4, month_net, currency_format)
            row += 1
        
        # Auto-adjust column widths
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 4, 15)
    
    def _create_month_sheet(self, workbook, sheet_name, transactions, header_format, currency_format, text_format, summary_header_format):
        """Create a sheet for a specific month."""
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Title
        worksheet.write(0, 0, f'{sheet_name} Analysis', header_format)
        worksheet.merge_range(0, 0, 0, 5, f'{sheet_name} Analysis', header_format)
        
        row = 2
        
        # Monthly summary
        month_income = sum(self._clean_amount(t.get('amount', 0)) for t in transactions if self._clean_amount(t.get('amount', 0)) > 0)
        month_expenses = abs(sum(self._clean_amount(t.get('amount', 0)) for t in transactions if self._clean_amount(t.get('amount', 0)) < 0))
        month_net = month_income - month_expenses
        
        worksheet.write(row, 0, 'Monthly Summary', summary_header_format)
        worksheet.merge_range(row, 0, row, 1, 'Monthly Summary', summary_header_format)
        row += 1
        
        monthly_summary = [
            ['Total Transactions', len(transactions)],
            ['Total Income', month_income],
            ['Total Expenses', month_expenses],
            ['Net Amount', month_net]
        ]
        
        for label, value in monthly_summary:
            worksheet.write(row, 0, label, text_format)
            if isinstance(value, (int, float)) and 'Amount' in label or 'Income' in label or 'Expenses' in label:
                worksheet.write(row, 1, value, currency_format)
            else:
                worksheet.write(row, 1, value, text_format)
            row += 1
        
        row += 2
        
        # Category breakdown
        category_summary = self._analyze_categories(transactions)
        
        worksheet.write(row, 0, 'Category Breakdown', summary_header_format)
        worksheet.merge_range(row, 0, row, 3, 'Category Breakdown', summary_header_format)
        row += 1
        
        # Category headers
        cat_headers = ['Category', 'Transactions', 'Total Amount', 'Avg Amount']
        for col, header in enumerate(cat_headers):
            worksheet.write(row, col, header, header_format)
        row += 1
        
        # Category data
        for category, stats in sorted(category_summary.items()):
            worksheet.write(row, 0, category, text_format)
            worksheet.write(row, 1, stats['count'], text_format)
            worksheet.write(row, 2, stats['total'], currency_format)
            worksheet.write(row, 3, stats['average'], currency_format)
            row += 1
        
        row += 2
        
        # Detailed transactions
        worksheet.write(row, 0, 'Detailed Transactions', summary_header_format)
        worksheet.merge_range(row, 0, row, 4, 'Detailed Transactions', summary_header_format)
        row += 1
        
        # Transaction headers
        trans_headers = ['Date', 'Description', 'Category', 'Amount', 'Source File']
        for col, header in enumerate(trans_headers):
            worksheet.write(row, col, header, header_format)
        row += 1
        
        # Transaction data
        sorted_transactions = sorted(transactions, key=lambda x: (x.get('category', ''), self._clean_amount(x.get('amount', 0))))
        
        for transaction in sorted_transactions:
            worksheet.write(row, 0, transaction.get('date', ''), text_format)
            worksheet.write(row, 1, transaction.get('description', ''), text_format)
            worksheet.write(row, 2, transaction.get('category', ''), text_format)
            worksheet.write(row, 3, self._clean_amount(transaction.get('amount', 0)), currency_format)
            worksheet.write(row, 4, transaction.get('source_file', ''), text_format)
            row += 1
        
        # Auto-adjust column widths
        worksheet.set_column(0, 0, 12)  # Date
        worksheet.set_column(1, 1, 40)  # Description
        worksheet.set_column(2, 2, 15)  # Category
        worksheet.set_column(3, 3, 12)  # Amount
        worksheet.set_column(4, 4, 20)  # Source File
    
    def _analyze_categories(self, transactions: List[Dict]) -> Dict:
        """Analyze transactions by category for a specific month."""
        category_stats = defaultdict(lambda: {'count': 0, 'total': 0.0, 'average': 0.0})
        
        for transaction in transactions:
            category = transaction.get('category', 'Uncategorized')
            amount = self._clean_amount(transaction.get('amount', 0))
            
            category_stats[category]['count'] += 1
            category_stats[category]['total'] += amount
        
        # Calculate averages
        for category in category_stats:
            count = category_stats[category]['count']
            total = category_stats[category]['total']
            category_stats[category]['average'] = total / count if count > 0 else 0.0
        
        return dict(category_stats)
    
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
