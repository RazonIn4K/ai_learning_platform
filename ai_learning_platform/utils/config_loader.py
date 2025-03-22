"""Configuration loader for the AI Learning Platform."""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Loads and manages configuration for the platform."""
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the config loader."""
        if not self._config:
            self._load_default_config()
    
    def _load_default_config(self) -> None:
        """Load default configuration values."""
        self._config = {
            "model": {
                "default_provider": "anthropic",
                "default_model": "claude-3-sonnet",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "learning": {
                "min_mastery_threshold": 0.7,
                "max_session_duration": 3600,
                "topics_per_session": 3
            },
            "workspace": {
                "save_state": True,
                "state_dir": "workspace_states",
                "log_level": "INFO"
            }
        }
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from a file."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"Config file not found: {config_path}")
                return
            
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                
            # Update configuration
            self._update_config(file_config)
            logger.info(f"Configuration loaded from {config_path}")
            
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}", exc_info=True)
            raise
    
    def _update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        def deep_update(d: dict, u: dict) -> dict:
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        self._config = deep_update(self._config, new_config)
    
    def get_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration values."""
        if section:
            return self._config.get(section, {})
        return self._config
    
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        keys = key.split('.')
        current = self._config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value

def get_config_loader() -> ConfigLoader:
    """Get the singleton config loader instance."""
    return ConfigLoader()
