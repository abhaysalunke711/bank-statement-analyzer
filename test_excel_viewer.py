"""
Test the Excel viewer functionality.
"""

import sys
import os
sys.path.append('src')

from excel_viewer import ExcelViewer

def test_excel_viewer():
    """Test the Excel viewer with existing Excel files."""
    print("🔍 Testing Excel Viewer")
    print("=" * 40)
    
    viewer = ExcelViewer()
    
    # Find Excel files in output directory
    output_dir = "output"
    if not os.path.exists(output_dir):
        print(f"❌ Output directory not found: {output_dir}")
        return
    
    excel_files = [f for f in os.listdir(output_dir) if f.endswith('.xlsx') and not f.startswith('~$')]
    if not excel_files:
        print(f"❌ No Excel files found in {output_dir}/")
        return
    
    print(f"📁 Found {len(excel_files)} Excel files:")
    for i, file in enumerate(excel_files, 1):
        print(f"   {i}. {file}")
    
    # Test with the latest file
    latest_file = sorted(excel_files)[-1]
    excel_path = os.path.join(output_dir, latest_file)
    
    print(f"\n📊 Testing with: {latest_file}")
    print("-" * 50)
    
    # Read Excel file
    excel_data = viewer.read_excel_file(excel_path)
    
    if not excel_data:
        print("❌ Failed to read Excel file")
        return
    
    print(f"✅ Successfully read Excel file")
    print(f"   📄 Total sheets: {excel_data['total_sheets']}")
    print(f"   📋 Sheet names: {', '.join(excel_data['sheet_names'])}")
    
    # Show sheet details
    print(f"\n📋 Sheet Details:")
    for sheet_name, sheet_data in excel_data['sheets'].items():
        print(f"   📄 {sheet_name}:")
        print(f"      Type: {sheet_data.get('type', 'unknown')}")
        print(f"      Rows: {sheet_data['summary']['total_rows']}")
        print(f"      Cols: {sheet_data['summary']['total_cols']}")
        if sheet_data['headers']:
            print(f"      Headers: {', '.join(sheet_data['headers'][:5])}...")
    
    # Generate HTML
    print(f"\n🌐 Generating HTML tables...")
    html_output = viewer.generate_html_tables(excel_data)
    
    if html_output:
        print(f"✅ HTML generated successfully")
        print(f"   📏 HTML length: {len(html_output):,} characters")
        
        # Save HTML for testing
        html_file = os.path.join(output_dir, "excel_preview.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Preview - {latest_file}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container-fluid py-4">
        <h1 class="mb-4">
            <i class="fas fa-file-excel text-success me-2"></i>
            Excel Preview: {latest_file}
        </h1>
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
            if sheet_info.get('is_summary'):
                print(f"      💰 Financial Summary Sheet")
                if 'total_income' in sheet_info:
                    print(f"         Income: {sheet_info['total_income']}")
                if 'total_expenses' in sheet_info:
                    print(f"         Expenses: {sheet_info['total_expenses']}")

if __name__ == "__main__":
    test_excel_viewer()
