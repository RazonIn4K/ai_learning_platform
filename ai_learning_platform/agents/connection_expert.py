# Core imports
from typing import Dict, List, Optional
from dataclasses import dataclass

# Project imports
from ..utils.decorators import handle_agent_operation
from ..core.base_agent import BaseAgent
from ..core.knowledge import KnowledgeMapper
from ..utils.types import AgentConfig

@dataclass
class TopicConnection:
    source: str
    target: str
    strength: float
    path: List[str]
    prerequisites: List[str]

class ConnectionExpert(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.knowledge_mapper = KnowledgeMapper()
    
    @handle_agent_operation()
    def analyze_topic_connections(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        exploration = self.knowledge_mapper.explore_from_topic(topic)
        return {
            "direct_connections": self._get_direct_connections(topic, exploration),
            "learning_paths": self._get_learning_paths(topic, context),
            "cross_domain_links": self._get_cross_domain_links(topic)
        }

    @handle_agent_operation()
    def find_concept_bridges(
        self,
        source: str,
        target: str
    ) -> List[Dict[str, Any]]:
        common_concepts = self.knowledge_mapper.find_common_concepts(source, target)
        return [
            {
                "concept": concept,
                "relevance": self.knowledge_mapper.calculate_relevance(concept, [source, target]),
                "path": self.knowledge_mapper.find_shortest_path(source, target, via=concept)
            }
            for concept in common_concepts
        ]

    def get_confidence_score(self, topic: Optional[str]) -> float:
        if not topic:
            return 0.0
        return self.knowledge_mapper.calculate_confidence(topic)
