"""Custom exceptions for the AI Learning Platform."""

class CoordinationError(Exception):
    """Raised when there is an error in agent coordination."""
    pass

class AgentError(Exception):
    """Raised when there is an error in agent operation."""
    pass

class WorkspaceError(Exception):
    """Raised when there is an error in workspace operation."""
    pass

class ModelError(Exception):
    """Raised when there is an error in model operation."""
    pass

class ConfigurationError(Exception):
    """Raised when there is an error in configuration."""
    pass