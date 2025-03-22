import logging
from typing import Dict, Any, Optional
from .model_registry import ModelRegistry, BaseModelClient

logger = logging.getLogger(__name__)

class ModelHandler:
    """Handles model interactions and fallbacks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or ConfigManager().get_component_config('model')
        self.primary_model = self._initialize_primary()
        self.backup_models = self._initialize_backups()
        
    def _initialize_primary(self) -> BaseModelClient:
        """Initialize primary model client with fallbacks."""
        return ModelRegistry.create_client_with_fallbacks(
            provider=self.config['provider'],
            model_name=self.config['model_name'],
            fallback_configs=self.config.get('fallback_models'),
            **self._get_client_kwargs()
        )
        
    def _initialize_backups(self) -> Dict[str, BaseModelClient]:
        """Initialize backup model clients."""
        backups = {}
        backup_configs = self.config.get('backup_models', {})
        
        for provider, config in backup_configs.items():
            try:
                backups[provider] = ModelRegistry.get_client(
                    provider=provider,
                    model_name=config['model_name'],
                    **self._get_client_kwargs(config)
                )
            except Exception as e:
                logger.warning(f"Failed to initialize backup model {provider}: {str(e)}")
                
        return backups
        
    def _get_client_kwargs(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get kwargs for client initialization."""
        config = config or self.config
        return {
            'temperature': config.get('temperature', 0.7),
            'max_tokens': config.get('max_tokens', 3000),
            'api_key': config.get('api_key')
        }
        
    async def generate_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response using models with fallback."""
        context = context or {}
        context.update(self._get_client_kwargs())
        
        try:
            # Try primary model with built-in fallbacks
            response_text = await self.primary_model.process_message(message, context)
            if response_text:
                return {
                    'content': response_text,
                    'model': self.primary_model.model_name,
                    'provider': self.config['provider']
                }
            
            # Try backup models if primary and its fallbacks fail
            for provider, model in self.backup_models.items():
                try:
                    response_text = await model.process_message(message, context)
                    return {
                        'content': response_text,
                        'model': model.model_name,
                        'provider': provider,
                        'used_backup': True
                    }
                except Exception as e:
                    logger.warning(f"Backup model {provider} failed: {str(e)}")
            
            raise RuntimeError("All models failed to generate response")
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
