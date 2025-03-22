import logging
from typing import Dict, Any, Optional

from .base_agent import BaseAgent
from ..workspace.learning_workspace import WorkspaceConfig

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
    
class Coordinator:
    """
    Coordinates messages between different specialized agents.
    """
    
    def __init__(self, 
                 model_name: str = "gpt-4", 
                 model_params: Optional[Dict[str, Any]] = None,
                 topic_navigator=None,
                 knowledge_agent=None,
                 research_agent=None,
                 connection_expert=None):
        """
        Initialize the coordinator.
        
        Args:
            model_name: Name of the base model to use
            model_params: Parameters for the model
            topic_navigator: Agent for topic navigation
            knowledge_agent: Agent for knowledge retrieval
            research_agent: Agent for research
            connection_expert: Agent for finding connections
        """
        self.model_name = model_name
        self.model_params = model_params or {"temperature": 0.7, "max_tokens": 1024}
        
        # Initialize component agents
        self.topic_navigator = topic_navigator
        self.knowledge_agent = knowledge_agent
        self.research_agent = research_agent
        self.connection_expert = connection_expert
        
        # Cache for domain experts
        self.domain_experts = {}
    
    def process_message(self, message: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process an incoming message by routing it to the appropriate agent.
        
        Args:
            message: The user's message
            user_context: Optional user context information
            
        Returns:
            Dictionary containing the response
        """
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
        
        # Include analysis in response for debugging
        response["analysis"] = analysis
        
        return response
    
    def _analyze_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a message to determine its characteristics.
        
        Args:
            message: The message to analyze
            context: Additional context
            
        Returns:
            Dictionary with analysis results
        """
        # In a real implementation, this would call the model to analyze the message
        # For now, use a simple rule-based approach
        analysis = {"confidence_score": 0.8}
        
        # Check for keywords to determine message type
        message_lower = message.lower()
        
        if "how are" in message_lower or "what is the connection" in message_lower:
            analysis["query_type"] = "connection_query"
            analysis["required_agents"] = ["connection_expert"]
        elif "learning path" in message_lower or "how do i learn" in message_lower:
            analysis["query_type"] = "learning_path_query"
            analysis["required_agents"] = ["topic_navigator"]
        elif "research" in message_lower or "find information" in message_lower:
            analysis["query_type"] = "research_query"
            analysis["required_agents"] = ["research_agent"]
        elif "what is" in message_lower or "explain" in message_lower:
            analysis["query_type"] = "domain_query"
            analysis["required_agents"] = ["domain_expert"]
        else:
            analysis["query_type"] = "knowledge_query"
            analysis["required_agents"] = ["knowledge_agent"]
        
        # Extract domains from context or use general
        analysis["domains"] = context.get("domains", ["general"])
        
        # Extract complexity level
        if "advanced" in message_lower or "complex" in message_lower:
            analysis["complexity"] = "advanced"
        else:
            analysis["complexity"] = "basic"
        
        return analysis
    
    def _route_message_to_agents(self, message_type: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route the message to the appropriate agent based on its type.
        
        Args:
            message_type: The type of the message
            message: The message content
            context: Additional context
            
        Returns:
            Dictionary containing the agent's response
        """
        if message_type == "connection_query":
            return self.connection_expert.handle_message(message, context)
        elif message_type == "learning_path_query":
            return self.topic_navigator.handle_message(message, context)
        elif message_type == "research_query":
            return self.research_agent.handle_message(message, context)
        elif message_type == "domain_query":
            domain = context["domain"]
            if domain not in self.domain_experts:
                self.domain_experts[domain] = self._create_domain_expert(domain)
            return self.domain_experts[domain].handle_message(message, context)
        else:
            return self.knowledge_agent.handle_message(message, context)
    
    def _create_domain_expert(self, domain: str):
        """
        Create a domain expert for a specific domain.
        
        Args:
            domain: The domain for which to create an expert
            
        Returns:
            The created domain expert
        """
        # In a real implementation, this would create and return a domain expert
        # For now, return a mock object
        return MockDomainExpert(domain)
    
class MockDomainExpert:
    def __init__(self, domain: str):
        self.domain = domain
    
    def handle_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": f"Handling {message} in domain {self.domain}"}
