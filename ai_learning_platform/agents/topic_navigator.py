# ai_learning_platform/agents/topic_navigator.py

import logging
from typing import Dict, Any, List, Optional

from ..utils.topic_hierarchy import TopicHierarchy, create_default_hierarchy
from .base_agent import BaseAgent
from .agent_model_adapter import AgentModelAdapter
from ..models.model_response_formatter import ModelResponseFormatter

logger = logging.getLogger(__name__)

class TopicNavigatorAgent(BaseAgent):
    """Agent responsible for topic navigation and learning path adaptation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the topic navigator agent."""
        super().__init__("topic_navigator", config)
        self.topic_hierarchy = self._initialize_topic_hierarchy()
        self.model_adapter = AgentModelAdapter()
    
    def _initialize_topic_hierarchy(self) -> TopicHierarchy:
        """Initialize the topic hierarchy."""
        # Check if we have a file path in the config
        hierarchy_path = self.config.get('topic_hierarchy_path')
        if hierarchy_path:
            try:
                from ..utils.topic_hierarchy import load_topic_hierarchy
                return load_topic_hierarchy(hierarchy_path)
            except Exception as e:
                logger.error(f"Failed to load topic hierarchy from {hierarchy_path}: {str(e)}")
                
        # Fall back to default hierarchy
        return create_default_hierarchy()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        if not self._validate_input(input_data):
            raise ValueError(f"Invalid input for {self.agent_type} agent")
            
        query = input_data.get('query', '')
        user_profile = input_data.get('user_profile', {})
        
        try:
            # Analyze the query
            analysis = await self._analyze_query(query, user_profile)
            
            # If there's a current path, adapt it
            current_path = input_data.get('current_path', [])
            if current_path:
                adapted_path = self.adapt_learning_path(current_path, user_profile)
            else:
                # Generate a new learning path based on analysis
                adapted_path = await self._generate_learning_path(analysis, user_profile)
            
            return {
                "content": await self._format_response(query, adapted_path, analysis),
                "path": adapted_path,
                "analysis": analysis,
                "agent": self.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Error in {self.agent_type} agent: {str(e)}")
            return await self._process_with_fallback(input_data)
    
    async def _analyze_query(self, query: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the learning query."""
        prompt = f"""
        Analyze the following learning query and extract key information:
        
        Query: {query}
        
        Extract and return a JSON object with the following fields:
        - target_topic: The main topic the user wants to learn
        - related_topics: List of related topics mentioned or implied
        - complexity_level: Desired learning complexity (beginner, intermediate, advanced)
        - learning_style: Preferred learning approach (theoretical, practical, balanced)
        - estimated_duration: Estimated learning time for the main topic
        """
        
        response = await self.model_adapter.generate_agent_response(
            agent_type="topic_navigator",
            prompt=prompt,
            temperature=0.2,  # Lower temperature for more consistent analysis
            max_tokens=1000
        )
        
        # Parse the JSON from the response
        try:
            import json
            # Extract JSON from the response text
            content = response['content']
            json_str = self._extract_json(content)
            analysis = json.loads(json_str)
            
            # Extract topics from topic hierarchy as well
            extracted_topics = self.topic_hierarchy.extract_topics(query)
            if extracted_topics:
                analysis['extracted_topics'] = extracted_topics
                
            return analysis
        except Exception as e:
            logger.error(f"Failed to parse analysis JSON: {str(e)}")
            # Return a basic analysis
            return {
                "target_topic": query,
                "related_topics": [],
                "complexity_level": "intermediate",
                "learning_style": "balanced",
                "estimated_duration": "unknown"
            }
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from model response text."""
        # Look for JSON between curly braces
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # If no JSON found, return minimal valid JSON
        return '{"target_topic": "unknown"}'
    
    async def _generate_learning_path(self, analysis: Dict[str, Any], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a learning path based on analysis."""
        target_topic = analysis.get('target_topic', 'unknown')
        complexity = analysis.get('complexity_level', 'intermediate')
        
        # Get current knowledge
        known_topics = [
            topic["id"] for topic in user_profile.get("topics_learned", [])
            if topic.get("mastery_level", 0) >= 0.7
        ]
        
        prompt = f"""
        Generate a structured learning path for the topic: "{target_topic}"
        Complexity level: {complexity}
        
        The user already knows: {', '.join(known_topics) if known_topics else 'Not specified'}
        
        Return a JSON array of learning steps, where each step has:
        - topic: Topic identifier
        - title: Human readable title
        - description: Brief description of what will be learned
        - complexity: Complexity level (beginner, intermediate, advanced)
        - prerequisites: List of prerequisite topics
        - resources: List of suggested learning resources
        - estimated_duration: Estimated time to learn (e.g., "2 hours", "3 days")
        
        Focus on creating a logical progression that respects prerequisites and builds knowledge incrementally.
        """
        
        response = await self.model_adapter.generate_agent_response(
            agent_type="topic_navigator",
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse the JSON from the response
        try:
            import json
            # Extract JSON from the response text
            content = response['content']
            json_str = self._extract_json_array(content)
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse learning path JSON: {str(e)}")
            # Return a minimal path
            return [{
                "topic": target_topic,
                "title": target_topic.replace('_', ' ').title(),
                "description": f"Learn about {target_topic}",
                "complexity": complexity,
                "prerequisites": [],
                "resources": [],
                "estimated_duration": "unknown"
            }]
    
    def _extract_json_array(self, text: str) -> str:
        """Extract JSON array from model response text."""
        # Look for JSON array between square brackets
        import re
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # If no JSON array found, return minimal valid JSON array
        return '[{"topic": "unknown"}]'
    
    def adapt_learning_path(self, path: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Adapt learning path based on user profile and current knowledge.
        
        Args:
            path: Current learning path
            user_profile: User's learning profile and progress
            
        Returns:
            List of adapted learning steps
        """
        try:
            if not isinstance(path, list):
                logger.warning("Input path is not a list, initializing empty path")
                path = []

            # Get mastered topics
            mastered_topics = {
                topic["id"] for topic in user_profile.get("topics_learned", [])
                if topic.get("mastery_level", 0) >= 0.8
            }
            
            # Filter out mastered topics and keep the structure
            adapted_path = [
                step for step in path
                if step.get("topic") not in mastered_topics
            ]
            
            # If path is empty, generate a new one from topic hierarchy
            if not adapted_path:
                all_topics = self.topic_hierarchy.get_all_topics()
                for topic in all_topics:
                    if topic.id not in mastered_topics:
                        prerequisites_met = all(
                            prereq.id in mastered_topics 
                            for prereq in topic.prerequisites
                        )
                        if prerequisites_met:
                            adapted_path.append({
                                "topic": topic.id,
                                "title": topic.title,
                                "complexity": topic.complexity,
                                "estimated_duration": str(topic.estimated_duration),
                                "prerequisites": [p.id for p in topic.prerequisites]
                            })
            
            return adapted_path
            
        except Exception as e:
            logger.error(f"Error adapting learning path: {str(e)}")
            return []
    
    async def _format_response(self, query: str, path: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
        """Format the response for the user."""
        prompt = f"""
        Create a helpful response for a learning query.
        
        Query: {query}
        
        Based on the query, we've generated a learning path with {len(path)} steps.
        
        Here are the key details from our analysis:
        - Main topic: {analysis.get('target_topic', 'Not specified')}
        - Complexity level: {analysis.get('complexity_level', 'Not specified')}
        - Learning style: {analysis.get('learning_style', 'Not specified')}
        
        Present the learning path in a friendly, encouraging manner. Include:
        1. A brief introduction based on the query
        2. An overview of the learning path
        3. Details on the first 1-2 steps to get started
        4. Any additional tips or recommendations
        
        Make it conversational and motivating.
        """
        
        response = await self.model_adapter.generate_agent_response(
            agent_type="topic_navigator",
            prompt=prompt,
            temperature=0.7,  # Higher temperature for more creative response
            max_tokens=1500
        )
        
        return response['content']
    
    async def _process_with_fallback(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process using fallback logic."""
        query = input_data.get('query', '')
        
        # Create a basic response
        return {
            "content": f"I've created a simple learning path based on your query: '{query}'.",
            "path": [{
                "topic": query.replace(' ', '_').lower(),
                "title": query,
                "description": f"Learn about {query}",
                "complexity": "intermediate",
                "prerequisites": [],
                "resources": [],
                "estimated_duration": "unknown"
            }],
            "analysis": {
                "target_topic": query,
                "related_topics": [],
                "complexity_level": "intermediate",
                "learning_style": "balanced"
            },
            "agent": self.__class__.__name__
        }

    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        if not isinstance(input_data, dict):
            return False
        
        return True
