import logging
from ai_learning_platform.utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class EnvironmentSetup:
    """
    Sets up the environment for the AI Learning Platform.
    
    This class is responsible for loading configuration using the ConfigManager
    and making it available to other parts of the system. It does NOT load
    environment variables from .env or ~/.zshrc.
    """

    def __init__(self):
        """
        Initializes the EnvironmentSetup.
        """
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()

    def get_available_providers(self) -> dict:
        """
        Gets a dictionary of available model providers based on configured API keys.

        Returns:
            dict: A dictionary where keys are provider names (lowercase) and values
                  are booleans indicating if the provider is available (has an API key).
        """
        api_keys = self.config.get('api_keys', {})
        return {
            'openai': bool(api_keys.get('openai')),
            'anthropic': bool(api_keys.get('anthropic')),
            'google': bool(api_keys.get('google')),
            'openrouter': bool(api_keys.get('openrouter')),
            'camel': True  # CAMEL is always available as it can use other providers
        }

    def suggest_default_provider(self) -> str:
        """
        Suggests a default provider based on available API keys.

        Returns:
            str: The suggested default provider name (lowercase).
        """
        providers = self.get_available_providers()

        # Prefer Anthropic if available
        if providers['anthropic']:
            return 'anthropic'
        # Then OpenAI
        elif providers['openai']:
            return 'openai'
        # Then Google
        elif providers['google']:
            return 'google'
        # Then OpenRouter
        elif providers['openrouter']:
            return 'openrouter'
        # Fall back to CAMEL
        else:
            return 'camel'
