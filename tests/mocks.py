# In tests/mocks.py

from unittest.mock import MagicMock
from typing import Dict, Any, List, Optional
from datetime import timedelta

def create_mock_topic_hierarchy():
    """Create a mock topic hierarchy for testing."""
    mock = MagicMock()
    
    # Create mock topics
    topics = {
        "python_basics": MagicMock(
            id="python_basics",
            title="Python Basics",
            description="Introduction to Python",
            prerequisites=[],
            complexity="beginner",
            estimated_duration=timedelta(hours=4)
        ),
        "machine_learning": MagicMock(
            id="machine_learning",
            title="Machine Learning",
            description="Introduction to ML",
            prerequisites=["python_basics", "math_basics"],
            complexity="intermediate",
            estimated_duration=timedelta(hours=8)
        ),
        "cybersecurity": MagicMock(
            id="cybersecurity", 
            title="Cybersecurity",
            description="Security fundamentals",
            prerequisites=["python_basics"],
            complexity="intermediate",
            estimated_duration=timedelta(hours=6)
        )
    }
    
    # Mock extract_topics to return predefined topics
    def mock_extract_topics(query):
        query_lower = query.lower()
        if "python" in query_lower and "security" in query_lower:
            return ["python_basics", "cybersecurity"]
        elif "python" in query_lower:
            return ["python_basics"]
        elif "machine" in query_lower or "ml" in query_lower:
            return ["machine_learning"]
        elif "security" in query_lower or "cyber" in query_lower:
            return ["cybersecurity"]
        else:
            return ["python_basics"]  # Default
    
    mock.extract_topics.side_effect = mock_extract_topics
    
    # Mock get_topic to return predefined topics
    def mock_get_topic(topic_id):
        return topics.get(topic_id)
    
    mock.get_topic.side_effect = mock_get_topic
    
    # Mock get_all_topics to return all topics
    mock.get_all_topics.return_value = list(topics.values())
    
    return mock

def create_mock_knowledge_mapper():
    """Create a mock knowledge mapper for testing."""
    mock = MagicMock()
    
    # Mock knowledge states
    knowledge_states = {
        "user1": {
            "python_basics": 0.8,
            "machine_learning": 0.4,
            "cybersecurity": 0.2
        },
        "user2": {
            "python_basics": 0.9,
            "machine_learning": 0.6,
            "cybersecurity": 0.7
        }
    }
    
    # Mock get_knowledge_state with two possible signatures
    def mock_get_knowledge_state(user_id, topic_id=None):
        if user_id not in knowledge_states:
            return {} if topic_id is None else 0.0
            
        if topic_id is None:
            return knowledge_states[user_id]
        else:
            return knowledge_states[user_id].get(topic_id, 0.0)
    
    mock.get_knowledge_state.side_effect = mock_get_knowledge_state
    
    return mock

def create_mock_model():
    """Create a mock model for testing."""
    mock = MagicMock()
    
    # Mock process_message to return predefined responses
    def mock_process_message(message, context=None):
        if "analyze" in message.lower():
            return """```json
            {
                "domains": ["python", "cybersecurity"],
                "is_navigation": true,
                "complexity_level": "intermediate",
                "learning_style": "balanced",
                "required_agents": ["topic_navigator", "python_expert", "cybersecurity_expert"],
                "confidence_score": 0.8
            }
            ```"""
        else:
            return "This is a mock response for general messages."
    
    mock.process_message.side_effect = mock_process_message
    
    return mock