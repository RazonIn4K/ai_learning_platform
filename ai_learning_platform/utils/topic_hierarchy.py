"""Topic hierarchy for the AI Learning Platform."""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import timedelta

logger = logging.getLogger(__name__)

@dataclass
class Topic:
    """Represents a topic in the learning hierarchy."""
    id: str
    title: str
    description: str
    complexity: str
    estimated_duration: timedelta
    learning_outcomes: Optional[List[str]] = field(default_factory=list)
    prerequisites: List["Topic"] = field(default_factory=list)
    subtopics: List["Topic"] = field(default_factory=list)

    @property
    def level(self) -> int:
        """Return the hierarchical level based on ID (e.g., '1.1.2' -> 3)."""
        return len(self.id.split('.'))

    @property
    def parent_id(self) -> Optional[str]:
        """Return the parent topic ID (e.g., '1.1.2' -> '1.1')."""
        parts = self.id.split('.')
        return '.'.join(parts[:-1]) if len(parts) > 1 else None

    def add_prerequisite(self, prerequisite: "Topic") -> None:
        """Add a prerequisite topic."""
        self.prerequisites.append(prerequisite)

class TopicHierarchy:
    """Manages a hierarchy of learning topics."""
    def __init__(self):
        self.topics: Dict[str, Topic] = {}

    def add_topic(self, topic: Topic) -> None:
        """
        Add a topic to the hierarchy.
        
        Args:
            topic: The Topic object to add
        """
        if topic.id in self.topics:
            logger.warning(f"Topic with ID '{topic.id}' already exists. Skipping.")
            return
        self.topics[topic.id] = topic

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        """
        Get a topic by its ID.
        
        Args:
            topic_id: The ID of the topic to retrieve
            
        Returns:
            The Topic object if found, None otherwise
        """
        return self.topics.get(topic_id)

    def get_all_topics(self) -> List[Topic]:
        """
        Get all topics in the hierarchy.
        
        Returns:
            List of all Topic objects
        """
        return list(self.topics.values())

    def get_prerequisites(self, topic_id: str) -> List[str]:
        """
        Get prerequisites for a topic.
        
        Args:
            topic_id: The ID of the topic to get prerequisites for
            
        Returns:
            List of prerequisite topic IDs
        """
        topic = self.get_topic(topic_id)
        if topic:
            return [p.id for p in topic.prerequisites]
        return []

    def extract_topics(self, query: str) -> List[str]:
        """
        Extract topics from a query.
        
        Args:
            query: The query to extract topics from
            
        Returns:
            List of topic IDs
        """
        # Simple keyword-based extraction for this mock implementation
        query_lower = query.lower()
        extracted_topics = []
        
        for topic_id, topic in self.topics.items():
            if topic_id in query_lower or topic.title.lower() in query_lower:
                extracted_topics.append(topic_id)
        
        return extracted_topics

def load_topic_hierarchy(filepath: str) -> TopicHierarchy:
    """
    Load a topic hierarchy from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        TopicHierarchy instance
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        hierarchy = TopicHierarchy()
        
        # Recursive function to process topics and their subtopics
        def process_topic(topic_data, parent_id=None):
            # Create default values for backward compatibility
            topic_id = topic_data.get("id", "")
            topic_name = topic_data.get("name", "")
            
            # For backward compatibility, use title if name is not present
            title = topic_data.get("title", topic_name)
            
            # Set default values for required fields if not present
            description = topic_data.get("description", f"Description for {title}")
            complexity = topic_data.get("complexity", "intermediate")
            duration_seconds = topic_data.get("estimated_duration", 3600)  # Default 1 hour
            
            topic = Topic(
                id=topic_id,
                title=title,
                description=description,
                complexity=complexity,
                estimated_duration=timedelta(seconds=duration_seconds),
                learning_outcomes=topic_data.get("learning_outcomes", [])
            )
            
            hierarchy.add_topic(topic)
            
            # Process subtopics if present
            for subtopic_data in topic_data.get("subtopics", []):
                subtopic = process_topic(subtopic_data, topic_id)
                topic.subtopics.append(subtopic)
            
            return topic
        
        # Process all top-level topics
        for topic_data in data.get("topics", []):
            process_topic(topic_data)
        
        # Add prerequisites after all topics are loaded
        for topic_id, topic in hierarchy.topics.items():
            # If parent_id exists, add it as a prerequisite
            parent_id = topic.parent_id
            if parent_id and parent_id in hierarchy.topics:
                parent = hierarchy.get_topic(parent_id)
                if parent:
                    topic.add_prerequisite(parent)
        
        logger.info(f"Successfully loaded topic hierarchy from {filepath}")
        return hierarchy
        
    except Exception as e:
        logger.error(f"Failed to load topic hierarchy from {filepath}: {str(e)}")
        raise

def create_default_hierarchy() -> TopicHierarchy:
    """
    Create a default topic hierarchy.
    
    Returns:
        TopicHierarchy instance
    """
    hierarchy = TopicHierarchy()
    
    # Create topics
    python_basics = Topic(
        id="python_basics",
        title="Python Basics",
        description="Introduction to Python programming",
        complexity="beginner",
        estimated_duration=timedelta(hours=4)
    )
    
    machine_learning = Topic(
        id="machine_learning",
        title="Machine Learning",
        description="Introduction to machine learning",
        complexity="intermediate",
        estimated_duration=timedelta(hours=8)
    )
    
    cybersecurity = Topic(
        id="cybersecurity",
        title="Cybersecurity",
        description="Fundamentals of cybersecurity",
        complexity="intermediate",
        estimated_duration=timedelta(hours=6)
    )
    
    # Add prerequisites
    machine_learning.add_prerequisite(python_basics)
    cybersecurity.add_prerequisite(python_basics)
    
    # Add topics to hierarchy
    hierarchy.add_topic(python_basics)
    hierarchy.add_topic(machine_learning)
    hierarchy.add_topic(cybersecurity)
    
    return hierarchy
