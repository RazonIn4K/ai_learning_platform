# ai_learning_platform/utils/response_quality.py

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ResponseQualityChecker:
    """
    Checks the quality of model responses.
    
    This class provides methods to evaluate model responses for length,
    relevance, repetition, and other quality metrics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize ResponseQualityChecker with optional configuration.
        
        Args:
            config: Optional configuration dictionary with quality check settings
        """
        self.config = config or {}
        
        # Default quality thresholds
        self.min_length = self.config.get('min_length', 10)  # Min characters
        self.max_repetition = self.config.get('max_repetition', 0.3)  # Max repetition ratio
        
        # Default settings for relevance check
        self.relevance_threshold = self.config.get('relevance_threshold', 0.5)
    
    def check_quality(self, response: str, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Check the quality of a model response.
        
        Args:
            response: The response to check
            query: Optional original query for relevance checking
            
        Returns:
            Dictionary containing quality check results
        """
        if not response:
            return {
                'passes_checks': False,
                'issues': ['Empty response'],
                'length_check': False,
                'repetition_check': False,
                'relevance_check': False
            }
            
        # Check length
        length_check = len(response) >= self.min_length
        
        # Check repetition
        repetition_check = self._check_repetition(response)
        
        # Check relevance if query is provided
        relevance_check = True
        if query:
            relevance_check = self._check_relevance(response, query)
            
        # Compile results
        issues = []
        if not length_check:
            issues.append(f"Response too short (min: {self.min_length})")
        if not repetition_check:
            issues.append("Response contains too much repetition")
        if not relevance_check:
            issues.append("Response may not be relevant to the query")
            
        passes_checks = length_check and repetition_check and relevance_check
        
        return {
            'passes_checks': passes_checks,
            'issues': issues,
            'length_check': length_check,
            'repetition_check': repetition_check,
            'relevance_check': relevance_check
        }
    
    def _check_repetition(self, text: str) -> bool:
        """
        Check for excessive repetition in text.
        
        Args:
            text: The text to check
            
        Returns:
            True if repetition is below threshold, False otherwise
        """
        # Simple repetition check: look for repeated n-grams
        words = text.lower().split()
        if len(words) < 10:
            return True  # Skip check for very short responses
            
        # Check for repeated trigrams
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        unique_trigrams = set(trigrams)
        
        if not trigrams:
            return True
            
        # Calculate repetition ratio
        repetition_ratio = 1 - (len(unique_trigrams) / len(trigrams))
        
        return repetition_ratio <= self.max_repetition
    
    def _check_relevance(self, response: str, query: str) -> bool:
        """
        Check if response is relevant to query.
        
        Args:
            response: The response to check
            query: The original query
            
        Returns:
            True if response is relevant, False otherwise
        """
        # Simple relevance check: look for key terms from query in response
        # This is a basic implementation - a real system would use more sophisticated
        # semantic similarity checks
        
        # Extract key terms from query (non-stop words)
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        response_lower = response.lower()
        
        # Count how many key terms appear in response
        matches = sum(1 for word in query_words if word in response_lower)
        
        if not query_words:
            return True
            
        # Calculate relevance score
        relevance_score = matches / len(query_words)
        
        return relevance_score >= self.relevance_threshold