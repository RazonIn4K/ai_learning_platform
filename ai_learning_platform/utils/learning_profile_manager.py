import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class LearningProfileManager:
    """
    Manages learning profiles, including loading, saving, and updating user preferences.
    """
    def __init__(self, config_path: str = "configs/workspace_config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"profiles": {}}

    def save_config(self) -> None:
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def profile_exists(self, user_id: str) -> bool:
        """Check if a profile exists for the given user ID."""
        return user_id in self.config.get("profiles", {})

    def load_history(self, user_id: str, history_data: list) -> bool:
        """Load learning history for a user."""
        profile = self.get_profile(user_id)
        if not profile:
            return False
        profile["session_history"] = history_data
        self.update_profile(user_id, profile)
        return True

    def create_profile(self, profile_data: Dict[str, Any]) -> None:
        """Creates a new learning profile."""
        profile_name = profile_data.get("user_id", "default")
        if "profiles" not in self.config:
            self.config["profiles"] = {}
        self.config["profiles"][profile_name] = profile_data
        self.save_config()

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user's learning profile."""
        return self.config.get("profiles", {}).get(user_id)

    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """Update a user's learning profile."""
        if "profiles" not in self.config:
            self.config["profiles"] = {}
        self.config["profiles"][user_id] = profile_data
        self.save_config()

    def delete_profile(self, profile_name: str) -> None:
        """
        Deletes a learning profile.
        """
        if profile_name in self.config.get("profiles", {}):
            del self.config["profiles"][profile_name]
            self.save_config()
        else:
            print(f"Error: Profile '{profile_name}' not found.")

    def get_learning_context(self, profile_name: str = None) -> Dict[str, Any]:
        """
        Get the current learning context for a user.
        
        Args:
            profile_name: Optional profile name to get context for
            
        Returns:
            Dictionary containing learning context
        """
        profile = self.get_profile(profile_name) if profile_name else self.config.get("current_profile", {})
        
        return {
            "topics_learned": profile.get("topics_learned", []),
            "interests": profile.get("interests", []),
            "learning_style": profile.get("learning_style", "self_paced"),
            "complexity_preference": profile.get("complexity_preference", "beginner"),
            "current_topics": profile.get("current_topics", []),
            "recent_sessions": profile.get("session_history", [])[-5:],  # Last 5 sessions
            "mastered_topics": self.get_mastered_topics(profile_name)
        }

    def get_mastered_topics(self, profile_name: str = None) -> List[str]:
        """
        Get list of topics mastered by the user.
        
        Args:
            profile_name: Optional profile name to get mastered topics for
            
        Returns:
            List of mastered topic IDs
        """
        profile = self.get_profile(profile_name) if profile_name else self.config.get("current_profile", {})
        return [
            topic for topic in profile.get("topics_learned", [])
            if self._check_topic_mastery(topic, profile)
        ]

    def extract_mastered_topics(
        self,
        topics: List[str],
        learning_metrics: Dict[str, Any]
    ) -> List[str]:
        """
        Extract mastered topics from learning response.
        
        Args:
            topics: List of topics covered
            learning_metrics: Metrics from learning session
            
        Returns:
            List of newly mastered topics
        """
        mastered = []
        for topic in topics:
            topic_metrics = learning_metrics.get(topic, {})
            if self._is_topic_mastered(topic_metrics):
                mastered.append(topic)
        return mastered

    def update_progress(
        self,
        profile: Dict[str, Any],
        mastered_topics: List[str],
        learning_metrics: Dict[str, Any]
    ) -> None:
        """
        Update user progress with new learning achievements.
        
        Args:
            profile: User profile to update
            mastered_topics: List of newly mastered topics
            learning_metrics: Metrics from learning session
        """
        # Update topics learned
        if "topics_learned" not in profile:
            profile["topics_learned"] = []
        profile["topics_learned"].extend(mastered_topics)
        profile["topics_learned"] = list(set(profile["topics_learned"]))  # Remove duplicates

        # Update session history
        if "session_history" not in profile:
            profile["session_history"] = []
        profile["session_history"].append({
            "timestamp": datetime.now().isoformat(),
            "topics_covered": mastered_topics,
            "metrics": learning_metrics
        })

        # Update learning metrics
        if "learning_metrics" not in profile:
            profile["learning_metrics"] = {}
        for topic, metrics in learning_metrics.items():
            if topic not in profile["learning_metrics"]:
                profile["learning_metrics"][topic] = metrics
            else:
                profile["learning_metrics"][topic].update(metrics)

        # Save updated profile
        self.update_profile(profile.get("name", "default"), profile)

    def _check_topic_mastery(self, topic: str, profile: Dict[str, Any]) -> bool:
        """
        Check if a topic is considered mastered based on learning metrics.
        
        Args:
            topic: Topic to check
            profile: User profile containing learning metrics
            
        Returns:
            True if topic is mastered
        """
        metrics = profile.get("learning_metrics", {}).get(topic, {})
        return self._is_topic_mastered(metrics)

    def _is_topic_mastered(self, metrics: Dict[str, Any]) -> bool:
        """
        Determine if a topic is mastered based on metrics.
        
        Args:
            metrics: Learning metrics for the topic
            
        Returns:
            True if metrics indicate mastery
        """
        if not metrics:
            return False

        # Example mastery criteria - adjust based on your needs
        required_score = 0.8
        required_practice = 3

        completion_score = metrics.get("completion_score", 0)
        practice_count = metrics.get("practice_completed", 0)
        assessment_score = metrics.get("assessment_score", 0)

        return (
            completion_score >= required_score
            and practice_count >= required_practice
            and assessment_score >= required_score
        )

    def record_session_event(
        self,
        profile_name: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """Record a learning session event.
        
        Args:
            profile_name: Name of the profile to record event for
            event_type: Type of event (e.g., 'completion', 'assessment', 'practice')
            event_data: Data associated with the event
        """
        profile = self.get_profile(profile_name)
        if not profile:
            print(f"Error: Profile '{profile_name}' not found.")
            return
            
        if "session_history" not in profile:
            profile["session_history"] = []
            
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": event_data
        }
        
        profile["session_history"].append(event)
        self.update_profile(profile_name, profile)
        
    def get_learning_history(
        self,
        profile_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get learning history for a profile.
        
        Args:
            profile_name: Name of the profile to get history for
            start_date: Optional ISO format date to filter from
            end_date: Optional ISO format date to filter to
            event_types: Optional list of event types to filter by
            
        Returns:
            List of learning history events
        """
        profile = self.get_profile(profile_name)
        if not profile:
            print(f"Error: Profile '{profile_name}' not found.")
            return []
            
        history = profile.get("session_history", [])
        
        # Apply date filters if provided
        if start_date:
            history = [
                event for event in history
                if event["timestamp"] >= start_date
            ]
            
        if end_date:
            history = [
                event for event in history
                if event["timestamp"] <= end_date
            ]
            
        # Apply event type filter if provided
        if event_types:
            history = [
                event for event in history
                if event["type"] in event_types
            ]
            
        return history

    def update_topic_mastery(self, user_id: str, topic: str, mastery_metrics: Dict[str, Any]) -> None:
        """
        Update topic mastery for a user.
        
        Args:
            user_id: User identifier
            topic: Topic identifier
            mastery_metrics: Metrics for the topic mastery
        """
        # Get the user profile
        profile = self.get_profile(user_id)
        if not profile:
            logger.warning(f"Profile not found for user {user_id}")
            return
        
        # Ensure learning_metrics exists
        if "learning_metrics" not in profile:
            profile["learning_metrics"] = {}
        
        # Ensure topic entry exists
        if topic not in profile["learning_metrics"]:
            profile["learning_metrics"][topic] = {}
        
        # Update metrics
        profile["learning_metrics"][topic].update(mastery_metrics)
        
        # Calculate overall mastery level
        if "overall_mastery" not in profile["learning_metrics"][topic]:
            # Compute weighted average of metrics
            metrics_values = [v for k, v in mastery_metrics.items() 
                            if isinstance(v, (int, float))]
            if metrics_values:
                overall_mastery = sum(metrics_values) / len(metrics_values)
                profile["learning_metrics"][topic]["overall_mastery"] = overall_mastery
        
        # Save the updated profile
        self.update_profile(user_id, profile)
        
        # Check if topic is now mastered
        if self._is_topic_mastered(profile["learning_metrics"][topic]):
            # Add to mastered topics if not already there
            if "mastered_topics" not in profile:
                profile["mastered_topics"] = []
            if topic not in profile["mastered_topics"]:
                profile["mastered_topics"].append(topic)
                # Save again with mastered topics updated
                self.update_profile(user_id, profile)

    def get_learning_progress(self, user_id: str) -> Dict[str, Any]:
        """Get learning progress for a user."""
        profile = self.get_profile(user_id)
        if not profile:
            return {}
        return {
            "completed_topics": profile.get("topics_learned", []),
            "current_progress": profile.get("current_progress", {}),
            "mastery_levels": profile.get("mastery_levels", {})
        }

    def update_learning_progress(self, user_id: str, topic: str, status: str) -> None:
        """Update learning progress for a specific topic."""
        profile = self.get_profile(user_id)
        if not profile:
            profile = {
                "user_id": user_id,
                "topics_learned": [],
                "current_progress": {},
                "mastery_levels": {}
            }
        
        if status == "completed":
            if topic not in profile["topics_learned"]:
                profile["topics_learned"].append(topic)
            profile["current_progress"][topic] = 100
        elif status == "in_progress":
            if topic in profile["topics_learned"]:
                profile["topics_learned"].remove(topic)
            profile["current_progress"][topic] = 50
        elif status == "reset":
            if topic in profile["topics_learned"]:
                profile["topics_learned"].remove(topic)
            profile["current_progress"].pop(topic, None)
            profile["mastery_levels"].pop(topic, None)
        
        self.update_profile(user_id, profile)
