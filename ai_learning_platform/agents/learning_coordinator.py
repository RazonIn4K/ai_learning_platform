import logging
from typing import Dict, Any, Optional

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class LearningCoordinatorAgent(BaseAgent):
    """Agent responsible for coordinating learning activities."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the coordinator agent."""
        super().__init__(config)
        self.config = config  # Ensure config is stored
        self.domain_experts = {}
    
    def process_message(self, message: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process an incoming message by routing it to the appropriate agent."""
        try:
            context = user_context or {}
            
            # Analyze the message to determine its type
            analysis = self._analyze_message(message, context)
            message_type = analysis.get("query_type", "general_query")
            
            # Update context with analysis
            context.update({
                "analysis": analysis,
                "domain": analysis.get("domains", ["general"])[0]
            })
            
            # Route to appropriate agent
            response = self._route_message_to_agents(message_type, message, context)
            
            # If this is a learning path request, ensure we have a valid path
            if message_type == "learning_path_query":
                if "path" not in response or not isinstance(response["path"], list):
                    response["path"] = []
                    logger.warning("Learning path response did not contain valid path")
            
            # Include analysis in response for debugging
            response["analysis"] = analysis
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return {
                "content": "Error processing your request",
                "error": str(e),
                "agent": self.__class__.__name__
            }
    
    def handle_agent_error(self, agent_type: str, function_name: str, 
                          error: Exception, query: str, 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors from delegated agent operations."""
        return {
            "success": False,
            "error": str(error),
            "content": "An error occurred during processing",
            "fallback_response": "Using fallback processing path",
            "error_details": {
                "agent": agent_type,
                "function": function_name,
                "query": query,
                "context": context
            }
        }
    
    def delegate_specialized_function(self, agent_type: str, function_name: str, **kwargs) -> Any:
        """Delegate a specialized function to the appropriate agent."""
        try:
            if agent_type == "topic_navigator":
                from .topic_navigator import TopicNavigatorAgent
                # Pass the stored config to the new agent
                agent = TopicNavigatorAgent(self.config)
                func = getattr(agent, function_name)
                result = func(**kwargs)
                
                # Ensure we always return a list for adapt_learning_path
                if function_name == "adapt_learning_path":
                    return result if isinstance(result, list) else []
                    
                return result
                
        except Exception as e:
            logger.error(f"Error delegating to {agent_type}.{function_name}: {str(e)}")
            return [] if function_name == "adapt_learning_path" else None