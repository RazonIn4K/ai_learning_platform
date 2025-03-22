"""Integration tests for AI Learning Platform."""

import logging
from typing import Dict, Any, List

from ai_learning_platform.workspace.workspace_config import WorkspaceConfig
from ai_learning_platform.workspace.learning_workspace import LearningWorkspace
from ai_learning_platform.utils.topic_hierarchy import TopicHierarchy
from ai_learning_platform.utils.knowledge_mapper import KnowledgeMapper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_workspace():
    """Create a test workspace with all components."""
    config = WorkspaceConfig(
        domains=["python", "cybersecurity"],
        enable_research=True,
        learning_style="balanced",
        model_type="standard",
        tracking_level="detailed"
    )
    
    user_profile = {
        "user_id": "test_user",
        "learning_style": "balanced",
        "experience_level": "intermediate",
        "interests": ["python", "security"]
    }
    
    return LearningWorkspace(
        config=config,
        user_profile=user_profile,
        topic_hierarchy=TopicHierarchy(),
        knowledge_mapper=KnowledgeMapper()
    )

def test_complete_learning_session():
    """Test a complete learning session flow."""
    logger.info("Starting integration test: complete learning session")
    
    try:
        workspace = create_test_workspace()
        query = """
        I want to learn about secure coding practices in Python.
        I already know basic Python programming and have some
        understanding of web security concepts.
        """
        
        response = workspace.process_learning_session(query)
        assert "content" in response, "Response missing content"
        assert "learning_path" in response, "Response missing learning path"
        
        return True
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling and fallback mechanisms."""
    logger.info("Starting error handling test")
    
    try:
        workspace = create_test_workspace()
        response = workspace.explore_topic(None)
        assert False, "Should have raised error for None topic"
    except ValueError:
        return True
    except Exception as e:
        logger.error(f"Error handling test failed: {str(e)}")
        return False

def test_progress_tracking():
    """Test progress tracking system."""
    logger.info("Starting progress tracking test")
    
    try:
        workspace = create_test_workspace()
        topics = ["python_security", "web_security"]
        metrics = {
            "python_security": {
                "comprehension": 0.8,
                "application": 0.7
            }
        }
        
        progress = workspace.track_learning_progress(
            topics,
            metrics,
            workspace.user_profile
        )
        
        assert "topic_mastery" in progress, "Missing topic mastery"
        return True
    except Exception as e:
        logger.error(f"Progress tracking test failed: {str(e)}")
        return False

if __name__ == "__main__":
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
    
    print("\nTest Summary:")
    print("-" * 40)
    for test_name, success in results:
        print(f"{test_name}: {'PASSED' if success else 'FAILED'}")
    
    exit(0 if all(success for _, success in results) else 1)
