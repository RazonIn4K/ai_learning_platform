import logging
from typing import Dict, Any, List, Optional

from ..utils.topic_hierarchy import TopicHierarchy, create_default_hierarchy
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class TopicNavigatorAgent(BaseAgent):
    """Agent responsible for topic navigation and learning path adaptation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the topic navigator agent."""
        super().__init__(config)
        self.topic_hierarchy = self._initialize_topic_hierarchy()
    
    def _initialize_topic_hierarchy(self) -> TopicHierarchy:
        """Initialize the topic hierarchy."""
        return create_default_hierarchy()
    
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

    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a navigation-related message."""
        try:
            context = context or {}
            analysis = self._analyze_query(message, context)
            adapted_path = self.adapt_learning_path(
                context.get("current_path", []),
                context.get("user_profile", {})
            )
            
            return {
                "content": "Learning path adapted successfully",
                "path": adapted_path,
                "analysis": analysis,
                "agent": self.__class__.__name__
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "content": "Error adapting learning path",
                "error": str(e),
                "path": [],  # Always include a path, even if empty
                "agent": self.__class__.__name__
            }
