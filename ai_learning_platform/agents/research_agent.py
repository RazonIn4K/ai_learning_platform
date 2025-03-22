import logging
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Agent responsible for conducting research on topics based on user queries.
    """
    
    def __init__(self, topic_hierarchy=None, research_sources=None):
        """
        Initialize the research agent.
        
        Args:
            topic_hierarchy: Optional topic hierarchy for categorizing research
            research_sources: Optional research sources to use
        """
        self.topic_hierarchy = topic_hierarchy
        self.research_sources = research_sources or ["default"]
        
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a research-related query.
        
        Args:
            query: The user's query
            context: Optional context information
            
        Returns:
            Dictionary containing the research response
        """
        try:
            # Analyze the query to understand research needs
            analysis = self._analyze_query(query, context or {})
            
            # Perform research based on the analysis
            research_results = self.research_topic(
                query=query,
                topics=analysis.get("topics", []),
                depth=analysis.get("depth", "medium"),
                sources=analysis.get("preferred_sources", [])
            )
            
            return {
                "content": self._format_research_results(research_results),
                "research": research_results,
                "analysis": analysis,
                "agent": self.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Error processing research query: {str(e)}", exc_info=True)
            return {
                "content": "I encountered an error while researching this topic.",
                "error": str(e),
                "agent": self.__class__.__name__
            }

    def _analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a research query to determine its characteristics.
        
        Args:
            query: The user's query
            context: Context information
            
        Returns:
            Dictionary with analysis results
        """
        # Extract topics from the query if not provided
        topics = context.get("topics", [])
        if not topics and hasattr(self, "topic_hierarchy") and self.topic_hierarchy:
            topics = self.topic_hierarchy.extract_topics(query)
        
        # Determine depth of research requested
        depth = "medium"  # default
        if "basic" in query.lower() or "quick" in query.lower() or "summary" in query.lower():
            depth = "basic"
        elif "thorough" in query.lower() or "detailed" in query.lower() or "in-depth" in query.lower():
            depth = "advanced"
        
        # Identify preferred sources if mentioned
        preferred_sources = []
        if "academic" in query.lower() or "journal" in query.lower() or "paper" in query.lower():
            preferred_sources.append("academic")
        if "book" in query.lower() or "textbook" in query.lower():
            preferred_sources.append("books")
        if "recent" in query.lower() or "latest" in query.lower() or "new" in query.lower():
            preferred_sources.append("recent")
        
        return {
            "topics": topics,
            "depth": depth,
            "preferred_sources": preferred_sources,
            "query_type": "research",
            "complexity": "high"
        }
    
    def research_topic(self, query: str, topics: List[str], depth: str = "medium", sources: List[str] = None) -> Dict[str, Any]:
        """
        Conduct research on a topic based on the query.
        
        Args:
            query: The user's query
            topics: List of topics to research
            depth: Depth of research (basic, medium, advanced)
            sources: Preferred sources to use
            
        Returns:
            Dictionary with research results
        """
        # This would typically involve external API calls or database lookups
        # For now, return a mock research result
        sources_used = sources or ["general"]
        
        if depth == "basic":
            detail_level = "overview"
            resources = 3
        elif depth == "advanced":
            detail_level = "comprehensive"
            resources = 8
        else:  # medium
            detail_level = "detailed"
            resources = 5
        
        # Mock research results based on topics
        results = {}
        for topic in topics:
            results[topic] = {
                "summary": f"Research summary for {topic} ({detail_level} level)",
                "sources": [f"Source {i} for {topic}" for i in range(1, resources+1)],
                "key_concepts": [f"Concept {i} for {topic}" for i in range(1, 4)],
                "detail_level": detail_level
            }
        
        return {
            "query": query,
            "results_by_topic": results,
            "depth": depth,
            "sources_used": sources_used,
            "completion_status": "success"
        }
    
    def _format_research_results(self, research_results: Dict[str, Any]) -> str:
        """
        Format research results for presentation to the user.
        
        Args:
            research_results: The research results to format
            
        Returns:
            Formatted research content as a string
        """
        formatted_content = ["## Research Results"]
        
        # Add query
        formatted_content.append(f"\n**Query:** {research_results.get('query', 'N/A')}")
        
        # Add results by topic
        for topic, result in research_results.get("results_by_topic", {}).items():
            formatted_content.append(f"\n### {topic.replace('_', ' ').title()}")
            formatted_content.append(f"\n{result.get('summary', 'No summary available.')}")
            
            # Add key concepts
            if "key_concepts" in result and result["key_concepts"]:
                formatted_content.append("\n**Key Concepts:**")
                for concept in result["key_concepts"]:
                    formatted_content.append(f"\n- {concept}")
            
            # Add sources
            if "sources" in result and result["sources"]:
                formatted_content.append("\n**Sources:**")
                for source in result["sources"][:3]:  # Limit to 3 sources
                    formatted_content.append(f"\n- {source}")
                
                if len(result.get("sources", [])) > 3:
                    formatted_content.append(f"\n  *...and {len(result['sources']) - 3} more sources*")
        
        return "\n".join(formatted_content)
