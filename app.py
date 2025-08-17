"""
Flask web application for Bank Statement Analyzer.
Provides web interface for uploading PDF files and viewing analysis results.
"""

import os
import sys
import logging
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import shutil

# Add src directory to path
sys.path.append('src')

from main import BankStatementAnalyzer
from enhanced_pdf_reader import EnhancedPDFReader
from monthly_report_generator import MonthlyReportGenerator
from enhanced_monthly_report_generator import EnhancedMonthlyReportGenerator
from pivot_monthly_report_generator import PivotMonthlyReportGenerator
from excel_viewer import ExcelViewer

app = Flask(__name__)
app.secret_key = 'bank_analyzer_secret_key_2024'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and process bank statements."""
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            flash('No files selected', 'error')
            return redirect(url_for('index'))
        
        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            flash('No files selected', 'error')
            return redirect(url_for('index'))
        
        # Clear previous uploads
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Could not delete {file_path}: {e}")
        
        uploaded_files = []
        
        # Save uploaded files
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                uploaded_files.append(file_path)
                logger.info(f"Uploaded file: {filename}")
            else:
                flash(f'Invalid file type: {file.filename}. Only PDF files are allowed.', 'error')
        
        if not uploaded_files:
            flash('No valid PDF files uploaded', 'error')
            return redirect(url_for('index'))
        
        # Process the uploaded files
        analyzer = BankStatementAnalyzer(data_dir=UPLOAD_FOLDER)
        monthly_generator = MonthlyReportGenerator()
        enhanced_generator = EnhancedMonthlyReportGenerator()
        pivot_generator = PivotMonthlyReportGenerator()
        
        # Run analysis
        results = analyzer.run_analysis(
            pdf_files=uploaded_files,
            create_reports=True,
            export_csv=True
        )
        
        if results['total_transactions'] == 0:
            flash('No transactions found in the uploaded files', 'warning')
            return redirect(url_for('index'))
        
        # Get the processed transactions for monthly report
        transactions = []
        for file_path in uploaded_files:
            filename = os.path.basename(file_path)
            text = analyzer.pdf_reader.extract_text_from_pdf(file_path)
            if text:
                file_transactions = analyzer.pdf_reader.extract_transactions(text)
                for transaction in file_transactions:
                    transaction['source_file'] = filename
                transactions.extend(file_transactions)
        
        # Categorize transactions
        categorized_transactions = analyzer.keyword_matcher.batch_categorize(transactions)
        
        # Create pivot-style Excel report with color coding
        excel_path = pivot_generator.create_pivot_excel_report(categorized_transactions)
        
        # Generate Excel viewer data for browser display
        excel_viewer = ExcelViewer()
        excel_data = {}
        excel_stats = {}
        
        if excel_path and os.path.exists(excel_path):
            excel_data = excel_viewer.read_excel_file(excel_path)
            excel_stats = excel_viewer.get_summary_stats(excel_data)
            excel_html = excel_viewer.generate_html_tables(excel_data)
        else:
            excel_html = "<p class='text-muted'>Excel file not available</p>"
        
        # Prepare results for display
        results['excel_path'] = excel_path
        results['excel_data'] = excel_data
        results['excel_stats'] = excel_stats
        results['excel_html'] = excel_html
        results['uploaded_files'] = [os.path.basename(f) for f in uploaded_files]
        
        flash(f'Successfully processed {results["total_transactions"]} transactions from {len(uploaded_files)} files', 'success')
        
        return render_template('results.html', results=results)
        
    except Exception as e:
        logger.error(f"Error processing files: {e}", exc_info=True)
        flash(f'Error processing files: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download generated reports."""
    try:
        # Security check - only allow downloads from output directory
        if not filename.startswith('output/'):
            filename = f'output/{filename}'
        
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            flash('File not found', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        flash('Error downloading file', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for programmatic analysis."""
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Process files (similar to upload_files but return JSON)
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                uploaded_files.append(file_path)
        
        if not uploaded_files:
            return jsonify({'error': 'No valid PDF files'}), 400
        
        # Analyze files
        analyzer = BankStatementAnalyzer(data_dir=UPLOAD_FOLDER)
        monthly_generator = MonthlyReportGenerator()
        
        results = analyzer.run_analysis(
            pdf_files=uploaded_files,
            create_reports=True,
            export_csv=True
        )
        
        # Get transactions for monthly report
        transactions = []
        for file_path in uploaded_files:
            filename = os.path.basename(file_path)
            text = analyzer.pdf_reader.extract_text_from_pdf(file_path)
            if text:
                file_transactions = analyzer.pdf_reader.extract_transactions(text)
                for transaction in file_transactions:
                    transaction['source_file'] = filename
                transactions.extend(file_transactions)
        
        categorized_transactions = analyzer.keyword_matcher.batch_categorize(transactions)
        excel_path = monthly_generator.create_monthly_excel_report(categorized_transactions)
        
        # Return JSON response
        return jsonify({
            'success': True,
            'total_transactions': results['total_transactions'],
            'categories_found': results['categories_found'],
            'excel_file': os.path.basename(excel_path) if excel_path else None,
            'csv_file': os.path.basename(results.get('csv_path', '')) if results.get('csv_path') else None,
            'report_files': {k: os.path.basename(v) for k, v in results.get('report_files', {}).items()}
        })
        
    except Exception as e:
        logger.error(f"API error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/clear')
def clear_uploads():
    """Clear uploaded files and results."""
    try:
        # Clear uploads
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Could not delete {file_path}: {e}")
        
        flash('Cleared all uploaded files', 'success')
        
    except Exception as e:
        logger.error(f"Error clearing files: {e}")
        flash('Error clearing files', 'error')
    
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File is too large. Maximum size is 16MB per file.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal error: {e}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("🏦 Bank Statement Analyzer Web App")
    print("=" * 50)
    print("🌐 Starting web server...")
    print("📁 Upload folder:", UPLOAD_FOLDER)
    print("📊 Output folder: output/")
    print("🔗 Access the app at: http://localhost:5000")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
