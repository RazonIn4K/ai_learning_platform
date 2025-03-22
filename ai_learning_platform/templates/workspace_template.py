from ai_learning_platform.workspace import LearningWorkspace
from ai_learning_platform.workspace.workspace_config import WorkspaceConfig
from typing import List, Dict, Any
from pathlib import Path
import json

class WorkspaceTemplate:
    """Template for creating consistent learning workspaces."""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
        self.base_config = {
            "enable_research": True,
            "learning_style": "theory_to_practice",
            "model_type": "advanced",
            "tracking_level": "comprehensive"
        }
    
    @classmethod
    def create_vectorstrategist_workspace(cls) -> LearningWorkspace:
        """Create a pre-configured workspace for VectorStrategist projects."""
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
            ]
        )
    
    @classmethod
    def create_ml_security_workspace(cls) -> LearningWorkspace:
        """Create a pre-configured workspace for ML security projects."""
        template = cls("ml_security")
        return template.build_workspace(
            domains=[
                "machine_learning",
                "cybersecurity",
                "python_development",
                "data_science"
            ]
        )
    
    def build_workspace(
        self,
        domains: List[str],
        custom_config: Dict[str, Any] = None
    ) -> LearningWorkspace:
        """Build a workspace with specified configuration."""
        config = self.base_config.copy()
        if custom_config:
            config.update(custom_config)
            
        workspace_config = WorkspaceConfig(
            domains=domains,
            **config
        )
        
        return LearningWorkspace(workspace_config)
    
    def save_workspace_state(
        self,
        workspace: LearningWorkspace,
        save_path: str
    ) -> None:
        """Save workspace state for later restoration."""
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        config_path = save_dir / f"{self.template_name}_config.json"
        with open(config_path, "w") as f:
            json.dump(workspace.config.to_dict(), f, indent=2)
            
        # Save learning progress if available
        if hasattr(workspace, "profile_manager"):
            progress_path = save_dir / f"{self.template_name}_progress.json"
            progress_data = workspace.profile_manager.get_learning_progress()
            with open(progress_path, "w") as f:
                json.dump(progress_data, f, indent=2)
    
    @classmethod
    def load_workspace_state(
        cls,
        template_name: str,
        load_path: str
    ) -> LearningWorkspace:
        """Load a previously saved workspace state."""
        load_dir = Path(load_path)
        
        # Load configuration
        config_path = load_dir / f"{template_name}_config.json"
        with open(config_path) as f:
            config_data = json.load(f)
            
        # Create workspace with saved configuration
        template = cls(template_name)
        workspace = template.build_workspace(
            domains=config_data["domains"],
            custom_config={
                k: v for k, v in config_data.items()
                if k != "domains"
            }
        )
        
        # Load progress if available
        progress_path = load_dir / f"{template_name}_progress.json"
        if progress_path.exists():
            with open(progress_path) as f:
                progress_data = json.load(f)
                workspace.profile_manager.load_progress(progress_data)
        
        return workspace