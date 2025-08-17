"""
Keyword matching module for categorizing bank transactions.
Supports fuzzy matching and configurable keyword categories.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

class KeywordMatcher:
    def __init__(self, keywords_config_path: str = None):
        self.logger = logging.getLogger(__name__)
        self.keywords = {}
        self.fuzzy_threshold = 0.8  # Similarity threshold for fuzzy matching
        
        if keywords_config_path:
            self.load_keywords(keywords_config_path)
    
    def load_keywords(self, config_path: str) -> None:
        """
        Load keywords configuration from JSON file.
        
        Args:
            config_path: Path to keywords configuration file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.keywords = json.load(f)
            self.logger.info(f"Loaded keywords from {config_path}")
            self.logger.info(f"Categories: {list(self.keywords.keys())}")
        except FileNotFoundError:
            self.logger.error(f"Keywords file not found: {config_path}")
            self.keywords = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in keywords file: {e}")
            self.keywords = {}
    
    def set_keywords(self, keywords: Dict[str, List[str]]) -> None:
        """
        Set keywords dictionary programmatically.
        
        Args:
            keywords: Dictionary with category names as keys and keyword lists as values
        """
        self.keywords = keywords
        self.logger.info(f"Set keywords for categories: {list(keywords.keys())}")
    
    def match_transaction(self, description: str, amount: float = None) -> Optional[str]:
        """
        Match a transaction description against configured keywords.
        
        Args:
            description: Transaction description text
            amount: Transaction amount (optional, for amount-based rules)
            
        Returns:
            Category name if match found, None otherwise
        """
        description_lower = description.lower().strip()
        
        # First try exact matching
        exact_match = self._exact_match(description_lower)
        if exact_match:
            return exact_match
        
        # Then try fuzzy matching
        fuzzy_match = self._fuzzy_match(description_lower)
        if fuzzy_match:
            return fuzzy_match
        
        # Finally try regex matching
        regex_match = self._regex_match(description_lower)
        if regex_match:
            return regex_match
        
        return None
    
    def _exact_match(self, description: str) -> Optional[str]:
        """Find exact keyword matches in description."""
        for category, keywords in self.keywords.items():
            if isinstance(keywords, dict):
                keyword_list = keywords.get('exact', [])
            else:
                keyword_list = keywords
            
            for keyword in keyword_list:
                if keyword.lower() in description:
                    self.logger.debug(f"Exact match: '{keyword}' -> {category}")
                    return category
        
        return None
    
    def _fuzzy_match(self, description: str) -> Optional[str]:
        """Find fuzzy matches using similarity scoring."""
        best_match = None
        best_score = 0
        
        for category, keywords in self.keywords.items():
            if isinstance(keywords, dict):
                keyword_list = keywords.get('fuzzy', [])
            else:
                continue  # Skip if not configured for fuzzy matching
            
            for keyword in keyword_list:
                # Calculate similarity
                similarity = SequenceMatcher(None, keyword.lower(), description).ratio()
                
                # Also check if keyword is a substring
                if keyword.lower() in description:
                    similarity = max(similarity, 0.9)
                
                if similarity > self.fuzzy_threshold and similarity > best_score:
                    best_score = similarity
                    best_match = category
                    self.logger.debug(f"Fuzzy match: '{keyword}' -> {category} (score: {similarity:.2f})")
        
        return best_match
    
    def _regex_match(self, description: str) -> Optional[str]:
        """Find matches using regular expressions."""
        for category, keywords in self.keywords.items():
            if isinstance(keywords, dict):
                regex_patterns = keywords.get('regex', [])
            else:
                continue  # Skip if not configured for regex matching
            
            for pattern in regex_patterns:
                try:
                    if re.search(pattern, description, re.IGNORECASE):
                        self.logger.debug(f"Regex match: '{pattern}' -> {category}")
                        return category
                except re.error as e:
                    self.logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        
        return None
    
    def batch_categorize(self, transactions: List[Dict]) -> List[Dict]:
        """
        Categorize a batch of transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of transactions with added 'category' field
        """
        categorized = []
        
        for transaction in transactions:
            description = transaction.get('description', '')
            amount = transaction.get('amount', 0)
            
            # Convert amount to float if it's a string
            if isinstance(amount, str):
                try:
                    amount = float(re.sub(r'[\$,]', '', amount))
                except (ValueError, AttributeError):
                    amount = 0
            
            category = self.match_transaction(description, amount)
            
            # Create new transaction dict with category
            categorized_transaction = transaction.copy()
            categorized_transaction['category'] = category or 'Uncategorized'
            categorized.append(categorized_transaction)
        
        return categorized
    
    def get_statistics(self, transactions: List[Dict]) -> Dict[str, int]:
        """
        Get categorization statistics.
        
        Args:
            transactions: List of categorized transactions
            
        Returns:
            Dictionary with category counts
        """
        stats = {}
        for transaction in transactions:
            category = transaction.get('category', 'Uncategorized')
            stats[category] = stats.get(category, 0) + 1
        
        return stats
    
    def export_keywords_template(self, output_path: str) -> None:
        """
        Export a template keywords configuration file.
        
        Args:
            output_path: Path where to save the template
        """
        template = {
            "Food & Dining": {
                "exact": ["restaurant", "cafe", "pizza", "mcdonald", "starbucks", "subway"],
                "fuzzy": ["dining", "food", "lunch", "dinner"],
                "regex": [r".*restaurant.*", r".*cafe.*"]
            },
            "Transportation": {
                "exact": ["gas", "fuel", "uber", "lyft", "taxi", "parking"],
                "fuzzy": ["transport", "travel"],
                "regex": [r".*gas.*station.*", r".*parking.*"]
            },
            "Shopping": {
                "exact": ["amazon", "walmart", "target", "costco", "mall"],
                "fuzzy": ["shopping", "store"],
                "regex": [r".*shop.*", r".*store.*"]
            },
            "Utilities": {
                "exact": ["electric", "water", "gas bill", "internet", "phone"],
                "fuzzy": ["utility", "bill"],
                "regex": [r".*electric.*company.*", r".*water.*dept.*"]
            },
            "Healthcare": {
                "exact": ["hospital", "pharmacy", "doctor", "medical"],
                "fuzzy": ["health", "medical"],
                "regex": [r".*medical.*", r".*pharmacy.*"]
            }
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Keywords template exported to {output_path}")
        except Exception as e:
            self.logger.error(f"Error exporting template: {e}")
