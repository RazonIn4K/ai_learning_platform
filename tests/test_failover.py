# tests/test_failover.py

import unittest
import asyncio
import logging
from unittest.mock import patch, MagicMock

from ai_learning_platform.models.enhanced_model_manager import EnhancedModelManager, ModelProvider
from ai_learning_platform.utils.exceptions import RateLimitError, TokenLimitError, ModelError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFailover(unittest.TestCase):
    """Test failover between providers."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock config with fallbacks
        self.mock_config = {
            'api_keys': {
                'anthropic': 'mock_anthropic_key',
                'openai': 'mock_openai_key',
                'google': 'mock_google_key',
                'openrouter': 'mock_openrouter_key'
            },
            'model_parameters': {
                'provider': 'anthropic',
                'model_name': 'claude-3-opus-20240229',
                'temperature': 0.7,
                'max_tokens': 3000
            },
            'fallback_models': [
                {
                    'provider': 'google',
                    'model_name': 'gemini-pro',
                    'model_params': {
                        'temperature': 0.6,
                        'max_tokens': 2500
                    }
                },
                {
                    'provider': 'openrouter',
                    'model_name': 'mistralai/mistral-medium',
                    'model_params': {
                        'temperature': 0.6,
                        'max_tokens': 2500
                    }
                },
                {
                    'provider': 'openai',
                    'model_name': 'gpt-4',
                    'model_params': {
                        'temperature': 0.5,
                        'max_tokens': 2000
                    }
                }
            ],
            'rate_limits': {
                'anthropic': {'requests_per_minute': 10},
                'openai': {'requests_per_minute': 20},
                'google': {'requests_per_minute': 60},
                'openrouter': {'requests_per_minute': 30}
            }
        }
        
        # Initialize model manager with mocked config
        self.model_manager = EnhancedModelManager()
        self.model_manager.config = self.mock_config
        
        # Mock clients
        self.model_manager.clients = {
            ModelProvider.ANTHROPIC: MagicMock(),
            ModelProvider.OPENAI: MagicMock(),
            ModelProvider.GOOGLE: MagicMock(),
            ModelProvider.OPENROUTER: MagicMock()
        }
    
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_anthropic_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openai_response')
    async def test_rate_limit_failover(self, mock_openai_formatter, mock_anthropic_formatter):
        """Test failover when Anthropic rate limit is hit."""
        # Mock Anthropic to raise RateLimitError
        self.model_manager._generate_anthropic_response = MagicMock(side_effect=RateLimitError("Rate limit exceeded"))
        
        # Mock OpenAI response
        openai_response = MagicMock()
        self.model_manager._generate_openai_response = MagicMock(return_value=openai_response)
        
        # Mock formatters
        mock_openai_formatter.return_value = {
            'content': 'This is a response from OpenAI',
            'provider': 'openai',
            'model': 'gpt-4',
            'raw_response': openai_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        mock_anthropic_formatter.return_value = {  # Add mock return for anthropic
            'content': 'This is a response from Anthropic',
            'provider': 'anthropic',
            'model': 'claude-3-opus-20240229',
            'raw_response': MagicMock(),
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        
        # Test generate_response
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='anthropic',
            model_name='claude-3-opus-20240229'
        )
        
        # Verify fallback was used
        self.assertEqual(response['provider'], 'google')
        self.assertEqual(response['model'], 'gemini-pro')
        self.assertTrue(response.get('fallback_used', False))
        # self.assertEqual(response['content'], 'This is a response from OpenAI') #Content will be different
        
        # Verify Anthropic was called and failed
        self.model_manager._generate_anthropic_response.assert_called_once()
        
        # Verify Gemini was called as fallback
        self.model_manager._generate_gemini_response.assert_called_once()
    
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_anthropic_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openai_response')
    async def test_token_limit_failover(self, mock_openai_formatter, mock_anthropic_formatter):
        """Test failover when Anthropic token limit is exceeded."""
        # Mock Anthropic to raise TokenLimitError
        self.model_manager._generate_anthropic_response = MagicMock(side_effect=TokenLimitError("Token limit exceeded"))
        
        # Mock OpenAI response
        openai_response = MagicMock()
        self.model_manager._generate_openai_response = MagicMock(return_value=openai_response)
        
        # Mock formatters
        mock_openai_formatter.return_value = {
            'content': 'This is a response from OpenAI',
            'provider': 'openai',
            'model': 'gpt-4',
            'raw_response': openai_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        mock_anthropic_formatter.return_value = {  # Add mock return for anthropic
            'content': 'This is a response from Anthropic',
            'provider': 'anthropic',
            'model': 'claude-3-opus-20240229',
            'raw_response': MagicMock(),
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        
        # Test generate_response with a large prompt
        large_prompt = "Test prompt " * 1000  # Very large prompt to trigger token limit
        response = await self.model_manager.generate_response(
            prompt=large_prompt,
            provider='anthropic',
            model_name='claude-3-opus-20240229'
        )
        
        # Verify fallback was used
        self.assertEqual(response['provider'], 'google')
        self.assertEqual(response['model'], 'gemini-pro')
        self.assertTrue(response.get('fallback_used', False))
        #self.assertEqual(response['content'], 'This is a response from OpenAI')
        
        # Verify Anthropic was called and failed
        self.model_manager._generate_anthropic_response.assert_called_once()
        
        # Verify Gemini was called as fallback
        self.model_manager._generate_gemini_response.assert_called_once()
    
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_anthropic_response')
    async def test_simpler_query_fallback(self, mock_anthropic_formatter):
        """Test fallback with simplified query when Anthropic initially fails."""
        # Mock Anthropic to fail first then succeed with simpler query
        anthropic_response = MagicMock()
        
        # Create a side effect function to fail on first call and succeed on second
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ModelError("Model error")
            return anthropic_response
            
        self.model_manager._generate_anthropic_response = MagicMock(side_effect=side_effect)
        
        # Mock formatter
        mock_anthropic_formatter.return_value = {
            'content': 'This is a simplified response from Claude',
            'provider': 'anthropic',
            'model': 'claude-3-opus-20240229',
            'raw_response': anthropic_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        
        # Test generate_response
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='anthropic',
            model_name='claude-3-opus-20240229'
        )
        
        # Verify fallback was used
        self.assertEqual(response['provider'], 'anthropic')
        self.assertEqual(response['model'], 'claude-3-opus-20240229')
        self.assertTrue(response.get('fallback_used', False))
        self.assertEqual(response['content'], 'This is a simplified response from Claude')
        
        # Verify Anthropic was called twice (once for original, once for simplified)
        self.assertEqual(self.model_manager._generate_anthropic_response.call_count, 2)
        
        # Verify second call had a simplified prompt
        second_call_args = self.model_manager._generate_anthropic_response.call_args_list[1]
        self.assertIn('brief and simple', second_call_args[0][2])  # Check if prompt was simplified

    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_gemini_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openrouter_response')
    async def test_gemini_rate_limit_failover(self, mock_openrouter_formatter, mock_gemini_formatter):
        """Test failover when Gemini rate limit is hit."""
        # Mock Gemini to raise RateLimitError
        self.model_manager._generate_gemini_response = MagicMock(side_effect=RateLimitError("Rate limit exceeded"))

        # Mock OpenRouter response
        openrouter_response = MagicMock()
        self.model_manager._generate_openrouter_response = MagicMock(return_value=openrouter_response)

        # Mock formatters
        mock_openrouter_formatter.return_value = {
            'content': 'This is a response from OpenRouter',
            'provider': 'openrouter',
            'model': 'mistralai/mistral-medium',
            'raw_response': openrouter_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        mock_gemini_formatter.return_value = {  # Add mock return for gemini
            'content': 'This is a response from Gemini',
            'provider': 'google',
            'model': 'gemini-pro',
            'raw_response': MagicMock(),
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }

        # Test generate_response
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='google',
            model_name='gemini-pro'
        )

        # Verify fallback was used
        self.assertEqual(response['provider'], 'openrouter')
        self.assertEqual(response['model'], 'mistralai/mistral-medium')
        self.assertTrue(response.get('fallback_used', False))

        # Verify Gemini was called and failed
        self.model_manager._generate_gemini_response.assert_called_once()

        # Verify OpenRouter was called as fallback
        self.model_manager._generate_openrouter_response.assert_called_once()

    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_gemini_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openrouter_response')
    async def test_gemini_model_error_failover(self, mock_openrouter_formatter, mock_gemini_formatter):
        """Test failover when Gemini has a ModelError."""
        # Mock Gemini to raise ModelError
        self.model_manager._generate_gemini_response = MagicMock(side_effect=ModelError("Model error"))

        # Mock OpenRouter response
        openrouter_response = MagicMock()
        self.model_manager._generate_openrouter_response = MagicMock(return_value=openrouter_response)

        # Mock formatters
        mock_openrouter_formatter.return_value = {
            'content': 'This is a response from OpenRouter',
            'provider': 'openrouter',
            'model': 'mistralai/mistral-medium',
            'raw_response': openrouter_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        mock_gemini_formatter.return_value = {
            'content': 'This is a response from Gemini',
            'provider': 'google',
            'model': 'gemini-pro',
            'raw_response': MagicMock(),
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }

        # Test generate_response
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='google',
            model_name='gemini-pro'
        )

        # Verify fallback was used
        self.assertEqual(response['provider'], 'openrouter')
        self.assertEqual(response['model'], 'mistralai/mistral-medium')
        self.assertTrue(response.get('fallback_used', False))

        # Verify Gemini was called and failed
        self.model_manager._generate_gemini_response.assert_called_once()

        # Verify OpenRouter was called as fallback
        self.model_manager._generate_openrouter_response.assert_called_once()


    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openrouter_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openai_response')
    async def test_openrouter_rate_limit_failover(self, mock_openai_formatter, mock_openrouter_formatter):
        """Test failover when OpenRouter rate limit is hit."""
        # Mock OpenRouter to raise RateLimitError
        self.model_manager._generate_openrouter_response = MagicMock(side_effect=RateLimitError("Rate limit exceeded"))

        # Mock OpenAI response
        openai_response = MagicMock()
        self.model_manager._generate_openai_response = MagicMock(return_value=openai_response)

        # Mock formatters
        mock_openai_formatter.return_value = {
            'content': 'This is a response from OpenAI',
            'provider': 'openai',
            'model': 'gpt-4',
            'raw_response': openai_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        mock_openrouter_formatter.return_value = {
            'content': 'This is a response from OpenRouter',
            'provider': 'openrouter',
            'model': 'mistralai/mistral-medium',
            'raw_response': MagicMock(),
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }

        # Test generate_response
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='openrouter',
            model_name='mistralai/mistral-medium'
        )

        # Verify fallback was used
        self.assertEqual(response['provider'], 'openai')
        self.assertEqual(response['model'], 'gpt-4')
        self.assertTrue(response.get('fallback_used', False))

        # Verify OpenRouter was called and failed
        self.model_manager._generate_openrouter_response.assert_called_once()

        # Verify OpenAI was called as fallback
        self.model_manager._generate_openai_response.assert_called_once()

    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openrouter_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openai_response')
    async def test_openrouter_model_error_failover(self, mock_openai_formatter, mock_openrouter_formatter):
        """Test failover when OpenRouter has a ModelError."""
        # Mock OpenRouter to raise ModelError
        self.model_manager._generate_openrouter_response = MagicMock(side_effect=ModelError("Model error"))

        # Mock OpenAI response
        openai_response = MagicMock()
        self.model_manager._generate_openai_response = MagicMock(return_value=openai_response)

        # Mock formatters
        mock_openai_formatter.return_value = {
            'content': 'This is a response from OpenAI',
            'provider': 'openai',
            'model': 'gpt-4',
            'raw_response': openai_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        mock_openrouter_formatter.return_value = {
            'content': 'This is a response from OpenRouter',
            'provider': 'openrouter',
            'model': 'mistralai/mistral-medium',
            'raw_response': MagicMock(),
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }

        # Test generate_response
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='openrouter',
            model_name='mistralai/mistral-medium'
        )

        # Verify fallback was used
        self.assertEqual(response['provider'], 'openai')
        self.assertEqual(response['model'], 'gpt-4')
        self.assertTrue(response.get('fallback_used', False))

        # Verify OpenRouter was called and failed
        self.model_manager._generate_openrouter_response.assert_called_once()

        # Verify OpenAI was called as fallback
        self.model_manager._generate_openai_response.assert_called_once()

    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_anthropic_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_gemini_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openrouter_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_openai_response')
    async def test_multiple_provider_failover(self, mock_openai_formatter, mock_openrouter_formatter, mock_gemini_formatter, mock_anthropic_formatter):
        """Test failover with multiple providers failing."""

        # Mock all providers to raise RateLimitError in sequence
        self.model_manager._generate_anthropic_response = MagicMock(side_effect=RateLimitError("Anthropic rate limit"))
        self.model_manager._generate_gemini_response = MagicMock(side_effect=RateLimitError("Gemini rate limit"))
        self.model_manager._generate_openrouter_response = MagicMock(side_effect=RateLimitError("OpenRouter rate limit"))

        # Mock OpenAI response
        openai_response = MagicMock()
        self.model_manager._generate_openai_response = MagicMock(return_value=openai_response)

        # Mock formatters
        mock_openai_formatter.return_value = {
            'content': 'This is a response from OpenAI',
            'provider': 'openai',
            'model': 'gpt-4',
            'raw_response': openai_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        mock_anthropic_formatter.return_value = {  # Add mock return for anthropic
            'content': 'This is a response from Anthropic',
            'provider': 'anthropic',
            'model': 'claude-3-opus-20240229',
            'raw_response': MagicMock(),
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        mock_gemini_formatter.return_value = {  # Add mock return for gemini
            'content': 'This is a response from Gemini',
            'provider': 'google',
            'model': 'gemini-pro',
            'raw_response': MagicMock(),
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }
        mock_openrouter_formatter.return_value = {  # Add mock return for OpenRouter
            'content': 'This is a response from OpenRouter',
            'provider': 'openrouter',
            'model': 'mistralai/mistral-medium',
            'raw_response': MagicMock(),
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'fallback_used': False
        }

        # Test generate_response starting with Anthropic
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='anthropic',
            model_name='claude-3-opus-20240229'
        )

        # Verify fallback was used and ended up at OpenAI
        self.assertEqual(response['provider'], 'openai')
        self.assertEqual(response['model'], 'gpt-4')
        self.assertTrue(response.get('fallback_used', False))

        # Verify calls
        self.model_manager._generate_anthropic_response.assert_called_once()
        self.model_manager._generate_gemini_response.assert_called_once()
        self.model_manager._generate_openrouter_response.assert_called_once()
        self.model_manager._generate_openai_response.assert_called_once()

if __name__ == '__main__':
    unittest.main()
