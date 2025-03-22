from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from .config_loader import ConfigLoader

logger = logging.getLogger(__name__)

@dataclass
class UnifiedConfig:
    """Single source of truth for all configuration settings"""
    model: Dict[str, Any]
    learning: Dict[str, Any]
    workspace: Dict[str, Any]
    storage: Dict[str, Any]
    logging: Dict[str, Any]
    domains: list
    default_user_profile: Dict[str, Any]
    model_configurations: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'UnifiedConfig':
        return cls(**config_dict)

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config_loader = ConfigLoader()
            self.unified_config = None
            self.initialized = True
    
    def initialize(self, config_path: Optional[str] = None) -> None:
        """Initialize configuration from file or defaults"""
        config_dict = self.config_loader.load_config(config_path)
        self.unified_config = UnifiedConfig.from_dict(config_dict)
        
    def get_config(self) -> UnifiedConfig:
        """Get the unified configuration"""
        if self.unified_config is None:
            self.initialize()
        return self.unified_config
    
    def get_component_config(self, component_name: str) -> Dict[str, Any]:
        """Get configuration for a specific component"""
        config_dict = asdict(self.get_config())
        return config_dict.get(component_name, {})