# ai_learning_platform/agents/coordinator.py

import logging
from typing import Dict, Any, Optional

from .learning_coordinator import LearningCoordinatorAgent
from .topic_navigator import TopicNavigatorAgent
from .knowledge_agent import KnowledgeAgent
from .research_agent import ResearchAgent
from .domain_expert import DomainExpert
from .connection_expert import ConnectionExpert
from ..models.enhanced_model_manager import EnhancedModelManager

logger = logging.getLogger(__name__)
    
class Coordinator:
    """
    Coordinates messages between different specialized agents.
    """
    
    def __init__(self, 
                 model_name: Optional[str] = None, 
                 model_provider: Optional[str] = None,
                 model_params: Optional[Dict[str, Any]] = None,
                 topic_navigator=None,
                 knowledge_agent=None,
                 research_agent=None,
                 connection_expert=None):
        """
        Initialize the coordinator.
        
        Args:
            model_name: Name of the base model to use
            model_provider: Provider of the model to use
            model_params: Parameters for the model
            topic_navigator: Agent for topic navigation
            knowledge_agent: Agent for knowledge retrieval
            research_agent: Agent for research
            connection_expert: Agent for finding connections
        """
        self.model_name = model_name
        self.model_provider = model_provider
        self.model_params = model_params or {"temperature": 0.7, "max_tokens": 1024}
        
        # Initialize model manager
        self.model_manager = EnhancedModelManager()
        
        # Initialize component agents
        self.topic_navigator = topic_navigator or TopicNavigatorAgent(self._get_agent_config())
        self.knowledge_agent = knowledge_agent or KnowledgeAgent(self._get_agent_config())
        self.research_agent = research_agent or ResearchAgent(self._get_agent_config())
        self.connection_expert = connection_expert or ConnectionExpert(self._get_agent_config())
        
        # Cache for domain experts
        self.domain_experts = {}
    
    async def process_message(self, message: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        analysis = await self._analyze_message(message, context)
        message_type = analysis.get("query_type", "general_query")
        
        # Update context with analysis
        context.update({
            "analysis": analysis,
            "domain": analysis.get("domains", ["general"])[0]
        })
        
        # Route to appropriate agent
        response = await self._route_message_to_agents(message_type, message, context)
        
        # Include analysis in response for debugging
        response["analysis"] = analysis
        
        return response
    
    async def _analyze_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a message to determine its characteristics.
        
        Args:
            message: The message to analyze
            context: Additional context
            
        Returns:
            Dictionary with analysis results
        """
        # Create analysis prompt
        prompt = f"""
        Analyze the following message to determine how it should be handled:
        
        MESSAGE: {message}
        
        Return a JSON object with the following fields:
        - query_type: The type of query (connection_query, learning_path_query, research_query, domain_query, knowledge_query)
        - domains: List of domains relevant to the query
        - complexity: Complexity level (basic, intermediate, advanced)
        - required_agents: List of agents needed to handle this query
        - confidence_score: How confident are you in this analysis (0.0-1.0)
        """
        
        # Use model manager for analysis
        response = await self.model_manager.generate_response(
            prompt,
            provider=self.model_provider,
            model_name=self.model_name,
            temperature=0.3,  # Low temperature for more consistent analysis
            max_tokens=1000
        )
        
        # Try to parse JSON from response
        try:
            import json
            from ..utils.json_extractor import extract_json_from_text
            
            json_str = extract_json_from_text(response['content'])
            analysis = json.loads(json_str)
            
            # Ensure required fields are present
            if "query_type" not in analysis:
                analysis["query_type"] = "general_query"
            if "domains" not in analysis:
                analysis["domains"] = ["general"]
            if "complexity" not in analysis:
                analysis["complexity"] = "basic"
            if "required_agents" not in analysis:
                analysis["required_agents"] = ["knowledge_agent"]
            if "confidence_score" not in analysis:
                analysis["confidence_score"] = 0.8
                
            return analysis
            
        except Exception as e:
            logger.error(f"Error parsing analysis JSON: {str(e)}")
            
            # Fall back to rule-based analysis
            return self._rule_based_analysis(message, context)
    
    def _rule_based_analysis(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use rule-based approach as fallback for message analysis.
        
        Args:
            message: The message to analyze
            context: Additional context
            
        Returns:
            Dictionary with analysis results
        """
        # Simple rule-based analysis
        analysis = {"confidence_score": 0.6}
        
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
    
    async def _route_message_to_agents(
        self, 
        message_type: str, 
        message: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route the message to the appropriate agent based on its type.
        
        Args:
            message_type: The type of the message
            message: The message content
            context: Additional context
            
        Returns:
            Dictionary containing the agent's response
        """
        try:
            if message_type == "connection_query":
                return await self.connection_expert.process({
                    'query': message,
                    'context': context
                })
            elif message_type == "learning_path_query":
                return await self.topic_navigator.process({
                    'query': message,
                    'user_profile': context.get('user_profile', {}),
                    'context': context
                })
            elif message_type == "research_query":
                return await self.research_agent.process({
                    'query': message,
                    'context': context
                })
            elif message_type == "domain_query":
                domain = context["domain"]
                if domain not in self.domain_experts:
                    self.domain_experts[domain] = self._create_domain_expert(domain)
                return await self.domain_experts[domain].process({
                    'query': message,
                    'context': context
                })
            else:
                return await self.knowledge_agent.process({
                    'query': message,
                    'context': context
                })
        except Exception as e:
            logger.error(f"Error routing message: {str(e)}")
            
            # Fallback response
            return {
                "content": "I encountered an issue while processing your request. Let me provide a general response.",
                "status": "error",
                "error": str(e)
            }
    
    def _get_agent_config(self) -> Dict[str, Any]:
        """Get the configuration for agent initialization."""
        return {
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "model_params": self.model_params
        }
        
    def _create_domain_expert(self, domain: str) -> DomainExpert:
        """
        Create a domain expert for a specific domain.
        
        Args:
            domain: The domain for which to create an expert
            
        Returns:
            The created domain expert
        """
        config = self._get_agent_config()
        # Set domain-specific prompt enhancement for the model
        config['domain'] = domain
        return DomainExpert(config)
