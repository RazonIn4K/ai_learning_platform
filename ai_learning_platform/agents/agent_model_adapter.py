# ai_learning_platform/agents/agent_model_adapter.py

import logging
from typing import Dict, Any, Optional, List, Union

from ..utils.exceptions import AgentError, ModelError
from ..models.enhanced_model_manager import EnhancedModelManager
from ..utils.json_extractor import ensure_json_response

logger = logging.getLogger(__name__)

class AgentModelAdapter:
    """
    Adapts agents to use the EnhancedModelManager.
    
    This class provides a consistent interface for agents to interact with
    different model providers through the EnhancedModelManager.
    """
    
    def __init__(self, model_manager: Optional[EnhancedModelManager] = None):
        """
        Initialize AgentModelAdapter.
        
        Args:
            model_manager: Optional EnhancedModelManager instance
        """
        self.model_manager = model_manager or EnhancedModelManager()
    
    async def generate_agent_response(
        self,
        agent_type: str,
        prompt: str,
        role_description: Optional[str] = None,
        expect_json: bool = False,
        json_schema: Optional[Dict[str, Any]] = None,
        role_playing: bool = False,
        assistant_role: Optional[str] = None,
        user_role: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response for an agent.
        
        Args:
            agent_type: The type of agent (e.g., 'topic_navigator')
            prompt: The prompt to send to the model
            role_description: Optional role description to include
            expect_json: Whether to expect a JSON response
            json_schema: Optional JSON schema for validation
            role_playing: Whether to use role-playing capabilities
            assistant_role: Optional role for the assistant (CAMeL-AI specific)
            user_role: Optional role for the user (CAMeL-AI specific)
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Get agent-specific model settings if available
            provider = kwargs.get('provider')
            model_name = kwargs.get('model_name')
            
            # Check if role-playing is requested and set up
            if role_playing:
                # Force CAMeL-AI provider if role-playing is requested
                provider = 'camel'
                
                # Set up role-playing parameters
                if assistant_role and user_role:
                    # Dual role setup
                    kwargs['assistant_role'] = assistant_role
                    kwargs['user_role'] = user_role
                elif role_description:
                    # Single role setup
                    kwargs['role'] = role_description
                else:
                    # Default role based on agent type
                    kwargs['role'] = self._get_default_role_for_agent(agent_type)
            else:
                # Standard processing
                # Build full prompt with role description if provided
                full_prompt = prompt
                if role_description:
                    full_prompt = f"{role_description}\n\n{prompt}"
                    
                # Add JSON formatting instruction if needed
                if expect_json:
                    full_prompt += "\n\nPlease provide your response as a valid JSON object."
                    if json_schema:
                        schema_str = json.dumps(json_schema, indent=2)
                        full_prompt += f"\n\nYour response should follow this schema:\n```json\n{schema_str}\n```"
                        
                # Update prompt
                prompt = full_prompt
            
            # Generate response
            response = await self.model_manager.generate_response(
                prompt=prompt,
                provider=provider,
                model_name=model_name,
                **kwargs
            )
            
            # Process JSON response if expected
            if expect_json and response.get('content'):
                json_result = ensure_json_response(response['content'], json_schema)
                
                if not json_result['success']:
                    logger.warning(f"JSON extraction failed: {json_result['error']}")
                    
                response['json'] = json_result['json']
                response['json_extraction_success'] = json_result['success']
                response['json_extraction_error'] = json_result['error']
            
            # Add agent context
            response['agent_type'] = agent_type
            
            return response
            
        except ModelError as e:
            logger.error(f"Model error in agent {agent_type}: {str(e)}")
            raise AgentError(f"Model error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating response for agent {agent_type}: {str(e)}")
            raise AgentError(f"Agent adapter error: {str(e)}")

    def _get_default_role_for_agent(self, agent_type: str) -> str:
        """
        Get a default role description for an agent type.
        
        Args:
            agent_type: The type of agent
            
        Returns:
            Default role description
        """
        role_definitions = {
            'topic_navigator': """
                You are an expert learning path designer. Your role is to analyze learning queries,
                identify key topics, and create personalized learning paths that effectively guide
                students through complex subjects. You excel at breaking down difficult concepts into
                manageable steps, setting appropriate prerequisites, and adapting paths based on
                a learner's existing knowledge.
            """,
            'connection_expert': """
                You are a cross-disciplinary knowledge connector. Your role is to identify meaningful
                relationships between different domains and topics, highlighting how concepts from one
                area can inform or enhance understanding in another. You excel at finding non-obvious
                connections and explaining their relevance to learners.
            """,
            'domain_expert': """
                You are a specialist with deep knowledge in a specific domain. Your role is to provide
                accurate, detailed explanations of concepts within your area of expertise, addressing
                common misconceptions and offering practical applications. You excel at calibrating your
                explanations to match the learner's level of understanding.
            """,
            'research_agent': """
                You are a thorough research analyst. Your role is to gather, synthesize, and present
                information on specific topics. You excel at finding high-quality sources, extracting
                key insights, and organizing information in a way that facilitates learning and
                decision-making.
            """,
            'knowledge_agent': """
                You are a comprehensive knowledge base. Your role is to provide accurate information
                across a wide range of topics. You excel at retrieving relevant facts, concepts, and
                explanations, and presenting them in a clear, accessible manner.
            """
        }
        
        return role_definitions.get(agent_type, """
            You are an educational AI assistant. Your role is to help learners understand complex topics,
            answer their questions, and guide their learning process in a supportive, informative manner.
        """)

    async def generate_role_playing_response(
        self,
        agent_type: str,
        prompt: str,
        assistant_role: str,
        user_role: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using CAMeL-AI's role-playing capabilities.
        
        Args:
            agent_type: The type of agent
            prompt: The user's message
            assistant_role: Role description for the assistant
            user_role: Role description for the user
            **kwargs: Additional arguments
            
        Returns:
            Response dictionary
        """
        return await self.generate_agent_response(
            agent_type=agent_type,
            prompt=prompt,
            role_playing=True,
            assistant_role=assistant_role,
            user_role=user_role,
            **kwargs
        )
    
    async def analyze_query(
        self,
        agent_type: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze a query to extract structured information.
        
        Args:
            agent_type: The type of agent (e.g., 'topic_navigator')
            query: The query to analyze
            context: Optional additional context
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Dictionary containing the analysis results
        """
        try:
            # Build analysis prompt
            analysis_prompt = f"""
            Analyze the following query for an {agent_type} agent:
            
            QUERY: {query}
            
            Provide a structured analysis as a JSON object with the following fields:
            1. topics: List of relevant topics mentioned in the query
            2. complexity_level: Estimated complexity level (basic, intermediate, advanced)
            3. query_type: The type of query (information, learning_path, etc.)
            4. specific_requests: Any specific requests or constraints mentioned
            """
            
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                analysis_prompt += f"\n\nCONTEXT:\n{context_str}"
            
            # Generate analysis
            response = await self.generate_agent_response(
                agent_type=agent_type,
                prompt=analysis_prompt,
                expect_json=True,
                **kwargs
            )
            
            # Extract JSON analysis
            if response.get('json'):
                return response['json']
            else:
                logger.warning(f"Failed to extract JSON analysis for {agent_type}")
                return {
                    'topics': [],
                    'complexity_level': 'intermediate',
                    'query_type': 'unknown',
                    'specific_requests': []
                }
                
        except Exception as e:
            logger.error(f"Error analyzing query for agent {agent_type}: {str(e)}")
            return {
                'topics': [],
                'complexity_level': 'intermediate',
                'query_type': 'unknown',
                'specific_requests': [],
                'error': str(e)
            }
