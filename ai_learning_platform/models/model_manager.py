from typing import Dict, Any, Optional, Type
from abc import ABC, abstractmethod
import logging
from ..config import ConfigManager
from .exceptions import ModelError

logger = logging.getLogger(__name__)

class BaseModelProvider(ABC):
    """Base class for model providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from the model."""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> list:
        """Generate embeddings for text."""
        pass

class ModelManager:
    """Centralized model management system."""
    _instance = None
    _providers: Dict[str, Type[BaseModelProvider]] = {}
    _active_models: Dict[str, BaseModelProvider] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = ConfigManager().get_config('models')
            self.initialized = True
            self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize configured model providers."""
        provider_configs = self.config.get('providers', {})
        
        for provider_name, config in provider_configs.items():
            try:
                provider_class = self._get_provider_class(provider_name)
                self._providers[provider_name] = provider_class(**config)
            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_name}: {str(e)}")
    
    def _get_provider_class(self, provider: str) -> Type[BaseModelProvider]:
        """Get the provider class based on provider name."""
        provider_map = {
            'anthropic': AnthropicProvider,
            'openai': OpenAIProvider,
            'google': GeminiProvider
        }
        
        if provider not in provider_map:
            raise ModelError(f"Unsupported provider: {provider}")
        return provider_map[provider]
    
    async def generate_response(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using specified or default model."""
        provider = provider or self.config['default_provider']
        model_name = model_name or self.config['default_model']
        
        try:
            provider_instance = self._providers[provider]
            response = await provider_instance.generate(prompt, model=model_name, **kwargs)
            
            return {
                'content': response,
                'provider': provider,
                'model': model_name
            }
            
        except Exception as e:
            logger.error(f"Generation failed with {provider}/{model_name}: {str(e)}")
            return await self._try_fallback(prompt, **kwargs)
    
    async def _try_fallback(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Attempt to generate response using fallback models."""
        fallbacks = self.config.get('fallback_models', [])
        
        for fallback in fallbacks:
            try:
                provider = fallback['provider']
                model = fallback['model_name']
                provider_instance = self._providers[provider]
                
                response = await provider_instance.generate(
                    prompt,
                    model=model,
                    **fallback.get('kwargs', {}),
                    **kwargs
                )
                
                return {
                    'content': response,
                    'provider': provider,
                    'model': model,
                    'used_fallback': True
                }
                
            except Exception as e:
                logger.warning(f"Fallback to {provider}/{model} failed: {str(e)}")
                
        raise ModelError("All models (including fallbacks) failed to generate response")
    
    def get_model_config(self, provider: str, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        provider_config = self.config.get('providers', {}).get(provider, {})
        model_config = provider_config.get('models', {}).get(model_name, {})
        
        if not model_config:
            raise ModelError(f"No configuration found for {provider}/{model_name}")
            
        return model_config