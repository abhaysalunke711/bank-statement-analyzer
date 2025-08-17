# 🏦 Bank Statement Analyzer - Web Application

A powerful web-based application that analyzes PDF bank statements, automatically categorizes transactions, and generates comprehensive monthly reports with Excel tabs for each month.

## 🌟 Features

### 🌐 Web Interface
- **Modern drag & drop interface** for uploading PDF files
- **Responsive design** works on desktop and mobile
- **Real-time progress tracking** during analysis
- **Secure file handling** with automatic cleanup

### 📊 Smart Analysis
- **AI-powered categorization** (Food, Shopping, Transportation, etc.)
- **Monthly organization** with separate Excel tabs
- **Financial summaries** with income vs expense breakdowns
- **Visual charts** and comprehensive reports

### 📁 Multiple Output Formats
- **Excel files** with monthly tabs (Jan 2024, Feb 2024, etc.)
- **CSV backups** for compatibility
- **PNG charts** for visualization
- **Detailed transaction logs**

## 🚀 Quick Start

### Method 1: Windows Launcher (Easiest)
1. Double-click `start_web_app.bat`
2. Your browser will automatically open to http://localhost:5000
3. Upload your PDF bank statements and analyze!

### Method 2: Python Command
```bash
# Install dependencies
pip install -r requirements.txt

# Start the web application
python start_web_app.py
```

### Method 3: Direct Flask
```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## 📋 How to Use

1. **Upload PDFs**: Drag & drop or browse for PDF bank statements
2. **Automatic Processing**: The system extracts and categorizes all transactions
3. **Monthly Reports**: Download Excel files with separate tabs for each month
4. **Visual Analysis**: View charts and comprehensive summaries

## 📊 What You Get

### Excel Report Structure
- **📄 Summary Tab**: Overall financial overview and monthly breakdown
- **📄 Monthly Tabs**: Separate tabs for each month (e.g., "Jan 2024", "Feb 2024")
  - Monthly summary statistics
  - Category-wise breakdowns  
  - Detailed transaction lists
  - Professional formatting with colors

### Example Monthly Tab Contents
```
Jan 2024 Analysis
├── Monthly Summary
│   ├── Total Income: $3,200.00
│   ├── Total Expenses: $1,319.86
│   └── Net Amount: $1,880.14
├── Category Breakdown
│   ├── Shopping: $972.66 (6 transactions)
│   ├── Food & Dining: $108.39 (5 transactions)
│   └── Transportation: $93.55 (3 transactions)
└── Detailed Transactions
    └── Complete list with dates, descriptions, categories
```

## 🔧 Configuration

### Keywords Customization
Edit `config/keywords.json` to customize transaction categories:

```json
{
  "Food & Dining": {
    "exact": ["starbucks", "mcdonald", "restaurant"],
    "fuzzy": ["food", "dining", "cafe"],
    "regex": [".*restaurant.*", ".*cafe.*"]
  }
}
```

### Optional: Google Sheets Integration
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Sheets API
3. Create service account and download JSON key
4. Save as `config/service_account.json`

## 📁 Project Structure

```
bankstatementanalyzer/
├── 🌐 Web Application
│   ├── app.py                     # Flask web server
│   ├── templates/                 # HTML templates
│   ├── static/                    # CSS, JS, images
│   └── uploads/                   # Temporary file storage
├── 🧠 Core Analysis Engine
│   ├── src/main.py               # Main analyzer
│   ├── src/pdf_reader.py         # PDF text extraction
│   ├── src/keyword_matcher.py    # Transaction categorization
│   ├── src/monthly_report_generator.py  # Excel with monthly tabs
│   └── src/google_sheets_client.py      # Google Sheets API
├── ⚙️ Configuration
│   ├── config/keywords.json      # Category definitions
│   └── config/setup_instructions.md
├── 📊 Output
│   ├── output/                   # Generated reports
│   └── Monthly Excel files with tabs
└── 🚀 Launchers
    ├── start_web_app.py         # Python launcher
    └── start_web_app.bat        # Windows launcher
```

## 🎯 Key Features Highlighted

- ✅ **Monthly Organization**: Each statement month gets its own Excel tab
- ✅ **Smart Categorization**: 10+ built-in categories with fuzzy matching
- ✅ **Web-Based**: No command line needed, just upload and download
- ✅ **Multiple Formats**: Excel, CSV, and PNG chart outputs
- ✅ **Financial Summaries**: Income, expenses, and net calculations
- ✅ **Professional Reports**: Color-coded, formatted Excel files
- ✅ **Secure Processing**: Files deleted after analysis
- ✅ **Mobile Friendly**: Responsive web interface

## 💡 Tips

- **File Naming**: Name your PDFs with dates for better organization (e.g., "Jan_2024_Statement.pdf")
- **Multiple Files**: Upload all your monthly statements at once for complete analysis
- **Categories**: Customize keywords in `config/keywords.json` for better categorization
- **Excel Tabs**: Each month appears as a separate tab in the Excel file

## 🛠️ Troubleshooting

### Common Issues
1. **"No transactions found"**: PDF might be image-based (scanned), try OCR tools first
2. **"Port already in use"**: Close other instances or change port in `app.py`
3. **File upload fails**: Check file size (16MB max) and ensure it's a valid PDF

### Getting Help
- Check the logs in the `output/` directory
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify PDF files are text-based (not scanned images)

## 🎉 Success Story

Transform this:
```
📄 jan_statement.pdf (unorganized transactions)
📄 feb_statement.pdf (unorganized transactions) 
📄 mar_statement.pdf (unorganized transactions)
```

Into this:
```
📊 monthly_analysis_2024.xlsx
├── 📋 Summary (Overall statistics)
├── 📅 Jan 2024 (5 transactions, categorized)
├── 📅 Feb 2024 (7 transactions, categorized)
└── 📅 Mar 2024 (6 transactions, categorized)
```

**Your financial data, organized by month, categorized intelligently, and ready for analysis!** 🎯
