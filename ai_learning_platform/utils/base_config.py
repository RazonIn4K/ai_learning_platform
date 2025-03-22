from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class BaseConfig:
    confidence_threshold: float = 0.7
    max_retries: int = 3
    default_timeout: int = 30
    domains: List[str] = field(default_factory=lambda: ["web", "mobile", "data"])
    model_settings: Dict[str, Any] = field(default_factory=lambda: {
        "temperature": 0.7,
        "max_tokens": 2000
    })
    
    def get_domain_config(self, domain: str) -> Dict[str, Any]:
        return self.domain_specific.get(domain, {})
