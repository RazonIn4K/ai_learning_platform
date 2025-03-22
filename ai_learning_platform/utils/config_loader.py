"""Configuration loader for the AI Learning Platform."""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    provider: str
    model_name: str
    temperature: float
    max_tokens: int

@dataclass
class LearningConfig:
    mastery_threshold: float
    session_duration: int
    topics_per_session: int

@dataclass
class PlatformConfig:
    model: ModelConfig
    learning: LearningConfig
    workspace_dir: Path
    log_level: str
    storage: Dict[str, Any]
    logging: Dict[str, Any]

class ConfigLoader:
    """Loads and manages platform configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "configs/workspace_config.json"
        
    def get_config(self) -> Dict[str, Any]:
        """Get the platform configuration."""
        # Default configuration
        default_config = {
            "model": {
                "provider": "anthropic",
                "model_name": "claude-3-7-sonnet-20250219",
                "temperature": 0.3,
                "max_tokens": 3000
            },
            "learning": {
                "mastery_threshold": 0.9,
                "session_duration": 1800,
                "topics_per_session": 2
            },
            "storage": {
                "path": "data/progress"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "workspace_dir": "workspace_data",
            "log_level": "INFO"
        }
        
        # Try to load custom config
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path) as f:
                    custom_config = json.load(f)
                    # Merge custom config with defaults
                    default_config.update(custom_config)
        except Exception as e:
            logger.warning(f"Failed to load custom config: {str(e)}")
            
        return default_config

def get_config_loader() -> ConfigLoader:
    """Get the singleton config loader instance."""
    return ConfigLoader()
