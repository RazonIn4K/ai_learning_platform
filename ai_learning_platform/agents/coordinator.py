import logging
from typing import Dict, Any, Optional

from .learning_coordinator import LearningCoordinatorAgent
from .topic_navigator import TopicNavigatorAgent
from .knowledge_agent import KnowledgeAgent
from .research_agent import ResearchAgent
from .domain_expert import DomainExpert
from .connection_expert import ConnectionExpert

logger = logging.getLogger(__name__)
    
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
        self.topic_navigator = topic_navigator or TopicNavigatorAgent(self._get_agent_config())
        self.knowledge_agent = knowledge_agent or KnowledgeAgent(self._get_agent_config())
        self.research_agent = research_agent or ResearchAgent(self._get_agent_config())
        self.connection_expert = connection_expert or ConnectionExpert(self._get_agent_config())
        
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
    
    def _get_agent_config(self) -> Dict[str, Any]:
        """Get the configuration for agent initialization."""
        return {
            "model_name": self.model_name,
            "model_params": self.model_params
        }
        
    def _create_domain_expert(self, domain: str):
        """
        Create a domain expert for a specific domain.
        
        Args:
            domain: The domain for which to create an expert
            
        Returns:
            The created domain expert
        """
        return DomainExpert(self._get_agent_config(), domain=domain)
