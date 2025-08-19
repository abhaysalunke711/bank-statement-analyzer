"""
Receipt processor module for extracting information from receipt images.
Uses OCR to extract text and machine learning to categorize items.
"""

import os
import cv2
import numpy as np
import easyocr
import pytesseract

# Set Tesseract path for Windows
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
import logging
from dataclasses import dataclass

@dataclass
class ReceiptItem:
    """Data class to store receipt item information."""
    name: str
    amount: float
    quantity: float = 1.0
    category: str = "Uncategorized"

@dataclass
class Receipt:
    """Data class to store receipt information."""
    date: datetime
    total_amount: float
    store_name: str
    items: List[ReceiptItem]
    image_path: str
    raw_text: str

class ReceiptProcessor:
    def __init__(self, output_dir: str = 'output'):
        """Initialize the receipt processor."""
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Initialize OCR reader
        try:
            self.reader = easyocr.Reader(['en'])
            self.logger.info("Successfully initialized EasyOCR")
        except Exception as e:
            self.logger.error(f"Error initializing EasyOCR: {e}")
            raise
        
        # Common patterns in receipts
        self.date_patterns = [
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{1,2}/\d{1,2}/\d{2}',  # M/D/YY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        ]
        
        self.amount_patterns = [
            r'\$?\d+\.\d{2}',  # $XX.XX or XX.XX
            r'\$\d+,\d{3}\.\d{2}',  # $X,XXX.XX
        ]
        
        # Common store names for better recognition
        self.store_patterns = [
            r'walmart', r'target', r'costco', r'safeway', r'kroger',
            r'whole foods', r'trader joe\'s', r'cvs', r'walgreens'
        ]

    def process_image(self, image_path: str) -> Receipt:
        """
        Process a receipt image and extract information.
        
        Args:
            image_path: Path to the receipt image file
            
        Returns:
            Receipt object containing extracted information
        """
        try:
            # Read and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text using OCR
            results = self.reader.readtext(processed_image)
            text_blocks = [text[1] for text in results]
            full_text = '\n'.join(text_blocks)
            
            # Extract key information
            date = self._extract_date(text_blocks)
            store_name = self._extract_store_name(text_blocks)
            total_amount = self._extract_total_amount(text_blocks)
            items = self._extract_items(text_blocks)
            
            # Create Receipt object
            receipt = Receipt(
                date=date,
                total_amount=total_amount,
                store_name=store_name,
                items=items,
                image_path=image_path,
                raw_text=full_text
            )
            
            return receipt
            
        except Exception as e:
            self.logger.error(f"Error processing receipt image {image_path}: {e}")
            raise

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 21, 11
            )
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh)
            
            return denoised
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}")
            raise

    def _extract_date(self, text_blocks: List[str]) -> datetime:
        """Extract date from receipt text."""
        for text in text_blocks:
            for pattern in self.date_patterns:
                match = re.search(pattern, text)
                if match:
                    date_str = match.group()
                    try:
                        # Try different date formats
                        for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%Y-%m-%d']:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
                    except Exception as e:
                        self.logger.warning(f"Could not parse date {date_str}: {e}")
        
        # If no date found, use current date
        self.logger.warning("No date found in receipt, using current date")
        return datetime.now()

    def _extract_store_name(self, text_blocks: List[str]) -> str:
        """Extract store name from receipt text."""
        # Check first few lines for store name
        for text in text_blocks[:5]:
            text_lower = text.lower()
            for pattern in self.store_patterns:
                if pattern in text_lower:
                    return text.strip()
        
        # If no known store found, return first line
        return text_blocks[0].strip() if text_blocks else "Unknown Store"

    def _extract_total_amount(self, text_blocks: List[str]) -> float:
        """Extract total amount from receipt text."""
        # Look for total amount patterns from bottom up
        for text in reversed(text_blocks):
            text_lower = text.lower()
            if 'total' in text_lower:
                for pattern in self.amount_patterns:
                    match = re.search(pattern, text)
                    if match:
                        amount_str = match.group().replace('$', '').replace(',', '')
                        try:
                            return float(amount_str)
                        except ValueError:
                            continue
        
        # If no total found, try to find the largest amount
        amounts = []
        for text in text_blocks:
            for pattern in self.amount_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    amount_str = match.group().replace('$', '').replace(',', '')
                    try:
                        amounts.append(float(amount_str))
                    except ValueError:
                        continue
        
        return max(amounts) if amounts else 0.0

    def _extract_items(self, text_blocks: List[str]) -> List[ReceiptItem]:
        """Extract individual items from receipt text."""
        items = []
        current_item = None
        
        for text in text_blocks:
            # Skip header and footer lines
            if any(word in text.lower() for word in ['total', 'subtotal', 'tax', 'date', 'store', 'receipt']):
                continue
            
            # Look for amount pattern
            amount_match = None
            for pattern in self.amount_patterns:
                match = re.search(pattern, text)
                if match:
                    amount_match = match
                    break
            
            if amount_match:
                # Extract amount
                amount_str = amount_match.group().replace('$', '').replace(',', '')
                try:
                    amount = float(amount_str)
                    
                    # Extract item name (text before amount)
                    name = text[:amount_match.start()].strip()
                    if name:
                        # Try to extract quantity if present (e.g., "2 x Item")
                        qty_match = re.match(r'^(\d+)\s*x\s*(.+)$', name)
                        if qty_match:
                            quantity = float(qty_match.group(1))
                            name = qty_match.group(2).strip()
                        else:
                            quantity = 1.0
                        
                        # Create item
                        item = ReceiptItem(
                            name=name,
                            amount=amount,
                            quantity=quantity,
                            category=self._categorize_item(name)
                        )
                        items.append(item)
                except ValueError:
                    continue
        
        return items

    def _categorize_item(self, item_name: str) -> str:
        """Categorize item based on name."""
        item_lower = item_name.lower()
        
        # Define category patterns
        categories = {
            'Groceries': ['milk', 'bread', 'cheese', 'meat', 'fish', 'vegetable', 'fruit'],
            'Electronics': ['battery', 'charger', 'cable', 'phone', 'computer'],
            'Clothing': ['shirt', 'pants', 'dress', 'shoes', 'jacket'],
            'Health': ['medicine', 'vitamin', 'pharmacy', 'prescription'],
            'Beauty': ['shampoo', 'soap', 'cosmetic', 'lotion'],
            'Home': ['cleaner', 'paper', 'towel', 'furniture'],
            'Food': ['burger', 'pizza', 'sandwich', 'drink', 'beverage'],
            'Transportation': ['gas', 'fuel', 'ticket', 'fare'],
        }
        
        # Check each category's patterns
        for category, patterns in categories.items():
            if any(pattern in item_lower for pattern in patterns):
                return category
        
        return "Miscellaneous"

    def save_to_excel(self, receipts: List[Receipt], excel_path: str):
        """Save receipt data to Excel file."""
        try:
            import pandas as pd
            
            # Create DataFrame for items
            items_data = []
            for receipt in receipts:
                for item in receipt.items:
                    items_data.append({
                        'Date': receipt.date,
                        'Store': receipt.store_name,
                        'Item': item.name,
                        'Category': item.category,
                        'Quantity': item.quantity,
                        'Amount': item.amount,
                        'Receipt Total': receipt.total_amount
                    })
            
            df = pd.DataFrame(items_data)
            
            # Save to Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Write items sheet
                df.to_excel(writer, sheet_name='Receipt Items', index=False)
                
                # Write summary sheet
                summary = df.pivot_table(
                    values='Amount',
                    index=['Category'],
                    columns=pd.Grouper(key='Date', freq='M'),
                    aggfunc='sum',
                    fill_value=0
                )
                summary.to_excel(writer, sheet_name='Category Summary')
            
            self.logger.info(f"Saved receipt data to {excel_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving receipt data to Excel: {e}")
            raise
