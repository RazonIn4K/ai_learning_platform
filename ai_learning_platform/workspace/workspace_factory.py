"""Factory for creating and configuring learning workspaces."""

from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path

from .learning_workspace import LearningWorkspace, WorkspaceConfig
from ..utils.topic_hierarchy import TopicHierarchy
from ..utils.knowledge_mapper import KnowledgeMapper
from ..utils.learning_profile_manager import LearningProfileManager
from ..utils.config_loader import ConfigLoader
from ..utils.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class WorkspaceFactory:
    """Factory for creating and configuring learning workspaces."""
    
    @classmethod
    def create_workspace(
        cls,
        config_path: Optional[str] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        domains: Optional[List[str]] = None,
        model_type: str = "standard"
    ) -> LearningWorkspace:
        """
        Create a configured learning workspace.
        
        Args:
            config_path: Path to workspace configuration file
            user_profile: User profile information
            domains: List of domain names to include
            model_type: Type of model to use (standard, enhanced, etc.)
            
        Returns:
            Configured LearningWorkspace instance
        """
        # Load configuration
        config = cls._load_configuration(config_path)
        
        # Override with provided parameters
        if domains:
            config.domains = domains
        if model_type:
            config.model_type = model_type
            
        # Initialize components
        topic_hierarchy = cls._initialize_topic_hierarchy()
        knowledge_mapper = cls._initialize_knowledge_mapper(topic_hierarchy)
        profile_manager = cls._initialize_profile_manager(user_profile)
        
        # Create workspace
        workspace = LearningWorkspace(
            config=config,
            user_profile=user_profile,
            topic_hierarchy=topic_hierarchy,
            knowledge_mapper=knowledge_mapper,
            profile_manager=profile_manager
        )
        
        logger.info(f"Created workspace with {len(config.domains)} domains and {config.model_type} model type")
        return workspace
    
    @classmethod
    def _load_configuration(cls, config_path: Optional[str]) -> WorkspaceConfig:
        """Load workspace configuration from file or defaults."""
        try:
            if config_path:
                config_loader = ConfigLoader()
                config_data = config_loader.load_json_config(config_path)
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
        return TopicHierarchy()
    
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
            with open(config_path, "r") as f:
                config_data = json.load(f)
            
            # Load user profile
            profile_path = workspace_dir / "profile.json"
            with open(profile_path, "r") as f:
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
        """Load additional workspace state."""
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
