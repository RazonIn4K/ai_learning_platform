from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from ..config import ConfigManager
from ..models import ModelManager

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_type: str, config: Optional[Dict[str, Any]] = None):
        self.agent_type = agent_type
        self.config = config or ConfigManager().get_config('agents').get(agent_type, {})
        self.model_manager = ModelManager()
        self.max_retries = self.config.get('max_retries', 3)
        self.timeout = self.config.get('timeout', 30)
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        pass
    
    async def _generate_response(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using configured model."""
        model_config = self.config.get('model', {})
        return await self.model_manager.generate_response(
            prompt,
            provider=model_config.get('provider'),
            model_name=model_config.get('model_name'),
            **kwargs
        )
    
    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for processing."""
        required_fields = self.config.get('required_fields', [])
        return all(field in input_data for field in required_fields)
    
    async def _handle_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle errors during processing."""
        logger.error(
            f"Error in {self.agent_type} agent: {str(error)}",
            extra={'context': context}
        )
        
        if self.config.get('fallback_enabled', True):
            return await self._process_with_fallback(context)
            
        raise error
    
    @abstractmethod
    async def _process_with_fallback(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process using fallback logic."""
        pass
