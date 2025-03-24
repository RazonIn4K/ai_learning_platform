"""Model registry for managing AI model clients."""

import logging
from typing import Dict, Any, Optional, Type, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseModelClient(ABC):
    """Base class for model clients."""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.client = kwargs.get('client')
        self.fallback_models = kwargs.get('fallback_models', [])
        logger.info(f"Initialized {self.__class__.__name__} with model_name: {model_name}, client: {self.client}, fallbacks: {self.fallback_models}")
        
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using the model."""
        pass
        
    async def fallback_process(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """Attempt to process using fallback models."""
        for fallback in self.fallback_models:
            try:
                return await fallback.process_message(message, context)
            except Exception as e:
                logger.warning(f"Fallback to {fallback.model_name} failed: {str(e)}")
        return None

class AnthropicClient(BaseModelClient):
    """Client for Anthropic models."""
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using Anthropic models."""
        logger.info(f"Processing message with AnthropicClient: {message[:50]}...")  # Log first 50 chars
        if not self.client:
            error_msg = "Anthropic client not initialized"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
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
            logger.info(f"Anthropic response: {response.content[0].text[:50]}...") # Log first 50 chars of response
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error processing message with Anthropic: {str(e)}")
            raise

class OpenAIClient(BaseModelClient):
    """Client for OpenAI models."""
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using OpenAI models."""
        logger.info(f"Processing message with OpenAIClient (Mock): {message[:50]}...")
        # Mock implementation
        return "Mock OpenAI response"

class GeminiClient(BaseModelClient):
    """Client for Google Gemini models."""
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using Gemini models."""
        logger.info(f"Processing message with GeminiClient (Mock): {message[:50]}...")
        # Mock implementation
        return "Mock Gemini response"

class ModelRegistry:
    """Registry for model clients."""
    
    _clients: Dict[str, Type[BaseModelClient]] = {}
    _instances: Dict[str, Dict[str, BaseModelClient]] = {}
    
    @classmethod
    def register_client(cls, provider: str, client_class: Type[BaseModelClient]) -> None:
        """Register a new model client class."""
        logger.info(f"Registering client: {provider} - {client_class.__name__}")
        cls._clients[provider] = client_class
        cls._instances[provider] = {}
    
    @classmethod
    def get_client(
        cls,
        provider: str,
        model_name: str,
        **kwargs
    ) -> BaseModelClient:
        """Get or create a model client instance."""
        logger.info(f"Getting client for provider: {provider}, model_name: {model_name}")
        if provider not in cls._clients:
            error_msg = f"Unsupported model provider: {provider}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        instance_key = f"{provider}:{model_name}"
        if instance_key not in cls._instances[provider]:
            logger.info(f"Creating new client instance for: {instance_key}")
            client_class = cls._clients[provider]
            try:
                cls._instances[provider][instance_key] = client_class(
                    model_name=model_name,
                    **kwargs
                )
            except Exception as e:
                logger.exception(f"Error creating client instance for {instance_key}: {e}")
                raise
        else:
            logger.info(f"Using existing client instance for: {instance_key}")

        return cls._instances[provider][instance_key]
    
    @classmethod
    def create_client_with_fallbacks(
        cls,
        provider: str,
        model_name: str,
        fallback_configs: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> BaseModelClient:
        """Create a model client with fallback options."""
        primary_client = cls.get_client(provider, model_name, **kwargs)
        
        if fallback_configs:
            fallbacks = []
            for config in fallback_configs:
                try:
                    fallback = cls.get_client(
                        config['provider'],
                        config['model_name'],
                        **config.get('kwargs', {})
                    )
                    fallbacks.append(fallback)
                except Exception as e:
                    logger.warning(f"Failed to initialize fallback {config}: {str(e)}")
            
            primary_client.fallback_models = fallbacks
            
        return primary_client

# Register built-in clients
ModelRegistry.register_client('anthropic', AnthropicClient)
ModelRegistry.register_client('openai', OpenAIClient)
ModelRegistry.register_client('google', GeminiClient)
