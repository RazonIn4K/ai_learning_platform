# ai_learning_platform/utils/json_extractor.py

import json
import re
import logging
from typing import Any, Dict, Optional, Union, List

logger = logging.getLogger(__name__)

def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON string from text.
    
    Args:
        text: The text to extract JSON from
        
    Returns:
        Extracted JSON string or None if no JSON found
    """
    if not text:
        return None
        
    # Try to find JSON object in text
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    
    if match:
        return match.group(1)
        
    # If no JSON object with braces found, try to find JSON array
    json_array_pattern = r'```(?:json)?\s*(\[.*?\])\s*```'
    match = re.search(json_array_pattern, text, re.DOTALL)
    
    if match:
        return match.group(1)
        
    # Look for JSON without code block markers
    json_pattern = r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})'
    match = re.search(json_pattern, text, re.DOTALL)
    
    if match:
        return match.group(1)
        
    # Look for JSON array without code block markers
    json_array_pattern = r'(\[(?:[^\[\]]|(?:\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\]))*\])'
    match = re.search(json_array_pattern, text, re.DOTALL)
    
    if match:
        return match.group(1)
        
    return None

def parse_json_safely(json_str: str) -> Optional[Union[Dict, List]]:
    """
    Parse JSON string safely, handling potential errors.
    
    Args:
        json_str: The JSON string to parse
        
    Returns:
        Parsed JSON object or None if parsing fails
    """
    if not json_str:
        return None
        
    try:
        # Try to parse JSON directly
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {str(e)}")
        
        try:
            # Try to fix common JSON issues
            
            # Fix single quotes
            fixed_str = json_str.replace("'", "\"")
            
            # Fix unquoted keys
            # This is a simplified fix - a real implementation would be more robust
            key_pattern = r'([{,]\s*)(\w+)(\s*:)'
            fixed_str = re.sub(key_pattern, r'\1"\2"\3', fixed_str)
            
            # Fix trailing commas
            fixed_str = re.sub(r',\s*([}\]])', r'\1', fixed_str)
            
            return json.loads(fixed_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON after fixing: {json_str}")
            return None

def ensure_json_response(text: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Ensure response contains valid JSON, optionally validating against schema.
    
    Args:
        text: The text to extract and validate JSON from
        schema: Optional JSON schema to validate against
        
    Returns:
        Dictionary containing result and extracted JSON
    """
    json_str = extract_json_from_text(text)
    
    if not json_str:
        return {
            'success': False,
            'error': 'No JSON found in response',
            'json': None
        }
        
    parsed_json = parse_json_safely(json_str)
    
    if not parsed_json:
        return {
            'success': False,
            'error': 'Failed to parse JSON',
            'json': None
        }
    
    # Schema validation (simple implementation)
    if schema and isinstance(parsed_json, dict):
        missing_keys = [key for key in schema if key not in parsed_json]
        if missing_keys:
            return {
                'success': False,
                'error': f'Missing required keys: {", ".join(missing_keys)}',
                'json': parsed_json
            }
    
    return {
        'success': True,
        'error': None,
        'json': parsed_json
    }