"""Agent module initialization."""

from .base_agent import BaseLearningAgent
from .topic_navigator import TopicNavigatorAgent
from .connection_expert import ConnectionExpert
from .domain_expert import DomainExpertAgent
from .research_agent import ResearchAgent
from .knowledge_agent import KnowledgeAgent
from .coordinator import LearningCoordinatorAgent

__all__ = [
    'BaseLearningAgent',
    'TopicNavigatorAgent',
    'ConnectionExpert',
    'DomainExpertAgent',
    'ResearchAgent',
    'KnowledgeAgent',
    'LearningCoordinatorAgent'
]