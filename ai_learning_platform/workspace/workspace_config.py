from typing import Dict, Any, List
from dataclasses import dataclass, asdict

@dataclass
class WorkspaceConfig:
    """Configuration for the learning workspace."""
    domains: List[str]
    enable_research: bool
    learning_style: str
    model_type: str
    tracking_level: str
    project_focus: str

    def __init__(
        self,
        domains: List[str] = None,
        enable_research: bool = False,
        learning_style: str = "balanced",
        model_type: str = "standard",
        tracking_level: str = "basic",
        project_focus: str = "general"
    ):
        self.domains = domains or ["general"]
        self.enable_research = enable_research
        self.learning_style = learning_style
        self.model_type = model_type
        self.tracking_level = tracking_level
        self.project_focus = project_focus
        self._validate()

    def _validate(self):
        """Validate configuration values."""
        if not self.domains:
            self.domains = ["general"]
        if self.learning_style not in ["balanced", "self_taught", "guided"]:
            self.learning_style = "balanced"
        if self.tracking_level not in ["basic", "detailed"]:
            self.tracking_level = "basic"

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "domains": self.domains,
            "enable_research": self.enable_research,
            "learning_style": self.learning_style,
            "model_type": self.model_type,
            "tracking_level": self.tracking_level,
            "project_focus": self.project_focus
        }
