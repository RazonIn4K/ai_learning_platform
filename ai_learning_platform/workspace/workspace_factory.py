"""Factory for creating and configuring learning workspaces."""

from typing import Dict, Any, Optional
import logging
import json
from pathlib import Path

from .learning_workspace import LearningWorkspace, WorkspaceConfig
from ..utils.topic_hierarchy import TopicHierarchy, create_default_hierarchy
from ..utils.knowledge_mapper import KnowledgeMapper
from ..utils.learning_profile_manager import LearningProfileManager
from ..utils.config_manager import ConfigManager
from ..utils.exceptions import ConfigurationError
from ..config import ConfigManager
from ..models import ModelManager
from ..agents import AgentRegistry

logger = logging.getLogger(__name__)

class WorkspaceFactory:
    """Factory for creating and configuring workspaces."""
    
    @classmethod
    def create_workspace(
        cls,
        workspace_type: str,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> LearningWorkspace:
        """Create a configured workspace instance."""
        config_manager = ConfigManager()
        base_config = config_manager.get_config('workspace')
        
        # Apply type-specific configuration
        if workspace_type != 'default':
            type_config = config_manager.get_config(f'workspace_types').get(workspace_type, {})
            base_config.update(type_config)
        
        # Apply overrides
        if config_overrides:
            base_config.update(config_overrides)
        
        # Validate final configuration
        config_manager.validate_config('workspace')
        
        # Initialize required components
        model_manager = ModelManager()
        agents = cls._initialize_agents(base_config)
        
        return LearningWorkspace(
            config=base_config,
            model_manager=model_manager,
            agents=agents
        )
    
    @classmethod
    def _initialize_agents(
        cls,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize required agents for the workspace."""
        agent_registry = AgentRegistry()
        agents = {}
        
        for agent_type in config.get('required_agents', []):
            agents[agent_type] = agent_registry.create_agent(agent_type, config)
            
        return agents
    
    @classmethod
    def create_vectorstrategist_workspace(
        cls,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> LearningWorkspace:
        """Create a specialized VectorStrategist workspace."""
        return cls.create_workspace('vectorstrategist', config_overrides)
    
    @classmethod
    def _load_configuration(cls, config_path: Optional[str]) -> WorkspaceConfig:
        """Load workspace configuration from file or defaults."""
        try:
            if config_path:
                config_manager = ConfigManager()
                config_data = config_manager.load_json_config(config_path)
                return WorkspaceConfig(**config_data)
            else:
                # Default configuration
                return WorkspaceConfig(
                    domains=["general"],
                    enable_research=False,
                    learning_style="balanced",
                    model_type="standard",
                    tracking_level="basic"
                )
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Configuration loading failed: {str(e)}")
    
    @classmethod
    def _initialize_topic_hierarchy(cls) -> TopicHierarchy:
        """Initialize topic hierarchy component."""
        return create_default_hierarchy()
    
    @classmethod
    def _initialize_knowledge_mapper(cls, topic_hierarchy: TopicHierarchy) -> KnowledgeMapper:
        """Initialize knowledge mapper component."""
        return KnowledgeMapper(topic_hierarchy=topic_hierarchy)
    
    @classmethod
    def _initialize_profile_manager(cls, user_profile: Optional[Dict[str, Any]]) -> LearningProfileManager:
        """Initialize learning profile manager."""
        profile_manager = LearningProfileManager()
        
        # If user profile provided, ensure it's registered
        if user_profile and "user_id" in user_profile:
            if not profile_manager.profile_exists(user_profile["user_id"]):
                profile_manager.create_profile(user_profile)
        
        return profile_manager
    
    @classmethod
    def load_workspace(cls, workspace_path: str) -> LearningWorkspace:
        """
        Load a previously saved workspace.
        
        Args:
            workspace_path: Path to saved workspace
            
        Returns:
            Loaded LearningWorkspace instance
        """
        try:
            workspace_dir = Path(workspace_path)
            
            # Load configuration
            config_path = workspace_dir / "config.json"
            with open(config_path) as f:
                config_data = json.load(f)
            
            # Load user profile
            profile_path = workspace_dir / "profile.json"
            with open(profile_path) as f:
                user_profile = json.load(f)
            
            # Create workspace with saved configuration
            workspace = cls.create_workspace(
                config_path=str(config_path),
                user_profile=user_profile
            )
            
            # Load additional state if needed
            cls._load_workspace_state(workspace, workspace_dir)
            
            logger.info(f"Loaded workspace from {workspace_path}")
            return workspace
            
        except Exception as e:
            logger.error(f"Failed to load workspace: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Workspace loading failed: {str(e)}")
    
    @classmethod
    def _load_workspace_state(cls, workspace: LearningWorkspace, workspace_dir: Path) -> None:
        """
        Load additional workspace state.
        
        Args:
            workspace: LearningWorkspace instance
            workspace_dir: Directory containing workspace state
        """
        # Load learning history
        history_path = workspace_dir / "learning_history.json"
        if history_path.exists():
            with open(history_path, "r") as f:
                history_data = json.load(f)
                workspace.profile_manager.load_history(
                    workspace.user_profile["user_id"],
                    history_data
                )
        
        # Load knowledge graph if available
        knowledge_path = workspace_dir / "knowledge_graph.json"
        if knowledge_path.exists():
            # Fix: Call the knowledge_mapper's load_graph method
            workspace.knowledge_mapper.load_graph(str(knowledge_path))
    
    @classmethod
    def save_workspace(cls, workspace: LearningWorkspace, output_dir: str) -> str:
        """
        Save workspace state to disk.
        
        Args:
            workspace: Workspace to save
            output_dir: Directory to save workspace in
            
        Returns:
            Path to saved workspace
        """
        try:
            workspace_dir = Path(output_dir)
            workspace_dir.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            config_path = workspace_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(workspace.config.__dict__, f, indent=2)
            
            # Save user profile if available
            if workspace.user_profile:
                profile_path = workspace_dir / "profile.json"
                with open(profile_path, "w") as f:
                    json.dump(workspace.user_profile, f, indent=2)
            
            # Save learning history if available
            if workspace.profile_manager and workspace.user_profile.get("user_id"):
                # Fix: Call the profile_manager's get_learning_history method
                history = workspace.profile_manager.get_learning_history(
                    workspace.user_profile["user_id"]
                )
                if history:
                    history_path = workspace_dir / "learning_history.json"
                    with open(history_path, "w") as f:
                        json.dump(history, f, indent=2)
            
            logger.info(f"Workspace saved to {workspace_dir}")
            return str(workspace_dir)
            
        except Exception as e:
            logger.error(f"Failed to save workspace: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Workspace saving failed: {str(e)}")
