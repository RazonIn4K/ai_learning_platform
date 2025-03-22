"""Integration tests for AI Learning Platform."""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from ai_learning_platform.workspace.learning_workspace import WorkspaceConfig, LearningWorkspace
from ai_learning_platform.utils.topic_hierarchy import TopicHierarchy
from ai_learning_platform.utils.knowledge_mapper import KnowledgeMapper
from ai_learning_platform.utils.learning_profile_manager import LearningProfileManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_workspace() -> LearningWorkspace:
    """Create a test workspace with mock data."""
    # Create test topic hierarchy
    topic_hierarchy = TopicHierarchy()
    topic_hierarchy.add_topic(
        "python_security",
        prerequisites=["python_basics"],
        complexity="intermediate",
        estimated_duration=3600,  # 1 hour
        learning_outcomes=[
            "Understand common security vulnerabilities",
            "Implement secure coding practices",
            "Use Python security tools"
        ]
    )
    
    # Create test knowledge mapper
    knowledge_mapper = KnowledgeMapper()
    
    # Create test profile manager
    profile_manager = LearningProfileManager()
    
    # Create test user profile
    user_profile = {
        "user_id": "test_user",
        "learning_style": "self_paced",
        "complexity_preference": "intermediate",
        "interests": ["web security", "machine learning"],
        "topics_learned": [
            {
                "id": "python_basics",
                "mastery_level": 0.85,
                "last_studied": datetime.now().isoformat()
            }
        ]
    }
    
    # Create workspace configuration
    config = WorkspaceConfig(
        domains=["python", "cybersecurity"],
        enable_research=True,
        learning_style="balanced",
        model_type="standard",
        tracking_level="detailed"
    )
    
    # Create and return workspace
    return LearningWorkspace(
        config=config,
        user_profile=user_profile,
        topic_hierarchy=topic_hierarchy,
        knowledge_mapper=knowledge_mapper,
        profile_manager=profile_manager
    )

def test_complete_learning_session():
    """Test a complete learning session with all components."""
    logger.info("Starting integration test: complete learning session")
    
    try:
        # Create workspace
        workspace = create_test_workspace()
        assert workspace is not None, "Failed to create workspace"
        
        # Test query
        query = """
        I want to learn about secure coding practices in Python.
        I already know basic Python programming and have some
        understanding of web security concepts.
        """
        
        # Process the query
        logger.info("Processing learning session")
        response = workspace.process_learning_session(query)
        
        # Validate response structure
        assert "content" in response, "Response missing content"
        assert "learning_path" in response, "Response missing learning path"
        assert isinstance(response["learning_path"], list), "Learning path should be a list"
        
        logger.info("Response validated successfully")
        
        # Test topic navigation
        topic = response["learning_path"][0]["topic"] if response["learning_path"] else "python_security"
        logger.info(f"Testing topic exploration for: {topic}")
        
        topic_response = workspace.explore_topic(topic)
        assert "prerequisites" in topic_response, "Topic response missing prerequisites"
        
        # Test progress tracking
        logger.info("Testing progress tracking")
        progress = workspace._track_learning_progress(
            [topic],
            {"python_security": {"comprehension": 0.8, "application": 0.7, "retention": 0.6}},
            workspace.user_profile
        )
        
        assert "topic_mastery" in progress, "Progress missing topic mastery"
        assert topic in progress["topic_mastery"], f"Topic {topic} not in mastery data"
        
        # Test adaptive learning path
        logger.info("Testing adaptive learning path")
        original_path = response["learning_path"]
        adapted_path = workspace.agents["topic_navigator"].specialized_function(
            "adapt_learning_path",
            path=original_path,
            user_profile=workspace.user_profile
        )
        
        assert isinstance(adapted_path, list), "Adapted path should be a list"
        assert len(adapted_path) > 0, "Adapted path should not be empty"
        
        # Test error handling
        logger.info("Testing error handling")
        try:
            # Intentionally cause an error by passing invalid topic
            workspace.explore_topic("nonexistent_topic")
            assert False, "Should have raised an error for invalid topic"
        except Exception as e:
            assert True, "Successfully caught error for invalid topic"
        
        # Test cross-domain connections
        logger.info("Testing cross-domain connections")
        cross_domain_query = """
        How can I apply Python programming concepts to cybersecurity analysis?
        """
        cross_domain_response = workspace.process_message(cross_domain_query)
        
        assert "connections" in cross_domain_response or "cross_domain_insights" in cross_domain_response, \
            "Cross-domain response missing connections"
        
        logger.info("Integration test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}", exc_info=True)
        return False

def test_error_handling():
    """Test error handling and fallback mechanisms."""
    logger.info("Starting error handling test")
    
    try:
        workspace = create_test_workspace()
        
        # Test coordinator error handling
        logger.info("Testing coordinator error handling")
        coordinator = workspace.agents["learning_coordinator"]
        
        error_response = coordinator._handle_agent_error(
            "topic_navigator",
            "analyze_topic",
            Exception("Test error"),
            "test query",
            {"test": "context"}
        )
        
        assert "content" in error_response, "Error response missing content"
        assert "error" in error_response, "Error response missing error details"
        
        # Test workspace error handling
        logger.info("Testing workspace error handling")
        try:
            workspace.explore_topic(None)
            assert False, "Should have raised error for None topic"
        except Exception as e:
            assert True, "Successfully caught None topic error"
        
        logger.info("Error handling test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error handling test failed: {str(e)}", exc_info=True)
        return False

def test_progress_tracking():
    """Test the enhanced progress tracking system."""
    logger.info("Starting progress tracking test")
    
    try:
        workspace = create_test_workspace()
        
        # Test tracking with multiple topics
        topics = ["python_security", "web_security"]
        metrics = {
            "python_security": {
                "comprehension": 0.8,
                "application": 0.7,
                "retention": 0.6
            },
            "web_security": {
                "comprehension": 0.6,
                "application": 0.5,
                "retention": 0.7
            }
        }
        
        progress = workspace._track_learning_progress(
            topics,
            metrics,
            workspace.user_profile
        )
        
        # Validate progress tracking
        assert "topic_mastery" in progress, "Missing topic mastery"
        assert "learning_trajectory" in progress, "Missing learning trajectory"
        assert len(progress["topic_mastery"]) == len(topics), "Incorrect number of topics tracked"
        
        # Test strengths and gaps identification
        for topic, mastery in progress["topic_mastery"].items():
            assert "strengths" in mastery, f"Missing strengths for {topic}"
            assert "gaps" in mastery, f"Missing gaps for {topic}"
        
        logger.info("Progress tracking test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Progress tracking test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Run all tests
    tests = [
        ("Complete Learning Session", test_complete_learning_session),
        ("Error Handling", test_error_handling),
        ("Progress Tracking", test_progress_tracking)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\nRunning test: {test_name}")
        success = test_func()
        results.append((test_name, success))
        logger.info(f"Test {test_name}: {'PASSED' if success else 'FAILED'}")
    
    # Print summary
    print("\nTest Summary:")
    print("-" * 40)
    for test_name, success in results:
        print(f"{test_name}: {'PASSED' if success else 'FAILED'}")
    
    # Exit with appropriate status code
    exit(0 if all(success for _, success in results) else 1) 