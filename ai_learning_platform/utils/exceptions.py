# In ai_learning_platform/utils/exceptions.py

class AILearningPlatformError(Exception):
    """Base exception for all AI Learning Platform errors."""
    pass

class TopicHierarchyError(AILearningPlatformError):
    """Raised when there's an error in the topic hierarchy or its operation fails."""
    pass

class KnowledgeBaseError(AILearningPlatformError):
    """Raised when there's an error in the knowledge base or its operation fails."""
    pass

class AgentOperationError(AILearningPlatformError):
    """Raised when an agent operation fails or is not supported."""
    pass

class ModelError(AILearningPlatformError):
    """Raised when there's an error in the model or its operation fails."""
    pass

class CoordinationError(AILearningPlatformError):
    """Raised when there's an error in agent coordination or its operation fails."""
    pass

class WorkspaceError(AILearningPlatformError):
    """Raised when there's an error in the learning workspace or its operation fails."""
    pass

class ConfigurationError(AILearningPlatformError):
    """Raised when there's an error in the configuration or its operation fails."""
    pass

class LearningPathError(AILearningPlatformError):
    """Raised when there's an error in the learning path or its operation fails."""
    pass

class ProfileError(AILearningPlatformError):
    """Raised when there's an error in the user profile or its operation fails."""
    pass

