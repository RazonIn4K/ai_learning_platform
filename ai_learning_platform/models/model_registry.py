"""Model registry for managing AI model clients."""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseModelClient(ABC):
    """Base class for model clients."""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.client = kwargs.get('client')
        
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using the model."""
        pass

class AnthropicClient(BaseModelClient):
    """Client for Anthropic models."""
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using Anthropic models."""
        if not self.client:
            raise ValueError("Anthropic client not initialized")
            
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=context.get('max_tokens', 3000),
                temperature=context.get('temperature', 0.7),
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error processing message with Anthropic: {str(e)}")
            raise

class OpenAIClient(BaseModelClient):
    """Client for OpenAI models."""
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using OpenAI models."""
        # Mock implementation
        return "Mock OpenAI response"

class GeminiClient(BaseModelClient):
    """Client for Google Gemini models."""
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using Gemini models."""
        # Mock implementation
        return "Mock Gemini response"

class ModelRegistry:
    """Registry for model clients."""
    
    _clients = {
        'anthropic': AnthropicClient,
        'openai': OpenAIClient,
        'google': GeminiClient
    }
    
    @classmethod
    def create_client(
        cls,
        provider: str,
        model_name: str,
        **kwargs
    ) -> BaseModelClient:
        """Create a model client."""
        if provider not in cls._clients:
            raise ValueError(f"Unsupported model provider: {provider}")
            
        client_class = cls._clients[provider]
        return client_class(model_name=model_name, **kwargs)
