"""
Enhanced PDF Reader with bank-specific parsing capabilities.
Handles different bank statement formats including Chase, Bank of America, etc.
"""

import os
import logging
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pdfplumber
import PyPDF2

class EnhancedPDFReader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def extract_text_from_pdf(self, pdf_path: str, method: str = 'pdfplumber') -> str:
        """Extract text from PDF using specified method."""
        try:
            if method == 'pdfplumber':
                return self._extract_with_pdfplumber(pdf_path)
            elif method == 'pypdf2':
                return self._extract_with_pypdf2(pdf_path)
            else:
                raise ValueError(f"Unsupported extraction method: {method}")
        except Exception as e:
            self.logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            # Try alternative method if primary fails
            try:
                alternative_method = 'pypdf2' if method == 'pdfplumber' else 'pdfplumber'
                self.logger.info(f"Trying alternative method: {alternative_method}")
                return self.extract_text_from_pdf(pdf_path, alternative_method)
            except Exception as e2:
                self.logger.error(f"Alternative method also failed: {str(e2)}")
                return ""
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber library."""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2 library."""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    def detect_bank_type(self, text: str) -> str:
        """Detect the bank type from the PDF text."""
        text_lower = text.lower()
        
        if 'jpmorgan chase' in text_lower or 'chase bank' in text_lower:
            return 'chase'
        elif 'bank of america' in text_lower or 'boa' in text_lower:
            return 'bofa'
        elif 'wells fargo' in text_lower:
            return 'wells_fargo'
        elif 'citibank' in text_lower or 'citi' in text_lower:
            return 'citi'
        elif 'capital one' in text_lower:
            return 'capital_one'
        else:
            return 'generic'
    
    def extract_transactions(self, text: str) -> List[Dict[str, str]]:
        """
        Extract transactions using bank-specific parsing.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            List of transaction dictionaries
        """
        # Detect bank type
        bank_type = self.detect_bank_type(text)
        self.logger.info(f"Detected bank type: {bank_type}")
        
        # Use bank-specific parser
        if bank_type == 'chase':
            return self._parse_chase_statement(text)
        elif bank_type == 'bofa':
            return self._parse_bofa_statement(text)
        elif bank_type == 'wells_fargo':
            return self._parse_wells_fargo_statement(text)
        else:
            # Fall back to generic parser
            return self._parse_generic_statement(text)
    
    def _parse_chase_statement(self, text: str) -> List[Dict[str, str]]:
        """Parse Chase bank statement format."""
        transactions = []
        lines = text.split('\n')
        
        # Chase statements often have transactions in a table format
        # Look for transaction sections
        in_transaction_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Look for transaction section headers
            if any(keyword in line.lower() for keyword in ['checking account activity', 'transaction', 'deposits and other credits', 'checks paid', 'electronic withdrawals']):
                in_transaction_section = True
                continue
            
            # Look for end of transaction section
            if in_transaction_section and any(keyword in line.lower() for keyword in ['summary', 'balance', 'fees', 'interest']):
                if not any(trans_keyword in line.lower() for trans_keyword in ['transaction', 'deposit', 'withdrawal', 'check']):
                    in_transaction_section = False
                    continue
            
            if in_transaction_section:
                # Try to parse Chase transaction format
                transaction = self._parse_chase_transaction_line(line, i, lines)
                if transaction:
                    transactions.append(transaction)
        
        # If no transactions found in sections, try line-by-line parsing
        if not transactions:
            self.logger.info("No transactions found in sections, trying line-by-line parsing")
            transactions = self._parse_chase_line_by_line(lines)
        
        return transactions
    
    def _parse_chase_transaction_line(self, line: str, line_index: int, all_lines: List[str]) -> Optional[Dict[str, str]]:
        """Parse a single Chase transaction line."""
        # Chase format variations:
        # MM/DD Description Amount
        # MM/DD/YY Description Amount
        # Check for date at start of line
        
        # Multiple date patterns for Chase
        date_patterns = [
            r'^(\d{1,2}/\d{1,2}/\d{2,4})',  # MM/DD/YY or MM/DD/YYYY at start
            r'^(\d{1,2}/\d{1,2})',          # MM/DD at start
            r'(\d{1,2}/\d{1,2}/\d{2,4})',   # MM/DD/YY anywhere
            r'(\d{1,2}/\d{1,2})\s',         # MM/DD followed by space
        ]
        
        # Amount patterns (Chase often uses spaces and various formats)
        amount_patterns = [
            r'([-+]?\$?\d{1,3}(?:,\d{3})*\.\d{2})$',  # Amount at end of line
            r'([-+]?\$?\d{1,3}(?:,\d{3})*\.\d{2})\s*$',  # Amount at end with possible spaces
            r'\s([-+]?\$?\d{1,3}(?:,\d{3})*\.\d{2})\s',  # Amount surrounded by spaces
            r'([-+]?\d{1,3}(?:,\d{3})*\.\d{2})$',  # Amount without $ at end
        ]
        
        date_match = None
        amount_match = None
        
        # Try to find date
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match:
                date_match = match.group(1)
                break
        
        # Try to find amount
        for pattern in amount_patterns:
            match = re.search(pattern, line)
            if match:
                amount_match = match.group(1)
                break
        
        # If we have both date and amount, it's likely a transaction
        if date_match and amount_match:
            # Extract description (everything between date and amount)
            description = line
            if date_match in line:
                description = line.split(date_match, 1)[-1].strip()
            if amount_match in description:
                description = description.replace(amount_match, '').strip()
            
            return {
                'date': date_match,
                'description': description or line,
                'amount': amount_match,
                'raw_line': line
            }
        
        return None
    
    def _parse_chase_line_by_line(self, lines: List[str]) -> List[Dict[str, str]]:
        """Parse Chase statement line by line when section parsing fails."""
        transactions = []
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:  # Skip very short lines
                continue
            
            # Look for lines that might contain transactions
            # Chase transactions often have: Date, Description, Amount
            
            # Multiple patterns to catch different Chase formats
            patterns = [
                # MM/DD/YY Description Amount
                r'^(\d{1,2}/\d{1,2}/\d{2,4})\s+(.+?)\s+([-+]?\$?\d{1,3}(?:,\d{3})*\.\d{2})$',
                # MM/DD Description Amount  
                r'^(\d{1,2}/\d{1,2})\s+(.+?)\s+([-+]?\$?\d{1,3}(?:,\d{3})*\.\d{2})$',
                # Date anywhere, amount at end
                r'.*(\d{1,2}/\d{1,2}/\d{2,4}).*\s+([-+]?\$?\d{1,3}(?:,\d{3})*\.\d{2})$',
                r'.*(\d{1,2}/\d{1,2}).*\s+([-+]?\$?\d{1,3}(?:,\d{3})*\.\d{2})$',
            ]
            
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    if len(groups) >= 3:
                        date, description, amount = groups[0], groups[1], groups[2]
                    elif len(groups) == 2:
                        date, amount = groups
                        description = line.replace(date, '').replace(amount, '').strip()
                    else:
                        continue
                    
                    transactions.append({
                        'date': date,
                        'description': description,
                        'amount': amount,
                        'raw_line': line
                    })
                    break
        
        return transactions
    
    def _parse_bofa_statement(self, text: str) -> List[Dict[str, str]]:
        """Parse Bank of America statement format."""
        # Bank of America has its own format - implement as needed
        return self._parse_generic_statement(text)
    
    def _parse_wells_fargo_statement(self, text: str) -> List[Dict[str, str]]:
        """Parse Wells Fargo statement format."""
        # Wells Fargo has its own format - implement as needed
        return self._parse_generic_statement(text)
    
    def _parse_generic_statement(self, text: str) -> List[Dict[str, str]]:
        """Generic parser for unknown bank formats."""
        transactions = []
        lines = text.split('\n')
        
        # Generic patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\d{1,2}\s+\w{3}\s+\d{4}\b',
        ]
        
        amount_pattern = r'[-+]?\$?\d{1,3}(?:,\d{3})*\.?\d{0,2}'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for lines that contain both date and amount patterns
            dates_found = []
            for pattern in date_patterns:
                dates = re.findall(pattern, line)
                dates_found.extend(dates)
            
            amounts = re.findall(amount_pattern, line)
            
            if dates_found and amounts:
                transaction = {
                    'date': dates_found[0],
                    'description': line,
                    'amount': amounts[-1],  # Usually the last amount is the transaction amount
                    'raw_line': line
                }
                transactions.append(transaction)
        
        return transactions
    
    def clean_amount(self, amount_str: str) -> float:
        """Clean and convert amount string to float."""
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[\$,]', '', amount_str.strip())
            
            # Handle negative amounts in parentheses
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            # Handle + prefix
            if cleaned.startswith('+'):
                cleaned = cleaned[1:]
            
            return float(cleaned)
        except (ValueError, AttributeError):
            self.logger.warning(f"Could not parse amount: {amount_str}")
            return 0.0
