import logging
import os
from typing import Dict, Any, Optional
from anthropic import Anthropic
from .model_registry import ModelRegistry, BaseModelClient

logger = logging.getLogger(__name__)

class ModelHandler:
    """Handles model interactions and fallbacks."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.primary_model = self._initialize_primary()
        self.backup_models = self._initialize_backups()
        
    def _initialize_primary(self) -> BaseModelClient:
        """Initialize primary model client."""
        model_config = self.config['model']
        return ModelRegistry.create_client(
            provider=model_config['provider'],
            model_name=model_config['model_name'],
            client=self.anthropic_client
        )
        
    def _initialize_backups(self) -> Dict[str, BaseModelClient]:
        """Initialize backup model clients."""
        backups = {}
        backup_configs = self.config.get('backup_models', {})
        
        for provider, config in backup_configs.items():
            try:
                backups[provider] = ModelRegistry.create_client(
                    provider=provider,
                    model_name=config['model_name']
                )
            except Exception as e:
                logger.warning(f"Failed to initialize backup model {provider}: {str(e)}")
                
        return backups
        
    async def generate_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response using models with fallback."""
        context = context or {}
        context.update({
            'max_tokens': self.config['model'].get('max_tokens', 3000),
            'temperature': self.config['model'].get('temperature', 0.7)
        })
        
        try:
            response_text = await self.primary_model.process_message(message, context)
            return {
                'content': response_text,
                'model': self.config['model']['model_name']
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
