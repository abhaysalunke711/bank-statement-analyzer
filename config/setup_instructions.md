# Setup Instructions for Bank Statement Analyzer

## Google Sheets API Setup

### Option 1: Service Account (Recommended for automated use)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create a service account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create
5. Create a key for the service account:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Download the file and save it as `config/service_account.json`

### Option 2: OAuth 2.0 (For personal use)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API (same as above)
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials file and save it as `config/credentials.json`

## Configuration Files

1. **Keywords Configuration**: `config/keywords.json`
   - Already created with common categories
   - Customize the keywords for your specific needs
   - Supports exact matching, fuzzy matching, and regex patterns

2. **Environment Variables**: `config/env_template`
   - Copy to `.env` if you want to use environment variables
   - Most settings have sensible defaults

## Directory Structure

```
bankstatementanalyzer/
├── config/
│   ├── keywords.json          # Keyword categories
│   ├── credentials.json       # OAuth credentials (you create)
│   ├── service_account.json   # Service account key (you create)
│   └── setup_instructions.md  # This file
├── data/                      # Place PDF files here
├── output/                    # Generated reports and logs
├── src/                       # Source code
└── requirements.txt           # Dependencies
```

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Place your PDF bank statements in the `data/` directory

3. Run the analyzer:
   ```bash
   python src/main.py
   ```

4. Check the `output/` directory for logs and CSV backups

## Troubleshooting

### Common Issues

1. **"No module named 'google'"**
   - Run: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

2. **"Credentials not found"**
   - Make sure you have either `credentials.json` or `service_account.json` in the `config/` directory
   - Check the file permissions

3. **"No PDF files found"**
   - Ensure PDF files are in the `data/` directory
   - Check file extensions (must be `.pdf`)

4. **"Failed to extract text"**
   - Some PDFs might be scanned images - consider using OCR tools first
   - Try different PDF files to test the system

### Getting Help

Check the log files in the `output/` directory for detailed error messages.
