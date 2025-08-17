"""
Demonstration of the enhanced bank statement analyzer features.
Shows category summaries, visualizations, and organized reports.
"""

import sys
import os
sys.path.append('src')

from main import BankStatementAnalyzer
from report_generator import ReportGenerator
import pandas as pd

def demonstrate_enhanced_features():
    """Demonstrate all the new enhanced features."""
    print("🏦 Enhanced Bank Statement Analyzer Demo")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = BankStatementAnalyzer()
    
    # Run comprehensive analysis
    print("📊 Running comprehensive analysis...")
    results = analyzer.run_analysis(
        create_reports=True,
        export_csv=True
    )
    
    print(f"\n✅ Analysis Complete!")
    print(f"   📈 Processed: {results['total_transactions']} transactions")
    print(f"   🏷️  Categories: {results['categories_found']} categories")
    
    # Show financial summary
    if results['report_files']:
        print(f"\n💰 Financial Summary:")
        
        # Read the category summary to show key metrics
        category_csv = results['report_files'].get('category_summary_csv')
        if category_csv and os.path.exists(category_csv):
            try:
                # Read the summary section
                with open(category_csv, 'r') as f:
                    lines = f.readlines()
                
                # Extract key metrics
                for line in lines[1:5]:  # Lines with Total Income, Expenses, etc.
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            print(f"   {parts[0]}: {parts[1]}")
                
            except Exception as e:
                print(f"   Error reading summary: {e}")
        
        print(f"\n📁 Generated Files:")
        for report_type, file_path in results['report_files'].items():
            report_name = report_type.replace('_', ' ').title()
            print(f"   📄 {report_name}: {os.path.basename(file_path)}")
    
    return results

def show_category_breakdown():
    """Show detailed category breakdown."""
    print(f"\n📊 Category Breakdown:")
    print("=" * 40)
    
    # Find the latest category summary file
    output_files = [f for f in os.listdir('output') if f.startswith('category_summary_') and f.endswith('.csv')]
    if not output_files:
        print("No category summary file found.")
        return
    
    latest_file = sorted(output_files)[-1]
    file_path = os.path.join('output', latest_file)
    
    try:
        # Read and display the category breakdown
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find the category breakdown section
        start_idx = None
        for i, line in enumerate(lines):
            if 'CATEGORY BREAKDOWN' in line:
                start_idx = i + 1
                break
        
        if start_idx:
            # Display header
            header_line = lines[start_idx].strip()
            if header_line:
                headers = header_line.split(',')
                print(f"{'Category':<20} {'Expenses':<12} {'Count':<6} {'Avg/Trans':<10}")
                print("-" * 50)
                
                # Display category data
                for line in lines[start_idx + 1:]:
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 5:
                            category = parts[0][:18]  # Truncate long names
                            expenses = parts[1]
                            count = parts[4]
                            avg = parts[5]
                            print(f"{category:<20} {expenses:<12} {count:<6} {avg:<10}")
    
    except Exception as e:
        print(f"Error reading category breakdown: {e}")

def show_visualization_info():
    """Show information about generated visualizations."""
    print(f"\n📈 Generated Visualizations:")
    print("=" * 40)
    
    # Find chart files
    chart_files = [f for f in os.listdir('output') if f.endswith('.png')]
    
    if not chart_files:
        print("No chart files found.")
        return
    
    for chart_file in sorted(chart_files):
        print(f"📊 {chart_file}")
        
        if 'expense_chart' in chart_file:
            print("   → Bar chart showing expenses by category")
            print("   → X-axis: Expense categories")
            print("   → Y-axis: Amount spent ($)")
            
        elif 'income_vs_expense' in chart_file:
            print("   → Comparison chart of income vs expenses")
            print("   → Shows both income and expenses by category")
            print("   → Helps identify spending patterns")
        
        print()

def show_file_organization():
    """Show how files are organized."""
    print(f"\n📁 File Organization:")
    print("=" * 40)
    
    print("📂 Input:")
    print("   └── data/")
    print("       └── sample_bank_statement.pdf")
    
    print("\n📂 Output:")
    print("   └── output/")
    
    output_files = os.listdir('output')
    
    # Group files by type
    csv_files = [f for f in output_files if f.endswith('.csv')]
    png_files = [f for f in output_files if f.endswith('.png')]
    log_files = [f for f in output_files if f.endswith('.log')]
    
    if csv_files:
        print("       ├── 📊 CSV Reports:")
        for f in sorted(csv_files):
            if 'category_summary' in f:
                print(f"       │   ├── {f} (Category totals & summary)")
            elif 'detailed_transactions' in f:
                print(f"       │   ├── {f} (All transactions, organized)")
            else:
                print(f"       │   ├── {f} (Basic transaction export)")
    
    if png_files:
        print("       ├── 📈 Charts:")
        for f in sorted(png_files):
            print(f"       │   ├── {f}")
    
    if log_files:
        print("       └── 📝 Logs:")
        for f in sorted(log_files):
            print(f"           └── {f}")

def main():
    """Run the complete demonstration."""
    # Run the enhanced analysis
    results = demonstrate_enhanced_features()
    
    # Show detailed breakdowns
    show_category_breakdown()
    show_visualization_info()
    show_file_organization()
    
    print(f"\n🎯 Key Features Demonstrated:")
    print("=" * 40)
    print("✅ PDF text extraction and transaction parsing")
    print("✅ Smart keyword-based categorization")
    print("✅ Category-wise expense and income summaries")
    print("✅ Financial overview with totals and net amount")
    print("✅ Bar chart visualization of expense categories")
    print("✅ Income vs expense comparison charts")
    print("✅ Organized CSV exports with category grouping")
    print("✅ Detailed transaction logs and analysis")
    
    print(f"\n💡 Next Steps:")
    print("=" * 40)
    print("🔧 Customize keywords in config/keywords.json")
    print("📄 Add your own PDF bank statements to data/")
    print("☁️  Set up Google Sheets API for cloud integration")
    print("📊 Open the generated PNG charts to view visualizations")
    print("📈 Use the CSV files for further analysis in Excel/Sheets")
    
    print(f"\n🎉 Your enhanced bank statement analyzer is ready!")

if __name__ == "__main__":
    main()
