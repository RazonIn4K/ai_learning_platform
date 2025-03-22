"""Tests for agent coordination and cross-domain functionality."""

import logging
import pytest
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import MagicMock

from ai_learning_platform.workspace.learning_workspace import WorkspaceConfig, LearningWorkspace
from ai_learning_platform.agents.coordinator import LearningCoordinatorAgent
from ai_learning_platform.agents.topic_navigator import TopicNavigatorAgent
from ai_learning_platform.agents.connection_expert import ConnectionExpert
from ai_learning_platform.utils.topic_hierarchy import TopicHierarchy, Topic
from ai_learning_platform.utils.knowledge_mapper import KnowledgeMapper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_topic_hierarchy():
    hierarchy = MagicMock()
    
    # Mock extract_topics to return predefined topics
    hierarchy.extract_topics.side_effect = lambda query: [
        "python_basics" if "python" in query.lower() else
        "machine_learning" if "ml" in query.lower() or "machine learning" in query.lower() else
        "cybersecurity" if "security" in query.lower() else
        "data_structures"
    ]
    
    # Mock get_all_topics to return a list of predefined topics
    hierarchy.get_all_topics.return_value = [
        Topic("python_basics", "Python Basics", "Introduction to Python programming"),
        Topic("machine_learning", "Machine Learning", "Introduction to ML concepts"),
        Topic("cybersecurity", "Cybersecurity", "Basic security concepts"),
        Topic("data_structures", "Data Structures", "Common data structures")
    ]
    
    return hierarchy

@pytest.fixture
def mock_knowledge_mapper():
    mapper = MagicMock()
    
    # Mock get_knowledge_state to return predefined states
    def mock_get_knowledge_state(user_id):
        states = {
            "python_basics": 0.8,  # Mastered
            "machine_learning": 0.4,  # In progress
            "cybersecurity": 0.1,  # Beginner
            "data_structures": 0.6  # Advanced beginner
        }
        return states
    
    mapper.get_knowledge_state.side_effect = mock_get_knowledge_state
    return mapper

@pytest.fixture
def test_workspace(mock_topic_hierarchy, mock_knowledge_mapper):
    """Create a test workspace with all necessary agents."""
    config = WorkspaceConfig(
        domains=["python", "cybersecurity", "machine_learning"],
        enable_research=True,
        learning_style="balanced",
        model_type="standard",
        tracking_level="detailed",
        project_focus="general"
    )
    
    user_profile = {
        "user_id": "test_user",
        "learning_style": "self_paced",
        "complexity_preference": "intermediate",
        "interests": ["web security", "machine learning", "data science"],
        "topics_learned": [
            {
                "id": "python_basics",
                "mastery_level": 0.85,
                "last_studied": datetime.now().isoformat()
            },
            {
                "id": "basic_statistics",
                "mastery_level": 0.75,
                "last_studied": datetime.now().isoformat()
            }
        ]
    }
    
    return LearningWorkspace(
        config=config,
        user_profile=user_profile,
        topic_hierarchy=mock_topic_hierarchy,
        knowledge_mapper=mock_knowledge_mapper
    )

def test_coordinator_specialized_functions(test_workspace):
    """Test that the coordinator correctly delegates specialized functions."""
    coordinator = test_workspace.agents["learning_coordinator"]
    
    # Test delegation to topic navigator
    result = coordinator.delegate_specialized_function(
        "topic_navigator",
        "adapt_learning_path",
        path=[{"topic": "machine_learning_basics"}],
        user_profile=test_workspace.user_profile
    )
    
    assert result is not None, "Delegation failed"
    assert isinstance(result, list), "Expected list response from adapt_learning_path"

def test_cross_domain_query_handling(test_workspace):
    """Test handling of queries that span multiple domains."""
    query = """
    How can I use machine learning techniques to detect security vulnerabilities in Python code?
    I have basic knowledge of Python and statistics.
    """
    
    response = test_workspace.process_learning_session(query)
    
    assert "learning_path" in response, "Missing learning path"
    assert "connections" in response, "Missing cross-domain connections"
    
    # Verify that the learning path includes topics from all relevant domains
    topics = [step["topic"] for step in response["learning_path"]]
    domains_covered = set()
    for topic in topics:
        if "python" in topic.lower():
            domains_covered.add("python")
        if "security" in topic.lower():
            domains_covered.add("cybersecurity")
        if "ml" in topic.lower() or "machine" in topic.lower():
            domains_covered.add("machine_learning")
    
    assert len(domains_covered) >= 2, "Learning path should cover multiple domains"

def test_connection_expert_bridging(test_workspace):
    """Test the Connection Expert's ability to identify meaningful bridges."""
    connection_expert = test_workspace.agents["connection_expert"]
    
    bridges = connection_expert.find_domain_bridges(
        source_domain="python",
        target_domain="cybersecurity",
        context="code security analysis"
    )
    
    assert bridges is not None, "No bridges found"
    assert len(bridges) > 0, "Expected at least one bridge between domains"
    
    for bridge in bridges:
        assert "source_topic" in bridge, "Bridge missing source topic"
        assert "target_topic" in bridge, "Bridge missing target topic"
        assert "connection_type" in bridge, "Bridge missing connection type"
        assert "relevance_score" in bridge, "Bridge missing relevance score"

def test_adaptive_path_adjustment(test_workspace):
    """Test the system's ability to adapt learning paths based on progress."""
    # Initial learning path
    initial_query = "I want to learn about machine learning for cybersecurity"
    initial_response = test_workspace.process_learning_session(initial_query)
    initial_path = initial_response["learning_path"]
    
    # Simulate progress
    test_workspace.user_profile["topics_learned"].append({
        "id": "machine_learning_basics",
        "mastery_level": 0.9,
        "last_studied": datetime.now().isoformat()
    })
    
    # Get adapted path
    adapted_path = test_workspace.agents["learning_coordinator"].delegate_specialized_function(
        "topic_navigator",
        "adapt_learning_path",
        path=initial_path,
        user_profile=test_workspace.user_profile
    )
    
    assert len(adapted_path) <= len(initial_path), "Adapted path should skip mastered topics"
    
    # Verify that mastered topics are not repeated
    mastered_topics = {topic["id"] for topic in test_workspace.user_profile["topics_learned"]}
    adapted_topics = {step["topic"] for step in adapted_path}
    assert not (mastered_topics & adapted_topics), "Adapted path contains already mastered topics"

def test_error_recovery(test_workspace):
    """Test the system's ability to recover from agent failures."""
    coordinator = test_workspace.agents["learning_coordinator"]
    
    # Simulate agent failure
    error_response = coordinator.handle_agent_error(
        "topic_navigator",
        "analyze_topic",
        Exception("Simulated failure"),
        "complex cross-domain query",
        {"domain": "cybersecurity"}
    )
    
    assert "fallback_response" in error_response, "Missing fallback response"
    assert "error_details" in error_response, "Missing error details"
    assert error_response["success"] is False, "Error not properly indicated"

def test_learning_effectiveness_metrics(test_workspace):
    """Test the collection and analysis of learning effectiveness metrics."""
    metrics = test_workspace.analyze_learning_effectiveness(
        user_id="test_user",
        time_period_days=30
    )
    
    assert "completion_rate" in metrics, "Missing completion rate"
    assert "topic_mastery_growth" in metrics, "Missing mastery growth"
    assert "engagement_metrics" in metrics, "Missing engagement metrics"
    assert "recommended_adjustments" in metrics, "Missing recommended adjustments"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 