import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

from .base_agent import BaseAgent

class ConnectionExpert(BaseAgent):
    """Agent responsible for finding connections between topics and domains."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query related to connections between domains or topics.
        
        Args:
            query: The user's query
            context: Optional context information
            
        Returns:
            Dictionary containing the connection analysis
        """
        try:
            # Analyze the query to understand what connections are sought
            analysis = self._analyze_query(query, context or {})
            
            # Find connections based on the analysis
            connections = self.find_connections(
                topics=analysis.get("topics", []),
                domains=analysis.get("domains", []),
                connection_type=analysis.get("connection_type", "general")
            )
            
            return {
                "content": self._format_connections(connections),
                "connections": connections,
                "analysis": analysis,
                "agent": self.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Error processing connection query: {str(e)}", exc_info=True)
            return {
                "content": "I encountered an error finding connections between topics.",
                "error": str(e),
                "agent": self.__class__.__name__
            }

    def _analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a query to identify connection-related properties.
        
        Args:
            query: The user's query
            context: Context information
            
        Returns:
            Dictionary with analysis results
        """
        # Extract topics from the query if not provided in context
        topics = context.get("topics", [])
        if not topics and hasattr(self, "topic_hierarchy") and self.topic_hierarchy:
            topics = self.topic_hierarchy.extract_topics(query)
        
        # Identify domains if not provided
        domains = context.get("domains", [])
        if not domains and hasattr(self, "knowledge_mapper") and self.knowledge_mapper:
            domains = [
                self.knowledge_mapper.get_topic_domain(topic) 
                for topic in topics if topic
            ]
            domains = list(set(filter(None, domains)))
        
        # Determine connection type based on query language
        connection_type = "relationship"  # default
        if "prerequisite" in query.lower() or "before" in query.lower():
            connection_type = "prerequisite"
        elif "similar" in query.lower() or "like" in query.lower():
            connection_type = "similarity"
        elif "apply" in query.lower() or "use" in query.lower():
            connection_type = "application"
        
        return {
            "topics": topics,
            "domains": domains,
            "connection_type": connection_type
        }
    
    def find_connections(self, topics: List[str], domains: List[str], connection_type: str) -> List[Dict[str, Any]]:
        """
        Find connections between topics and domains.
        
        Args:
            topics: List of topics
            domains: List of domains
            connection_type: Type of connection to find
            
        Returns:
            List of dictionaries representing the connections
        """
        # Placeholder implementation
        connections = []
        for topic in topics:
            for domain in domains:
                connections.append({
                    "topic": topic,
                    "domain": domain,
                    "connection_type": connection_type,
                    "description": f"Connection between {topic} and {domain} as {connection_type}"
                })
        return connections
    
    def _format_connections(self, connections: List[Dict[str, Any]]) -> str:
        """
        Format the connections into a human-readable string.
        
        Args:
            connections: List of connections
            
        Returns:
            Formatted string
        """
        formatted = "\n".join(
            [f"{conn['topic']} -> {conn['domain']} ({conn['connection_type']}): {conn['description']}" 
             for conn in connections]
        )
        return formatted
