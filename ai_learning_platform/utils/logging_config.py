"""Logging configuration for the AI Learning Platform."""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class LearningAnalytics:
    """Analytics handler for learning-related events."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up analytics logger
        self.logger = logging.getLogger("learning_analytics")
        self.logger.setLevel(logging.INFO)
        
        # Analytics file handler
        analytics_file = self.log_dir / "learning_analytics.jsonl"
        file_handler = logging.FileHandler(analytics_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(file_handler)

    def log_learning_event(
        self,
        event_type: str,
        user_id: str,
        data: Dict[str, Any],
        session_id: Optional[str] = None
    ):
        """Log a learning-related event with analytics data."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "session_id": session_id,
            "data": data
        }
        
        self.logger.info(json.dumps(event))
        return event

    def log_topic_completion(
        self,
        user_id: str,
        topic_id: str,
        mastery_level: float,
        time_spent: int,
        session_id: Optional[str] = None
    ):
        """Log topic completion event with mastery metrics."""
        return self.log_learning_event(
            "topic_completion",
            user_id,
            {
                "topic_id": topic_id,
                "mastery_level": mastery_level,
                "time_spent_seconds": time_spent
            },
            session_id
        )

    def log_learning_path_adaptation(
        self,
        user_id: str,
        original_path: list,
        adapted_path: list,
        reason: str,
        session_id: Optional[str] = None
    ):
        """Log when a learning path is adapted."""
        return self.log_learning_event(
            "path_adaptation",
            user_id,
            {
                "original_path": original_path,
                "adapted_path": adapted_path,
                "adaptation_reason": reason
            },
            session_id
        )

    def log_cross_domain_connection(
        self,
        user_id: str,
        source_domain: str,
        target_domain: str,
        connection_strength: float,
        session_id: Optional[str] = None
    ):
        """Log when a cross-domain connection is identified."""
        return self.log_learning_event(
            "cross_domain_connection",
            user_id,
            {
                "source_domain": source_domain,
                "target_domain": target_domain,
                "connection_strength": connection_strength
            },
            session_id
        )

    def log_error(
        self,
        user_id: str,
        error_type: str,
        error_message: str,
        context: Dict[str, Any],
        session_id: Optional[str] = None
    ):
        """Log error events with context."""
        return self.log_learning_event(
            "error",
            user_id,
            {
                "error_type": error_type,
                "error_message": error_message,
                "context": context
            },
            session_id
        )

def setup_logging(
    log_dir: str = "logs",
    log_level: int = logging.INFO
) -> LearningAnalytics:
    """Set up logging configuration for the platform."""
    # Create log directory
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(exist_ok=True)
    
    # Basic logging configuration
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir_path / "ai_learning.log"),
            logging.StreamHandler()
        ]
    )
    
    # Create analytics handler
    analytics = LearningAnalytics(log_dir)
    
    # Set up loggers for different components
    components = ["coordinator", "topic_navigator", "connection_expert", "workspace"]
    for component in components:
        logger = logging.getLogger(f"ai_learning.{component}")
        logger.setLevel(log_level)
        
        # Add file handler for component
        handler = logging.FileHandler(log_dir_path / f"{component}.log")
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(handler)
    
    return analytics 