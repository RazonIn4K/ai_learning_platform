from typing import Dict, Any, Optional, List, TypeVar, Union, Callable
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class BaseLearningAgent:
    """
    Base class for all learning agents in the platform.
    
    The BaseLearningAgent provides a foundation for specialized agents with common
    functionality for processing queries, handling errors, and executing specialized functions.
    It implements a pattern where specialized functionality is exposed through a unified
    interface that handles validation, error handling, and logging.
    
    Key Design Patterns:
    - Template Method: The process_query method defines a skeleton algorithm that specialized
      agents can customize by overriding the _analyze_query method.
    - Facade: Provides a simplified interface to the complex subsystem of model interactions.
    - Strategy: Different agent implementations can be swapped in as different strategies for
      handling learning queries.
    
    Usage:
    Specialized agents should inherit from this class and implement the _analyze_query method
    at minimum. Additional specialized functionality should be implemented as methods starting
    with an underscore, which can then be called through the specialized_function method.
    """
    
    def __init__(self, model_name: str, model_params: Dict[str, Any], system_message: Optional[str] = None):
        """Initialize the base learning agent.
        
        Args:
            model_name: Name of the model to use (e.g., "gpt-4", "claude-3-sonnet")
            model_params: Parameters for the model (e.g., temperature, max_tokens)
            system_message: Optional system message for the model that defines its behavior
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
        """
        Execute specialized agent functions with error handling and validation.
        
        This method implements a controlled access pattern for specialized functionality,
        providing a unified interface with consistent error handling, parameter validation,
        and logging. It's designed to make specialized agent capabilities more robust and
        maintainable by centralizing common concerns.
        
        The pattern works as follows:
        1. Validate that the requested function exists (must be prefixed with '_')
        2. Validate that all required parameters are provided
        3. Execute the function with appropriate logging
        4. Handle and log any exceptions that occur
        
        Args:
            function_name: Name of the specialized function to execute (without '_' prefix)
            **kwargs: Parameters to pass to the specialized function
            
        Returns:
            Result of the specialized function
            
        Raises:
            ValueError: If the function doesn't exist or required parameters are missing
            Various exceptions: Any exceptions raised by the specialized function
            
        Example:
            ```python
            # Define a specialized function in your agent subclass
            def _calculate_topic_similarity(self, topic1: str, topic2: str) -> float:
                # Implementation...
                
            # Call it through the specialized_function interface
            similarity = agent.specialized_function(
                "calculate_topic_similarity",
                topic1="python",
                topic2="programming"
            )
            ```
        """
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
            
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user query and return a response.
        
        Args:
            query: The user's query
            context: Optional context information
            
        Returns:
            Dictionary containing the response
        """
        try:
            # Default implementation - analyze the query and return a response
            analysis = self._analyze_query(query, context or {})
            
            # Process the query based on the analysis
            return {
                "content": f"Processed query: {query[:50]}...",
                "analysis": analysis,
                "agent": self.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                "content": "I encountered an error processing your query.",
                "error": str(e),
                "agent": self.__class__.__name__
            }
            
    def _analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a user query to determine its characteristics.
        
        Args:
            query: The user's query
            context: Context information
            
        Returns:
            Dictionary with analysis results
        """
        # Base implementation - should be overridden by specialized agents
        return {
            "query_type": "general",
            "complexity": "medium",
            "topics": []
        }
