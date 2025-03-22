from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from ..core.base_agent import BaseAgent
from ..core.knowledge import KnowledgeBase
from ..utils.decorators import agent_method, validate_input

class QuestionType(Enum):
    FACTUAL = "factual"
    CONCEPTUAL = "conceptual"
    APPLIED = "applied"
    ANALYTICAL = "analytical"
    GENERAL = "general"

@dataclass
class Question:
    text: str
    type: QuestionType
    complexity: str
    context: Optional[Dict] = None

class DomainExpert(BaseAgent):
    def __init__(self, config: AgentConfig, domain: str):
        super().__init__(config)
        self.domain = domain
        self.knowledge_base = KnowledgeBase(domain)
        self._question_patterns = {
            QuestionType.FACTUAL: ["what", "definition", "describe", "who", "where", "when"],
            QuestionType.CONCEPTUAL: ["why", "how does", "explain", "understand", "concept"],
            QuestionType.APPLIED: ["how to", "apply", "implement", "use", "practice"],
            QuestionType.ANALYTICAL: ["analyze", "evaluate", "compare", "synthesize", "design"]
        }

    @agent_method()
    @validate_input(query=str)
    def answer_question(self, query: str, context: Optional[Dict] = None) -> Dict:
        question = Question(
            text=query,
            type=self._classify_question(query),
            complexity=self._assess_complexity(query),
            context=context
        )
        
        return {
            "answer": self.knowledge_base.get_answer(
                question.text, 
                question.type, 
                question.complexity
            ),
            "topics": self._get_related_topics(question),
            "resources": self.knowledge_base.get_resources(
                question.text, 
                question.complexity, 
                limit=3
            )
        }

    def _classify_question(self, question: str) -> QuestionType:
        question_lower = question.lower()
        return next(
            (qtype for qtype, keywords in self._question_patterns.items()
             if any(word in question_lower for word in keywords)),
            QuestionType.GENERAL
        )

    def _assess_complexity(self, question: str) -> str:
        technical_terms = self.knowledge_base.get_technical_terms()
        analytical_words = ["implications", "analyze", "compare", "evaluate", "synthesize", "design"]
        
        score = (
            sum(term in question.lower() for term in technical_terms) +
            2 * sum(word in question.lower() for word in analytical_words) +
            2 * (question.count(";") + (question.count(",") > 2) + (question.count("?") > 1))
        )
        
        if score > 4: return "advanced"
        if score > 2: return "intermediate"
        return "beginner"

    def _get_related_topics(self, question: Question) -> List[Dict]:
        topics = self.knowledge_base.find_related_topics(question.text)
        return [
            {
                "name": topic["name"],
                "relevance": topic["relevance"],
                "why": topic["explanation"][:100]
            } 
            for topic in topics[:3]
        ]
