from pathlib import Path
import json
from typing import Dict, Any
import os

class ConfigLoader:
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.getenv('AI_LEARNING_CONFIG_PATH', 'configs')
        
    def load_config(self) -> Dict[str, Any]:
        """Load and merge all configuration files."""
        config = {}
        
        # Load base config
        base_config = self._load_json_file('base_config.json')
        config.update(base_config)
        
        # Load environment-specific config
        env = os.getenv('AI_LEARNING_ENV', 'development')
        env_config = self._load_json_file(f'{env}_config.json')
        config.update(env_config)
        
        # Load API keys from environment variables
        config['api_keys'] = {
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            'google': os.getenv('GOOGLE_API_KEY')
        }
        
        return config
        
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        path = Path(self.base_path) / filename
        if not path.exists():
            return {}
        with open(path) as f:
            return json.load(f)