"""
Pivot Monthly Report Generator module for creating Excel reports with pivot-style summaries.
"""

import os
import logging
from typing import List, Dict
import pandas as pd
import xlsxwriter
from datetime import datetime

class PivotMonthlyReportGenerator:
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def get_chart_data(self, transactions: List[Dict]) -> Dict:
        """
        Get data for expense and income charts.
        
        Args:
            transactions: List of categorized transactions
            
        Returns:
            Dictionary with chart data for expenses and income
        """
        try:
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(transactions)
            
            # Clean amount column
            df['amount'] = pd.to_numeric(df['amount'].str.replace('$', '').str.replace(',', ''), errors='coerce')
            
            # Convert dates
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Separate expenses and income
            expenses_df = df[df['amount'] < 0].copy()
            income_df = df[df['amount'] > 0].copy()
            
            # Group by month and category
            expenses_by_month = expenses_df.groupby([
                pd.Grouper(key='date', freq='M'),
                'category'
            ])['amount'].sum().abs()  # Use abs() to make expenses positive
            
            income_by_month = income_df.groupby([
                pd.Grouper(key='date', freq='M'),
                'category'
            ])['amount'].sum()
            
            # Prepare data for charts
            chart_data = {
                'expenses': {
                    'months': [],
                    'categories': []
                },
                'income': {
                    'months': [],
                    'sources': []
                }
            }
            
            # Process expenses
            if not expenses_by_month.empty:
                months = sorted(expenses_by_month.index.get_level_values(0).unique())
                categories = sorted(expenses_by_month.index.get_level_values(1).unique())
                
                # Convert expenses data to chart format
                expenses_data = []
                for category in categories:
                    values = []
                    for month in months:
                        try:
                            amount = expenses_by_month.loc[(month, category)]
                            values.append(float(amount))
                        except KeyError:
                            values.append(0)
                    expenses_data.append({'name': category, 'values': values})
                
                chart_data['expenses'] = {
                    'months': [m.strftime('%Y-%m') for m in months],
                    'categories': expenses_data
                }
            
            # Process income
            if not income_by_month.empty:
                months = sorted(income_by_month.index.get_level_values(0).unique())
                categories = sorted(income_by_month.index.get_level_values(1).unique())
                
                # Convert income data to chart format
                income_data = []
                for category in categories:
                    values = []
                    for month in months:
                        try:
                            amount = income_by_month.loc[(month, category)]
                            values.append(float(amount))
                        except KeyError:
                            values.append(0)
                    income_data.append({'name': category, 'values': values})
                
                chart_data['income'] = {
                    'months': [m.strftime('%Y-%m') for m in months],
                    'sources': income_data
                }
            
            return chart_data
            
        except Exception as e:
            self.logger.error(f"Error generating chart data: {e}")
            return {'expenses': {'months': [], 'categories': []}, 'income': {'months': [], 'sources': []}}
    
    def create_pivot_excel_report(self, transactions: List[Dict], grouped_transactions: Dict[str, List[Dict]] = None, receipt_data: List[Dict] = None) -> str:
        """
        Create an Excel report with pivot-style summaries and grouped transactions.
        
        Args:
            transactions: List of categorized transactions
            grouped_transactions: Dictionary of grouped transactions by section
            
        Returns:
            Path to created Excel file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bank_statement_analysis_{timestamp}.xlsx"
        excel_path = os.path.join(self.output_dir, filename)
        
        try:
            # Create Excel writer
            writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
            workbook = writer.book
            
            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1
            })
            
            money_format = workbook.add_format({
                'num_format': '$#,##0.00',
                'border': 1
            })
            
            date_format = workbook.add_format({
                'num_format': 'mm/dd/yyyy',
                'border': 1
            })
            
            border_format = workbook.add_format({
                'border': 1
            })
            
            # Create transactions DataFrame
            df = pd.DataFrame(transactions)
            
            # Clean amount column
            df['amount'] = pd.to_numeric(df['amount'].str.replace('$', '').str.replace(',', ''), errors='coerce')
            
            # Convert dates
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Create monthly pivot
            pivot = pd.pivot_table(
                df,
                values='amount',
                index='category',
                columns=pd.Grouper(key='date', freq='M'),
                aggfunc='sum',
                fill_value=0
            )
            
            # Add total row and column
            pivot.loc['Total'] = pivot.sum()
            pivot['Total'] = pivot.sum(axis=1)
            
            # Write pivot table to Excel
            pivot.to_excel(writer, sheet_name='Monthly Summary')
            worksheet = writer.sheets['Monthly Summary']
            
            # Format pivot table
            for col in range(len(pivot.columns) + 1):
                for row in range(len(pivot.index) + 1):
                    worksheet.write(row, col, None, money_format)
            
            # Write transactions to detail sheet
            df.to_excel(writer, sheet_name='Transaction Details', index=False)
            detail_sheet = writer.sheets['Transaction Details']
            
            # Format transaction details
            for col_num, value in enumerate(df.columns.values):
                detail_sheet.write(0, col_num, value, header_format)
                if value == 'amount':
                    detail_sheet.set_column(col_num, col_num, 12, money_format)
                elif value == 'date':
                    detail_sheet.set_column(col_num, col_num, 12, date_format)
                else:
                    detail_sheet.set_column(col_num, col_num, 20, border_format)
            
            # Add grouped transactions sheets if available
            if grouped_transactions:
                for section, groups in grouped_transactions.items():
                    sheet_name = section.title()[:31]  # Excel sheet names limited to 31 chars
                    
                    # Create DataFrame for the section
                    section_data = []
                    for group in groups:
                        section_data.append({
                            'Description': group['description'],
                            'Count': group['count'],
                            'Total Amount': float(group['total_amount'].replace('$', '').replace(',', '')),
                            'Average Amount': float(group['total_amount'].replace('$', '').replace(',', '')) / group['count']
                        })
                    
                    if section_data:
                        df_section = pd.DataFrame(section_data)
                        df_section.to_excel(writer, sheet_name=sheet_name, index=False)
                        section_sheet = writer.sheets[sheet_name]
                        
                        # Format section sheet
                        for col_num, value in enumerate(df_section.columns.values):
                            section_sheet.write(0, col_num, value, header_format)
                            if 'Amount' in value:
                                section_sheet.set_column(col_num, col_num, 15, money_format)
                            elif value == 'Count':
                                section_sheet.set_column(col_num, col_num, 8, border_format)
                            else:
                                section_sheet.set_column(col_num, col_num, 40, border_format)
                        
                        # Add transaction details below the summary
                        row_offset = len(section_data) + 3
                        section_sheet.write(row_offset, 0, "Transaction Details", header_format)
                        
                        # Write headers for transaction details
                        headers = ['Date', 'Description', 'Amount']
                        for col, header in enumerate(headers):
                            section_sheet.write(row_offset + 1, col, header, header_format)
                        
                        # Write transaction details
                        current_row = row_offset + 2
                        for group in groups:
                            for transaction in group['transactions']:
                                date = pd.to_datetime(transaction['date'])
                                section_sheet.write(current_row, 0, date, date_format)
                                section_sheet.write(current_row, 1, transaction['description'], border_format)
                                amount = float(transaction['amount'].replace('$', '').replace(',', ''))
                                section_sheet.write(current_row, 2, amount, money_format)
                                current_row += 1
            
            # Add receipt data if available
            if receipt_data:
                # Create receipts sheet
                sheet_name = 'Receipts'
                receipt_rows = []
                
                # Prepare data for DataFrame
                for receipt in receipt_data:
                    # Add receipt header
                    receipt_rows.append({
                        'Date': receipt['date'],
                        'Store': receipt['store_name'],
                        'Type': 'Header',
                        'Description': 'Receipt Total',
                        'Amount': float(receipt['totals']['total'])
                    })
                    
                    # Add receipt items
                    for item in receipt['items']:
                        receipt_rows.append({
                            'Date': receipt['date'],
                            'Store': receipt['store_name'],
                            'Type': 'Item',
                            'Description': item['name'],
                            'Amount': float(item['amount']),
                            'Quantity': float(item['quantity']),
                            'Category': item.get('category', 'Uncategorized')
                        })
                
                if receipt_rows:
                    df_receipts = pd.DataFrame(receipt_rows)
                    df_receipts.to_excel(writer, sheet_name=sheet_name, index=False)
                    receipt_sheet = writer.sheets[sheet_name]
                    
                    # Format receipt sheet
                    for col_num, value in enumerate(df_receipts.columns.values):
                        receipt_sheet.write(0, col_num, value, header_format)
                        if value in ['Amount']:
                            receipt_sheet.set_column(col_num, col_num, 12, money_format)
                        elif value == 'Date':
                            receipt_sheet.set_column(col_num, col_num, 12, date_format)
                        else:
                            receipt_sheet.set_column(col_num, col_num, 20, border_format)
                    
                    # Add conditional formatting for header rows
                    header_format_cond = workbook.add_format({
                        'bold': True,
                        'bg_color': '#E6F3FF',
                        'border': 1
                    })
                    
                    # Apply conditional formatting based on 'Type' column (column C)
                    receipt_sheet.conditional_format(1, 0, len(df_receipts), len(df_receipts.columns)-1, {
                        'type': 'formula',
                        'criteria': '$C2="Header"',
                        'format': header_format_cond
                    })
            
            # Save the workbook
            writer.close()
            
            self.logger.info(f"Excel report created: {excel_path}")
            return excel_path
            
        except Exception as e:
            self.logger.error(f"Error creating Excel report: {e}")
            return ""