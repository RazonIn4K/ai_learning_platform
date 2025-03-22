from typing import List, Dict, Any

class LearningProfileManager:
    def get_user_strengths(self, user_id: str) -> List[str]:
        """
        Get list of strengths for a user based on learning metrics.
        
        Args:
            user_id: User ID to get strengths for
            
        Returns:
            List of strength areas
        """
        profile = self.get_profile(user_id)
        if not profile:
            return []
        
        strengths = []
        # Extract strengths from learning metrics
        metrics = profile.get("learning_metrics", {})
        for topic, topic_metrics in metrics.items():
            if self._is_topic_strength(topic_metrics):
                strengths.append(topic)
            
        # Add explicitly recorded strengths
        strengths.extend(profile.get("recorded_strengths", []))
        
        return list(set(strengths))  # Remove duplicates

    def _is_topic_strength(self, metrics: Dict[str, Any]) -> bool:
        """
        Determine if a topic is a strength based on metrics.
        
        Args:
            metrics: Learning metrics for the topic
            
        Returns:
            True if metrics indicate strength
        """
        # Define criteria for strength
        threshold = 0.75
        
        # Check common metrics
        if metrics.get("mastery_level", 0) >= threshold:
            return True
        if metrics.get("completion_score", 0) >= threshold:
            return True
        if metrics.get("assessment_score", 0) >= threshold:
            return True
        
        return False

    def get_learning_gaps(self, user_id: str) -> List[str]:
        """
        Get list of learning gaps for a user.
        
        Args:
            user_id: User ID to get gaps for
            
        Returns:
            List of gap areas
        """
        profile = self.get_profile(user_id)
        if not profile:
            return []
        
        gaps = []
        # Extract gaps from learning metrics
        metrics = profile.get("learning_metrics", {})
        for topic, topic_metrics in metrics.items():
            if self._is_topic_gap(topic_metrics):
                gaps.append(topic)
            
        # Add explicitly recorded gaps
        gaps.extend(profile.get("recorded_gaps", []))
        
        return list(set(gaps))  # Remove duplicates

    def _is_topic_gap(self, metrics: Dict[str, Any]) -> bool:
        """
        Determine if a topic is a learning gap based on metrics.
        
        Args:
            metrics: Learning metrics for the topic
            
        Returns:
            True if metrics indicate a gap
        """
        # Define criteria for gap
        threshold = 0.4
        
        # Check if any metrics indicate a gap
        if metrics.get("mastery_level", 1) <= threshold:
            return True
        if metrics.get("completion_score", 1) <= threshold:
            return True
        if metrics.get("assessment_score", 1) <= threshold:
            return True
        
        return False 