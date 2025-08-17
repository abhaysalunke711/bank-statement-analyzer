"""
Income and Expense Analyzer for bank transactions.
Automatically detects and categorizes transactions as income or expenses
with intelligent rules and keyword matching.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TransactionType:
    """Data class for transaction type classification."""
    type: str  # 'income' or 'expense'
    confidence: float  # 0.0 to 1.0
    reason: str  # Why this classification was made

class IncomeExpenseAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Income indicators (keywords that suggest incoming money)
        self.income_keywords = {
            'salary': ['salary', 'payroll', 'wages', 'income', 'pay check', 'paycheck'],
            'deposit': ['deposit', 'direct deposit', 'ach credit', 'credit', 'transfer in'],
            'refund': ['refund', 'return', 'reimbursement', 'cashback', 'cash back'],
            'interest': ['interest', 'dividend', 'earnings'],
            'business': ['payment received', 'invoice payment', 'client payment'],
            'government': ['tax refund', 'stimulus', 'unemployment', 'social security'],
            'other': ['bonus', 'commission', 'freelance', 'consulting']
        }
        
        # Expense indicators (keywords that suggest outgoing money)
        self.expense_keywords = {
            'retail': ['purchase', 'walmart', 'target', 'amazon', 'costco', 'store'],
            'food': ['restaurant', 'cafe', 'food', 'dining', 'mcdonald', 'starbucks', 'pizza'],
            'transport': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'toll'],
            'utilities': ['electric', 'water', 'gas bill', 'internet', 'phone', 'cable'],
            'healthcare': ['hospital', 'pharmacy', 'doctor', 'medical', 'dental'],
            'banking': ['fee', 'charge', 'atm', 'overdraft', 'service charge'],
            'entertainment': ['movie', 'netflix', 'spotify', 'gaming', 'entertainment'],
            'housing': ['rent', 'mortgage', 'insurance', 'property'],
            'other': ['withdrawal', 'debit', 'payment', 'transfer out']
        }
        
        # Strong income patterns (regex)
        self.income_patterns = [
            r'direct dep|dd\s+|payroll|salary',
            r'ach credit|credit\s+\d+',
            r'deposit.*\+|\+.*deposit',
            r'refund|return|reimbursement',
            r'interest.*earned|dividend',
            r'transfer.*in|incoming'
        ]
        
        # Strong expense patterns (regex)
        self.expense_patterns = [
            r'debit purchase|pos purchase|card purchase',
            r'withdrawal|atm|cash advance',
            r'check.*\d+|ck\s+\d+',
            r'payment.*to|pay\s+to',
            r'fee|charge|penalty',
            r'transfer.*out|outgoing'
        ]
    
    def analyze_transaction(self, transaction: Dict) -> TransactionType:
        """
        Analyze a single transaction to determine if it's income or expense.
        
        Args:
            transaction: Dictionary containing transaction data
            
        Returns:
            TransactionType with classification and confidence
        """
        description = transaction.get('description', '').lower().strip()
        amount = self._clean_amount(transaction.get('amount', 0))
        
        # Start with amount-based classification
        if amount > 0:
            base_type = 'income'
            base_confidence = 0.6
        elif amount < 0:
            base_type = 'expense' 
            base_confidence = 0.6
        else:
            # Zero amount - try to classify by description
            base_type = 'expense'  # Default assumption
            base_confidence = 0.3
        
        # Enhance classification with description analysis
        pattern_result = self._analyze_patterns(description)
        keyword_result = self._analyze_keywords(description)
        
        # Combine all analyses
        final_type, final_confidence, reason = self._combine_analyses(
            base_type, base_confidence, pattern_result, keyword_result, amount
        )
        
        return TransactionType(
            type=final_type,
            confidence=final_confidence,
            reason=reason
        )
    
    def _analyze_patterns(self, description: str) -> Tuple[Optional[str], float, str]:
        """Analyze description using regex patterns."""
        # Check income patterns
        for pattern in self.income_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return 'income', 0.9, f'Income pattern: {pattern}'
        
        # Check expense patterns  
        for pattern in self.expense_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                return 'expense', 0.9, f'Expense pattern: {pattern}'
        
        return None, 0.0, 'No pattern match'
    
    def _analyze_keywords(self, description: str) -> Tuple[Optional[str], float, str]:
        """Analyze description using keyword matching."""
        income_score = 0
        expense_score = 0
        matched_keywords = []
        
        # Check income keywords
        for category, keywords in self.income_keywords.items():
            for keyword in keywords:
                if keyword in description:
                    income_score += 1
                    matched_keywords.append(f'income:{keyword}')
        
        # Check expense keywords
        for category, keywords in self.expense_keywords.items():
            for keyword in keywords:
                if keyword in description:
                    expense_score += 1
                    matched_keywords.append(f'expense:{keyword}')
        
        if income_score > expense_score:
            confidence = min(0.8, 0.5 + (income_score - expense_score) * 0.1)
            return 'income', confidence, f'Keywords: {", ".join(matched_keywords[:3])}'
        elif expense_score > income_score:
            confidence = min(0.8, 0.5 + (expense_score - income_score) * 0.1)
            return 'expense', confidence, f'Keywords: {", ".join(matched_keywords[:3])}'
        
        return None, 0.0, 'No keyword match'
    
    def _combine_analyses(self, base_type: str, base_confidence: float, 
                         pattern_result: Tuple, keyword_result: Tuple, amount: float) -> Tuple[str, float, str]:
        """Combine all analysis results into final classification."""
        pattern_type, pattern_conf, pattern_reason = pattern_result
        keyword_type, keyword_conf, keyword_reason = keyword_result
        
        # Pattern analysis has highest priority
        if pattern_type and pattern_conf >= 0.8:
            return pattern_type, pattern_conf, pattern_reason
        
        # Keyword analysis has medium priority
        if keyword_type and keyword_conf >= 0.6:
            return keyword_type, keyword_conf, keyword_reason
        
        # Use amount-based classification with some keyword influence
        if keyword_type and keyword_type != base_type and keyword_conf >= 0.4:
            # Keywords suggest different type - reduce confidence
            final_confidence = max(0.3, base_confidence - 0.2)
            reason = f'Amount-based ({base_type}) but {keyword_reason}'
        else:
            final_confidence = base_confidence
            reason = f'Amount-based classification (${amount:.2f})'
        
        return base_type, final_confidence, reason
    
    def classify_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """
        Classify a list of transactions as income or expenses.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of transactions with added 'transaction_type', 'type_confidence', and 'type_reason' fields
        """
        classified_transactions = []
        
        for transaction in transactions:
            classification = self.analyze_transaction(transaction)
            
            # Add classification to transaction
            enhanced_transaction = transaction.copy()
            enhanced_transaction['transaction_type'] = classification.type
            enhanced_transaction['type_confidence'] = classification.confidence
            enhanced_transaction['type_reason'] = classification.reason
            
            classified_transactions.append(enhanced_transaction)
        
        return classified_transactions
    
    def get_income_expense_summary(self, transactions: List[Dict]) -> Dict:
        """
        Generate summary statistics for income and expenses.
        
        Args:
            transactions: List of classified transactions
            
        Returns:
            Dictionary with income/expense statistics
        """
        income_transactions = [t for t in transactions if t.get('transaction_type') == 'income']
        expense_transactions = [t for t in transactions if t.get('transaction_type') == 'expense']
        
        total_income = sum(abs(self._clean_amount(t.get('amount', 0))) for t in income_transactions)
        total_expenses = sum(abs(self._clean_amount(t.get('amount', 0))) for t in expense_transactions)
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_amount': total_income - total_expenses,
            'income_count': len(income_transactions),
            'expense_count': len(expense_transactions),
            'income_avg': total_income / len(income_transactions) if income_transactions else 0,
            'expense_avg': total_expenses / len(expense_transactions) if expense_transactions else 0,
            'income_transactions': income_transactions,
            'expense_transactions': expense_transactions
        }
    
    def _clean_amount(self, amount_str) -> float:
        """Convert amount string to float."""
        try:
            if isinstance(amount_str, (int, float)):
                return float(amount_str)
            
            # Remove currency symbols and commas
            cleaned = str(amount_str).replace('$', '').replace(',', '').strip()
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            # Handle + prefix
            if cleaned.startswith('+'):
                cleaned = cleaned[1:]
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
