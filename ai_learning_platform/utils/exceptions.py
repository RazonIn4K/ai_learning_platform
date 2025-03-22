# In ai_learning_platform/utils/exceptions.py

class AILearningPlatformError(Exception):
    """Base exception for all AI Learning Platform errors."""
    pass

class TopicNotFoundError(AILearningPlatformError):
    """Raised when a topic is not found in the hierarchy."""
    pass

class KnowledgeBaseError(AILearningPlatformError):
    """Raised when there's an error accessing the knowledge base."""
    pass

class AgentOperationError(AILearningPlatformError):
    """Raised when an agent operation fails."""
    pass

class ModelError(AILearningPlatformError):
    """Raised when there's an error with a model."""
    pass

class CoordinationError(AILearningPlatformError):
    """Raised when there's an error coordinating multiple agents."""
    pass

class WorkspaceError(AILearningPlatformError):
    """Raised when there's an error in the learning workspace."""
    pass

class ConfigurationError(AILearningPlatformError):
    """Raised when there's an error in the configuration."""
    pass

class ConfigurationError(AILearningPlatformError):
    """Raised when there's an error in configuration."""
    pass

class LearningPathError(AILearningPlatformError):
    """Raised when there's an error creating a learning path."""
    pass

class ProfileError(AILearningPlatformError):
    """Raised when there's an error with a user profile."""
    pass

class WorkspaceError(AILearningPlatformError):
    """Raised when there's an error in the learning workspace."""
    pass