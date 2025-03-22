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

class ConfigLoader:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("configs/workspace_config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> PlatformConfig:
        with open(self.config_path) as f:
            data = json.load(f)
        return PlatformConfig(
            model=ModelConfig(**data["model"]),
            learning=LearningConfig(**data["learning"]),
            workspace_dir=Path(data["workspace"]["state_dir"]),
            log_level=data["workspace"]["log_level"]
        )
    
    def get_config(self) -> PlatformConfig:
        return self.config

def get_config_loader() -> ConfigLoader:
    """Get the singleton config loader instance."""
    return ConfigLoader()
