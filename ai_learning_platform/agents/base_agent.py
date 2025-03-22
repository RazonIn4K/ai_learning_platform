from typing import Dict, Any, Optional, List, TypeVar, Union, Callable
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class BaseLearningAgent:
    def __init__(self, model_name: str, model_params: Dict[str, Any], system_message: Optional[str] = None):
        """Initialize the base learning agent.
        
        Args:
            model_name: Name of the model to use
            model_params: Parameters for the model
            system_message: Optional system message for the model
        """
        self.model_name = model_name
        self.model_params = model_params
        self.system_message = system_message
        self.user_profile = {}

    def update_user_profile(self, new_profile: Dict[str, Any]) -> None:
        """
        Update the agent's user profile.
        
        Args:
            new_profile: New user profile data
        """
        self.user_profile = new_profile
        
    def can_handle_topic(self, topic: str) -> bool:
        """
        Check if this agent can handle a specific topic.
        
        Args:
            topic: Topic to check
            
        Returns:
            True if the agent can handle the topic
        """
        # Base implementation - should be overridden by specialized agents
        return False
        
    def get_insights(self, topics: List[str]) -> Dict[str, Any]:
        """
        Get insights about specific topics.
        
        Args:
            topics: List of topics to analyze
            
        Returns:
            Dictionary containing insights about the topics
        """
        # Base implementation - should be overridden by specialized agents
        return {}

    def specialized_function(self, function_name: str, **kwargs) -> Any:
        """Execute specialized agent functions with error handling and validation."""
        try:
            # Validate function exists
            if not hasattr(self, f"_{function_name}"):
                available_functions = self.get_available_functions()
                raise ValueError(
                    f"Unknown specialized function '{function_name}'. "
                    f"Available functions: {', '.join(available_functions)}"
                )
            
            # Validate required parameters
            function = getattr(self, f"_{function_name}")
            self._validate_function_params(function, kwargs)
                
            logger.debug(
                f"Agent {self.__class__.__name__} executing {function_name}",
                extra={
                    "agent": self.__class__.__name__,
                    "function": function_name,
                    "kwargs": kwargs
                }
            )
            
            result = function(**kwargs)
            
            logger.debug(
                f"Successfully executed {function_name}",
                extra={
                    "agent": self.__class__.__name__,
                    "function": function_name,
                    "success": True
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error in {self.__class__.__name__}.{function_name}: {str(e)}",
                exc_info=True,
                extra={
                    "agent": self.__class__.__name__,
                    "function": function_name,
                    "error": str(e)
                }
            )
            raise

    def get_available_functions(self) -> List[str]:
        """Get list of available specialized functions."""
        return [
            name[1:] for name in dir(self) 
            if name.startswith('_') and callable(getattr(self, name))
            and not name.startswith('__')
        ]

    def _validate_function_params(self, func: Callable, params: Dict[str, Any]) -> None:
        """Validate parameters for specialized function."""
        import inspect
        sig = inspect.signature(func)
        required_params = {
            name for name, param in sig.parameters.items()
            if param.default == inspect.Parameter.empty
            and param.kind != inspect.Parameter.VAR_KEYWORD
        }
        missing_params = required_params - set(params.keys())
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
