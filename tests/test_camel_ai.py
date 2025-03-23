# tests/test_camel_ai.py

import unittest
import asyncio
import logging
from unittest.mock import patch, MagicMock

from ai_learning_platform.models.enhanced_model_manager import EnhancedModelManager, ModelProvider
from ai_learning_platform.agents.agent_model_adapter import AgentModelAdapter
from ai_learning_platform.utils.exceptions import ModelError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCamelAI(unittest.TestCase):
    """Test CAMeL-AI integration."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock config with CAMeL-AI
        self.mock_config = {
            'api_keys': {
                'anthropic': 'mock_anthropic_key',
                'openai': 'mock_openai_key',
                'google': 'mock_google_key',
                'openrouter': 'mock_openrouter_key',
                'camel': 'mock_camel_key'
            },
            'model_parameters': {
                'provider': 'camel',
                'model_name': 'camel-base',
                'temperature': 0.7,
                'max_tokens': 3000
            },
            'fallback_models': [
                {
                    'provider': 'anthropic',
                    'model_name': 'claude-3-opus-20240229'
                }
            ],
            'rate_limits': {
                'anthropic': {'requests_per_minute': 10},
                'openai': {'requests_per_minute': 20},
                'google': {'requests_per_minute': 15},
                'openrouter': {'requests_per_minute': 10},
                'camel': {'requests_per_minute': 10}
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
            ModelProvider.OPENROUTER: MagicMock(),
            ModelProvider.CAMEL: MagicMock()
        }
        
        # Initialize agent adapter
        self.agent_adapter = AgentModelAdapter(self.model_manager)
    
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_camel_response')
    async def test_camel_response(self, mock_camel_formatter):
        """Test CAMeL-AI response generation."""
        # Mock CAMeL-AI response
        camel_response = MagicMock()
        camel_response.response = "This is a response from CAMeL-AI"
        camel_response.role = "AI education specialist"
        
        # Mock CAMeL-AI generation
        self.model_manager._generate_camel_response = MagicMock(return_value=camel_response)
        
        # Mock formatter
        mock_camel_formatter.return_value = {
            'content': 'This is a response from CAMeL-AI',
            'provider': 'camel',
            'model': 'camel-base',
            'raw_response': camel_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'role_info': {'role': 'AI education specialist'}
        }
        
        # Test generate_response
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='camel',
            model_name='camel-base'
        )
        
        # Verify response
        self.assertEqual(response['provider'], 'camel')
        self.assertEqual(response['model'], 'camel-base')
        self.assertEqual(response['content'], 'This is a response from CAMeL-AI')
        self.assertEqual(response['role_info']['role'], 'AI education specialist')
        
        # Verify CAMeL-AI was called
        self.model_manager._generate_camel_response.assert_called_once()
    
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_camel_response')
    async def test_camel_role_playing(self, mock_camel_formatter):
        """Test CAMeL-AI role-playing capabilities."""
        # Mock CAMeL-AI response
        camel_response = MagicMock()
        camel_response.response = "This is a role-playing response from CAMeL-AI"
        camel_response.role = "Cybersecurity expert"
        
        # Mock CAMeL-AI generation
        self.model_manager._generate_camel_response = MagicMock(return_value=camel_response)
        
        # Mock formatter
        mock_camel_formatter.return_value = {
            'content': 'This is a role-playing response from CAMeL-AI',
            'provider': 'camel',
            'model': 'camel-base',
            'raw_response': camel_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'role_info': {'role': 'Cybersecurity expert'}
        }
        
        # Test generate_response with role parameter
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='camel',
            model_name='camel-base',
            role="You are a cybersecurity expert advising on best practices."
        )
        
        # Verify response
        self.assertEqual(response['provider'], 'camel')
        self.assertEqual(response['model'], 'camel-base')
        self.assertEqual(response['content'], 'This is a role-playing response from CAMeL-AI')
        self.assertEqual(response['role_info']['role'], 'Cybersecurity expert')
        
        # Verify CAMeL-AI was called with role parameter
        self.model_manager._generate_camel_response.assert_called_once()
        args, kwargs = self.model_manager._generate_camel_response.call_args
        self.assertIn('role', kwargs[2])
    
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_camel_response')
    async def test_agent_adapter_role_playing(self, mock_camel_formatter):
        """Test agent adapter with CAMeL-AI role-playing."""
        # Mock CAMeL-AI response
        camel_response = MagicMock()
        camel_response.response = "This is an agent adapter role-playing response"
        camel_response.role = "Domain expert"
        
        # Mock CAMeL-AI generation
        self.model_manager._generate_camel_response = MagicMock(return_value=camel_response)
        
        # Mock formatter
        mock_camel_formatter.return_value = {
            'content': 'This is an agent adapter role-playing response',
            'provider': 'camel',
            'model': 'camel-base',
            'raw_response': camel_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None,
            'role_info': {'role': 'Domain expert'}
        }
        
        # Test generate_role_playing_response
        response = await self.agent_adapter.generate_role_playing_response(
            agent_type="domain_expert",
            prompt="Test prompt",
            assistant_role="You are a domain expert in cybersecurity",
            user_role="You are a student learning about cybersecurity",
            model_name="camel-base"
        )
        
        # Verify response
        self.assertEqual(response['provider'], 'camel')
        self.assertEqual(response['model'], 'camel-base')
        self.assertEqual(response['content'], 'This is an agent adapter role-playing response')
        self.assertEqual(response['role_info']['role'], 'Domain expert')
        self.assertEqual(response['agent_type'], 'domain_expert')
        
        # Verify CAMeL-AI was called with proper parameters
        self.model_manager._generate_camel_response.assert_called_once()
        args, kwargs = self.model_manager._generate_camel_response.call_args
        self.assertIn('assistant_role', kwargs[2])
        self.assertIn('user_role', kwargs[2])
    
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_camel_response')
    @patch('ai_learning_platform.models.enhanced_model_manager.ModelResponseFormatter._format_anthropic_response')
    async def test_camel_fallback(self, mock_anthropic_formatter, mock_camel_formatter):
        """Test fallback from CAMeL-AI to Anthropic."""
        # Mock CAMeL-AI to raise error
        self.model_manager._generate_camel_response = MagicMock(side_effect=ModelError("CAMeL-AI error"))
        
        # Mock Anthropic response
        anthropic_response = MagicMock()
        anthropic_response.content = [MagicMock(text="This is a fallback response from Anthropic")]
        
        # Mock Anthropic generation
        self.model_manager._generate_anthropic_response = MagicMock(return_value=anthropic_response)
        
        # Mock formatters
        mock_anthropic_formatter.return_value = {
            'content': 'This is a fallback response from Anthropic',
            'provider': 'anthropic',
            'model': 'claude-3-opus-20240229',
            'raw_response': anthropic_response,
            'token_usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            'error': None
        }
        
        # Test generate_response with CAMeL-AI as primary
        response = await self.model_manager.generate_response(
            prompt="Test prompt",
            provider='camel',
            model_name='camel-base'
        )
        
        # Verify fallback to Anthropic
        self.assertEqual(response['provider'], 'anthropic')
        self.assertEqual(response['model'], 'claude-3-opus-20240229')
        self.assertTrue(response.get('fallback_used', False))
        self.assertEqual(response['content'], 'This is a fallback response from Anthropic')
        
        # Verify call sequence
        self.model_manager._generate_camel_response.assert_called_once()
        self.model_manager._generate_anthropic_response.assert_called_once()

if __name__ == '__main__':
    unittest.main()
