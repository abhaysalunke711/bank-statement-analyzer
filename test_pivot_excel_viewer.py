"""
Test the Excel viewer with the new pivot-style report.
"""

import sys
import os
sys.path.append('src')

from excel_viewer import ExcelViewer

def test_pivot_excel_viewer():
    """Test the Excel viewer with the pivot report."""
    print("🧪 Testing Pivot Excel Viewer")
    print("=" * 40)
    
    viewer = ExcelViewer()
    
    # Check if the test pivot report exists
    pivot_file = "output/test_pivot_report.xlsx"
    if not os.path.exists(pivot_file):
        print(f"❌ Pivot test file not found: {pivot_file}")
        print("   Run 'python test_pivot_report.py' first to generate the test file.")
        return
    
    print(f"📊 Testing with: {pivot_file}")
    print("-" * 50)
    
    # Read the pivot Excel file
    excel_data = viewer.read_excel_file(pivot_file)
    
    if not excel_data:
        print("❌ Failed to read pivot Excel file")
        return
    
    print(f"✅ Successfully read pivot Excel file")
    print(f"   📄 Total sheets: {excel_data['total_sheets']}")
    print(f"   📋 Sheet names: {', '.join(excel_data['sheet_names'])}")
    
    # Show sheet details
    print(f"\n📋 Sheet Analysis:")
    for sheet_name, sheet_data in excel_data['sheets'].items():
        print(f"   📄 {sheet_name}:")
        print(f"      Type: {sheet_data.get('type', 'unknown')}")
        print(f"      Rows: {sheet_data['summary']['total_rows']}")
        print(f"      Cols: {sheet_data['summary']['total_cols']}")
        if sheet_data['headers']:
            print(f"      Headers: {', '.join(sheet_data['headers'][:5])}...")
        
        # Check for pivot-specific features
        if sheet_data.get('type') == 'pivot':
            print(f"      🎯 Pivot layout detected!")
            
            # Look for month columns
            month_cols = [h for h in sheet_data['headers'] if any(month in h.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun'])]
            if month_cols:
                print(f"      📅 Month columns: {', '.join(month_cols)}")
            
            # Look for total column
            total_cols = [h for h in sheet_data['headers'] if 'total' in h.lower()]
            if total_cols:
                print(f"      💰 Total columns: {', '.join(total_cols)}")
            
            # Look for income/expense sections
            income_rows = [row for row in sheet_data['rows'] if any('income' in str(cell).lower() for cell in row)]
            expense_rows = [row for row in sheet_data['rows'] if any('expense' in str(cell).lower() for cell in row)]
            
            print(f"      🟢 Income-related rows: {len(income_rows)}")
            print(f"      🔴 Expense-related rows: {len(expense_rows)}")
    
    # Generate HTML for web viewing
    print(f"\n🌐 Generating HTML for web viewing...")
    html_output = viewer.generate_html_tables(excel_data)
    
    if html_output:
        print(f"✅ HTML generated successfully")
        print(f"   📏 HTML length: {len(html_output):,} characters")
        
        # Save HTML for testing
        html_file = os.path.join("output", "pivot_preview.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pivot Excel Preview</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .bg-light-success {{
            background-color: rgba(25, 135, 84, 0.1) !important;
            border: 1px solid rgba(25, 135, 84, 0.2);
        }}
        .bg-light-danger {{
            background-color: rgba(220, 53, 69, 0.1) !important;
            border: 1px solid rgba(220, 53, 69, 0.2);
        }}
        .table th {{
            position: sticky;
            top: 0;
            background: var(--bs-dark) !important;
            z-index: 10;
        }}
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <h1 class="mb-4">
            <i class="fas fa-table text-primary me-2"></i>
            Pivot Excel Preview: {os.path.basename(pivot_file)}
        </h1>
        
        <div class="alert alert-info">
            <h6 class="alert-heading">
                <i class="fas fa-info-circle me-2"></i>
                Pivot Layout Structure
            </h6>
            <ul class="mb-0">
                <li><strong>Rows:</strong> Categories/Items from statements</li>
                <li><strong>Columns:</strong> Monthly breakdown + Total</li>
                <li><strong>Layout:</strong> Income at top, expenses at bottom</li>
                <li><strong>Colors:</strong> Green for income, red for expenses</li>
            </ul>
        </div>
        
        {html_output}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
            """)
        
        print(f"   💾 HTML preview saved: {html_file}")
    else:
        print("❌ Failed to generate HTML")
    
    # Get summary stats
    stats = viewer.get_summary_stats(excel_data)
    if stats:
        print(f"\n📊 Summary Statistics:")
        for sheet_info in stats.get('sheets_info', []):
            print(f"   📄 {sheet_info['name']}: {sheet_info['rows']} rows, {sheet_info['cols']} cols")
            if sheet_info.get('type') == 'pivot':
                print(f"      🎯 Pivot-style financial summary")

if __name__ == "__main__":
    test_pivot_excel_viewer()
    
    print("\n🚀 Next Steps:")
    print("1. Open the HTML preview to see how the pivot table looks in browser")
    print("2. Start the web app: python app.py")
    print("3. Upload PDF files to see the new pivot layout")
    print("4. Compare with the actual Excel file formatting")
