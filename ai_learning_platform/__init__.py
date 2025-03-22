"""AI Learning Platform with Topic Navigation and Multi-Agent Workspace capabilities."""

from .core.smart_learning_agent import SmartLearningAgent
from .core.learning_workspace import LearningWorkspace
from .core.workspace_config import WorkspaceConfig
from .utils.env_manager import EnvManager
from .utils.config_loader import ConfigLoader
from .tracking.progress_tracker import ProgressTracker
from .tracking.learning_metrics import LearningMetrics

__version__ = "0.1.0"

__all__ = [
    'SmartLearningAgent',
    'LearningWorkspace',
    'WorkspaceConfig',
    'EnvManager',
    'ConfigLoader',
    'ProgressTracker',
    'LearningMetrics',
]
