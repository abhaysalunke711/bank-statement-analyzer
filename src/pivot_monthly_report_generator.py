"""
Pivot-style Monthly Report Generator.
Creates a single Excel sheet with items as rows and months as columns,
separated into income and expense sections.
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

class PivotMonthlyReportGenerator:
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.income_expense_analyzer = IncomeExpenseAnalyzer()
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_pivot_excel_report(self, transactions: List[Dict], filename: str = None) -> str:
        """
        Create a pivot-style Excel file with items as rows and months as columns.
        
        Args:
            transactions: List of categorized transactions
            filename: Custom filename for the Excel file
            
        Returns:
            Path to created Excel file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pivot_bank_analysis_{timestamp}.xlsx"
        
        excel_path = os.path.join(self.output_dir, filename)
        
        try:
            # Classify transactions as income or expenses
            self.logger.info("Analyzing transactions for income/expense classification...")
            classified_transactions = self.income_expense_analyzer.classify_transactions(transactions)
            
            # Organize data for pivot layout
            pivot_data = self._organize_pivot_data(classified_transactions)
            
            if not pivot_data:
                self.logger.warning("No pivot data to process")
                return ""
            
            # Create Excel workbook
            workbook = xlsxwriter.Workbook(excel_path)
            
            # Define formats
            formats = self._create_pivot_formats(workbook)
            
            # Create the pivot sheet
            self._create_pivot_sheet(workbook, pivot_data, formats)
            
            workbook.close()
            
            self.logger.info(f"Pivot Excel report created: {excel_path}")
            
            return excel_path
            
        except Exception as e:
            self.logger.error(f"Error creating pivot Excel report: {e}")
            return ""
    
    def _organize_pivot_data(self, transactions: List[Dict]) -> Dict:
        """
        Organize transactions into pivot structure: items vs months.
        
        Args:
            transactions: List of classified transactions
            
        Returns:
            Dictionary with organized pivot data
        """
        # Separate income and expense transactions
        income_transactions = [t for t in transactions if t.get('transaction_type') == 'income']
        expense_transactions = [t for t in transactions if t.get('transaction_type') == 'expense']
        
        # Get all unique months
        all_months = set()
        for transaction in transactions:
            month_year = self._extract_month_year(transaction.get('date', ''))
            if month_year:
                all_months.add(month_year)
        
        sorted_months = sorted(list(all_months))
        
        # Organize income data by category and month
        income_data = self._organize_by_category_and_month(income_transactions, sorted_months)
        
        # Organize expense data by category and month
        expense_data = self._organize_by_category_and_month(expense_transactions, sorted_months)
        
        return {
            'months': sorted_months,
            'income_data': income_data,
            'expense_data': expense_data,
            'total_transactions': len(transactions),
            'income_count': len(income_transactions),
            'expense_count': len(expense_transactions)
        }
    
    def _organize_by_category_and_month(self, transactions: List[Dict], months: List[str]) -> Dict:
        """
        Organize transactions by category and month.
        
        Args:
            transactions: List of transactions (income or expense)
            months: List of sorted month strings
            
        Returns:
            Dictionary with category -> month -> amount mapping
        """
        category_month_data = defaultdict(lambda: defaultdict(float))
        
        for transaction in transactions:
            category = transaction.get('category', 'Uncategorized')
            month_year = self._extract_month_year(transaction.get('date', ''))
            amount = abs(self._clean_amount(transaction.get('amount', 0)))  # Use absolute values
            
            if month_year:
                category_month_data[category][month_year] += round(amount, 2)
        
        # Convert to regular dict and ensure all months are present
        result = {}
        for category in category_month_data:
            result[category] = {}
            total = 0
            for month in months:
                amount = category_month_data[category].get(month, 0)
                result[category][month] = round(amount, 2)
                total += amount
            result[category]['total'] = round(total, 2)
        
        return result
    
    def _extract_month_year(self, date_str: str) -> str:
        """Extract month-year from date string."""
        if not date_str:
            return None
        
        try:
            # Handle Chase format MM/DD (assume current year)
            if re.match(r'^\d{1,2}/\d{1,2}$', date_str):
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
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not parse date '{date_str}': {e}")
            return None
    
    def _create_pivot_formats(self, workbook) -> Dict:
        """Create all formatting styles for pivot layout."""
        formats = {}
        
        # Title format
        formats['title'] = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Section headers
        formats['income_header'] = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#70AD47',  # Green
            'font_color': 'white',
            'align': 'center',
            'border': 1
        })
        
        formats['expense_header'] = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#C5504B',  # Red
            'font_color': 'white',
            'align': 'center',
            'border': 1
        })
        
        # Column headers
        formats['column_header'] = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'font_color': '#1F4E79',
            'align': 'center',
            'border': 1,
            'text_wrap': True
        })
        
        # Category labels
        formats['income_category'] = workbook.add_format({
            'bold': True,
            'bg_color': '#E2EFDA',  # Light green
            'font_color': '#0D5016',  # Dark green
            'border': 1,
            'align': 'left'
        })
        
        formats['expense_category'] = workbook.add_format({
            'bold': True,
            'bg_color': '#FCE4D6',  # Light red
            'font_color': '#C5504B',  # Dark red
            'border': 1,
            'align': 'left'
        })
        
        # Amount formats
        formats['income_amount'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#E2EFDA',  # Light green
            'font_color': '#0D5016',  # Dark green
            'border': 1,
            'align': 'right'
        })
        
        formats['expense_amount'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#FCE4D6',  # Light red
            'font_color': '#C5504B',  # Dark red
            'border': 1,
            'align': 'right'
        })
        
        # Total formats
        formats['income_total'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#70AD47',  # Green
            'font_color': 'white',
            'border': 1,
            'bold': True,
            'align': 'right'
        })
        
        formats['expense_total'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#C5504B',  # Red
            'font_color': 'white',
            'border': 1,
            'bold': True,
            'align': 'right'
        })
        
        # Summary formats
        formats['summary_label'] = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'left'
        })
        
        formats['summary_amount'] = workbook.add_format({
            'num_format': '$#,##0.00',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'bold': True,
            'align': 'right'
        })
        
        return formats
    
    def _create_pivot_sheet(self, workbook, pivot_data: Dict, formats: Dict):
        """Create the main pivot sheet."""
        worksheet = workbook.add_worksheet('Financial Summary')
        
        months = pivot_data['months']
        income_data = pivot_data['income_data']
        expense_data = pivot_data['expense_data']
        
        # Calculate column positions
        num_months = len(months)
        total_cols = num_months + 2  # Category column + months + total column
        
        row = 0
        
        # Main title
        worksheet.merge_range(row, 0, row, total_cols - 1, 
                            'Bank Statement Financial Summary', formats['title'])
        row += 2
        
        # Create month headers
        month_headers = self._format_month_headers(months)
        
        # Column headers
        worksheet.write(row, 0, 'Category / Item', formats['column_header'])
        for col, month_header in enumerate(month_headers, 1):
            worksheet.write(row, col, month_header, formats['column_header'])
        worksheet.write(row, num_months + 1, 'Total', formats['column_header'])
        row += 1
        
        # INCOME SECTION
        worksheet.merge_range(row, 0, row, total_cols - 1, 
                            '💰 INCOME', formats['income_header'])
        row += 1
        
        # Income categories and data
        income_total_by_month = [0] * num_months
        income_grand_total = 0
        
        for category in sorted(income_data.keys()):
            category_data = income_data[category]
            
            # Category name
            worksheet.write(row, 0, category, formats['income_category'])
            
            # Monthly amounts
            for col, month in enumerate(months, 1):
                amount = category_data.get(month, 0)
                if amount > 0:
                    worksheet.write(row, col, round(amount, 2), formats['income_amount'])
                    income_total_by_month[col - 1] += amount
                else:
                    worksheet.write(row, col, '', formats['income_amount'])
            
            # Category total
            category_total = category_data.get('total', 0)
            worksheet.write(row, num_months + 1, round(category_total, 2), formats['income_total'])
            income_grand_total += category_total
            
            row += 1
        
        # Income totals row
        worksheet.write(row, 0, 'TOTAL INCOME', formats['income_total'])
        for col, monthly_total in enumerate(income_total_by_month, 1):
            worksheet.write(row, col, round(monthly_total, 2), formats['income_total'])
        worksheet.write(row, num_months + 1, round(income_grand_total, 2), formats['income_total'])
        row += 1
        
        # 4 empty rows separator
        for _ in range(4):
            row += 1
        
        # EXPENSE SECTION
        worksheet.merge_range(row, 0, row, total_cols - 1, 
                            '💸 EXPENSES', formats['expense_header'])
        row += 1
        
        # Expense categories and data
        expense_total_by_month = [0] * num_months
        expense_grand_total = 0
        
        for category in sorted(expense_data.keys()):
            category_data = expense_data[category]
            
            # Category name
            worksheet.write(row, 0, category, formats['expense_category'])
            
            # Monthly amounts
            for col, month in enumerate(months, 1):
                amount = category_data.get(month, 0)
                if amount > 0:
                    worksheet.write(row, col, round(amount, 2), formats['expense_amount'])
                    expense_total_by_month[col - 1] += amount
                else:
                    worksheet.write(row, col, '', formats['expense_amount'])
            
            # Category total
            category_total = category_data.get('total', 0)
            worksheet.write(row, num_months + 1, round(category_total, 2), formats['expense_total'])
            expense_grand_total += category_total
            
            row += 1
        
        # Expense totals row
        worksheet.write(row, 0, 'TOTAL EXPENSES', formats['expense_total'])
        for col, monthly_total in enumerate(expense_total_by_month, 1):
            worksheet.write(row, col, round(monthly_total, 2), formats['expense_total'])
        worksheet.write(row, num_months + 1, round(expense_grand_total, 2), formats['expense_total'])
        row += 2
        
        # NET AMOUNT SUMMARY
        worksheet.write(row, 0, 'NET AMOUNT', formats['summary_label'])
        for col in range(1, num_months + 1):
            net_amount = income_total_by_month[col - 1] - expense_total_by_month[col - 1]
            worksheet.write(row, col, round(net_amount, 2), formats['summary_amount'])
        
        net_total = income_grand_total - expense_grand_total
        worksheet.write(row, num_months + 1, round(net_total, 2), formats['summary_amount'])
        
        # Auto-adjust column widths
        worksheet.set_column(0, 0, 25)  # Category column
        for col in range(1, num_months + 1):  # Month columns
            worksheet.set_column(col, col, 12)
        worksheet.set_column(num_months + 1, num_months + 1, 15)  # Total column
        
        # Add summary statistics at the bottom
        row += 3
        stats_data = [
            ('Total Income Categories', len(income_data)),
            ('Total Expense Categories', len(expense_data)),
            ('Total Transactions Processed', pivot_data['total_transactions']),
            ('Analysis Period', f"{len(months)} months")
        ]
        
        for label, value in stats_data:
            worksheet.write(row, 0, label, formats['column_header'])
            worksheet.write(row, 1, value, formats['column_header'])
            row += 1
    
    def _format_month_headers(self, months: List[str]) -> List[str]:
        """Format month-year strings for column headers."""
        formatted_headers = []
        
        for month_year in months:
            try:
                year, month = month_year.split('-')
                month_names = [
                    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                ]
                month_name = month_names[int(month) - 1]
                formatted_headers.append(f"{month_name} {year}")
            except:
                formatted_headers.append(month_year)
        
        return formatted_headers
    
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
