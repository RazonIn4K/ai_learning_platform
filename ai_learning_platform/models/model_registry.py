"""Model registry for managing AI model clients."""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from ..agents.base_agent import BaseLearningAgent

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Available model types."""
    GPT4 = "openai/gpt-4"
    GPT35 = "openai/gpt-3.5-turbo"
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet"
    GEMINI_PRO = "google/gemini-pro"
    OPENCHAT_3_5 = "openchat/openchat-3.5"

class BaseModelClient:
    """Base class for model clients."""
    
    def __init__(self, model_type: str):
        """Initialize the model client.
        
        Args:
            model_type: Type of model to use
        """
        self.model_type = model_type
        
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using the model.
        
        Args:
            message: Message to process
            context: Additional context for processing
            
        Returns:
            Model's response
        """
        raise NotImplementedError("Subclasses must implement process_message")

class OpenAIClient(BaseModelClient):
    """Client for OpenAI models."""
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using OpenAI models."""
        # For testing, return a mock response
        if "query" in message.lower():
            return """
            {
                "domains": ["machine_learning", "cybersecurity"],
                "is_navigation": true,
                "complexity_level": "intermediate",
                "learning_style": "balanced",
                "required_agents": ["topic_navigator", "domain_expert"],
                "execution_order": ["analyze_prerequisites", "suggest_path"],
                "confidence_score": 0.85
            }
            """
        return "Mock OpenAI response"

class AnthropicClient(BaseModelClient):
    """Client for Anthropic models."""
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using Anthropic models."""
        # For testing, return a mock response
        if "query" in message.lower():
            return """
            {
                "domains": ["machine_learning", "cybersecurity"],
                "is_navigation": true,
                "complexity_level": "intermediate",
                "learning_style": "balanced",
                "required_agents": ["topic_navigator", "domain_expert"],
                "execution_order": ["analyze_prerequisites", "suggest_path"],
                "confidence_score": 0.85
            }
            """
        return "Mock Anthropic response"

class GeminiClient(BaseModelClient):
    """Client for Google Gemini models."""
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using Gemini models."""
        # For testing, return a mock response
        if "query" in message.lower():
            return """
            {
                "domains": ["machine_learning", "cybersecurity"],
                "is_navigation": true,
                "complexity_level": "intermediate",
                "learning_style": "balanced",
                "required_agents": ["topic_navigator", "domain_expert"],
                "execution_order": ["analyze_prerequisites", "suggest_path"],
                "confidence_score": 0.85
            }
            """
        return "Mock Gemini response"

class OpenChatClient(BaseModelClient):
    """Client for OpenChat models."""
    
    def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message using OpenChat models."""
        # For testing, return a mock response
        if "query" in message.lower():
            return """
            {
                "domains": ["machine_learning", "cybersecurity"],
                "is_navigation": true,
                "complexity_level": "intermediate",
                "learning_style": "balanced",
                "required_agents": ["topic_navigator", "domain_expert"],
                "execution_order": ["analyze_prerequisites", "suggest_path"],
                "confidence_score": 0.85
            }
            """
        return "Mock OpenChat response"

class ModelRegistry:
    """Registry for managing AI model clients."""
    
    # Model constants
    GPT4 = ModelType.GPT4.value
    GPT35 = ModelType.GPT35.value
    CLAUDE_3_SONNET = ModelType.CLAUDE_3_SONNET.value
    GEMINI_PRO = ModelType.GEMINI_PRO.value
    OPENCHAT_3_5 = ModelType.OPENCHAT_3_5.value
    
    _instance = None
    _clients = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_model(cls, model_type: str) -> BaseModelClient:
        """Get a model client by name.
        
        Args:
            model_type: Name of the model to get
            
        Returns:
            Model client instance
            
        Raises:
            ValueError: If model type is not supported
        """
        # Create client if it doesn't exist
        if model_type not in cls._clients:
            cls._clients[model_type] = cls._initialize_client(model_type)
            
        # Return the client
        return cls._clients[model_type]
    
    @classmethod
    def create_client(cls, model_type: str) -> BaseModelClient:
        """Create or get a model client."""
        if model_type not in cls._clients:
            cls._clients[model_type] = cls._initialize_client(model_type)
        return cls._clients[model_type]
    
    @classmethod
    def _initialize_client(cls, model_type: str) -> BaseModelClient:
        """Initialize a new model client."""
        try:
            if model_type == cls.GPT4 or model_type == cls.GPT35:
                return OpenAIClient(model_type)
            elif model_type == cls.CLAUDE_3_SONNET:
                return AnthropicClient(model_type)
            elif model_type == cls.GEMINI_PRO:
                return GeminiClient(model_type)
            elif model_type == cls.OPENCHAT_3_5:
                return OpenChatClient(model_type)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
        except Exception as e:
            logger.error(f"Failed to initialize model client: {str(e)}", exc_info=True)
            raise

class LearningCoordinatorAgent(BaseLearningAgent):
    """Coordinator agent for managing learning sessions."""
    
    def __init__(
        self,
        model_name: str = ModelType.GPT35.value,
        model_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(model_name=model_name, model_params=model_params, **kwargs)
        self.model_client = ModelRegistry.create_client(model_name)
