import networkx as nx
from typing import Dict, Any, List, Optional

class KnowledgeGraph:
    """Manages the knowledge graph of learning topics."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.topic_metadata = {}
        
    def add_topic(
        self,
        topic_id: str,
        metadata: Dict[str, Any],
        prerequisites: Optional[List[str]] = None
    ):
        """Add a topic to the knowledge graph."""
        prerequisites = prerequisites or []
        
        # Add the topic node
        self.graph.add_node(topic_id)
        self.topic_metadata[topic_id] = metadata
        
        # Add prerequisite relationships
        for prereq in prerequisites:
            self.graph.add_edge(prereq, topic_id)
            
    def get_learning_path(
        self,
        target_topic: str,
        current_knowledge: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate a learning path to reach a target topic."""
        current_knowledge = current_knowledge or []
        
        # Find all prerequisites using topological sort
        if target_topic not in self.graph:
            return []
            
        try:
            path = list(nx.topological_sort(
                self.graph.subgraph(
                    nx.ancestors(self.graph, target_topic) | {target_topic}
                )
            ))
        except nx.NetworkXUnfeasible:
            return []  # Graph has cycles
            
        # Filter out already known topics
        path = [topic for topic in path if topic not in current_knowledge]
        
        # Add metadata to path
        return [
            {
                'topic_id': topic,
                'metadata': self.topic_metadata.get(topic, {})
            }
            for topic in path
        ]