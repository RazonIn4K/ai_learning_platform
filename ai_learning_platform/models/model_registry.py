"""Model Registry for the AI Learning Platform."""

from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
from enum import Enum

try:
    from camel.typing import ModelType
    from camel.agents import Agent as CamelAgent
    from camel.configs import ModelConfig
except ImportError:
    # Define fallback types if CAMEL is not installed
    ModelType = str
    CamelAgent = Any
    ModelConfig = Any

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """Supported model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LOCAL = "local"

@dataclass
class ModelCapabilities:
    """Defines model capabilities and limitations."""
    max_tokens: int
    supports_functions: bool
    supports_vision: bool
    typical_latency: float  # in seconds
    cost_per_1k_tokens: float

class ModelRegistry:
    """Registry for AI model configurations."""
    
    # OpenAI Models
    GPT4_TURBO = "openai/gpt-4-0125-preview"
    GPT4 = "openai/gpt-4"
    GPT35_TURBO = "openai/gpt-3.5-turbo-0125"
    
    # Anthropic Models
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet-20240229"
    CLAUDE_3_OPUS = "anthropic/claude-3-opus-20240229"
    CLAUDE_3_HAIKU = "anthropic/claude-3-haiku-20240307"
    
    # Google Models
    GEMINI_PRO = "google/gemini-pro"
    GEMINI_ULTRA = "google/gemini-ultra"
    
    # Local Models
    OLLAMA_MISTRAL = "ollama/mistral-7b"
    OLLAMA_LLAMA = "ollama/llama2"
    
    # Model capabilities registry
    _CAPABILITIES = {
        GPT4_TURBO: ModelCapabilities(
            max_tokens=128000,
            supports_functions=True,
            supports_vision=True,
            typical_latency=2.5,
            cost_per_1k_tokens=0.01
        ),
        GPT35_TURBO: ModelCapabilities(
            max_tokens=16385,
            supports_functions=True,
            supports_vision=False,
            typical_latency=1.0,
            cost_per_1k_tokens=0.0015
        ),
        CLAUDE_3_OPUS: ModelCapabilities(
            max_tokens=200000,
            supports_functions=True,
            supports_vision=True,
            typical_latency=4.0,
            cost_per_1k_tokens=0.015
        ),
        CLAUDE_3_SONNET: ModelCapabilities(
            max_tokens=180000,
            supports_functions=True,
            supports_vision=True,
            typical_latency=2.0,
            cost_per_1k_tokens=0.008
        ),
        CLAUDE_3_HAIKU: ModelCapabilities(
            max_tokens=180000,
            supports_functions=True,
            supports_vision=True,
            typical_latency=1.0,
            cost_per_1k_tokens=0.003
        ),
    }
    
    @classmethod
    def create_client(cls, model_name: str) -> Any:
        """Create model client with proper configuration."""
        provider, model = model_name.split("/")
        
        if provider == "openai":
            return cls._create_openai_client(model)
        elif provider == "anthropic":
            return cls._create_anthropic_client(model)
        elif provider == "ollama":
            return cls._create_ollama_client(model)
        else:
            raise ValueError(f"Unknown model provider: {provider}")

    @classmethod
    def _create_openai_client(cls, model: str) -> CamelAgent:
        """Create an OpenAI model client."""
        config = {
            "api_type": "openai",
            "api_version": "2024-02-15"
        }
        model_config = ModelConfig(
            model_type=ModelType(model),
            provider="openai",
            **config
        )
        return CamelAgent(
            name=f"{model}_agent",
            model_config=model_config
        )

    @classmethod
    def _create_anthropic_client(cls, model: str) -> CamelAgent:
        """Create an Anthropic model client."""
        config = {
            "api_type": "anthropic",
            "api_version": "2024-01-31"
        }
        model_config = ModelConfig(
            model_type=ModelType(model),
            provider="anthropic",
            **config
        )
        return CamelAgent(
            name=f"{model}_agent",
            model_config=model_config
        )

    @classmethod
    def _create_ollama_client(cls, model: str) -> CamelAgent:
        """Create an Ollama model client."""
        config = {
            "api_type": "ollama",
            "api_version": "v1"
        }
        model_config = ModelConfig(
            model_type=ModelType(model),
            provider="ollama",
            **config
        )
        return CamelAgent(
            name=f"{model}_agent",
            model_config=model_config
        )

from .base_agent import BaseLearningAgent

class LearningCoordinatorAgent(BaseLearningAgent):
    """
    Agent for coordinating between specialized agents.
    """
    
    def __init__(
        self,
        specialized_agents: Dict[str, BaseLearningAgent],
        model_name: str = ModelRegistry.OPENAI_GPT35,
        model_params: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the learning coordinator agent.
        
        Args:
            specialized_agents: Dictionary of specialized agents
            model_name: Name of the model to use
            model_params: Additional parameters for model configuration
            user_profile: User profile information
        """
        system_message = """
        You are a Learning Coordinator, an AI that orchestrates interactions between specialized learning agents.
        Your purpose is to analyze user queries, determine which specialized agent(s) can best answer them,
        and synthesize their responses into cohesive, helpful answers.
        
        You have access to the following specialized agents:
        - Topic Navigator: Helps navigate the topic hierarchy and create learning paths
        - Domain Experts: Provide in-depth knowledge about specific domains (e.g., Python, Cybersecurity)
        
        Your responsibilities include:
        1. Analyzing user queries to determine their intent and domain
        2. Routing queries to the appropriate specialized agent(s)
        3. Synthesizing responses from multiple agents when needed
        4. Maintaining conversation context across interactions
        5. Recommending next steps in the learning journey
        
        Always strive to provide comprehensive, accurate responses that match the user's learning style and complexity preference.
        """
        
        super().__init__(
            name="Learning Coordinator",
            system_message=system_message,
            model_name=model_name,
            model_params=model_params,
            user_profile=user_profile
        )
        
        # Store specialized agents
        self.specialized_agents = specialized_agents
    
    def _enrich_message_with_context(self, message: str) -> str:
        """
        Enrich a message with context about available agents.
        
        Args:
            message: The original message
            
        Returns:
            Enriched message with context
        """
        enriched_message = super()._enrich_message_with_context(message)
        
        # Add information about available agents
        agents_context = "\n## Available Specialized Agents\n"
        for name, agent in self.specialized_agents.items():
            agents_context += f"- {name}: {type(agent).__name__}\n"
        
        return enriched_message + "\n" + agents_context
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a user query to determine which agents should handle it.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with analysis results
        """
        # Check for domain-specific keywords
        analysis = {
            "domains": [],
            "is_navigation": False,
            "requires_coordination": False
        }
        
        # Check for domain-specific keywords
        for agent_name in self.specialized_agents.keys():
            if "expert" in agent_name.lower() and agent_name.lower().split("_expert")[0] in query.lower():
                analysis["domains"].append(agent_name)
        
        # Check for navigation-related keywords
        navigation_keywords = [
            "topic", "hierarchy", "learning path", "prerequisite", "roadmap", 
            "next topic", "related topic", "subtopic"
        ]
        
        for keyword in navigation_keywords:
            if keyword in query.lower():
                analysis["is_navigation"] = True
                break
        
        # If no specific domain is detected, try to determine it
        if not analysis["domains"] and not analysis["is_navigation"]:
            # Default to using a domain expert if available
            for agent_name in self.specialized_agents.keys():
                if "expert" in agent_name.lower():
                    analysis["domains"].append(agent_name)
                    break
        
        # If still no domain, use the topic navigator
        if not analysis["domains"] and not analysis["is_navigation"]:
            analysis["is_navigation"] = True
        
        # Determine if coordination is required
        analysis["requires_coordination"] = len(analysis["domains"]) > 1 or (
            len(analysis["domains"]) > 0 and analysis["is_navigation"]
        )
        
        return analysis
    
    def process_query(self, query: str) -> str:
        """
        Process a user query and coordinate responses from specialized agents.
        
        Args:
            query: User query
            
        Returns:
            Coordinated response
        """
        # Analyze query
        analysis = self._analyze_query(query)
        
        # Handle single agent case
        if not analysis["requires_coordination"]:
            if analysis["is_navigation"] and "topic_navigator" in self.specialized_agents:
                return self.specialized_agents["topic_navigator"].process_message(query)
            elif analysis["domains"]:
                domain_agent = analysis["domains"][0]
                if domain_agent in self.specialized_agents:
                    return self.specialized_agents[domain_agent].process_message(query)
        
        # Handle multi-agent case
        responses = []
        
        # Get response from topic navigator if needed
        if analysis["is_navigation"] and "topic_navigator" in self.specialized_agents:
            nav_response = self.specialized_agents["topic_navigator"].process_message(query)
            responses.append(("Topic Navigator", nav_response))
        
        # Get responses from domain experts
        for domain in analysis["domains"]:
            if domain in self.specialized_agents:
                domain_response = self.specialized_agents[domain].process_message(query)
                responses.append((domain, domain_response))
        
        # If no responses yet, use all available agents
        if not responses:
            for name, agent in self.specialized_agents.items():
                agent_response = agent.process_message(query)
                responses.append((name, agent_response))
        
        # Synthesize responses
        if len(responses) == 1:
            return responses[0][1]
        else:
            return self._synthesize_responses(query, responses)
    
    def _synthesize_responses(self, query: str, responses: List[tuple]) -> str:
        """
        Synthesize responses from multiple agents.
        
        Args:
            query: Original user query
            responses: List of (agent_name, response) tuples
            
        Returns:
            Synthesized response
        """
        # Create a prompt for synthesis
        synthesis_prompt = f"""
        User Query: "{query}"
        
        I received responses from multiple specialized agents:
        
        """
        
        for agent_name, response in responses:
            synthesis_prompt += f"## {agent_name} Response\n{response}\n\n"
        
        synthesis_prompt += """
        Synthesize these responses into a comprehensive, cohesive answer that:
        1. Addresses all aspects of the user's query
        2. Eliminates redundant information
        3. Resolves any contradictions (if present)
        4. Organizes information in a logical flow
        5. Maintains a consistent tone and style
        
        Your response should read as a single, coherent answer rather than a collection of separate responses.
        """
        
        return self.process_message(synthesis_prompt)
    
    def recommend_next_steps(self) -> str:
        """
        Recommend next steps in the learning journey based on user profile.
        
        Returns:
            Recommendations for next steps
        """
        # Create a prompt for recommendations
        prompt = """
        Based on the user's profile and learning history, recommend next steps in their learning journey.
        
        Consider:
        1. Topics they've already learned
        2. Their stated interests
        3. Their learning style and complexity preference
        4. Natural progression in their domains of interest
        
        Provide specific recommendations for:
        - Next topics to explore
        - Skills to practice
        - Projects to attempt
        - Resources that might be helpful
        
        Format your response as a clear, actionable plan that motivates and guides the user.
        """
        
        return self.process_message(prompt)
    
    def specialized_function(self, function_type: str, *args, **kwargs) -> str:
        """
        Call specialized coordinator functions based on type.
        
        Args:
            function_type: Type of function to call
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result of the function call
        """
        if function_type == "process_query":
            return self.process_query(kwargs.get("query", ""))
        elif function_type == "recommend_next_steps":
            return self.recommend_next_steps()
        else:
            return f"Unknown function type: {function_type}"
