from ..workspace.workspace_template import WorkspaceTemplate
from pathlib import Path
import json

class VectorStrategistTemplate(WorkspaceTemplate):
    """Specialized template for VectorStrategist learning."""
    
    @classmethod
    def create_default(cls) -> 'VectorStrategistTemplate':
        """Create default VectorStrategist workspace."""
        template = cls("vectorstrategist")
        return template.build_workspace(
            domains=[
                "differential_geometry",
                "topology",
                "causal_inference",
                "dynamical_systems",
                "category_theory",
                "ai_security",
                "python_development"
            ],
            custom_config={
                "learning_style": "project_based",
                "tracking_level": "detailed",
                "project_focus": "security_manifolds"
            }
        )
    
    def load_project_context(self) -> None:
        """Load VectorStrategist-specific project context."""
        context_path = Path("configs/vectorstrategist_context.json")
        if context_path.exists():
            with open(context_path) as f:
                self.project_context = json.load(f)
    
    def get_recommended_path(self, topic: str) -> list:
        """Get VectorStrategist-specific learning path."""
        paths = {
            "prompt_injection": [
                "security_fundamentals",
                "llm_architecture",
                "prompt_engineering",
                "attack_vectors",
                "defense_strategies"
            ],
            "security_manifolds": [
                "differential_geometry_basics",
                "topological_analysis",
                "security_boundaries",
                "manifold_mapping"
            ]
        }
        return paths.get(topic, [])