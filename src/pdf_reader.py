"""
PDF Reader module for extracting text from bank statement PDFs.
Supports multiple PDF libraries for better compatibility.
"""

import os
import logging
from typing import List, Dict, Optional
import pdfplumber
import PyPDF2
import re
from datetime import datetime

class PDFReader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def extract_text_from_pdf(self, pdf_path: str, method: str = 'pdfplumber') -> str:
        """
        Extract text from PDF using specified method.
        
        Args:
            pdf_path: Path to the PDF file
            method: 'pdfplumber' or 'pypdf2'
            
        Returns:
            Extracted text as string
        """
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
    
    def process_multiple_pdfs(self, pdf_directory: str) -> Dict[str, str]:
        """
        Process multiple PDF files in a directory.
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            Dictionary mapping filename to extracted text
        """
        results = {}
        
        if not os.path.exists(pdf_directory):
            self.logger.error(f"Directory not found: {pdf_directory}")
            return results
        
        pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in {pdf_directory}")
            return results
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for filename in pdf_files:
            pdf_path = os.path.join(pdf_directory, filename)
            self.logger.info(f"Processing: {filename}")
            
            text = self.extract_text_from_pdf(pdf_path)
            if text:
                results[filename] = text
                self.logger.info(f"Successfully extracted text from {filename}")
            else:
                self.logger.warning(f"No text extracted from {filename}")
        
        return results
    
    def extract_transactions(self, text: str) -> List[Dict[str, str]]:
        """
        Extract transaction-like patterns from text.
        This is a basic implementation that can be customized based on bank format.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        lines = text.split('\n')
        
        # Common patterns for dates and amounts
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        amount_pattern = r'[-+]?\$?\d{1,3}(?:,\d{3})*\.?\d{0,2}'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for lines that contain both date and amount patterns
            dates = re.findall(date_pattern, line)
            amounts = re.findall(amount_pattern, line)
            
            if dates and amounts:
                transaction = {
                    'date': dates[0],
                    'description': line,
                    'amount': amounts[-1],  # Usually the last amount is the transaction amount
                    'raw_line': line
                }
                transactions.append(transaction)
        
        return transactions
    
    def clean_amount(self, amount_str: str) -> float:
        """
        Clean and convert amount string to float.
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Float value of amount
        """
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[\$,]', '', amount_str.strip())
            
            # Handle negative amounts in parentheses
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, AttributeError):
            self.logger.warning(f"Could not parse amount: {amount_str}")
            return 0.0
