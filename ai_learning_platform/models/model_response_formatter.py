# ai_learning_platform/models/model_response_formatter.py

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
class ModelResponseFormatter:
    """
    Standardizes responses from different model providers.
    
    This class converts provider-specific model responses into a standardized
    format for consistent handling across the platform.
    
    Supported providers:
    - Anthropic (Claude)
    - OpenAI
    - Google (Gemini)
    - OpenRouter
    - CAMEL
    """
    
    @staticmethod
    def standardize_response(
        provider: str,
        model_name: str,
        raw_response: Any,
        token_usage: Optional[Dict[str, int]] = None,
        error: Optional[Exception] = None,
        fallback_used: bool = False
    ) -> Dict[str, Any]:
        """
        Convert provider-specific response to standard format.
        
        Args:
            provider: The model provider (e.g., 'anthropic', 'openai')
            model_name: The name of the model used
            raw_response: The raw response from the model
            token_usage: Optional token usage statistics
            error: Optional error if one occurred
            fallback_used: Whether a fallback model was used
            
        Returns:
            Standardized response dictionary
        """
        formatter_method = getattr(
            ModelResponseFormatter, 
            f"_format_{provider.lower()}_response", 
            ModelResponseFormatter._format_generic_response
        )
        
        try:
            return formatter_method(
                model_name,
                raw_response,
                token_usage,
                error,
                fallback_used
            )
        except Exception as e:
            logger.error(f"Error formatting {provider} response: {str(e)}")
            # Return generic response in case of formatting error
            return ModelResponseFormatter._format_generic_response(
                model_name,
                raw_response,
                token_usage,
                error,
                fallback_used
            )
    
    @staticmethod
    def _format_anthropic_response(
        model_name: str,
        raw_response: Any,
        token_usage: Optional[Dict[str, int]] = None,
        error: Optional[Exception] = None,
        fallback_used: bool = False
    ) -> Dict[str, Any]:
        """
        Format Anthropic Claude response.
        
        Args:
            model_name: The name of the model used
            raw_response: The raw response from Claude
            token_usage: Optional token usage statistics
            error: Optional error if one occurred
            fallback_used: Whether a fallback model was used
            
        Returns:
            Standardized response dictionary
        """
        try:
            # For successful response
            if error is None and raw_response:
                # Extract content from Anthropic response
                content = ""
                if hasattr(raw_response, 'content') and raw_response.content:
                    # For Claude API v1, content[0].text contains the response
                    if isinstance(raw_response.content, list) and len(raw_response.content) > 0:
                        content = raw_response.content[0].text
                    else:
                        content = str(raw_response.content)
                elif hasattr(raw_response, 'completion'):
                    # For Claude API v0
                    content = raw_response.completion
                else:
                    content = str(raw_response)
                
                # Get token usage if available
                usage = token_usage or {}
                if hasattr(raw_response, 'usage'):
                    usage = {
                        'prompt_tokens': getattr(raw_response.usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(raw_response.usage, 'completion_tokens', 0),
                        'total_tokens': getattr(raw_response.usage, 'total_tokens', 0)
                    }
                
                return {
                    'content': content,
                    'provider': 'anthropic',
                    'model': model_name,
                    'raw_response': raw_response,
                    'token_usage': usage,
                    'error': None,
                    'fallback_used': fallback_used
                }
            
            # For error response
            return {
                'content': None,
                'provider': 'anthropic',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': str(error) if error else "Unknown error",
                'fallback_used': fallback_used
            }
            
        except Exception as e:
            logger.error(f"Error processing Anthropic response: {str(e)}")
            return {
                'content': None, 
                'provider': 'anthropic',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': f"Response formatting error: {str(e)}",
                'fallback_used': fallback_used
            }

    @staticmethod
    def _format_openai_response(
        model_name: str,
        raw_response: Any,
        token_usage: Optional[Dict[str, int]] = None,
        error: Optional[Exception] = None,
        fallback_used: bool = False
    ) -> Dict[str, Any]:
        """
        Format OpenAI response.

        Args:
            model_name: The name of the model used
            raw_response: The raw response from OpenAI
            token_usage: Optional token usage statistics
            error: Optional error if one occurred
            fallback_used: Whether a fallback model was used

        Returns:
            Standardized response dictionary
        """
        try:
            # For successful response
            if error is None and raw_response:
                # Extract content from OpenAI response
                content = ""
                if hasattr(raw_response, 'choices') and raw_response.choices:
                    # Get the first choice
                    choice = raw_response.choices[0]

                    # Extract message content
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        content = choice.message.content
                    # Fallback for older API versions or different response formats
                    elif hasattr(choice, 'text'):
                        content = choice.text
                    else:
                        content = str(choice)
                else:
                    content = str(raw_response)

                # Get token usage if available
                usage = token_usage or {}
                if hasattr(raw_response, 'usage'):
                    usage = {
                        'prompt_tokens': getattr(raw_response.usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(raw_response.usage, 'completion_tokens', 0),
                        'total_tokens': getattr(raw_response.usage, 'total_tokens', 0)
                    }

                return {
                    'content': content,
                    'provider': 'openai',
                    'model': model_name,
                    'raw_response': raw_response,
                    'token_usage': usage,
                    'error': None,
                    'fallback_used': fallback_used
                }

            # For error response
            return {
                'content': None,
                'provider': 'openai',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': str(error) if error else "Unknown error",
                'fallback_used': fallback_used
            }

        except Exception as e:
            logger.error(f"Error processing OpenAI response: {str(e)}")
            return {
                'content': None,
                'provider': 'openai',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': f"Response formatting error: {str(e)}",
                'fallback_used': fallback_used
            }

    @staticmethod
    def _format_gemini_response(
        model_name: str,
        raw_response: Any,
        token_usage: Optional[Dict[str, int]] = None,
        error: Optional[Exception] = None,
        fallback_used: bool = False
    ) -> Dict[str, Any]:
        """
        Format Google Gemini response.
        
        Args:
            model_name: The name of the model used
            raw_response: The raw response from Gemini
            token_usage: Optional token usage statistics
            error: Optional error if one occurred
            fallback_used: Whether a fallback model was used
            
        Returns:
            Standardized response dictionary
        """
        try:
            # For successful response
            if error is None and raw_response:
                # Extract content from Gemini response
                content = ""
                if hasattr(raw_response, 'text'):
                    # For Gemini API
                    content = raw_response.text
                elif hasattr(raw_response, 'candidates') and raw_response.candidates:
                    # Alternative response format
                    content = raw_response.candidates[0].content.parts[0].text
                else:
                    content = str(raw_response)
                
                # Get token usage if available
                usage = token_usage or {}
                if hasattr(raw_response, 'usage_metadata'):
                    usage = {
                        'prompt_tokens': getattr(raw_response.usage_metadata, 'prompt_token_count', 0),
                        'completion_tokens': getattr(raw_response.usage_metadata, 'candidates_token_count', 0),
                        'total_tokens': getattr(raw_response.usage_metadata, 'total_token_count', 0)
                    }
                
                return {
                    'content': content,
                    'provider': 'google',
                    'model': model_name,
                    'raw_response': raw_response,
                    'token_usage': usage,
                    'error': None,
                    'fallback_used': fallback_used
                }
            
            # For error response
            return {
                'content': None,
                'provider': 'google',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': str(error) if error else "Unknown error",
                'fallback_used': fallback_used
            }
            
        except Exception as e:
            logger.error(f"Error processing Gemini response: {str(e)}")
            return {
                'content': None, 
                'provider': 'google',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': f"Response formatting error: {str(e)}",
                'fallback_used': fallback_used
            }

    @staticmethod
    def _format_openrouter_response(
        model_name: str,
        raw_response: Any,
        token_usage: Optional[Dict[str, int]] = None,
        error: Optional[Exception] = None,
        fallback_used: bool = False
    ) -> Dict[str, Any]:
        """
        Format OpenRouter response.
        
        Args:
            model_name: The name of the model used
            raw_response: The raw response from OpenRouter
            token_usage: Optional token usage statistics
            error: Optional error if one occurred
            fallback_used: Whether a fallback model was used
            
        Returns:
            Standardized response dictionary
        """
        try:
            # For successful response
            if error is None and raw_response:
                # Extract content from OpenRouter response
                content = ""
                if hasattr(raw_response, 'choices') and raw_response.choices:
                    # OpenRouter uses OpenAI-compatible format
                    if hasattr(raw_response.choices[0], 'message'):
                        content = raw_response.choices[0].message.content
                    elif hasattr(raw_response.choices[0], 'text'):
                        content = raw_response.choices[0].text
                    else:
                        content = str(raw_response.choices[0])
                else:
                    content = str(raw_response)
                
                # Get token usage if available
                usage = token_usage or {}
                if hasattr(raw_response, 'usage'):
                    usage = {
                        'prompt_tokens': getattr(raw_response.usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(raw_response.usage, 'completion_tokens', 0),
                        'total_tokens': getattr(raw_response.usage, 'total_tokens', 0)
                    }
                
                # Get actual model used (OpenRouter provides this info)
                actual_model = model_name
                if hasattr(raw_response, 'model'):
                    actual_model = raw_response.model
                    
                # Get routing information if available
                routing_info = {}
                if hasattr(raw_response, 'routing'):
                    routing_info = {
                        'provider': getattr(raw_response.routing, 'provider', None),
                        'original_model': getattr(raw_response.routing, 'original_model', None)
                    }
                
                return {
                    'content': content,
                    'provider': 'openrouter',
                    'model': actual_model,
                    'raw_response': raw_response,
                    'token_usage': usage,
                    'error': None,
                    'fallback_used': fallback_used,
                    'routing_info': routing_info
                }
            
            # For error response
            return {
                'content': None,
                'provider': 'openrouter',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': str(error) if error else "Unknown error",
                'fallback_used': fallback_used
            }
            
        except Exception as e:
            logger.error(f"Error processing OpenRouter response: {str(e)}")
            return {
                'content': None, 
                'provider': 'openrouter',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': f"Response formatting error: {str(e)}",
                'fallback_used': fallback_used
            }

    @staticmethod
    def _format_camel_response(
        model_name: str,
        raw_response: Any,
        token_usage: Optional[Dict[str, int]] = None,
        error: Optional[Exception] = None,
        fallback_used: bool = False
    ) -> Dict[str, Any]:
        """
        Format CAMeL-AI response.
        
        Args:
            model_name: The name of the model used
            raw_response: The raw response from CAMeL-AI
            token_usage: Optional token usage statistics
            error: Optional error if one occurred
            fallback_used: Whether a fallback model was used
            
        Returns:
            Standardized response dictionary
        """
        try:
            # For successful response
            if error is None and raw_response:
                # Extract content from CAMeL-AI response
                content = ""
                if hasattr(raw_response, 'text'):
                    content = raw_response.text
                elif hasattr(raw_response, 'generated_text'):
                    content = raw_response.generated_text
                elif isinstance(raw_response, dict) and 'text' in raw_response:
                    content = raw_response['text']
                elif isinstance(raw_response, dict) and 'generated_text' in raw_response:
                    content = raw_response['generated_text']
                else:
                    content = str(raw_response)
                
                # Extract role information if available
                role_info = {}
                if hasattr(raw_response, 'role'):
                    role_info['role'] = raw_response.role
                elif hasattr(raw_response, 'system_name'):
                    role_info['role'] = raw_response.system_name
                elif isinstance(raw_response, dict):
                    role_info['role'] = raw_response.get('role', raw_response.get('system_name'))

                # Get token usage if available
                usage = token_usage or {}
                if hasattr(raw_response, 'usage'):
                    usage = {
                        'prompt_tokens': getattr(raw_response.usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(raw_response.usage, 'completion_tokens', 0),
                        'total_tokens': getattr(raw_response.usage, 'total_tokens', 0)
                    }
                elif isinstance(raw_response, dict) and 'usage' in raw_response:
                    usage = {
                        'prompt_tokens': raw_response['usage'].get('prompt_tokens', 0),
                        'completion_tokens': raw_response['usage'].get('completion_tokens', 0),
                        'total_tokens': raw_response['usage'].get('total_tokens', 0)
                    }
                
                return {
                    'content': content,
                    'provider': 'camel',
                    'model': model_name,
                    'raw_response': raw_response,
                    'token_usage': usage,
                    'error': None,
                    'fallback_used': fallback_used,
                    'role_info': role_info
                }
            
            # For error response
            return {
                'content': None,
                'provider': 'camel',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': str(error) if error else "Unknown error",
                'fallback_used': fallback_used,
                'role_info': {}
            }
            
        except Exception as e:
            logger.error(f"Error processing CAMeL-AI response: {str(e)}")
            return {
                'content': None, 
                'provider': 'camel',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': f"Response formatting error: {str(e)}",
                'fallback_used': fallback_used,
                'role_info': {}
            }

    @staticmethod
    def _format_gemini_response(
        model_name: str,
        raw_response: Any,
        token_usage: Optional[Dict[str, int]] = None,
        error: Optional[Exception] = None,
        fallback_used: bool = False
    ) -> Dict[str, Any]:
        """
        Format Google Gemini response.
        
        Args:
            model_name: The name of the model used
            raw_response: The raw response from Gemini
            token_usage: Optional token usage statistics
            error: Optional error if one occurred
            fallback_used: Whether a fallback model was used
            
        Returns:
            Standardized response dictionary
        """
        try:
            # For successful response
            if error is None and raw_response:
                # Extract content from Gemini response
                content = ""
                if hasattr(raw_response, 'text'):
                    content = raw_response.text
                elif hasattr(raw_response, 'parts') and raw_response.parts:
                    content = ''.join([part.text for part in raw_response.parts if hasattr(part, 'text')])
                elif isinstance(raw_response, dict) and 'text' in raw_response:
                    content = raw_response['text']
                elif isinstance(raw_response, dict) and 'content' in raw_response:
                    if isinstance(raw_response['content'], list):
                        content = ''.join([part.get('text', '') for part in raw_response['content'] if 'text' in part])
                    else:
                        content = raw_response['content']
                else:
                    content = str(raw_response)
                
                # Extract usage information if available
                usage = token_usage or {}
                if hasattr(raw_response, 'usage'):
                    usage = {
                        'prompt_tokens': getattr(raw_response.usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(raw_response.usage, 'completion_tokens', 0),
                        'total_tokens': getattr(raw_response.usage, 'total_tokens', 0)
                    }
                
                return {
                    'content': content,
                    'provider': 'google',
                    'model': model_name,
                    'raw_response': raw_response,
                    'token_usage': usage,
                    'error': None,
                    'fallback_used': fallback_used
                }
            
            # For error response
            return {
                'content': None,
                'provider': 'google',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': str(error) if error else "Unknown error",
                'fallback_used': fallback_used
            }
            
        except Exception as e:
            logger.error(f"Error processing Gemini response: {str(e)}")
            return {
                'content': None,
                'provider': 'google',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': f"Response formatting error: {str(e)}",
                'fallback_used': fallback_used
            }

    @staticmethod
    def _format_openrouter_response(
        model_name: str,
        raw_response: Any,
        token_usage: Optional[Dict[str, int]] = None,
        error: Optional[Exception] = None,
        fallback_used: bool = False
    ) -> Dict[str, Any]:
        """
        Format OpenRouter response.
        
        Args:
            model_name: The name of the model used
            raw_response: The raw response from OpenRouter
            token_usage: Optional token usage statistics
            error: Optional error if one occurred
            fallback_used: Whether a fallback model was used
            
        Returns:
            Standardized response dictionary
        """
        try:
            # For successful response
            if error is None and raw_response:
                # Extract content from OpenRouter response (OpenRouter uses OpenAI-compatible format)
                content = ""
                if hasattr(raw_response, 'choices') and raw_response.choices:
                    if hasattr(raw_response.choices[0], 'message') and hasattr(raw_response.choices[0].message, 'content'):
                        content = raw_response.choices[0].message.content
                    elif hasattr(raw_response.choices[0], 'text'):
                        content = raw_response.choices[0].text
                elif isinstance(raw_response, dict) and 'choices' in raw_response and raw_response['choices']:
                    if 'message' in raw_response['choices'][0] and 'content' in raw_response['choices'][0]['message']:
                        content = raw_response['choices'][0]['message']['content']
                    elif 'text' in raw_response['choices'][0]:
                        content = raw_response['choices'][0]['text']
                else:
                    content = str(raw_response)
                
                # Extract usage information
                usage = token_usage or {}
                if hasattr(raw_response, 'usage'):
                    usage = {
                        'prompt_tokens': getattr(raw_response.usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(raw_response.usage, 'completion_tokens', 0),
                        'total_tokens': getattr(raw_response.usage, 'total_tokens', 0)
                    }
                elif isinstance(raw_response, dict) and 'usage' in raw_response:
                    usage = {
                        'prompt_tokens': raw_response['usage'].get('prompt_tokens', 0),
                        'completion_tokens': raw_response['usage'].get('completion_tokens', 0),
                        'total_tokens': raw_response['usage'].get('total_tokens', 0)
                    }
                
                # Extract model info if available (OpenRouter provides model info in response)
                model_info = {}
                if hasattr(raw_response, 'model') and raw_response.model != model_name:
                    model_info['actual_model'] = raw_response.model
                elif isinstance(raw_response, dict) and 'model' in raw_response and raw_response['model'] != model_name:
                    model_info['actual_model'] = raw_response['model']
                
                return {
                    'content': content,
                    'provider': 'openrouter',
                    'model': model_name,
                    'raw_response': raw_response,
                    'token_usage': usage,
                    'error': None,
                    'fallback_used': fallback_used,
                    'model_info': model_info if model_info else None
                }
            
            # For error response
            return {
                'content': None,
                'provider': 'openrouter',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': str(error) if error else "Unknown error",
                'fallback_used': fallback_used
            }
            
        except Exception as e:
            logger.error(f"Error processing OpenRouter response: {str(e)}")
            return {
                'content': None,
                'provider': 'openrouter',
                'model': model_name,
                'raw_response': raw_response,
                'token_usage': token_usage or {},
                'error': f"Response formatting error: {str(e)}",
                'fallback_used': fallback_used
            }
            
    @staticmethod
    def extract_reasoning(response: Dict[str, Any]) -> Optional[str]:
        """
        Extract reasoning from a model response if available.
        
        Args:
            response: The standardized response dictionary
            
        Returns:
            Extracted reasoning as a string, or None if not available
        """
        # This is a placeholder - will be implemented in future phases
        # For now, return None to indicate no reasoning extracted
        return None
    
    @staticmethod
    def validate_consistency(response: Dict[str, Any]) -> bool:
        """
        Validate the consistency of a model response.
        
        Args:
            response: The standardized response dictionary
            
        Returns:
            True if response is consistent, False otherwise
        """
        # This is a placeholder - will be implemented in future phases
        # For now, return True to indicate all responses are valid
        return True
