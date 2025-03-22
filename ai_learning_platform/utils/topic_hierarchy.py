"""Topic Hierarchy utility for the AI Learning Platform."""

from typing import Dict, Any, Optional, List, Set, Union
import json
import re
import os
from pathlib import Path
import logging
from datetime import timedelta
from dataclasses import dataclass, field

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class Topic:
    """Represents a learning topic."""
    id: str
    title: str
    description: Optional[str] = None
    parent: Optional['Topic'] = None
    complexity: str = "intermediate"
    estimated_duration: Optional[timedelta] = timedelta(hours=2)
    learning_outcomes: Optional[List[str]] = None
    practical_applications: Optional[List[str]] = None
    resources: Optional[List[Dict[str, str]]] = None
    practice_items: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    related_topics: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = field(default_factory=list)

    def __post_init__(self):
        self.subtopics = []

    def add_subtopic(self, subtopic: 'Topic') -> None:
        """
        Add a subtopic to this topic.
        
        Args:
            subtopic: Subtopic to add
        """
        self.subtopics.append(subtopic)
        subtopic.parent = self
    
    def add_prerequisite(self, prerequisite: 'Topic') -> None:
        """
        Add a prerequisite to this topic.
        
        Args:
            prerequisite: Prerequisite topic
        """
        if prerequisite not in self.prerequisites:
            self.prerequisites.append(prerequisite)
    
    def get_subtopics(self) -> List['Topic']:
        """
        Get all subtopics of this topic.
        
        Returns:
            List of subtopics
        """
        return self.subtopics
    
    def get_prerequisites(self) -> List['Topic']:
        """
        Get all prerequisites of this topic.
        
        Returns:
            List of prerequisites
        """
        return self.prerequisites
    
    def get_ancestors(self) -> List['Topic']:
        """
        Get all ancestors of this topic.
        
        Returns:
            List of ancestors
        """
        ancestors = []
        current = self.parent
        
        while current:
            ancestors.append(current)
            current = current.parent
        
        return ancestors
    
    def get_path(self) -> str:
        """
        Get the full path of this topic.
        
        Returns:
            Path as a string (e.g., "Mathematics > Calculus > Integration")
        """
        path = [self.title]
        current = self.parent
        
        while current:
            path.insert(0, current.title)
            current = current.parent
        
        return " > ".join(path)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the topic to a dictionary.
        
        Returns:
            Topic as a dictionary
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "prerequisites": [p.id for p in self.prerequisites],
            "subtopics": [s.id for s in self.subtopics],
            "path": self.get_path()
        }
    
    def __str__(self) -> str:
        return f"{self.id}: {self.title}"
    
    def __repr__(self) -> str:
        return f"Topic(id='{self.id}', title='{self.title}')"

    @property
    def name(self) -> str:
        """Get the name of the topic."""
        return self.title

    @property
    def leads_to(self) -> List[str]:
        """Get the topics that this topic leads to."""
        return self.related_topics or []


class TopicHierarchy:
    """Class for managing a hierarchy of topics."""
    
    def __init__(self):
        """Initialize an empty topic hierarchy."""
        self.topics = {}  # Dictionary of topics by ID
        self.root_topics = []  # List of root topics
    
    def add_topic(
        self,
        id: str,
        title: str,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        prerequisite_ids: Optional[List[str]] = None
    ) -> Topic:
        """
        Add a topic to the hierarchy.
        
        Args:
            id: Topic ID
            title: Topic title
            description: Optional topic description
            parent_id: Optional parent topic ID
            prerequisite_ids: Optional list of prerequisite topic IDs
            
        Returns:
            The created topic
        """
        # Check if topic already exists
        if id in self.topics:
            logger.warning(f"Topic {id} already exists, updating title and description")
            topic = self.topics[id]
            topic.title = title
            if description:
                topic.description = description
            return topic
        
        # Create new topic
        parent = self.topics.get(parent_id) if parent_id else None
        topic = Topic(id, title, description, parent)
        self.topics[id] = topic
        
        # Add to parent if exists
        if parent:
            parent.add_subtopic(topic)
        else:
            self.root_topics.append(topic)
        
        # Add prerequisites if any
        if prerequisite_ids:
            for prereq_id in prerequisite_ids:
                if prereq_id in self.topics:
                    topic.add_prerequisite(self.topics[prereq_id])
                else:
                    logger.warning(f"Prerequisite {prereq_id} not found for topic {id}")
        
        return topic
    
    def get_topic(self, id: str) -> Optional[Topic]:
        """
        Get a topic by ID.
        
        Args:
            id: Topic ID
            
        Returns:
            Topic if found, None otherwise
        """
        return self.topics.get(id)
    
    def get_top_level_topics(self) -> List[Topic]:
        """
        Get all top-level topics.
        
        Returns:
            List of top-level topics
        """
        return self.root_topics
    
    def search_topics(self, query: str) -> List[Topic]:
        """
        Search for topics matching a query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching topics
        """
        query = query.lower()
        results = []
        
        for topic in self.topics.values():
            # Match ID, title, or description
            if (query in topic.id.lower() or 
                query in topic.title.lower() or 
                (topic.description and query in topic.description.lower())):
                results.append(topic)
        
        return results
    
    def get_all_topics(self) -> List[Topic]:
        """
        Get all topics in the hierarchy.
        
        Returns:
            List of all topics
        """
        return list(self.topics.values())
    
    def get_subtopics_recursive(self, topic_id: str) -> List[Topic]:
        """
        Get all subtopics of a topic recursively.
        
        Args:
            topic_id: Topic ID
            
        Returns:
            List of all subtopics
        """
        topic = self.get_topic(topic_id)
        if not topic:
            return []
        
        result = []
        
        def collect_subtopics(t: Topic):
            for subtopic in t.get_subtopics():
                result.append(subtopic)
                collect_subtopics(subtopic)
        
        collect_subtopics(topic)
        return result
    
    def get_learning_path(
        self,
        target_topic_id: str,
        known_topics: Optional[List[str]] = None
    ) -> List[Topic]:
        """
        Get a learning path to reach a target topic.
        
        Args:
            target_topic_id: Target topic ID
            known_topics: Optional list of already known topic IDs
            
        Returns:
            List of topics in the learning path
        """
        target = self.get_topic(target_topic_id)
        if not target:
            return []
        
        known_topics_set = set(known_topics or [])
        visited = set()
        path = []
        
        def visit(topic: Topic):
            if topic.id in visited or topic.id in known_topics_set:
                return
            
            visited.add(topic.id)
            
            # Visit prerequisites first
            for prereq in topic.get_prerequisites():
                visit(prereq)
            
            # Visit parent topics if needed
            if topic.parent and topic.parent.id not in visited and topic.parent.id not in known_topics_set:
                visit(topic.parent)
            
            path.append(topic)
        
        visit(target)
        return path
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the hierarchy to a dictionary.
        
        Returns:
            Hierarchy as a dictionary
        """
        return {
            "topics": {id: topic.to_dict() for id, topic in self.topics.items()},
            "root_topics": [topic.id for topic in self.root_topics]
        }
    
    def from_dict(self, data: Dict[str, Any]) -> 'TopicHierarchy':
        """
        Load the hierarchy from a dictionary.
        
        Args:
            data: Hierarchy data
            
        Returns:
            Self for chaining
        """
        # Clear existing data
        self.topics = {}
        self.root_topics = []
        
        # Create topics
        topics_data = data.get("topics", {})
        for id, topic_data in topics_data.items():
            self.add_topic(
                id=id,
                title=topic_data["title"],
                description=topic_data.get("description")
            )
        
        # Set parent-child relationships
        for id, topic_data in topics_data.items():
            topic = self.topics[id]
            
            # Add prerequisites
            for prereq_id in topic_data.get("prerequisites", []):
                if prereq_id in self.topics:
                    topic.add_prerequisite(self.topics[prereq_id])
        
        # Set root topics
        root_topic_ids = data.get("root_topics", [])
        self.root_topics = [self.topics[id] for id in root_topic_ids if id in self.topics]
        
        return self
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save the hierarchy to a JSON file.
        
        Args:
            filepath: Path to save the file
        """
        data = self.to_dict()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filepath: str) -> 'TopicHierarchy':
        """
        Load the hierarchy from a JSON file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Self for chaining
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            return self.from_dict(data)
        
        except Exception as e:
            logger.error(f"Error loading topic hierarchy from {filepath}: {str(e)}")
            return self

    def validate_hierarchy(self) -> List[str]:
        """
        Validate the topic hierarchy structure.
        
        Returns:
            List of validation errors, empty if valid
        """
        errors = []
        
        for topic_id, topic in self.topics.items():
            # Validate parent-child relationships
            parts = topic_id.split('.')
            if len(parts) > 1:
                parent_id = '.'.join(parts[:-1])
                if parent_id not in self.topics:
                    errors.append(f"Topic {topic_id} missing parent {parent_id}")
                elif topic.parent != self.topics[parent_id]:
                    errors.append(f"Topic {topic_id} has incorrect parent relationship")
        
        return errors

    def extract_topics(self, query: str) -> List[str]:
        """
        Extract topic IDs from a query string.
        
        Args:
            query: Query string to analyze
            
        Returns:
            List of topic IDs found in the query
        """
        # First try exact matches
        exact_matches = []
        query_lower = query.lower()
        
        for topic in self.topics.values():
            if topic.title.lower() in query_lower:
                exact_matches.append(topic.id)
        
        if exact_matches:
            return exact_matches
        
        # If no exact matches, try fuzzy search
        search_results = self.search_topics(query)
        return [topic.id for topic in search_results]


# Integrated topic hierarchy for Computer Science and Cybersecurity
INTEGRATED_TOPIC_HIERARCHY = {
    "topics": {
        # 1. Computing Foundations
        "1": {
            "title": "Computing Foundations",
            "description": "Core foundations of computer science"
        },
        
        # 1.1 Mathematical Foundations
        "1.1": {
            "title": "Mathematical Foundations",
            "description": "Mathematical basis for computing",
            "parent": "1"
        },
        "1.1.1": {
            "title": "Discrete Mathematics",
            "description": "Study of mathematical structures with discrete values",
            "parent": "1.1"
        },
        "1.1.2": {
            "title": "Linear Algebra and Calculus",
            "description": "Study of linear equations and continuous mathematics",
            "parent": "1.1"
        },
        "1.1.3": {
            "title": "Probability and Statistics",
            "description": "Study of randomness and data analysis",
            "parent": "1.1"
        },
        "1.1.4": {
            "title": "Information Theory",
            "description": "Study of quantification of information",
            "parent": "1.1",
            "prerequisites": ["1.1.1", "1.1.3"]
        },
        "1.1.5": {
            "title": "Graph Theory",
            "description": "Study of graphs and their properties",
            "parent": "1.1",
            "prerequisites": ["1.1.1"]
        },
        "1.1.6": {
            "title": "Topological Data Analysis",
            "description": "Study of shape in data",
            "parent": "1.1",
            "prerequisites": ["1.1.2", "1.1.3"]
        },
        "1.1.7": {
            "title": "Category Theory",
            "description": "Study of mathematical structures and relationships",
            "parent": "1.1",
            "prerequisites": ["1.1.1", "1.1.5"]
        },
        "1.1.8": {
            "title": "Formal Methods and Verification",
            "description": "Mathematical approaches to software correctness",
            "parent": "1.1",
            "prerequisites": ["1.1.1", "1.1.7"]
        },

        # 1.2 Theoretical Computer Science
        "1.2": {
            "title": "Theoretical Computer Science",
            "description": "Theoretical foundations of computing",
            "parent": "1",
            "prerequisites": ["1.1"]
        },
        "1.2.1": {
            "title": "Automata Theory",
            "description": "Study of abstract machines and formal languages",
            "parent": "1.2",
            "prerequisites": ["1.1.1"]
        },
        "1.2.2": {
            "title": "Computability Theory",
            "description": "Study of what can be computed",
            "parent": "1.2",
            "prerequisites": ["1.2.1"]
        },
        "1.2.3": {
            "title": "Complexity Theory",
            "description": "Study of computational resource requirements",
            "parent": "1.2",
            "prerequisites": ["1.2.2"]
        },
        "1.2.4": {
            "title": "Algorithm Analysis",
            "description": "Study of algorithm efficiency and performance",
            "parent": "1.2",
            "prerequisites": ["1.1.1", "1.1.3"]
        },

        # 2. Programming and Software Development
        "2": {
            "title": "Programming and Software Development",
            "description": "Software creation and engineering",
            "prerequisites": ["1.1", "1.2"]
        },
        
        # 2.1 Programming Fundamentals
        "2.1": {
            "title": "Programming Fundamentals",
            "description": "Basic programming concepts",
            "parent": "2"
        },
        "2.1.1": {
            "title": "Data Types and Variables",
            "description": "Fundamental data structures",
            "parent": "2.1"
        },
        "2.1.2": {
            "title": "Control Structures",
            "description": "Program flow control",
            "parent": "2.1",
            "prerequisites": ["2.1.1"]
        },
        "2.1.3": {
            "title": "Functions and Procedures",
            "description": "Code organization and reuse",
            "parent": "2.1",
            "prerequisites": ["2.1.2"]
        },
        "2.1.4": {
            "title": "Object-Oriented Programming",
            "description": "Object-based program design",
            "parent": "2.1",
            "prerequisites": ["2.1.3"]
        },
        
        # 2.2 Software Engineering
        "2.2": {
            "title": "Software Engineering",
            "description": "Professional software development",
            "parent": "2",
            "prerequisites": ["2.1"]
        },
        "2.2.1": {
            "title": "Requirements Engineering",
            "description": "Gathering and analyzing requirements",
            "parent": "2.2"
        },
        "2.2.2": {
            "title": "Software Design",
            "description": "Architectural and detailed design",
            "parent": "2.2",
            "prerequisites": ["2.2.1"]
        },
        "2.2.3": {
            "title": "Software Testing",
            "description": "Quality assurance and verification",
            "parent": "2.2",
            "prerequisites": ["2.2.2"]
        },
        "2.2.4": {
            "title": "Software Maintenance",
            "description": "System evolution and maintenance",
            "parent": "2.2",
            "prerequisites": ["2.2.3"]
        },
        
        # 3. Systems and Architecture
        "3": {
            "title": "Systems and Architecture",
            "description": "Computer systems and organization",
            "prerequisites": ["1.2", "2.1"]
        },
        
        # 3.1 Computer Architecture
        "3.1": {
            "title": "Computer Architecture",
            "description": "Hardware organization and design",
            "parent": "3"
        },
        "3.1.1": {
            "title": "Digital Logic",
            "description": "Boolean algebra and digital circuits",
            "parent": "3.1",
            "prerequisites": ["1.1.1"]
        },
        "3.1.2": {
            "title": "Processor Architecture",
            "description": "CPU design and organization",
            "parent": "3.1",
            "prerequisites": ["3.1.1"]
        },
        "3.1.3": {
            "title": "Memory Systems",
            "description": "Memory hierarchy and management",
            "parent": "3.1",
            "prerequisites": ["3.1.2"]
        },
        "3.1.4": {
            "title": "I/O Systems",
            "description": "Input/output architectures",
            "parent": "3.1",
            "prerequisites": ["3.1.2"]
        },
        
        # 3.2 Operating Systems
        "3.2": {
            "title": "Operating Systems",
            "description": "System software management",
            "parent": "3",
            "prerequisites": ["3.1"]
        },
        "3.2.1": {
            "title": "Process Management",
            "description": "Process scheduling and synchronization",
            "parent": "3.2"
        },
        "3.2.2": {
            "title": "Memory Management",
            "description": "Virtual memory and allocation",
            "parent": "3.2",
            "prerequisites": ["3.1.3"]
        },
        "3.2.3": {
            "title": "File Systems",
            "description": "File organization and management",
            "parent": "3.2",
            "prerequisites": ["3.2.1"]
        },
        "3.2.4": {
            "title": "Security and Protection",
            "description": "System security mechanisms",
            "parent": "3.2",
            "prerequisites": ["3.2.1", "3.2.2"]
        },
        
        # 4. Data and Information
        "4": {
            "title": "Data and Information",
            "description": "Data management and processing",
            "prerequisites": ["2.1", "1.1.3"]
        },
        
        # 4.1 Data Structures
        "4.1": {
            "title": "Data Structures",
            "description": "Organization of data",
            "parent": "4",
            "prerequisites": ["2.1.4"]
        },
        "4.1.1": {
            "title": "Arrays and Lists",
            "description": "Sequential data structures",
            "parent": "4.1"
        },
        "4.1.2": {
            "title": "Trees and Graphs",
            "description": "Hierarchical and network structures",
            "parent": "4.1",
            "prerequisites": ["4.1.1", "1.1.5"]
        },
        "4.1.3": {
            "title": "Hash Tables",
            "description": "Associative data structures",
            "parent": "4.1",
            "prerequisites": ["4.1.1"]
        },
        
        # 4.2 Databases
        "4.2": {
            "title": "Databases",
            "description": "Data storage and retrieval",
            "parent": "4",
            "prerequisites": ["4.1"]
        },
        "4.2.1": {
            "title": "Relational Databases",
            "description": "Relational data model",
            "parent": "4.2"
        },
        "4.2.2": {
            "title": "NoSQL Databases",
            "description": "Non-relational databases",
            "parent": "4.2",
            "prerequisites": ["4.2.1"]
        },
        "4.2.3": {
            "title": "Database Design",
            "description": "Schema design and normalization",
            "parent": "4.2",
            "prerequisites": ["4.2.1"]
        },
        
        # 5. Artificial Intelligence
        "5": {
            "title": "Artificial Intelligence",
            "description": "Intelligent systems and algorithms",
            "prerequisites": ["1.1.2", "1.1.3", "2.1"]
        },
        
        # 5.1 Machine Learning
        "5.1": {
            "title": "Machine Learning",
            "description": "Statistical learning methods",
            "parent": "5"
        },
        "5.1.1": {
            "title": "Supervised Learning",
            "description": "Predictive modeling",
            "parent": "5.1",
            "prerequisites": ["1.1.2", "1.1.3"]
        },
        "5.1.2": {
            "title": "Unsupervised Learning",
            "description": "Pattern discovery",
            "parent": "5.1",
            "prerequisites": ["5.1.1"]
        },
        "5.1.3": {
            "title": "Deep Learning",
            "description": "Neural networks",
            "parent": "5.1",
            "prerequisites": ["5.1.1"]
        },

        # 6. Cybersecurity
        "6": {
            "title": "Cybersecurity",
            "description": "Information security and protection",
            "prerequisites": ["2.2", "3.2"]
        },
        
        # 6.1 Security Fundamentals
        "6.1": {
            "title": "Security Fundamentals",
            "description": "Basic security concepts",
            "parent": "6"
        },
        "6.1.1": {
            "title": "Security Principles",
            "description": "Core security concepts",
            "parent": "6.1"
        },
        "6.1.2": {
            "title": "Threat Modeling",
            "description": "Identifying and analyzing threats",
            "parent": "6.1",
            "prerequisites": ["6.1.1"]
        },
        "6.1.3": {
            "title": "Risk Management",
            "description": "Managing security risks",
            "parent": "6.1",
            "prerequisites": ["6.1.2"]
        },

        # 6.2 Application Security
        "6.2": {
            "title": "Application Security",
            "description": "Securing software applications",
            "parent": "6",
            "prerequisites": ["6.1", "2.2"]
        },
        "6.2.1": {
            "title": "Secure Coding",
            "description": "Security in software development",
            "parent": "6.2"
        },
        "6.2.2": {
            "title": "Web Security",
            "description": "Securing web applications",
            "parent": "6.2",
            "prerequisites": ["6.2.1"]
        },
        "6.2.3": {
            "title": "Mobile Security",
            "description": "Securing mobile applications",
            "parent": "6.2",
            "prerequisites": ["6.2.1"]
        },

        # 7. Emerging Technologies
        "7": {
            "title": "Emerging Technologies",
            "description": "Current and future trends",
            "prerequisites": ["2.2", "5.1"]
        },
        
        # 7.1 Cloud Computing
        "7.1": {
            "title": "Cloud Computing",
            "description": "Distributed computing services",
            "parent": "7",
            "prerequisites": ["3.2", "4.2"]
        },
        "7.1.1": {
            "title": "Cloud Architecture",
            "description": "Cloud service models",
            "parent": "7.1"
        },
        "7.1.2": {
            "title": "Cloud Security",
            "description": "Securing cloud services",
            "parent": "7.1",
            "prerequisites": ["6.1", "7.1.1"]
        },

        # 7.2 Distributed Systems
        "7.2": {
            "title": "Distributed Systems",
            "description": "Decentralized computing",
            "parent": "7",
            "prerequisites": ["3.2", "4.2"]
        },
        "7.2.1": {
            "title": "Distributed Algorithms",
            "description": "Algorithms for distributed systems",
            "parent": "7.2"
        },
        "7.2.2": {
            "title": "Blockchain",
            "description": "Distributed ledger technology",
            "parent": "7.2",
            "prerequisites": ["7.2.1"]
        },
        "7.2.3": {
            "title": "Edge Computing",
            "description": "Edge-based processing",
            "parent": "7.2",
            "prerequisites": ["7.1"]
        }
    }
}


def create_default_hierarchy() -> TopicHierarchy:
    """Create a default topic hierarchy."""
    hierarchy = TopicHierarchy()
    
    # Add all topics first
    for id, data in INTEGRATED_TOPIC_HIERARCHY["topics"].items():
        hierarchy.add_topic(
            id=id,
            title=data["title"],
            description=data.get("description")
        )
    
    # Validate the hierarchy
    errors = hierarchy.validate_hierarchy()
    if errors:
        logger.warning("Hierarchy validation errors: %s", errors)
    
    return hierarchy


def load_topic_hierarchy(filepath: Optional[str] = None) -> TopicHierarchy:
    """
    Load a topic hierarchy from a file or create a default one.
    
    Args:
        filepath: Optional path to a hierarchy file
        
    Returns:
        Topic hierarchy
    """
    hierarchy = TopicHierarchy()
    
    if filepath and os.path.exists(filepath):
        try:
            hierarchy.load_from_file(filepath)
            logger.info(f"Loaded topic hierarchy from {filepath}")
            return hierarchy
        except Exception as e:
            logger.error(f"Error loading topic hierarchy from {filepath}: {str(e)}")
    
    # Fall back to default hierarchy
    logger.info("Creating default topic hierarchy")
    return create_default_hierarchy()


if __name__ == "__main__":
    """Generate a default topic hierarchy file if run as a script."""
    hierarchy = create_default_hierarchy()
    output_path = "topic_hierarchy.json"
    hierarchy.save_to_file(output_path)
    print(f"Generated default topic hierarchy at {output_path}")
    
    # Print some statistics
    print(f"Total topics: {len(hierarchy.topics)}")
    print(f"Root topics: {len(hierarchy.root_topics)}")
    
    # Example of learning path
    target = "9.7.4"  # Large Language Models
    known = ["1.1.1", "1.1.2", "4.1.1", "4.2.1"]  # Some basic topics
    path = hierarchy.get_learning_path(target, known)
    print(f"\nLearning path to {target}:")
    for topic in path:
        print(f"- {topic.id}: {topic.title}")
