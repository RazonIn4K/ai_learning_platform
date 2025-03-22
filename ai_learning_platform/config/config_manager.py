from typing import Any, Dict, Optional
from pathlib import Path
import yaml
import json
from dataclasses import dataclass
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConfigurationError(Exception):
    """Configuration-related errors."""
    message: str
    details: Optional[Dict[str, Any]] = None

class ConfigManager:
    """Centralized configuration management."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config_paths = {
                'base': Path('configs/base_config.yaml'),
                'models': Path('configs/models_config.yaml'),
                'workspace': Path('configs/workspace_config.yaml'),
                'agents': Path('configs/agents_config.yaml')
            }
            self.configs = {}
            self.initialized = True
            self._load_all_configs()
    
    def _load_all_configs(self) -> None:
        """Load all configuration files."""
        for config_type, path in self.config_paths.items():
            try:
                self.configs[config_type] = self._load_config(path)
            except Exception as e:
                logger.error(f"Failed to load {config_type} config: {str(e)}")
                raise ConfigurationError(
                    f"Configuration loading failed for {config_type}",
                    {'path': str(path), 'error': str(e)}
                )
    
    @lru_cache(maxsize=32)
    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load and cache a configuration file."""
        if not path.exists():
            raise ConfigurationError(f"Config file not found: {path}")
            
        try:
            with path.open('r') as f:
                if path.suffix == '.yaml':
                    return yaml.safe_load(f)
                return json.load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to parse config file: {path}", {'error': str(e)})
    
    def get_config(self, component: str) -> Dict[str, Any]:
        """Get configuration for a specific component."""
        if component not in self.configs:
            raise ConfigurationError(f"Unknown component configuration: {component}")
        return self.configs[component].copy()
    
    def update_config(self, component: str, updates: Dict[str, Any]) -> None:
        """Update configuration for a component."""
        if component not in self.configs:
            raise ConfigurationError(f"Cannot update unknown component: {component}")
            
        self.configs[component].update(updates)
        
        # Persist changes if needed
        path = self.config_paths[component]
        with path.open('w') as f:
            if path.suffix == '.yaml':
                yaml.dump(self.configs[component], f)
            else:
                json.dump(self.configs[component], f, indent=2)
    
    def validate_config(self, component: str) -> bool:
        """Validate component configuration."""
        validators = {
            'models': self._validate_models_config,
            'workspace': self._validate_workspace_config,
            'agents': self._validate_agents_config
        }
        
        if component not in validators:
            raise ConfigurationError(f"No validator for component: {component}")
            
        return validators[component](self.configs[component])
    
    def _validate_models_config(self, config: Dict[str, Any]) -> bool:
        """Enhanced validation for models configuration."""
        # Basic field validation
        required_fields = {'provider', 'model_name', 'temperature', 'max_tokens'}
        if not all(field in config for field in required_fields):
            raise ConfigurationError("Missing required fields in models config")
        
        # Value range validation
        if not 0 <= config['temperature'] <= 1:
            raise ConfigurationError("Temperature must be between 0 and 1")
        if not 0 < config['max_tokens'] <= 8192:
            raise ConfigurationError("max_tokens must be between 1 and 8192")
            
        # Provider-specific validation
        if config['provider'] == 'anthropic':
            if not config['model_name'].startswith('claude-'):
                raise ConfigurationError("Invalid Anthropic model name")
        
        # Fallback configuration validation
        if 'fallback_models' in config:
            for fallback in config['fallback_models']:
                if not all(field in fallback for field in required_fields):
                    raise ConfigurationError("Invalid fallback model configuration")
                if fallback['provider'] == config['provider'] and \
                   fallback['model_name'] == config['model_name']:
                    raise ConfigurationError("Fallback model cannot be same as primary")
        
        return True
    
    def _validate_workspace_config(self, config: Dict[str, Any]) -> bool:
        """Validate workspace configuration."""
        required_fields = {'domains', 'enable_research', 'learning_style'}
        if not all(field in config for field in required_fields):
            raise ConfigurationError("Missing required fields in workspace config")
        return True
    
    def _validate_agents_config(self, config: Dict[str, Any]) -> bool:
        """Validate agents configuration."""
        required_fields = {'agent_types', 'default_timeout', 'max_retries'}
        if not all(field in config for field in required_fields):
            raise ConfigurationError("Missing required fields in agents config")
        return True
