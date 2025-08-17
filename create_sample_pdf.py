"""
Create a sample PDF bank statement for testing.
This simulates a real bank statement with transactions.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os

def create_sample_bank_statement():
    """Create a sample PDF bank statement."""
    filename = "data/sample_bank_statement.pdf"
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph("SAMPLE BANK STATEMENT", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Account info
    account_info = Paragraph("Account Number: ****1234<br/>Statement Period: January 1-31, 2024", styles['Normal'])
    story.append(account_info)
    story.append(Spacer(1, 24))
    
    # Transaction data
    transactions = [
        ['Date', 'Description', 'Amount'],
        ['01/02/2024', 'STARBUCKS #12345 SEATTLE WA', '-$4.75'],
        ['01/03/2024', 'AMAZON.COM AMZN.COM/BILL WA', '-$89.99'],
        ['01/04/2024', 'SHELL OIL 87654321 REDMOND WA', '-$52.30'],
        ['01/05/2024', 'DEPOSIT PAYROLL', '+$3,200.00'],
        ['01/06/2024', 'WALMART SUPERCENTER #5678', '-$123.45'],
        ['01/07/2024', 'MCDONALDS #9876 BELLEVUE WA', '-$8.99'],
        ['01/08/2024', 'NETFLIX.COM NETFLIX.COM CA', '-$15.99'],
        ['01/09/2024', 'COSTCO WHOLESALE #123', '-$234.56'],
        ['01/10/2024', 'UBER TRIP SEATTLE WA', '-$18.75'],
        ['01/11/2024', 'CVS PHARMACY #4567', '-$34.28'],
        ['01/12/2024', 'SPOTIFY PREMIUM', '-$9.99'],
        ['01/13/2024', 'HOME DEPOT #8901', '-$156.78'],
        ['01/14/2024', 'CHIPOTLE #2345', '-$12.50'],
        ['01/15/2024', 'VERIZON WIRELESS', '-$85.00'],
        ['01/16/2024', 'TARGET T-1234', '-$67.89'],
        ['01/17/2024', 'DUNKIN #5678', '-$3.25'],
        ['01/18/2024', 'BEST BUY #9012', '-$299.99'],
        ['01/19/2024', 'WHOLE FOODS #3456', '-$78.90'],
        ['01/20/2024', 'LYFT RIDE', '-$22.50'],
    ]
    
    # Create table
    table = Table(transactions, colWidths=[1.5*inch, 4*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    print(f"Sample bank statement created: {filename}")
    return filename

if __name__ == "__main__":
    try:
        # Try to install reportlab if not available
        try:
            import reportlab
        except ImportError:
            print("Installing reportlab for PDF creation...")
            import subprocess
            subprocess.check_call(["pip", "install", "reportlab"])
            import reportlab
        
        filename = create_sample_bank_statement()
        print(f"✅ Sample PDF created: {filename}")
        print("You can now test the full analyzer with:")
        print("  python src/main.py")
        
    except Exception as e:
        print(f"Error creating sample PDF: {e}")
        print("You can manually create a PDF or use existing bank statements in the data/ folder")
