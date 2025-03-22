"""Knowledge agent for managing and analyzing learning knowledge."""

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseLearningAgent

logger = logging.getLogger(__name__)

class KnowledgeAgent(BaseLearningAgent):
    """Agent for managing and analyzing knowledge."""
    
    def __init__(
        self,
        model_name: str,
        model_params: Optional[Dict[str, Any]] = None,
        topic_hierarchy: Optional[Any] = None,
        profile_manager: Optional[Any] = None,
        knowledge_explorer: Optional[Any] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize the knowledge agent."""
        system_message = """
        You are a Knowledge Agent, specialized in managing and analyzing learning knowledge.
        Your role is to:
        1. Analyze user learning progress and patterns
        2. Identify knowledge gaps and strengths
        3. Recommend personalized learning strategies
        4. Track mastery of topics and concepts
        5. Generate insights about learning effectiveness
        
        Always strive to provide personalized, actionable insights that enhance learning outcomes.
        """
        
        super().__init__(
            model_name=model_name,
            model_params=model_params,
            system_message=system_message,
            **kwargs
        )
        
        self.topic_hierarchy = topic_hierarchy
        self.profile_manager = profile_manager
        self.knowledge_explorer = knowledge_explorer
        self.user_profile = user_profile or {}
    
    def analyze_progress(
        self,
        user_profile: Dict[str, Any],
        learning_history: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze user's learning progress."""
        try:
            # Create analysis prompt
            prompt = f"""
            Analyze learning progress for user with profile:
            {self._format_user_profile(user_profile)}
            
            Learning History:
            {self._format_learning_history(learning_history) if learning_history else 'No history available'}
            
            Please analyze:
            1. Overall progress and mastery
            2. Learning patterns and preferences
            3. Areas of strength
            4. Knowledge gaps
            5. Learning velocity and engagement
            """
            
            response = self.process_message(prompt)
            
            # Parse and structure the analysis
            analysis = self._parse_progress_analysis(response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing progress: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "status": "failed",
                "user_id": user_profile.get("user_id", "unknown")
            }
    
    def get_recommendations(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get personalized learning recommendations."""
        try:
            if not context:
                context = {}
            
            # Create recommendation prompt
            prompt = f"""
            Generate learning recommendations based on:
            User Profile: {self._format_user_profile(self.user_profile)}
            Context: {self._format_context(context)}
            
            Consider:
            1. User's learning goals and interests
            2. Current knowledge level and progress
            3. Learning style and preferences
            4. Available time and resources
            5. Previous learning patterns
            """
            
            response = self.process_message(prompt)
            
            # Parse and structure the recommendations
            recommendations = self._parse_recommendations(response)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def evaluate_mastery(
        self,
        topic: str,
        assessment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate mastery level for a specific topic."""
        try:
            # Create evaluation prompt
            prompt = f"""
            Evaluate mastery for topic: {topic}
            
            Assessment Data:
            {self._format_assessment_data(assessment_data)}
            
            Consider:
            1. Comprehension level
            2. Application ability
            3. Problem-solving skills
            4. Knowledge retention
            5. Practical implementation
            """
            
            response = self.process_message(prompt)
            
            # Parse and structure the evaluation
            evaluation = self._parse_mastery_evaluation(response)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating mastery: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "status": "failed",
                "topic": topic
            }
    
    def _format_user_profile(self, profile: Dict[str, Any]) -> str:
        """Format user profile for prompts."""
        sections = [
            f"User ID: {profile.get('user_id', 'unknown')}",
            f"Learning Style: {profile.get('learning_style', 'not specified')}",
            f"Interests: {', '.join(profile.get('interests', []))}",
            "Topics Learned:",
        ]
        
        for topic in profile.get("topics_learned", []):
            sections.append(f"- {topic.get('id', 'unknown')}: {topic.get('mastery_level', 0)}")
        
        return "\n".join(sections)
    
    def _format_learning_history(self, history: Dict[str, Any]) -> str:
        """Format learning history for prompts."""
        sections = ["Recent Learning Sessions:"]
        
        for session in history.get("sessions", [])[-5:]:  # Last 5 sessions
            sections.append(f"""
            Session: {session.get('session_id', 'unknown')}
            - Date: {session.get('timestamp', 'unknown')}
            - Topics: {', '.join(session.get('topics', []))}
            - Duration: {session.get('duration', 0)} minutes
            """)
        
        return "\n".join(sections)
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for prompts."""
        sections = []
        
        if "current_topic" in context:
            sections.append(f"Current Topic: {context['current_topic']}")
        
        if "learning_goals" in context:
            sections.append(f"Learning Goals: {', '.join(context['learning_goals'])}")
        
        if "time_available" in context:
            sections.append(f"Time Available: {context['time_available']} minutes")
        
        return "\n".join(sections) or "No specific context provided"
    
    def _format_assessment_data(self, data: Dict[str, Any]) -> str:
        """Format assessment data for prompts."""
        sections = [
            f"Comprehension Score: {data.get('comprehension', 0)}",
            f"Application Score: {data.get('application', 0)}",
            f"Problem-Solving Score: {data.get('problem_solving', 0)}",
            "Specific Areas:",
        ]
        
        for area, score in data.get("areas", {}).items():
            sections.append(f"- {area}: {score}")
        
        return "\n".join(sections)
    
    def _parse_progress_analysis(self, response: str) -> Dict[str, Any]:
        """Parse progress analysis from agent response."""
        # Implementation would parse the text response into structured data
        # This is a placeholder implementation
        return {
            "overall_progress": 0.75,
            "strengths": ["example_strength"],
            "gaps": ["example_gap"],
            "learning_velocity": "steady"
        }
    
    def _parse_recommendations(self, response: str) -> Dict[str, Any]:
        """Parse recommendations from agent response."""
        # Implementation would parse the text response into structured data
        # This is a placeholder implementation
        return {
            "next_topics": ["example_topic"],
            "learning_strategies": ["example_strategy"],
            "resources": ["example_resource"],
            "estimated_timeline": "2 weeks"
        }
    
    def _parse_mastery_evaluation(self, response: str) -> Dict[str, Any]:
        """Parse mastery evaluation from agent response."""
        # Implementation would parse the text response into structured data
        # This is a placeholder implementation
        return {
            "mastery_level": 0.8,
            "strengths": ["example_strength"],
            "areas_for_improvement": ["example_area"],
            "next_steps": ["example_step"]
        } 