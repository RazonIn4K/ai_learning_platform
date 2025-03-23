# ai_learning_platform/workspace/workspace_factory.py

from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path

from .learning_workspace import LearningWorkspace, WorkspaceConfig
from ..utils.topic_hierarchy import TopicHierarchy, create_default_hierarchy
from ..utils.knowledge_mapper import KnowledgeMapper
from ..utils.learning_profile_manager import LearningProfileManager
from ..utils.config_manager import ConfigManager
from ..utils.exceptions import ConfigurationError
from ..models.enhanced_model_manager import EnhancedModelManager

logger = logging.getLogger(__name__)

class WorkspaceFactory:
    """Factory for creating and configuring workspaces."""
    
    @classmethod
    def create_workspace(
        cls,
        workspace_type: str = 'default',
        config_overrides: Optional[Dict[str, Any]] = None,
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        use_camel: bool = False,
        use_openrouter: bool = False
    ) -> LearningWorkspace:
        """Create a configured workspace instance."""
        config_manager = ConfigManager()
        base_config = config_manager.get_config('workspace')
        
        # Apply type-specific configuration
        if workspace_type != 'default':
            type_config = config_manager.get_config('workspace_types').get(workspace_type, {})
            base_config.update(type_config)
        
        # Apply model provider overrides
        if model_provider or model_name or use_camel or use_openrouter:
            model_config = cls._create_model_config(
                model_provider, 
                model_name, 
                use_camel, 
                use_openrouter
            )
            base_config.update({"model": model_config})
        
        # Apply general overrides
        if config_overrides:
            base_config.update(config_overrides)
        
        # Create WorkspaceConfig instance
        workspace_config = WorkspaceConfig(
            domains=base_config.get('domains', ["general"]),
            enable_research=base_config.get('enable_research', False),
            learning_style=base_config.get('learning_style', "balanced"),
            model_type=base_config.get('model_type', "standard"),
            tracking_level=base_config.get('tracking_level', "detailed"),
            project_focus=base_config.get('project_focus', "general")
        )
        
        # Initialize the model manager
        model_manager = EnhancedModelManager()
        
        # Get user profile
        user_profile = config_manager.get_config('default_user_profile')
        
        # Create and return the workspace
        return LearningWorkspace(
            config=workspace_config,
            user_profile=user_profile,
            model_manager=model_manager
        )
    
    @classmethod
    def _create_model_config(
        cls,
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        use_camel: bool = False,
        use_openrouter: bool = False
    ) -> Dict[str, Any]:
        """Create model configuration."""
        if use_openrouter:
            provider = "openrouter"
        elif use_camel:
            provider = "camel"
        elif model_provider:
            provider = model_provider
        else:
            provider = "anthropic"  # Default to Anthropic
        
        # Determine appropriate model name if not specified
        if not model_name:
            if provider == "openai":
                model_name = "gpt-4o"
            elif provider == "anthropic":
                model_name = "claude-3-7-sonnet-20250219"
            elif provider == "google":
                model_name = "gemini-2.0-pro-exp-02-05"
            elif provider == "openrouter":
                model_name = "openai/gpt-4o"
            elif provider == "camel":
                model_name = "claude-3-7-sonnet"  # Model name for CAMEL to use
        
        return {
            "provider": provider,
            "model_name": model_name,
            "use_camel": use_camel,
            "temperature": 0.7,
            "max_tokens": 4000
        }
    
    @classmethod
    def quick_workspace(
        cls,
        provider: str = "anthropic",
        model: Optional[str] = None,
        domains: Optional[List[str]] = None
    ) -> LearningWorkspace:
        """Create a quick workspace with minimal configuration."""
        domains = domains or ["python", "machine_learning", "system_design"]
        return cls.create_workspace(
            config_overrides={
                "domains": domains,
                "enable_research": True,
                "learning_style": "balanced",
                "model_type": "standard"
            },
            model_provider=provider,
            model_name=model
        )
        
    @classmethod
    def create_vectorstrategist_workspace(
        cls,
        use_camel: bool = False,
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> LearningWorkspace:
        """Create a specialized VectorStrategist workspace."""
        return cls.create_workspace(
            workspace_type='vectorstrategist',
            model_provider=model_provider, 
            model_name=model_name, 
            use_camel=use_camel
        )
