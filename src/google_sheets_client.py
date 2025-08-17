"""
Google Sheets API client for creating and updating spreadsheets.
Handles authentication and data formatting for bank statement analysis.
"""

import os
import logging
from typing import List, Dict, Optional
import json
from datetime import datetime

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    logging.error(f"Google API libraries not installed: {e}")
    logging.error("Please install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

class GoogleSheetsClient:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, credentials_path: str = None, service_account_path: str = None):
        self.logger = logging.getLogger(__name__)
        self.service = None
        self.credentials_path = credentials_path
        self.service_account_path = service_account_path
        
        # Try to authenticate
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        creds = None
        
        # Try service account authentication first
        if self.service_account_path and os.path.exists(self.service_account_path):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    self.service_account_path, scopes=self.SCOPES)
                self.logger.info("Authenticated using service account")
            except Exception as e:
                self.logger.error(f"Service account authentication failed: {e}")
        
        # Fall back to OAuth flow
        if not creds and self.credentials_path:
            token_path = self.credentials_path.replace('.json', '_token.json')
            
            # Load existing token
            if os.path.exists(token_path):
                try:
                    creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                    self.logger.info("Loaded existing OAuth token")
                except Exception as e:
                    self.logger.warning(f"Failed to load existing token: {e}")
            
            # Refresh or create new token
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        self.logger.info("Refreshed OAuth token")
                    except Exception as e:
                        self.logger.error(f"Token refresh failed: {e}")
                        creds = None
                
                if not creds:
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                        self.logger.info("Created new OAuth token")
                    except Exception as e:
                        self.logger.error(f"OAuth flow failed: {e}")
                        return
                
                # Save token
                try:
                    with open(token_path, 'w') as token_file:
                        token_file.write(creds.to_json())
                    self.logger.info(f"Saved token to {token_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to save token: {e}")
        
        if creds:
            try:
                self.service = build('sheets', 'v4', credentials=creds)
                self.logger.info("Google Sheets service initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to build Google Sheets service: {e}")
        else:
            self.logger.error("No valid credentials found")
    
    def create_spreadsheet(self, title: str) -> Optional[str]:
        """
        Create a new Google Spreadsheet.
        
        Args:
            title: Title for the new spreadsheet
            
        Returns:
            Spreadsheet ID if successful, None otherwise
        """
        if not self.service:
            self.logger.error("Google Sheets service not initialized")
            return None
        
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            result = self.service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = result.get('spreadsheetId')
            
            self.logger.info(f"Created spreadsheet: {title} (ID: {spreadsheet_id})")
            return spreadsheet_id
            
        except HttpError as e:
            self.logger.error(f"Error creating spreadsheet: {e}")
            return None
    
    def write_data(self, spreadsheet_id: str, data: List[List], 
                   range_name: str = 'A1', sheet_name: str = 'Sheet1') -> bool:
        """
        Write data to a Google Spreadsheet.
        
        Args:
            spreadsheet_id: ID of the target spreadsheet
            data: 2D list of data to write
            range_name: Starting cell (e.g., 'A1')
            sheet_name: Name of the sheet
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            self.logger.error("Google Sheets service not initialized")
            return False
        
        try:
            full_range = f"{sheet_name}!{range_name}"
            
            body = {
                'values': data
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=full_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            self.logger.info(f"Updated {updated_cells} cells in {full_range}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Error writing data: {e}")
            return False
    
    def format_transactions_for_sheets(self, transactions: List[Dict], 
                                     include_source: bool = True) -> List[List]:
        """
        Format transaction data for Google Sheets.
        
        Args:
            transactions: List of transaction dictionaries
            include_source: Whether to include source file column
            
        Returns:
            2D list formatted for Google Sheets
        """
        # Header row
        headers = ['Date', 'Description', 'Category', 'Amount']
        if include_source:
            headers.append('Source File')
        
        data = [headers]
        
        for transaction in transactions:
            row = [
                transaction.get('date', ''),
                transaction.get('description', ''),
                transaction.get('category', 'Uncategorized'),
                transaction.get('amount', 0)
            ]
            
            if include_source:
                row.append(transaction.get('source_file', ''))
            
            data.append(row)
        
        return data
    
    def create_bank_statement_sheet(self, transactions: List[Dict], 
                                   title: str = None) -> Optional[str]:
        """
        Create a complete bank statement analysis spreadsheet.
        
        Args:
            transactions: List of categorized transactions
            title: Title for the spreadsheet
            
        Returns:
            Spreadsheet ID if successful, None otherwise
        """
        if not title:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            title = f"Bank Statement Analysis - {timestamp}"
        
        # Create spreadsheet
        spreadsheet_id = self.create_spreadsheet(title)
        if not spreadsheet_id:
            return None
        
        # Format data
        data = self.format_transactions_for_sheets(transactions)
        
        # Write data
        if self.write_data(spreadsheet_id, data):
            # Add summary sheet
            self._add_summary_sheet(spreadsheet_id, transactions)
            
            # Format the spreadsheet
            self._format_spreadsheet(spreadsheet_id)
            
            self.logger.info(f"Bank statement spreadsheet created: {title}")
            return spreadsheet_id
        
        return None
    
    def _add_summary_sheet(self, spreadsheet_id: str, transactions: List[Dict]):
        """Add a summary sheet with category totals."""
        try:
            # Create summary sheet
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': 'Summary'
                        }
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=request_body).execute()
            
            # Calculate category totals
            category_totals = {}
            for transaction in transactions:
                category = transaction.get('category', 'Uncategorized')
                amount = transaction.get('amount', 0)
                
                # Convert amount to float if it's a string
                if isinstance(amount, str):
                    try:
                        amount = float(amount.replace('$', '').replace(',', ''))
                    except (ValueError, AttributeError):
                        amount = 0
                
                category_totals[category] = category_totals.get(category, 0) + amount
            
            # Format summary data
            summary_data = [['Category', 'Total Amount', 'Transaction Count']]
            category_counts = {}
            
            for transaction in transactions:
                category = transaction.get('category', 'Uncategorized')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            for category, total in category_totals.items():
                count = category_counts.get(category, 0)
                summary_data.append([category, f"${total:.2f}", count])
            
            # Write summary data
            self.write_data(spreadsheet_id, summary_data, 'A1', 'Summary')
            
        except Exception as e:
            self.logger.warning(f"Failed to add summary sheet: {e}")
    
    def _format_spreadsheet(self, spreadsheet_id: str):
        """Apply basic formatting to the spreadsheet."""
        try:
            requests = [
                # Format header row
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                                'textFormat': {'bold': True}
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                },
                # Auto-resize columns
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': 0,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 5
                        }
                    }
                }
            ]
            
            body = {'requests': requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body).execute()
            
        except Exception as e:
            self.logger.warning(f"Failed to format spreadsheet: {e}")
    
    def get_spreadsheet_url(self, spreadsheet_id: str) -> str:
        """Get the URL for a spreadsheet."""
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
