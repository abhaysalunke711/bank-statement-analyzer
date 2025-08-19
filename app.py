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
from receipt_processor import ReceiptProcessor

app = Flask(__name__)
app.secret_key = 'bank_analyzer_secret_key_2024'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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
        # Prepare results for display - store both original and actual filenames
        uploaded_file_info = []
        for file_path in uploaded_files:
            actual_filename = os.path.basename(file_path)
            # Extract original filename (remove timestamp that was added during upload)
            # Format: originalname_YYYYMMDD_HHMMSS.ext
            if '_20' in actual_filename and actual_filename.count('_') >= 2:
                # Find the last two underscores (date and time)
                parts = actual_filename.rsplit('_', 2)  # Split from right, max 2 splits
                if len(parts) == 3:
                    # parts[0] = original name, parts[1] = date, parts[2] = time.ext
                    original_name = parts[0] + os.path.splitext(actual_filename)[1]
                else:
                    original_name = actual_filename
            else:
                original_name = actual_filename
            
            uploaded_file_info.append({
                'original_name': original_name,
                'actual_filename': actual_filename,
                'display_name': original_name
            })

        # Extract receipt data from uploaded files
        receipt_data = []
        for file_info in uploaded_file_info:
            file_path = os.path.join(UPLOAD_FOLDER, file_info['actual_filename'])
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    # Process receipt image
                    receipt_processor = ReceiptProcessor(output_dir=OUTPUT_FOLDER)
                    receipt = receipt_processor.process_image(file_path)
                    receipt_data.append({
                        'date': receipt.date.strftime('%Y-%m-%d'),
                        'store_name': receipt.store_name,
                        'items': [
                            {
                                'name': item.name,
                                'amount': str(item.amount),
                                'quantity': str(item.quantity),
                                'category': item.category
                            }
                            for item in receipt.items
                        ],
                        'totals': {
                            'total': str(receipt.total_amount)
                        }
                    })
                except Exception as e:
                    logger.warning(f"Could not process receipt {file_path}: {e}")
        
        # Create pivot-style Excel report with color coding
        excel_path = pivot_generator.create_pivot_excel_report(
            categorized_transactions,
            receipt_data=receipt_data
        )
        
        # Get chart data for visualization
        chart_data = pivot_generator.get_chart_data(categorized_transactions)
        
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
        
        # Prepare results for display - store both original and actual filenames
        uploaded_file_info = []
        for file_path in uploaded_files:
            actual_filename = os.path.basename(file_path)
            # Extract original filename (remove timestamp that was added during upload)
            # Format: originalname_YYYYMMDD_HHMMSS.ext
            if '_20' in actual_filename and actual_filename.count('_') >= 2:
                # Find the last two underscores (date and time)
                parts = actual_filename.rsplit('_', 2)  # Split from right, max 2 splits
                if len(parts) == 3:
                    # parts[0] = original name, parts[1] = date, parts[2] = time.ext
                    original_name = parts[0] + os.path.splitext(actual_filename)[1]
                else:
                    original_name = actual_filename
            else:
                original_name = actual_filename
            
            uploaded_file_info.append({
                'original_name': original_name,
                'actual_filename': actual_filename,
                'display_name': original_name
            })
        
        # Prepare results for display
        results['excel_path'] = excel_path
        results['excel_data'] = excel_data
        results['excel_stats'] = excel_stats
        results['excel_html'] = excel_html
        results['uploaded_files'] = [os.path.basename(f) for f in uploaded_files]  # Just use filenames
        results['chart_data'] = chart_data  # Add chart data to results
        
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

@app.route('/view_pdf/<filename>')
def view_pdf(filename):
    """Serve PDF files for viewing in browser."""
    try:
        logger.info(f"Attempting to serve PDF: {filename}")
        
        # Check in uploads folder first
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        logger.info(f"Checking upload path: {upload_path}")
        logger.info(f"Upload path exists: {os.path.exists(upload_path)}")
        
        if os.path.exists(upload_path):
            logger.info(f"Serving PDF from uploads: {upload_path}")
            return send_file(upload_path, mimetype='application/pdf', as_attachment=False)
        
        # Check in output folder as fallback
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        logger.info(f"Checking output path: {output_path}")
        logger.info(f"Output path exists: {os.path.exists(output_path)}")
        
        if os.path.exists(output_path):
            logger.info(f"Serving PDF from output: {output_path}")
            return send_file(output_path, mimetype='application/pdf', as_attachment=False)
        
        # List available files for debugging
        upload_files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
        output_files = os.listdir(OUTPUT_FOLDER) if os.path.exists(OUTPUT_FOLDER) else []
        
        logger.error(f"PDF file not found: {filename}")
        logger.error(f"Available upload files: {upload_files}")
        logger.error(f"Available output files: {output_files}")
        
        return f"PDF file '{filename}' not found. Available files: {upload_files + output_files}", 404
        
    except Exception as e:
        logger.error(f"Error serving PDF {filename}: {e}", exc_info=True)
        return f"Error loading PDF: {str(e)}", 500

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

@app.route('/api/process_receipt', methods=['POST'])
def process_receipt():
    """Process receipt image using OCR."""
    try:
        if 'receipt' not in request.files:
            return jsonify({'error': 'No receipt file provided'}), 400
        
        file = request.files['receipt']
        if not file or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if it's an image file
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            return jsonify({'error': 'Invalid file type. Only JPG and PNG are allowed'}), 400
        
        # Save the file temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(temp_path)
        
        try:
            # Process the receipt
            receipt_processor = ReceiptProcessor(output_dir=OUTPUT_FOLDER)
            receipt = receipt_processor.process_image(temp_path)
            
            # Format response data
            response_data = {
                'store_name': receipt.store_name,
                'date': receipt.date.strftime('%Y-%m-%d'),
                'items': [
                    {
                        'name': item.name,
                        'amount': str(item.amount),
                        'quantity': str(item.quantity),
                        'category': item.category
                    }
                    for item in receipt.items
                ],
                'total_amount': str(receipt.total_amount)
            }
            
            return jsonify(response_data)
            
        finally:
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except:
                pass
            
    except Exception as e:
        logger.error(f"Error processing receipt: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🏦 Bank Statement Analyzer Web App")
    print("=" * 50)
    print("🌐 Starting web server...")
    print("📁 Upload folder:", UPLOAD_FOLDER)
    print("📊 Output folder: output/")
    print("🔗 Access the app at: http://localhost:8080")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, host='127.0.0.1', port=8080)
