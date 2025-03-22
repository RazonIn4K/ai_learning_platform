from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class AgentConfig:
    confidence_threshold: float = 0.7
    max_retries: int = 3
    default_timeout: int = 30
    fallback_enabled: bool = True
    cache_enabled: bool = True
    
    # Enhanced granular settings
    performance_settings: Dict[str, Any] = field(default_factory=lambda: {
        "batch_size": 32,
        "concurrent_requests": 4,
        "request_timeout": 15,
        "cache_ttl": 3600
    })
    
    retry_settings: Dict[str, Any] = field(default_factory=lambda: {
        "backoff_factor": 1.5,
        "max_backoff": 60,
        "jitter": True,
        "retry_on_errors": ["timeout", "rate_limit"]
    })
    
    model_settings: Dict[str, Any] = field(default_factory=lambda: {
        "temperature_ranges": {
            "creative": (0.7, 0.9),
            "balanced": (0.3, 0.7),
            "precise": (0.1, 0.3)
        },
        "context_window": 8192,
        "response_format": "json"
    })
    
    # Domain-specific settings
    domains: List[str] = None
    expertise_levels: List[str] = None
    resource_types: List[str] = None
    
    def __post_init__(self):
        self.domains = self.domains or ["web", "mobile", "data", "security", "cloud"]
        self.expertise_levels = self.expertise_levels or ["beginner", "intermediate", "advanced"]
        self.resource_types = self.resource_types or ["text", "video", "interactive"]
