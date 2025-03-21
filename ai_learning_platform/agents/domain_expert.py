from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
import json

from .base_agent import BaseLearningAgent
from ..models.model_registry import ModelRegistry
from ..utils.knowledge_explorer import KnowledgeExplorer

logger = logging.getLogger(__name__)

@dataclass
class DomainExplanation:
    """Structure for domain explanations."""
    topic: str
    explanation: str
    concepts: List[str]
    examples: List[str]
    resources: List[Dict[str, str]]
    difficulty: str
    prerequisites: List[str]

class DomainExpertAgent(BaseLearningAgent):
    """Domain Expert for providing specialized knowledge in a specific domain."""
    
    def __init__(
        self,
        domain: str,
        knowledge_explorer: Optional[KnowledgeExplorer] = None,
        model_name: str = "anthropic/claude-3-sonnet",
        model_params: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ):
        super().__init__(model_name, model_params)
        self.domain = domain
        self.knowledge_explorer = knowledge_explorer
        self.user_profile = user_profile or {}
        
        logger.info(f"Domain Expert initialized for domain: {domain}")
        
    def get_available_functions(self) -> List[str]:
        """Get list of available specialized functions."""
        return [
            "provide_domain_knowledge",
            "answer_domain_question",
            "explain_topic",
            "find_related_topics",
            "analyze_topic_complexity",
            "suggest_learning_resources"
        ]

    def _provide_domain_knowledge(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Provide comprehensive domain knowledge response."""
        question_type = self._classify_question(query)
        complexity = self._assess_complexity(query)
        
        response = {
            "answer": self._generate_domain_answer(query, question_type, context),
            "complexity_level": complexity,
            "related_topics": self._find_related_topics(query, context),
            "suggested_resources": self._suggest_resources(query, complexity),
            "domain_context": self._get_domain_context(query)
        }
        
        return response

    def _answer_domain_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Answer a specific domain question."""
        question_type = self._classify_question(question)
        
        answer_methods = {
            "factual": self._answer_factual_question,
            "conceptual": self._answer_conceptual_question,
            "applied": self._answer_applied_question,
            "analytical": self._answer_analytical_question
        }
        
        answer_method = answer_methods.get(
            question_type,
            self._answer_general_question
        )
        
        return {
            "answer": answer_method(question, context),
            "question_type": question_type,
            "confidence_score": self._calculate_confidence(question),
            "supporting_info": self._get_supporting_info(question)
        }

    def _explain_topic(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Provide detailed topic explanation."""
        return {
            "explanation": self._generate_topic_explanation(topic, context),
            "key_concepts": self._extract_key_concepts(topic),
            "prerequisites": self._identify_prerequisites(topic),
            "learning_objectives": self._define_learning_objectives(topic)
        }

    def _find_related_topics(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Find and analyze related topics."""
        topics = self._discover_related_topics(query)
        return [
            {
                "topic": topic,
                "relevance": self._calculate_topic_relevance(topic, query),
                "relationship": self._describe_relationship(topic, query),
                "complexity": self._assess_topic_complexity(topic)
            }
            for topic in topics
        ]

    def _generate_domain_answer(
        self,
        query: str,
        question_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a comprehensive answer for the query."""
        if question_type == "factual":
            return self._answer_factual_question(query, context)
        elif question_type == "conceptual":
            return self._answer_conceptual_question(query, context)
        elif question_type == "applied":
            return self._answer_applied_question(query, context)
        else:
            return self._answer_general_question(query, context)

    def _suggest_resources(
        self,
        query: str,
        complexity: str
    ) -> List[Dict[str, Any]]:
        """Suggest learning resources based on query complexity."""
        resources = self._get_domain_resources()
        return [
            resource
            for resource in resources
            if self._is_resource_appropriate(resource, complexity)
        ]

    def _get_domain_resources(self) -> List[Dict[str, Any]]:
        """Get a list of domain-specific learning resources."""
        # This is a placeholder implementation
        return [
            {
                "title": "Resource 1",
                "url": "http://example.com/resource1",
                "type": "article",
                "level": "beginner"
            },
            {
                "title": "Resource 2",
                "url": "http://example.com/resource2",
                "type": "book",
                "level": "intermediate"
            },
            {
                "title": "Resource 3",
                "url": "http://example.com/resource3",
                "type": "video",
                "level": "advanced"
            }
        ]

    def _is_resource_appropriate(
        self,
        resource: Dict[str, Any],
        complexity: str
    ) -> bool:
        """Determine if a resource is appropriate for the given complexity level."""
        resource_level = resource.get("level", "intermediate")
        complexity_levels = ["beginner", "intermediate", "advanced"]
        
        resource_index = complexity_levels.index(resource_level)
        complexity_index = complexity_levels.index(complexity)
        
        return resource_index <= complexity_index

    def _get_domain_context(self, query: str) -> Dict[str, Any]:
        """Get context information about the domain."""
        # This is a placeholder implementation
        return {
            "domain": self.domain,
            "description": "A brief description of the domain",
            "key_topics": ["Topic 1", "Topic 2", "Topic 3"],
            "related_domains": ["Related Domain 1", "Related Domain 2"]
        }

    def _generate_topic_explanation(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a detailed explanation for a topic."""
        user_level = self._determine_user_level(context)
        
        if self.knowledge_explorer:
            try:
                knowledge = self.knowledge_explorer.get_topic_knowledge(topic, self.domain)
                if knowledge:
                    return knowledge.get("explanation", "")
            except Exception as e:
                logger.warning(f"Failed to get topic knowledge: {str(e)}")
        
        # Fallback: use LLM to generate explanation
        prompt = f"""
        Provide a detailed explanation of '{topic}' in the domain of {self.domain}.
        The explanation should be appropriate for a {user_level} level understanding.
        
        Return your response in this JSON format:
        {{
          "explanation": "Detailed explanation text",
          "concepts": ["Key concept 1", "Key concept 2", ...],
          "examples": ["Example 1", "Example 2", ...],
          "resources": [
            {{"title": "Resource 1", "url": "URL 1", "type": "article|book|video|tutorial"}},
            ...
          ],
          "difficulty": "beginner|intermediate|advanced",
          "prerequisites": ["Prerequisite 1", "Prerequisite 2", ...]
        }}
        """
        
        response = self.process_message(prompt)
        try:
            data = json.loads(response)
            return data.get("explanation", "")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse topic explanation: {str(e)}")
            return ""

    def _extract_key_concepts(
        self,
        topic: str
    ) -> List[str]:
        """Extract key concepts for a given topic."""
        if self.knowledge_explorer:
            try:
                knowledge = self.knowledge_explorer.get_topic_knowledge(topic, self.domain)
                if knowledge:
                    return knowledge.get("concepts", [])
            except Exception as e:
                logger.warning(f"Failed to get topic knowledge: {str(e)}")
        
        # Fallback: use LLM to extract concepts
        prompt = f"""
        Extract the key concepts for the topic '{topic}' in the domain of {self.domain}.
        
        Return ONLY a JSON array of concept strings.
        """
        
        response = self.process_message(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return []

    def _identify_prerequisites(
        self,
        topic: str
    ) -> List[str]:
        """Identify prerequisites for a given topic."""
        if self.knowledge_explorer:
            try:
                knowledge = self.knowledge_explorer.get_topic_knowledge(topic, self.domain)
                if knowledge:
                    return knowledge.get("prerequisites", [])
            except Exception as e:
                logger.warning(f"Failed to get topic knowledge: {str(e)}")
        
        # Fallback: use LLM to identify prerequisites
        prompt = f"""
        Identify the prerequisites for the topic '{topic}' in the domain of {self.domain}.
        
        Return ONLY a JSON array of prerequisite strings.
        """
        
        response = self.process_message(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return []

    def _define_learning_objectives(
        self,
        topic: str
    ) -> List[str]:
        """Define learning objectives for a given topic."""
        if self.knowledge_explorer:
            try:
                knowledge = self.knowledge_explorer.get_topic_knowledge(topic, self.domain)
                if knowledge:
                    return knowledge.get("learning_objectives", [])
            except Exception as e:
                logger.warning(f"Failed to get topic knowledge: {str(e)}")
        
        # Fallback: use LLM to define learning objectives
        prompt = f"""
        Define the learning objectives for the topic '{topic}' in the domain of {self.domain}.
        
        Return ONLY a JSON array of learning objective strings.
        """
        
        response = self.process_message(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return []

    def _discover_related_topics(
        self,
        query: str
    ) -> List[str]:
        """Discover related topics for a given query."""
        if self.knowledge_explorer:
            try:
                return self.knowledge_explorer.find_related_topics(query, self.domain)
            except Exception as e:
                logger.warning(f"Failed to find related topics: {str(e)}")
        
        # Fallback: use LLM to suggest related topics
        prompt = f"""
        For this query about {self.domain}:
        
        "{query}"
        
        Suggest 3-5 related topics that would be valuable for the learner to explore next.
        For each topic, include:
        1. The topic name
        2. Why it's related to the query
        3. How it builds on or extends the current topic
        
        Return your response in this JSON format:
        [
          {{
            "topic": "Topic name",
            "relation": "How it relates to the query",
            "importance": 0.1-1.0,
            "next_step": true/false
          }},
          ...
        ]
        """
        
        response = self.process_message(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse related topics: {str(e)}")
            return []

    def _calculate_topic_relevance(
        self,
        topic: str,
        query: str
    ) -> float:
        """Calculate the relevance of a topic to a query."""
        if self.knowledge_explorer:
            try:
                return self.knowledge_explorer.calculate_relevance(topic, query, self.domain)
            except Exception as e:
                logger.warning(f"Failed to calculate relevance: {str(e)}")
        
        # Fallback: use LLM to estimate relevance
        prompt = f"""
        Estimate the relevance of the topic '{topic}' to the query '{query}' in the domain of {self.domain}.
        
        Return a value between 0.0 (not relevant) and 1.0 (very relevant).
        """
        
        response = self.process_message(prompt)
        try:
            return float(response)
        except ValueError:
            return 0.0

    def _describe_relationship(
        self,
        topic: str,
        query: str
    ) -> str:
        """Describe the relationship between a topic and a query."""
        if self.knowledge_explorer:
            try:
                return self.knowledge_explorer.describe_relationship(topic, query, self.domain)
            except Exception as e:
                logger.warning(f"Failed to describe relationship: {str(e)}")
        
        # Fallback: use LLM to describe the relationship
        prompt = f"""
        Describe the relationship between the topic '{topic}' and the query '{query}' in the domain of {self.domain}.
        
        Return a brief description of how the topic relates to the query.
        """
        
        return self.process_message(prompt)

    def _assess_topic_complexity(
        self,
        topic: str
    ) -> str:
        """Assess the complexity of a topic."""
        if self.knowledge_explorer:
            try:
                return self.knowledge_explorer.assess_topic_complexity(topic, self.domain)
            except Exception as e:
                logger.warning(f"Failed to assess topic complexity: {str(e)}")
        
        # Fallback: use LLM to assess complexity
        prompt = f"""
        Assess the complexity of the topic '{topic}' in the domain of {self.domain}.
        
        Return one of the following: "beginner", "intermediate", or "advanced".
        """
        
        response = self.process_message(prompt)
        return response.strip().lower() if response else "intermediate"

    def _get_supporting_info(
        self,
        question: str
    ) -> Dict[str, Any]:
        """Get supporting information for a question."""
        supporting_info = {
            "related_topics": self._find_related_topics(question),
            "topic_complexity": self._assess_complexity(question),
            "domain_context": self._get_domain_context(question)
        }
        
        return supporting_info

    def _calculate_confidence(
        self,
        question: str
    ) -> float:
        """Calculate confidence score for an answer."""
        # Base confidence
        confidence = 0.7
        
        # Increase confidence based on question characteristics
        if len(question) > 50:  # Longer questions often require more complex answers
            confidence += 0.1
        
        if any(term in question for term in ["how", "what", "why", "where", "when", "who"]):  # Basic questions
            confidence += 0.05
        
        if any(term in question for term in ["analyze", "evaluate", "compare", "synthesize", "design"]):  # Analytical questions
            confidence += 0.1
        
        if any(term in question for term in ["!important!"]):  # Marked as important
            confidence += 0.2
        
        # Cap confidence
        return min(max(confidence, 0.4), 1.0)

    def _answer_factual_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Answer a factual domain question."""
        user_level = self._determine_user_level(context)
        
        prompt = f"""
        Answer this factual question about {self.domain}:
        
        "{question}"
        
        Provide a clear, accurate answer appropriate for a {user_level} level understanding.
        Include relevant facts and definitions. Be concise but thorough.
        """
        
        return self.process_message(prompt)

    def _answer_conceptual_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Answer a conceptual domain question."""
        user_level = self._determine_user_level(context)
        
        prompt = f"""
        Answer this conceptual question about {self.domain}:
        
        "{question}"
        
        Provide an explanation that builds understanding of the underlying concepts.
        Use analogies where helpful. Make complex ideas accessible for someone at a {user_level} level.
        """
        
        return self.process_message(prompt)

    def _answer_applied_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Answer an applied domain question."""
        user_level = self._determine_user_level(context)
        
        prompt = f"""
        Answer this practical/applied question about {self.domain}:
        
        "{question}"
        
        Provide step-by-step guidance with practical examples.
        Include sample code or procedures where relevant.
        Make your answer suitable for someone at a {user_level} level.
        """
        
        return self.process_message(prompt)

    def _answer_general_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Answer a general domain question."""
        user_level = self._determine_user_level(context)
        
        prompt = f"""
        Answer this question about {self.domain}:
        
        "{question}"
        
        Provide a comprehensive answer that covers both theoretical understanding and practical application.
        Make your explanation suitable for someone at a {user_level} level.
        """
        
        return self.process_message(prompt)

    def _answer_analytical_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Answer an analytical domain question."""
        user_level = self._determine_user_level(context)
        
        prompt = f"""
        Answer this analytical question about {self.domain}:
        
        "{question}"
        
        Provide a detailed analysis, including reasoning, evidence, and conclusions.
        Make your answer suitable for someone at a {user_level} level.
        """
        
        return self.process_message(prompt)

    def _classify_question(self, question: str) -> str:
        """Classify the type of domain question."""
        question_lower = question.lower()
        
        if any(w in question_lower for w in ["what", "definition", "describe", "who", "where", "when"]):
            return "factual"
        elif any(w in question_lower for w in ["why", "how does", "explain", "understand", "concept"]):
            return "conceptual"
        elif any(w in question_lower for w in ["how to", "apply", "implement", "use", "practice"]):
            return "applied"
        elif any(w in question_lower for w in ["analyze", "evaluate", "compare", "synthesize", "design"]):
            return "analytical"
        else:
            return "general"

    def _assess_complexity(self, question: str) -> str:
        """Assess the complexity of a question."""
        # Count indicators of complexity
        complexity_indicators = 0
        
        # Technical terms indicate higher complexity
        domain_terms = self._get_domain_terms()
        for term in domain_terms:
            if term.lower() in question.lower():
                complexity_indicators += 1
        
        # Advanced question words indicate higher complexity
        advanced_words = ["implications", "analyze", "compare", "evaluate", "synthesize", "design"]
        for word in advanced_words:
            if word.lower() in question.lower():
                complexity_indicators += 2
                
        # Multi-part questions are more complex
        if ";" in question or question.count(",") > 2 or question.count("?") > 1:
            complexity_indicators += 2
            
        # Determine complexity level
        if complexity_indicators > 4:
            return "advanced"
        elif complexity_indicators > 2:
            return "intermediate"
        else:
            return "beginner"

    def _get_domain_terms(self) -> List[str]:
        """Get domain-specific technical terms."""
        # This is a placeholder - in a real implementation, this would access a domain-specific vocabulary
        return ["algorithm", "framework", "paradigm", "architecture", "protocol", "implementation"]
