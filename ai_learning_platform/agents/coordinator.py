"""Learning Coordinator Agent for orchestrating multi-agent learning interactions."""

from typing import Dict, Any, Optional, List, Tuple, Set
import logging
from dataclasses import dataclass
import json
from enum import Enum
from datetime import datetime

from .base_agent import BaseLearningAgent
from ..models.model_registry import ModelRegistry
from ..utils.exceptions import CoordinationError
from ..utils.knowledge_explorer import LearningContext, KnowledgeExplorer

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    NAVIGATOR = "navigator"
    DOMAIN_EXPERT = "domain_expert"
    CONNECTION_EXPERT = "connection_expert"
    KNOWLEDGE_AGENT = "knowledge_agent"
    RESEARCH_AGENT = "research_agent"

@dataclass
class QueryAnalysis:
    """Analysis of a learning query."""
    domains: List[str]
    is_navigation: bool
    complexity_level: str
    learning_style: str
    required_agents: List[str]
    confidence_score: float
    requires_coordination: bool = True

class LearningCoordinatorAgent(BaseLearningAgent):
    """Coordinates multiple specialized agents for comprehensive learning responses."""
    
    def __init__(
        self,
        specialized_agents: Dict[str, BaseLearningAgent],
        model_name: str = "anthropic/claude-3-sonnet",
        model_params: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        profile_manager: Optional[Any] = None,
        knowledge_explorer: Optional[KnowledgeExplorer] = None
    ):
        super().__init__(model_name, model_params)
        self.specialized_agents = specialized_agents
        self.user_profile = user_profile or {}
        self.profile_manager = profile_manager
        self.knowledge_explorer = knowledge_explorer
        self.agent_capabilities = self._map_agent_capabilities()
        
        logger.info("Learning Coordinator initialized with %d specialized agents",
                   len(specialized_agents))
    
    def _map_agent_capabilities(self) -> Dict[str, Set[str]]:
        """Map agent names to their specialized functions."""
        capabilities = {}
        for name, agent in self.specialized_agents.items():
            if hasattr(agent, "specialized_function"):
                capabilities[name] = self._discover_agent_functions(agent)
            else:
                capabilities[name] = {"process_query"}
        return capabilities
    
    def _discover_agent_functions(self, agent: BaseLearningAgent) -> Set[str]:
        """Discover specialized functions for an agent."""
        try:
            # Try to get the function list directly
            if hasattr(agent, "get_available_functions"):
                return set(agent.get_available_functions())
            
            # Fallback to a predefined set based on agent type
            if "topic_navigator" in agent.__class__.__name__.lower():
                return {"analyze_learning_path", "suggest_next_topics", "analyze_topic"}
            elif "domain_expert" in agent.__class__.__name__.lower():
                return {"provide_domain_knowledge", "answer_domain_question"}
            elif "connection_expert" in agent.__class__.__name__.lower():
                return {"analyze_topic_connections", "explore_topic_connections"}
            else:
                return {"process_query"}
        except Exception as e:
            logger.warning(f"Failed to discover agent functions: {str(e)}")
            return {"process_query"}

    def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Coordinate multiple agents to process a learning query."""
        try:
            logger.info("Processing query: %s", query)
            analysis = self._analyze_query(query)
            
            if not analysis.requires_coordination:
                return self._handle_single_agent_query(query, analysis, context)
            
            return self._handle_coordinated_query(query, analysis, context)
            
        except Exception as e:
            logger.error("Error processing query: %s", str(e), exc_info=True)
            raise CoordinationError(f"Failed to process query: {str(e)}")

    def _analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze query to determine required agents and approach."""
        prompt = f"""Analyze this learning query and provide a detailed execution plan.

        QUERY: {query}

        Provide a JSON response with:
        {{
            "domains": ["list", "of", "relevant", "domains"],
            "is_navigation": boolean,
            "complexity_level": "beginner|intermediate|advanced",
            "learning_style": "conceptual|practical|visual|balanced",
            "required_agents": ["agent1", "agent2"],
            "execution_order": ["step1", "step2"],
            "confidence_score": 0.0-1.0
        }}"""
        
        result = self.process_message(prompt)
        
        try:
            parsed = json.loads(result)
            return QueryAnalysis(
                domains=parsed["domains"],
                is_navigation=parsed["is_navigation"],
                complexity_level=parsed["complexity_level"],
                learning_style=parsed["learning_style"],
                required_agents=parsed.get("required_agents", self._determine_required_agents(parsed)),
                confidence_score=parsed.get("confidence_score", 0.7),
                requires_coordination=len(parsed.get("required_agents", [])) > 1
            )
        except json.JSONDecodeError:
            logger.error("Failed to parse analysis result")
            raise CoordinationError("Failed to analyze query")

    def _handle_single_agent_query(
        self,
        query: str,
        analysis: QueryAnalysis,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle query that requires only one specialized agent."""
        agent_name = analysis.required_agents[0]
        agent = self.specialized_agents.get(agent_name)
        
        if not agent:
            raise CoordinationError(f"Required agent {agent_name} not found")
        
        # Select the appropriate specialized function based on capabilities
        function_name = "process_query"  # Default fallback
        if agent_name in self.agent_capabilities:
            if "provide_domain_knowledge" in self.agent_capabilities[agent_name] and "domain_expert" in agent_name:
                function_name = "provide_domain_knowledge"
            elif "analyze_learning_path" in self.agent_capabilities[agent_name] and agent_name == "topic_navigator":
                function_name = "analyze_learning_path"
            elif "analyze_topic_connections" in self.agent_capabilities[agent_name] and agent_name == "connection_expert":
                function_name = "analyze_topic_connections"
        
        logger.info(f"Using specialized function '{function_name}' for agent '{agent_name}'")
        try:
            # Call the specialized function dynamically
            response = agent.specialized_function(
                function_name,
                query=query,
                context=self._enrich_context(context, analysis)
            )
            return self._format_response(response, agent_name)
        except Exception as e:
            logger.error(f"Error calling specialized function '{function_name}' on {agent_name}: {str(e)}")
            # Use error handling
            error_response = self._handle_agent_error(
                agent_name,
                function_name,
                e,
                query,
                self._enrich_context(context, analysis)
            )
            return self._format_response(error_response, f"{agent_name}_fallback")
            
    def _format_response(self, response: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """Format the response from a single agent."""
        # Convert response to standard format if needed
        if isinstance(response, dict) and "content" in response:
            return {
                "content": response["content"],
                "sources": [agent_name],
                "metadata": response.get("metadata", {}),
                "confidence_score": response.get("confidence_score", 0.8),
                "learning_path": response.get("learning_path", [])
            }
        elif isinstance(response, str):
            # If the response is just a string, wrap it
            return {
                "content": response,
                "sources": [agent_name],
                "metadata": {},
                "confidence_score": 0.8,
                "learning_path": []
            }
        else:
            logger.warning(f"Unexpected response format from {agent_name}")
            return {
                "content": str(response),
                "sources": [agent_name],
                "metadata": {},
                "confidence_score": 0.5,
                "learning_path": []
            }

    def _handle_coordinated_query(
        self,
        query: str,
        analysis: QueryAnalysis,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle query requiring multiple agent coordination."""
        enriched_context = self._enrich_context(context, analysis)
        agent_responses = []
        execution_plan = []
        
        # Step 1: Always start with navigation if needed
        if "topic_navigator" in analysis.required_agents:
            nav_response = self._get_navigation_response(query, enriched_context)
            agent_responses.append(("topic_navigator", nav_response))
            enriched_context = self._update_context_with_navigation(
                enriched_context,
                nav_response
            )
            execution_plan.append({
                "stage": "navigation",
                "agent": "topic_navigator",
                "output": nav_response
            })
        
        # Step 2: Get domain expert knowledge
        domain_responses = []
        for domain in analysis.domains:
            expert_name = f"{domain}_expert"
            if expert_name in self.specialized_agents:
                expert_response = self._get_expert_response(
                    expert_name,
                    query,
                    enriched_context
                )
                domain_responses.append((expert_name, expert_response))
                execution_plan.append({
                    "stage": "domain_knowledge",
                    "agent": expert_name,
                    "output": expert_response
                })
        
        # Step 3: Analyze connections between domain knowledge
        if len(domain_responses) > 1 or "connection_expert" in analysis.required_agents:
            conn_response = self._get_connection_response(
                query,
                enriched_context,
                domain_responses
            )
            agent_responses.extend(domain_responses)
            agent_responses.append(("connection_expert", conn_response))
            execution_plan.append({
                "stage": "connection_analysis",
                "agent": "connection_expert",
                "output": conn_response
            })
        else:
            agent_responses.extend(domain_responses)
        
        # Step 4: Optional research phase for cutting-edge or complex topics
        if "research_agent" in analysis.required_agents:
            research_response = self._get_research_response(
                query,
                enriched_context,
                agent_responses
            )
            agent_responses.append(("research_agent", research_response))
            execution_plan.append({
                "stage": "research",
                "agent": "research_agent",
                "output": research_response
            })
        
        # Step 5: Synthesize all responses
        final_response = self._synthesize_responses(agent_responses, analysis)
        final_response["execution_plan"] = execution_plan
        
        return final_response

    def _get_navigation_response(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get response from topic navigator."""
        navigator = self.specialized_agents["topic_navigator"]
        return navigator.specialized_function(
            "analyze_learning_path",
            query=query,
            context=context
        )

    def _get_expert_response(
        self,
        expert_name: str,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get response from domain expert."""
        expert = self.specialized_agents[expert_name]
        return expert.specialized_function(
            "provide_domain_knowledge",
            query=query,
            context=context
        )

    def _get_connection_response(
        self,
        query: str,
        context: Dict[str, Any],
        previous_responses: List[Tuple[str, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Get response from connection expert."""
        connection_expert = self.specialized_agents["connection_expert"]
        enriched_context = self._enrich_context_with_responses(
            context,
            previous_responses
        )
        return connection_expert.specialized_function(
            "analyze_topic_connections",
            query=query,
            context=enriched_context
        )

    def _synthesize_responses(
        self,
        agent_responses: List[Tuple[str, Dict[str, Any]]],
        analysis: QueryAnalysis
    ) -> Dict[str, Any]:
        """Synthesize responses from multiple agents into a coherent response."""
        synthesis_prompt = f"""
        Create a comprehensive learning response that integrates information from multiple expert agents.
        
        CONTEXT:
        - Complexity Level: {analysis.complexity_level}
        - Learning Style: {analysis.learning_style}
        - Domains: {', '.join(analysis.domains)}
        
        AGENT RESPONSES:
        {self._format_agent_responses(agent_responses)}
        
        SYNTHESIS REQUIREMENTS:
        1. Start with core concepts and progressively build complexity
        2. Maintain coherence between different domain perspectives
        3. Highlight practical applications and connections
        4. Include specific examples that bridge multiple domains
        5. Address any contradictions or complementary viewpoints
        6. Provide clear learning progression steps
        
        FORMAT:
        {{
            "core_concepts": ["concept1", "concept2"],
            "main_content": "synthesized explanation",
            "practical_applications": ["application1", "application2"],
            "learning_path": {{
                "prerequisites": ["prereq1", "prereq2"],
                "steps": ["step1", "step2"],
                "advanced_topics": ["topic1", "topic2"]
            }},
            "cross_domain_insights": ["insight1", "insight2"]
        }}
        """
        
        synthesis = self.process_message(synthesis_prompt)
        
        try:
            parsed_synthesis = json.loads(synthesis)
            return {
                "content": parsed_synthesis["main_content"],
                "learning_path": parsed_synthesis["learning_path"],
                "practical_applications": parsed_synthesis["practical_applications"],
                "cross_domain_insights": parsed_synthesis["cross_domain_insights"],
                "confidence_score": analysis.confidence_score,
                "metadata": {
                    "complexity_level": analysis.complexity_level,
                    "learning_style": analysis.learning_style,
                    "domains": analysis.domains,
                    "contributing_agents": [agent for agent, _ in agent_responses]
                }
            }
        except json.JSONDecodeError as e:
            logger.error("Failed to parse synthesis: %s", str(e))
            raise CoordinationError("Failed to synthesize agent responses")

    def _format_agent_responses(
        self,
        agent_responses: List[Tuple[str, Dict[str, Any]]]
    ) -> str:
        """Format agent responses for synthesis prompt."""
        formatted = []
        for agent_name, response in agent_responses:
            content = response.get("content", str(response))
            formatted.append(f"=== {agent_name.upper()} ===\n{content}")
        return "\n\n".join(formatted)

    def _enrich_context(
        self,
        context: Optional[Dict[str, Any]],
        analysis: QueryAnalysis
    ) -> Dict[str, Any]:
        """Enrich context with analysis results, user profile, and knowledge insights."""
        enriched = context.copy() if context else {}
        
        # Add query analysis
        enriched["analysis"] = analysis.__dict__
        
        # Add user profile and preferences
        enriched["user_profile"] = self.user_profile
        
        # Add learning history if available
        if self.profile_manager and self.user_profile and "user_id" in self.user_profile:
            try:
                user_id = self.user_profile["user_id"]
                enriched["learning_history"] = self.profile_manager.get_learning_history(user_id) or {}
                enriched["user_strengths"] = self.profile_manager.get_user_strengths(user_id) or []
                enriched["learning_gaps"] = self.profile_manager.get_learning_gaps(user_id) or []
            except Exception as e:
                logger.warning(f"Failed to get user learning history: {str(e)}")
        
        # Add domain-specific knowledge context if available
        if self.knowledge_explorer:
            try:
                # Add topic insights for each identified domain
                for domain in analysis.domains:
                    domain_key = f"{domain}_knowledge"
                    enriched[domain_key] = self.knowledge_explorer.get_domain_context(domain)
                
                # Add general learning context
                learning_context = self.knowledge_explorer.create_learning_context(
                    domains=analysis.domains,
                    complexity=analysis.complexity_level,
                    learning_style=analysis.learning_style
                )
                enriched["learning_context"] = learning_context
            except Exception as e:
                logger.warning(f"Failed to add knowledge context: {str(e)}")
        
        # Add timestamp
        enriched["timestamp"] = datetime.now().isoformat()
        enriched["session_id"] = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return enriched

    def _determine_required_agents(self, analysis: Dict[str, Any]) -> List[str]:
        """Determine which agents are required based on analysis."""
        required = []
        
        if analysis.get("is_navigation", False):
            required.append("topic_navigator")
            
        for domain in analysis.get("domains", []):
            required.append(f"{domain}_expert")
            
        if analysis.get("needs_connections", False):
            required.append("connection_expert")
            
        if analysis.get("needs_research", False):
            required.append("research_agent")
            
        return required

    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis."""
        base_score = analysis.get("base_confidence", 0.7)
        modifiers = {
            "clear_domain": 0.1,
            "clear_intent": 0.1,
            "sufficient_context": 0.1,
            "known_topic": 0.1
        }
        
        final_score = base_score
        for key, modifier in modifiers.items():
            if analysis.get(key, False):
                final_score += modifier
                
        return min(final_score, 1.0)
        
    def _create_analysis_prompt(self, query: str) -> str:
        """Create prompt for analyzing a learning query."""
        return f"""
        You are an intelligent query analyzer for a learning system. Your task is to analyze
        the following learning query and determine the best approach to answer it.
        
        QUERY: {query}
        
        Analyze the query and provide the following information in JSON format:
        
        1. domains: List of relevant knowledge domains (e.g., "programming", "math", "history")
        2. is_navigation: Whether this query requires learning path navigation (true/false)
        3. complexity_level: Estimated complexity level ("beginner", "intermediate", "advanced")
        4. learning_style: Preferred learning style based on query ("conceptual", "practical", "visual", "balanced")
        5. needs_connections: Whether this query requires connecting different topics (true/false)
        6. needs_research: Whether this query requires current or specialized research (true/false)
        7. base_confidence: Base confidence score for analyzing this query (0.0-1.0)
        8. clear_domain: Whether the query has a clear domain focus (true/false)
        9. clear_intent: Whether the query has a clear learning intent (true/false)
        10. sufficient_context: Whether there is sufficient context in the query (true/false)
        11. known_topic: Whether the query is about a commonly known topic (true/false)
        
        Respond with ONLY the JSON object containing these fields.
        """
    
    def _create_synthesis_prompt(
        self,
        agent_responses: List[Tuple[str, Dict[str, Any]]],
        analysis: QueryAnalysis
    ) -> str:
        """Create prompt for synthesizing multiple agent responses."""
        # Format agent responses for the prompt
        formatted_responses = []
        for agent_name, response in agent_responses:
            content = response.get("content", str(response)) if isinstance(response, dict) else str(response)
            formatted_responses.append(f"=== {agent_name.upper()} RESPONSE ===\n{content}\n")
        
        responses_text = "\n".join(formatted_responses)
        
        return f"""
        You are an expert learning facilitator synthesizing information from multiple specialized agents.
        Your goal is to create a coherent, well-structured response that integrates all the information
        provided by different agents.
        
        QUERY ANALYSIS:
        - Domains: {', '.join(analysis.domains)}
        - Complexity Level: {analysis.complexity_level}
        - Learning Style: {analysis.learning_style}
        
        AGENT RESPONSES:
        {responses_text}
        
        INSTRUCTIONS:
        1. Integrate the information from all agent responses into a cohesive, well-structured answer
        2. Prioritize accuracy and depth of knowledge
        3. Ensure the synthesized response matches the complexity level: {analysis.complexity_level}
        4. Adapt the style to match the learning style: {analysis.learning_style}
        5. Cite specific concepts from the agent responses
        6. Include concrete examples that illustrate the concepts
        7. Address any conflicting information from different agents (if present)
        8. Provide a clear learning progression when relevant
        
        Your synthesis should be comprehensive yet focused, and should help the learner
        develop a deep understanding of the subject.
        """
                
    def _update_context_with_navigation(
        self,
        enriched_context: Dict[str, Any],
        nav_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update context with navigation response."""
        updated_context = enriched_context.copy()
        
        # Extract learning path if available
        if "learning_path" in nav_response:
            updated_context["learning_path"] = nav_response["learning_path"]
            
        # Extract topic hierarchy if available
        if "topic_hierarchy" in nav_response:
            updated_context["topic_hierarchy"] = nav_response["topic_hierarchy"]
            
        # Extract current topic if available
        if "current_topic" in nav_response:
            updated_context["current_topic"] = nav_response["current_topic"]
            
        # Extract prerequisites if available
        if "prerequisites" in nav_response:
            updated_context["prerequisites"] = nav_response["prerequisites"]
            
        # Add the full navigation response
        updated_context["navigation_response"] = nav_response
            
        return updated_context
    
    def _enrich_context_with_responses(
        self,
        context: Dict[str, Any],
        previous_responses: List[Tuple[str, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Enrich context with previous agent responses."""
        enriched = context.copy()
        
        # Add each agent response to the context
        for agent_name, response in previous_responses:
            enriched[f"{agent_name}_response"] = response
            
        # Create a combined knowledge base from all responses
        combined_knowledge = {}
        for agent_name, response in previous_responses:
            if isinstance(response, dict):
                if "content" in response:
                    combined_knowledge[agent_name] = response["content"]
                if "learning_path" in response and response["learning_path"]:
                    if "learning_paths" not in combined_knowledge:
                        combined_knowledge["learning_paths"] = []
                    combined_knowledge["learning_paths"].append({
                        "source": agent_name,
                        "path": response["learning_path"]
                    })
        
        enriched["combined_knowledge"] = combined_knowledge
        return enriched
    
    def _extract_learning_path(self, agent_responses: List[Tuple[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Extract learning path from agent responses."""
        learning_path = []
        
        # First check for navigator's learning path as it's most authoritative
        for agent_name, response in agent_responses:
            if agent_name == "topic_navigator" and isinstance(response, dict):
                if "learning_path" in response and response["learning_path"]:
                    return response["learning_path"]
        
        # If no navigator path, collect paths from all agents and merge
        for agent_name, response in agent_responses:
            if isinstance(response, dict) and "learning_path" in response:
                if response["learning_path"]:
                    for path_item in response["learning_path"]:
                        if path_item not in learning_path:
                            learning_path.append(path_item)
        
        return learning_path

    def _handle_agent_error(
        self,
        agent_name: str,
        function_name: str,
        error: Exception,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle errors from specialized agents gracefully."""
        logger.error(
            f"Error in {agent_name}.{function_name}: {str(error)}",
            exc_info=True
        )
        
        error_details = {
            "agent": agent_name,
            "function": function_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "query": query,
            "context_keys": list(context.keys())
        }
        
        # Try to get a fallback response
        try:
            if agent_name == "topic_navigator" and "connection_expert" in self.specialized_agents:
                # Try using connection expert as fallback
                fallback = self.specialized_agents["connection_expert"].specialized_function(
                    "analyze_topic_connections",
                    query=query,
                    context=context
                )
                return {
                    **fallback,
                    "error": str(error),
                    "error_details": error_details,
                    "is_fallback": True,
                    "fallback_response": "Used connection expert as fallback",
                    "success": False
                }
            elif "domain" in agent_name and "topic_navigator" in self.specialized_agents:
                # For domain expert errors, fall back to topic navigator
                fallback = self.specialized_agents["topic_navigator"].specialized_function(
                    "analyze_topic",
                    query=query,
                    context=context
                )
                return {
                    **fallback,
                    "error": str(error),
                    "error_details": error_details,
                    "is_fallback": True,
                    "fallback_response": "Used topic navigator as fallback",
                    "success": False
                }
            else:
                # Last resort: generate a direct response
                return {
                    "content": self.process_message(
                        f"The specialized agent encountered an error. Please provide a helpful "
                        f"response to this query: {query}"
                    ),
                    "error": str(error),
                    "error_details": error_details,
                    "is_fallback": True,
                    "fallback_response": "Generated direct response as fallback",
                    "success": False
                }
        except Exception as fallback_error:
            # If even the fallback fails, return a simple error message
            error_details["fallback_error"] = str(fallback_error)
            return {
                "content": f"I apologize, but I encountered an error processing your request. "
                          f"Please try rephrasing or asking a different question.",
                "error": str(error),
                "error_details": error_details,
                "fallback_error": str(fallback_error),
                "is_fallback": True,
                "fallback_response": "All fallback attempts failed",
                "success": False
            }

    def delegate_specialized_function(
        self,
        agent_name: str,
        function_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Delegate a specialized function to a specific agent.
        
        Args:
            agent_name: Name of the agent to delegate to
            function_name: Name of the function to call
            **kwargs: Additional arguments for the function
            
        Returns:
            Response from the agent
        """
        agent = self.specialized_agents.get(agent_name)
        if not agent:
            raise CoordinationError(f"Agent {agent_name} not found")
            
        try:
            return agent.specialized_function(function_name, **kwargs)
        except Exception as e:
            logger.error(f"Error delegating {function_name} to {agent_name}: {str(e)}")
            return self._handle_agent_error(agent_name, function_name, e, "", kwargs)

    def process_learning_session(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a comprehensive learning session.
        
        Args:
            query: User's learning query
            context: Additional context for the session
            session_id: Unique identifier for the session
            
        Returns:
            Comprehensive learning response
        """
        try:
            # Analyze the query
            analysis = self._analyze_query(query)
            
            # Enrich context with session info
            enriched_context = self._enrich_context(context, analysis)
            if session_id:
                enriched_context["session_id"] = session_id
                
            # Process based on coordination needs
            if not analysis.requires_coordination:
                response = self._handle_single_agent_query(query, analysis, enriched_context)
            else:
                response = self._handle_coordinated_query(query, analysis, enriched_context)
                
            # Add session metadata
            response["session_id"] = session_id
            response["timestamp"] = datetime.now().isoformat()
            response["query_analysis"] = {
                "domains": analysis.domains,
                "complexity_level": analysis.complexity_level,
                "learning_style": analysis.learning_style
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing learning session: {str(e)}", exc_info=True)
            raise CoordinationError(f"Learning session failed: {str(e)}")

    def process_message(self, message: str) -> str:
        """Process a message using the model.
        
        Args:
            message: The message to process
            
        Returns:
            The model's response
        """
        try:
            # Get the model from the registry
            model = ModelRegistry.get_model(self.model_name)
            
            # Prepare the context with system message
            context = {
                "system_message": """
                You are a Learning Coordinator, responsible for analyzing learning queries and coordinating multiple specialized agents.
                Your role is to:
                1. Analyze queries to determine required domains and expertise
                2. Plan the execution strategy for complex learning requests
                3. Coordinate multiple agents for comprehensive responses
                4. Ensure learning goals are met effectively
                
                Always provide structured, actionable analysis that can guide the learning process.
                """,
                "model_params": self.model_params or {}
            }
            
            # Process the message
            response = model.process_message(message, context)
            
            # Log the interaction
            logger.debug(f"Processed message: {message[:100]}...")
            logger.debug(f"Response: {response[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise CoordinationError(f"Failed to process message: {str(e)}")
