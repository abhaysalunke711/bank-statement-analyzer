"""
Report generator module for creating summaries and visualizations.
Handles category-wise analysis, charts, and enhanced CSV exports.
"""

import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import List, Dict, Tuple
import numpy as np

class ReportGenerator:
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def analyze_transactions(self, transactions: List[Dict]) -> Dict:
        """
        Analyze transactions and create comprehensive summary.
        
        Args:
            transactions: List of categorized transactions
            
        Returns:
            Dictionary with analysis results
        """
        if not transactions:
            return {}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(transactions)
        
        # Clean and convert amounts
        df['amount_numeric'] = df['amount'].apply(self._clean_amount)
        
        # Separate income and expenses
        df['transaction_type'] = df['amount_numeric'].apply(
            lambda x: 'Income' if x > 0 else 'Expense'
        )
        
        # Category analysis
        category_summary = self._analyze_by_category(df)
        
        # Time analysis (if dates are available)
        time_summary = self._analyze_by_time(df)
        
        # Overall summary
        overall_summary = self._calculate_overall_summary(df)
        
        analysis = {
            'overall': overall_summary,
            'by_category': category_summary,
            'by_time': time_summary,
            'transactions_df': df
        }
        
        return analysis
    
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
            self.logger.warning(f"Could not parse amount: {amount_str}")
            return 0.0
    
    def _analyze_by_category(self, df: pd.DataFrame) -> Dict:
        """Analyze transactions by category."""
        category_stats = {}
        
        for category in df['category'].unique():
            cat_data = df[df['category'] == category]
            
            expenses = cat_data[cat_data['amount_numeric'] < 0]['amount_numeric'].sum()
            income = cat_data[cat_data['amount_numeric'] > 0]['amount_numeric'].sum()
            net = cat_data['amount_numeric'].sum()
            count = len(cat_data)
            
            category_stats[category] = {
                'total_expenses': abs(expenses),
                'total_income': income,
                'net_amount': net,
                'transaction_count': count,
                'avg_transaction': net / count if count > 0 else 0
            }
        
        return category_stats
    
    def _analyze_by_time(self, df: pd.DataFrame) -> Dict:
        """Analyze transactions by time period."""
        if 'date' not in df.columns:
            return {}
        
        try:
            # Try to parse dates
            df['parsed_date'] = pd.to_datetime(df['date'], errors='coerce')
            
            if df['parsed_date'].isna().all():
                return {}
            
            # Group by month
            df['month_year'] = df['parsed_date'].dt.to_period('M')
            monthly_summary = df.groupby('month_year').agg({
                'amount_numeric': ['sum', 'count'],
                'category': lambda x: x.value_counts().to_dict()
            }).to_dict()
            
            return {'monthly': monthly_summary}
            
        except Exception as e:
            self.logger.warning(f"Could not analyze by time: {e}")
            return {}
    
    def _calculate_overall_summary(self, df: pd.DataFrame) -> Dict:
        """Calculate overall financial summary."""
        total_income = df[df['amount_numeric'] > 0]['amount_numeric'].sum()
        total_expenses = abs(df[df['amount_numeric'] < 0]['amount_numeric'].sum())
        net_amount = total_income - total_expenses
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_amount': net_amount,
            'total_transactions': len(df),
            'expense_categories': len(df[df['amount_numeric'] < 0]['category'].unique()),
            'income_categories': len(df[df['amount_numeric'] > 0]['category'].unique())
        }
    
    def create_category_summary_csv(self, analysis: Dict, filename: str = None) -> str:
        """
        Create a CSV file with category-wise summary.
        
        Args:
            analysis: Analysis results from analyze_transactions
            filename: Custom filename for the CSV
            
        Returns:
            Path to created CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"category_summary_{timestamp}.csv"
        
        csv_path = os.path.join(self.output_dir, filename)
        
        try:
            # Create category summary DataFrame
            category_data = []
            for category, stats in analysis['by_category'].items():
                category_data.append({
                    'Category': category,
                    'Total Expenses': f"${stats['total_expenses']:.2f}",
                    'Total Income': f"${stats['total_income']:.2f}",
                    'Net Amount': f"${stats['net_amount']:.2f}",
                    'Transaction Count': stats['transaction_count'],
                    'Average per Transaction': f"${stats['avg_transaction']:.2f}"
                })
            
            df_summary = pd.DataFrame(category_data)
            
            # Sort by total expenses (descending)
            df_summary['sort_expenses'] = df_summary['Total Expenses'].str.replace('$', '').str.replace(',', '').astype(float)
            df_summary = df_summary.sort_values('sort_expenses', ascending=False)
            df_summary = df_summary.drop('sort_expenses', axis=1)
            
            # Add overall summary at the top
            overall = analysis['overall']
            summary_rows = [
                ['=== OVERALL SUMMARY ===', '', '', '', '', ''],
                ['Total Income', f"${overall['total_income']:.2f}", '', '', '', ''],
                ['Total Expenses', f"${overall['total_expenses']:.2f}", '', '', '', ''],
                ['Net Amount', f"${overall['net_amount']:.2f}", '', '', '', ''],
                ['Total Transactions', str(overall['total_transactions']), '', '', '', ''],
                ['', '', '', '', '', ''],
                ['=== CATEGORY BREAKDOWN ===', '', '', '', '', '']
            ]
            
            # Write to CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                # Write summary rows
                for row in summary_rows:
                    f.write(','.join(row) + '\n')
                
                # Write category data
                df_summary.to_csv(f, index=False)
            
            self.logger.info(f"Category summary CSV created: {csv_path}")
            return csv_path
            
        except Exception as e:
            self.logger.error(f"Error creating category summary CSV: {e}")
            return ""
    
    def create_expense_bar_chart(self, analysis: Dict, filename: str = None) -> str:
        """
        Create a bar chart of expense categories.
        
        Args:
            analysis: Analysis results from analyze_transactions
            filename: Custom filename for the chart
            
        Returns:
            Path to created chart file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expense_categories_chart_{timestamp}.png"
        
        chart_path = os.path.join(self.output_dir, filename)
        
        try:
            # Prepare data for chart
            categories = []
            expenses = []
            
            for category, stats in analysis['by_category'].items():
                if stats['total_expenses'] > 0:  # Only include categories with expenses
                    categories.append(category)
                    expenses.append(stats['total_expenses'])
            
            if not categories:
                self.logger.warning("No expense categories found for chart")
                return ""
            
            # Sort by expense amount
            sorted_data = sorted(zip(categories, expenses), key=lambda x: x[1], reverse=True)
            categories, expenses = zip(*sorted_data)
            
            # Create the chart
            plt.figure(figsize=(12, 8))
            bars = plt.bar(range(len(categories)), expenses, color=sns.color_palette("husl", len(categories)))
            
            # Customize the chart
            plt.title('Expenses by Category', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Categories', fontsize=12, fontweight='bold')
            plt.ylabel('Amount ($)', fontsize=12, fontweight='bold')
            
            # Set x-axis labels
            plt.xticks(range(len(categories)), categories, rotation=45, ha='right')
            
            # Add value labels on bars
            for i, (bar, expense) in enumerate(zip(bars, expenses)):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + max(expenses) * 0.01,
                        f'${expense:.2f}', ha='center', va='bottom', fontweight='bold')
            
            # Format y-axis
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add grid for better readability
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save the chart
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Expense bar chart created: {chart_path}")
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Error creating bar chart: {e}")
            return ""
    
    def create_income_vs_expense_chart(self, analysis: Dict, filename: str = None) -> str:
        """
        Create a comparison chart of income vs expenses by category.
        
        Args:
            analysis: Analysis results from analyze_transactions
            filename: Custom filename for the chart
            
        Returns:
            Path to created chart file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"income_vs_expense_chart_{timestamp}.png"
        
        chart_path = os.path.join(self.output_dir, filename)
        
        try:
            # Prepare data
            categories = []
            expenses = []
            incomes = []
            
            for category, stats in analysis['by_category'].items():
                categories.append(category)
                expenses.append(stats['total_expenses'])
                incomes.append(stats['total_income'])
            
            # Create the chart
            x = np.arange(len(categories))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(14, 8))
            bars1 = ax.bar(x - width/2, expenses, width, label='Expenses', color='#ff6b6b', alpha=0.8)
            bars2 = ax.bar(x + width/2, incomes, width, label='Income', color='#4ecdc4', alpha=0.8)
            
            # Customize the chart
            ax.set_title('Income vs Expenses by Category', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Categories', fontsize=12, fontweight='bold')
            ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45, ha='right')
            ax.legend()
            
            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + max(max(expenses), max(incomes)) * 0.01,
                               f'${height:.2f}', ha='center', va='bottom', fontsize=9)
            
            # Format y-axis
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add grid
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Income vs expense chart created: {chart_path}")
            return chart_path
            
        except Exception as e:
            self.logger.error(f"Error creating income vs expense chart: {e}")
            return ""
    
    def create_comprehensive_report(self, analysis: Dict) -> Dict[str, str]:
        """
        Create a comprehensive report with all summaries and charts.
        
        Args:
            analysis: Analysis results from analyze_transactions
            
        Returns:
            Dictionary with paths to created files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_files = {}
        
        # Create category summary CSV
        csv_path = self.create_category_summary_csv(analysis, f"category_summary_{timestamp}.csv")
        if csv_path:
            report_files['category_summary_csv'] = csv_path
        
        # Create expense bar chart
        chart_path = self.create_expense_bar_chart(analysis, f"expense_chart_{timestamp}.png")
        if chart_path:
            report_files['expense_chart'] = chart_path
        
        # Create income vs expense chart
        comparison_chart = self.create_income_vs_expense_chart(analysis, f"income_vs_expense_{timestamp}.png")
        if comparison_chart:
            report_files['income_vs_expense_chart'] = comparison_chart
        
        # Create detailed transactions CSV (organized by category)
        detailed_csv = self._create_detailed_transactions_csv(analysis, f"detailed_transactions_{timestamp}.csv")
        if detailed_csv:
            report_files['detailed_transactions_csv'] = detailed_csv
        
        return report_files
    
    def _create_detailed_transactions_csv(self, analysis: Dict, filename: str) -> str:
        """Create a detailed transactions CSV organized by category."""
        csv_path = os.path.join(self.output_dir, filename)
        
        try:
            df = analysis['transactions_df']
            
            # Sort by category, then by amount (largest expenses first)
            df_sorted = df.sort_values(['category', 'amount_numeric']).copy()
            
            # Select and rename columns for output
            output_df = df_sorted[['date', 'description', 'category', 'amount', 'source_file']].copy()
            output_df.columns = ['Date', 'Description', 'Category', 'Amount', 'Source File']
            
            output_df.to_csv(csv_path, index=False)
            
            self.logger.info(f"Detailed transactions CSV created: {csv_path}")
            return csv_path
            
        except Exception as e:
            self.logger.error(f"Error creating detailed transactions CSV: {e}")
            return ""
