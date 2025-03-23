# ai_learning_platform/utils/content_filter.py

import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Set

logger = logging.getLogger(__name__)

class ContentFilter:
    """
    Filters inappropriate content from model responses.
    
    This class provides methods to detect and filter out inappropriate content
    based on keywords, regex patterns, and other filtering mechanisms.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize ContentFilter with optional configuration.
        
        Args:
            config: Optional configuration dictionary with filter settings
        """
        self.config = config or {}
        
        # Default blocked keywords - would be expanded in a real implementation
        self._blocked_keywords = self.config.get('blocked_keywords', [
            'profanity',  # Placeholder - real impl would have actual words
            'explicit',   # Placeholder - real impl would have actual words
        ])
        
        # Default blocked regex patterns
        self._blocked_patterns = self.config.get('blocked_patterns', [
            r'(?i)prompt\s*injection',  # Basic prompt injection detection
            r'(?i)system\s*prompt',     # System prompt reference detection
            r'(?i)ignore\s*previous\s*instructions',  # Instruction override attempt
        ])
        
        # Compile regex patterns for efficiency
        self._compiled_patterns = [re.compile(pattern) for pattern in self._blocked_patterns]
    
    def filter_content(self, content: str) -> Tuple[str, List[str], bool]:
        """
        Filter inappropriate content from model response.
        
        Args:
            content: The content to filter
            
        Returns:
            Tuple of (filtered_content, detected_issues, is_blocked)
            where is_blocked indicates if content should be fully blocked
        """
        if not content:
            return "", [], False
            
        detected_issues = []
        is_blocked = False
        filtered_content = content
        
        # Check for blocked keywords
        for keyword in self._blocked_keywords:
            if keyword.lower() in content.lower():
                detected_issues.append(f"Blocked keyword: {keyword}")
                # Replace keyword with asterisks
                filtered_content = re.sub(
                    re.escape(keyword),
                    '*' * len(keyword),
                    filtered_content,
                    flags=re.IGNORECASE
                )
        
        # Check for blocked patterns
        for i, pattern in enumerate(self._compiled_patterns):
            if pattern.search(content):
                detected_issues.append(f"Blocked pattern: {self._blocked_patterns[i]}")
                # Replace matched content with [FILTERED]
                filtered_content = pattern.sub('[FILTERED]', filtered_content)
        
        # Determine if content should be blocked entirely
        block_threshold = self.config.get('block_threshold', 3)
        is_blocked = len(detected_issues) >= block_threshold
        
        if detected_issues:
            logger.warning(f"Content filter detected {len(detected_issues)} issues: {', '.join(detected_issues)}")
            
        return filtered_content, detected_issues, is_blocked
    
    def is_safe(self, content: str) -> bool:
        """
        Check if content is safe (no filtering issues).
        
        Args:
            content: The content to check
            
        Returns:
            True if content is safe, False otherwise
        """
        _, issues, is_blocked = self.filter_content(content)
        return len(issues) == 0 and not is_blocked