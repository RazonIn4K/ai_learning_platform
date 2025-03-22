"""AI Learning Platform with Topic Navigation and Multi-Agent Workspace capabilities."""

from .workspace import LearningWorkspace
from .agents import ResearchAgent, TopicNavigator
from .utils import EnvManager, ConfigLoader

__version__ = "0.1.0"
__all__ = [
    'LearningWorkspace',
    'ResearchAgent',
    'TopicNavigator',
    'EnvManager',
    'ConfigLoader'
]
