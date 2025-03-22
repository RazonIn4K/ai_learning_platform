from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AgentConfig:
    confidence_threshold: float = 0.7
    max_retries: int = 3
    default_timeout: int = 30
    fallback_enabled: bool = True
    cache_enabled: bool = True
    
    # Domain-specific settings
    domains: List[str] = None
    expertise_levels: List[str] = None
    resource_types: List[str] = None
    
    def __post_init__(self):
        self.domains = self.domains or ["web", "mobile", "data", "security", "cloud"]
        self.expertise_levels = self.expertise_levels or ["beginner", "intermediate", "advanced"]
        self.resource_types = self.resource_types or ["text", "video", "interactive"]