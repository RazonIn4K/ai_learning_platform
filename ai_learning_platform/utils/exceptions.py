# ai_learning_platform/utils/exceptions.py

class LearningPlatformError(Exception):
    """Base exception for all AI Learning Platform errors."""
    pass

class ModelError(LearningPlatformError):
    """Raised when a model operation fails."""
    pass

class AgentError(LearningPlatformError):
    """Raised when an agent operation fails."""
    pass

class CredentialError(LearningPlatformError):
    """Raised when credential validation fails."""
    pass

class ConfigError(LearningPlatformError):
    """Raised when configuration is invalid or missing."""
    pass

class RateLimitError(ModelError):
    """Raised when a rate limit is hit for a model API."""
    pass

class TokenLimitError(ModelError):
    """Raised when a token limit is exceeded."""
    pass

class ModelResponseError(ModelError):
    """Raised when a model response is invalid or contains errors."""
    pass

class ValidationError(LearningPlatformError):
    """Raised when validation fails for inputs or outputs."""
    pass

class ContentFilterError(ValidationError):
    """Raised when content is filtered due to safety concerns."""
    pass

class QualityCheckError(ValidationError):
    """Raised when quality checks fail for model responses."""
    pass