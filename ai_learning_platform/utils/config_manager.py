# ai_learning_platform/utils/config_manager.py

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages configuration for the AI Learning Platform.
    
    This class handles loading, validation, and providing access to 
    configuration settings, including API keys, model parameters,
    fallback strategies, and other settings.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton implementation to ensure only one config manager exists."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the ConfigManager if not already initialized."""
        if not getattr(self, '_initialized', False):
            self._config_path = Path.home() / '.ai_learning_platform' / 'config.json'
            self._config = None
            self._profile = "default"
            self._initialized = True
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Optional path to config file. If not provided,
                         uses default path ~/.ai_learning_platform/config.json
        
        Returns:
            Dict containing configuration settings
        """
        if config_path:
            path = Path(config_path)
        else:
            path = self._config_path
            
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # If file doesn't exist, create with default config
        if not path.exists():
            self._create_default_config(path)
            
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                self._config = config
                return config
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {str(e)}")
            if self._config is None:
                # Create and return default config if can't load
                self._config = self._get_default_config()
            return self._config
    
    def _create_default_config(self, path: Path) -> None:
        """
        Create default configuration file.
        
        Args:
            path: Path to create the config file
        """
        default_config = self._get_default_config()
        
        try:
            with open(path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config at {path}")
        except Exception as e:
            logger.error(f"Failed to create default config at {path}: {str(e)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Dict containing default configuration
        """
        return {
            "profiles": {
                "default": {
                    "api_keys": {
                        "anthropic": "",
                        "openai": "",
                        "google": "",
                        "openrouter": ""
                    },
                    "model_parameters": {
                        "temperature": 0.7,
                        "max_tokens": 3000
                    },
                    "fallback_models": [
                        {
                            "provider": "anthropic",
                            "model_name": "claude-3-sonnet-20240229"
                        }
                    ],
                    "timeouts": {
                        "default": 30,
                        "research": 60
                    },
                    "token_limits": {
                        "default": 8000,
                        "research": 16000
                    }
                },
                "dev": {
                    "api_keys": {
                        "anthropic": "",
                        "openai": "",
                        "google": "",
                        "openrouter": ""
                    },
                    "model_parameters": {
                        "temperature": 1.0,
                        "max_tokens": 2000
                    },
                    "fallback_models": [
                        {
                            "provider": "anthropic",
                            "model_name": "claude-3-sonnet-20240229"
                        }
                    ],
                    "timeouts": {
                        "default": 15,
                        "research": 30
                    },
                    "token_limits": {
                        "default": 4000,
                        "research": 8000
                    }
                }
            },
            "active_profile": "default",
            "enable_telemetry": True,
            "cache_settings": {
                "enabled": True,
                "max_size": 100,
                "expiration": 3600
            }
        }
    
    def get_config(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration settings, optionally filtered by component.
        
        Args:
            component: Optional component name to filter by
        
        Returns:
            Dict containing configuration settings
        """
        if self._config is None:
            self.load_config()
            
        active_profile = self._config.get("active_profile", "default")
        profile_config = self._config.get("profiles", {}).get(active_profile, {})
        
        # Add global settings to profile config
        result = {
            **profile_config,
            "enable_telemetry": self._config.get("enable_telemetry", True),
            "cache_settings": self._config.get("cache_settings", {"enabled": True, "max_size": 100, "expiration": 3600})
        }
        
        if component:
            return result.get(component, {})
        
        return result
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Dict containing configuration to save
        """
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self._config = config
            logger.info(f"Saved config to {self._config_path}")
        except Exception as e:
            logger.error(f"Failed to save config to {self._config_path}: {str(e)}")
    
    def update_config(self, updates: Dict[str, Any], component: Optional[str] = None) -> None:
        """
        Update configuration settings.
        
        Args:
            updates: Dict containing updates to apply
            component: Optional component name to update
        """
        if self._config is None:
            self.load_config()
            
        if component:
            active_profile = self._config.get("active_profile", "default")
            if "profiles" not in self._config:
                self._config["profiles"] = {}
            if active_profile not in self._config["profiles"]:
                self._config["profiles"][active_profile] = {}
            
            if component not in self._config["profiles"][active_profile]:
                self._config["profiles"][active_profile][component] = {}
                
            self._config["profiles"][active_profile][component].update(updates)
        else:
            self._config.update(updates)
            
        self.save_config(self._config)
    
    def set_profile(self, profile: str) -> None:
        """
        Set active profile.
        
        Args:
            profile: Profile name to set as active
        """
        if self._config is None:
            self.load_config()
            
        if "profiles" not in self._config:
            self._config["profiles"] = {}
            
        if profile not in self._config["profiles"]:
            self._config["profiles"][profile] = {}
            
        self._config["active_profile"] = profile
        self._profile = profile
        
        self.save_config(self._config)
        logger.info(f"Set active profile to {profile}")
    
    def get_active_profile(self) -> str:
        """
        Get active profile name.
        
        Returns:
            String containing active profile name
        """
        if self._config is None:
            self.load_config()
            
        return self._config.get("active_profile", "default")
    
    def validate_config(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if valid, False otherwise
        """
        if self._config is None:
            self.load_config()
            
        active_profile = self._config.get("active_profile", "default")
        profile_config = self._config.get("profiles", {}).get(active_profile, {})
        
        # Check for required settings
        required_keys = ["api_keys", "model_parameters"]
        for key in required_keys:
            if key not in profile_config:
                logger.error(f"Missing required config key: {key}")
                return False
                
        # Check API keys
        api_keys = profile_config.get("api_keys", {})
        if not any(api_keys.values()):
            logger.warning("No API keys configured. Some features may not work.")
            
        return True