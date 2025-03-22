"""Topic Navigator Agent for guiding users through learning paths."""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
import logging
import networkx as nx
from datetime import timedelta

from .base_agent import BaseLearningAgent
from ..models.model_registry import ModelRegistry
from ..utils.topic_hierarchy import TopicHierarchy
from ..utils.knowledge_mapper import KnowledgeMapper, KnowledgeNode
from ..utils.decorators import handle_agent_errors, validate_input
from ..utils.base_config import BaseConfig

logger = logging.getLogger(__name__)

@dataclass
class TopicAnalysis:
    """Detailed analysis of a learning topic."""
    topic_id: str
    prerequisites: List[str]
    related_topics: List[str]
    estimated_time: timedelta
    complexity_level: str
    learning_outcomes: List[str]
    practical_applications: List[str]

@dataclass
class LearningPathNode:
    """Node in a learning path."""
    topic_id: str
    dependencies: Set[str]
    estimated_time: timedelta
    resources: List[Dict[str, str]]
    practice_items: List[Dict[str, Any]]

class TopicNavigatorAgent(BaseLearningAgent):
    """Topic Navigator Agent for guiding users through learning paths."""
    
    def __init__(
        self,
        topic_hierarchy: TopicHierarchy,
        knowledge_mapper: KnowledgeMapper,
        model_name: str,
        model_params: Dict[str, Any],
        user_profile: Dict[str, Any]
    ):
        super().__init__(model_name, model_params)
        self.topic_hierarchy = topic_hierarchy
        self.knowledge_mapper = knowledge_mapper
        self.user_profile = user_profile
        self.learning_graph = self._build_learning_graph()

    def _analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized function for analyzing learning queries."""
        topics = self.topic_hierarchy.extract_topics(query)
        knowledge_state = self.knowledge_mapper.get_knowledge_state(
            self.user_profile["user_id"]
        )
        
        return {
            "identified_topics": topics,
            "current_knowledge": knowledge_state,
            "suggested_path": self._generate_learning_path(topics, knowledge_state),
            "prerequisites": self._identify_prerequisites(topics),
            "estimated_time": self._estimate_learning_time(topics)
        }

    def _generate_learning_path(
        self,
        topics: List[str],
        knowledge_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create personalized learning path."""
        path = []
        for topic in topics:
            prerequisites = self._get_prerequisites(topic)
            
            missing_prereqs = [
                p for p in prerequisites 
                if not self._check_prerequisite_mastery(p, knowledge_state)
            ]
            
            path.extend([
                {
                    "topic": prereq,
                    "type": "prerequisite",
                    "estimated_time": self._estimate_topic_time(prereq)
                }
                for prereq in missing_prereqs
            ])
            
            path.append({
                "topic": topic,
                "type": "main_topic",
                "estimated_time": self._estimate_topic_time(topic),
                "subtopics": self._get_subtopics(topic)
            })
        
        return path

    def _build_learning_graph(self) -> nx.DiGraph:
        """Build a directed graph representing topic relationships."""
        graph = nx.DiGraph()
        
        for topic in self.topic_hierarchy.get_all_topics():
            graph.add_node(
                topic.id,
                complexity=topic.complexity,
                duration=topic.estimated_duration,
                prerequisites=topic.prerequisites
            )
            
            # Add edges for prerequisites
            for prereq in topic.prerequisites:
                graph.add_edge(prereq, topic.id, weight=1)
            
            # Add edges for related topics
            for related in topic.related_topics:
                graph.add_edge(topic.id, related, weight=0.5)
        
        return graph

    def analyze_topic(self, topic_id: str) -> TopicAnalysis:
        """
        Perform detailed analysis of a topic.
        
        Args:
            topic_id: Unique identifier of the topic
            
        Returns:
            Comprehensive topic analysis
        """
        topic = self.topic_hierarchy.get_topic(topic_id)
        if not topic:
            raise ValueError(f"Topic {topic_id} not found")
            
        # Get prerequisites with confidence scores
        prereqs = self._analyze_prerequisites(topic)
        
        # Find related topics using graph analysis
        related = self._find_related_topics(topic_id)
        
        # Estimate completion time based on user profile
        estimated_time = self._estimate_completion_time(
            topic,
            self.user_profile.get("learning_pace", "normal")
        )
        
        # Analyze complexity and learning outcomes
        complexity = self._analyze_complexity(topic)
        outcomes = self._identify_learning_outcomes(topic)
        
        # Find practical applications
        applications = self._find_practical_applications(topic)
        
        return TopicAnalysis(
            topic_id=topic_id,
            prerequisites=prereqs,
            related_topics=related,
            estimated_time=estimated_time,
            complexity_level=complexity,
            learning_outcomes=outcomes,
            practical_applications=applications
        )

    def create_learning_path(
        self,
        target_topic: str,
        include_practice: bool = True
    ) -> List[LearningPathNode]:
        """
        Create an optimized learning path to a target topic.
        
        Args:
            target_topic: Target topic ID
            include_practice: Whether to include practice items
            
        Returns:
            Ordered list of learning path nodes
        """
        # Get user's current knowledge
        known_topics = set(self.user_profile.get("topics_learned", []))
        
        # Find shortest path considering prerequisites
        path = nx.shortest_path(
            self.learning_graph,
            source=self._find_start_topic(known_topics),
            target=target_topic,
            weight="weight"
        )
        
        # Build detailed path nodes
        learning_path = []
        for topic_id in path:
            node = self._create_path_node(topic_id, include_practice)
            learning_path.append(node)
        
        return learning_path

    def suggest_next_topics(
        self,
        current_topics: List[str],
        max_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Suggest next topics based on current learning progress.
        
        Args:
            current_topics: Currently studied topics
            max_suggestions: Maximum number of suggestions
            
        Returns:
            Ranked list of topic suggestions with explanations
        """
        suggestions = []
        seen = set(current_topics)
        
        # Get neighboring topics in the learning graph
        for topic in current_topics:
            neighbors = set(self.learning_graph.neighbors(topic)) - seen
            for neighbor in neighbors:
                if len(suggestions) >= max_suggestions:
                    break
                    
                relevance = self._calculate_topic_relevance(
                    neighbor,
                    current_topics,
                    self.user_profile
                )
                
                if relevance > 0.5:  # Minimum relevance threshold
                    suggestions.append({
                        "topic_id": neighbor,
                        "relevance_score": relevance,
                        "reasoning": self._explain_suggestion(neighbor, current_topics),
                        "prerequisites_met": self._check_prerequisites(neighbor),
                        "estimated_time": self._estimate_completion_time(
                            self.topic_hierarchy.get_topic(neighbor),
                            self.user_profile.get("learning_pace", "normal")
                        )
                    })
        
        return sorted(suggestions, key=lambda x: x["relevance_score"], reverse=True)

    def _find_start_topic(self, known_topics: Set[str]) -> str:
        """Find the best starting topic based on user's knowledge."""
        if not known_topics:
            return self.topic_hierarchy.get_root_topics()[0].id
            
        # Find the most advanced known topic that connects to the target
        known_topics_sorted = sorted(
            known_topics,
            key=lambda t: self.topic_hierarchy.get_topic(t).complexity,
            reverse=True
        )
        
        return known_topics_sorted[0]

    def _create_path_node(
        self,
        topic_id: str,
        include_practice: bool
    ) -> LearningPathNode:
        """Create a detailed learning path node."""
        topic = self.topic_hierarchy.get_topic(topic_id)
        
        resources = self._gather_topic_resources(topic)
        practice_items = (
            self._generate_practice_items(topic)
            if include_practice else []
        )
        
        return LearningPathNode(
            topic_id=topic_id,
            dependencies=set(topic.prerequisites),
            estimated_time=self._estimate_completion_time(
                topic,
                self.user_profile.get("learning_pace", "normal")
            ),
            resources=resources,
            practice_items=practice_items
        )

    def _calculate_topic_relevance(
        self,
        topic_id: str,
        current_topics: List[str],
        user_profile: Dict[str, Any]
    ) -> float:
        """Calculate topic relevance score."""
        topic = self.topic_hierarchy.get_topic(topic_id)
        score = 0.0
        
        # Check alignment with interests
        interests = user_profile.get("interests", [])
        if any(interest in topic.tags for interest in interests):
            score += 0.3
            
        # Check prerequisite completion
        if self._check_prerequisites(topic_id):
            score += 0.3
            
        # Check connection strength to current topics
        connections = sum(
            1 for t in current_topics
            if nx.has_path(self.learning_graph, t, topic_id)
        )
        score += 0.2 * (connections / len(current_topics))
        
        # Check complexity alignment
        preferred_complexity = user_profile.get("complexity_preference", "intermediate")
        if topic.complexity == preferred_complexity:
            score += 0.2
            
        return min(score, 1.0)

    def _explain_suggestion(
        self,
        topic_id: str,
        current_topics: List[str]
    ) -> str:
        """Generate explanation for topic suggestion."""
        topic = self.topic_hierarchy.get_topic(topic_id)
        
        # Find strongest connection to current topics
        connections = []
        for current in current_topics:
            if nx.has_path(self.learning_graph, current, topic_id):
                path = nx.shortest_path(self.learning_graph, current, topic_id)
                connections.append((current, len(path)))
                
        strongest_connection = min(connections, key=lambda x: x[1])
        
        return (
            f"This topic builds upon your knowledge of "
            f"{strongest_connection[0]} and will help you understand "
            f"{', '.join(topic.leads_to)} in the future."
        )

    def analyze_learning_path(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze and create a learning path based on a query.
        
        Args:
            query: User's learning query
            context: Additional context including user profile and analysis
            
        Returns:
            List of learning path steps with metadata
        """
        # Extract topics from query
        topics = self.topic_hierarchy.extract_topics(query)
        
        # Get user's current knowledge state
        knowledge_state = self.knowledge_mapper.get_knowledge_state(
            self.user_profile["user_id"]
        )
        
        # Create initial learning path
        path = self._generate_learning_path(topics, knowledge_state)
        
        # Enrich path with additional metadata
        enriched_path = []
        for step in path:
            topic_analysis = self.analyze_topic(step["topic"])
            enriched_step = {
                **step,
                "prerequisites": topic_analysis.prerequisites,
                "learning_outcomes": topic_analysis.learning_outcomes,
                "practical_applications": topic_analysis.practical_applications[:2],  # Limit to top 2
                "complexity": topic_analysis.complexity_level
            }
            enriched_path.append(enriched_step)
        
        return enriched_path

    def adapt_learning_path(
        self,
        path: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Adapt a learning path based on user's current knowledge and progress.
        
        Args:
            path: Original learning path to adapt
            user_profile: User's profile with learning history
            
        Returns:
            Adapted learning path
        """
        # Get user's mastered topics
        mastered_topics = {
            topic["id"]
            for topic in user_profile.get("topics_learned", [])
            if topic.get("mastery_level", 0) >= 0.8
        }
        
        # Filter out mastered topics and their prerequisites
        adapted_path = []
        for step in path:
            topic_id = step["topic"]
            
            # Skip if topic is already mastered
            if topic_id in mastered_topics:
                continue
                
            # Get topic details
            topic = self.topic_hierarchy.get_topic(topic_id)
            if not topic:
                continue
                
            # Check prerequisites
            prerequisites = topic.get("prerequisites", [])
            missing_prereqs = [
                prereq for prereq in prerequisites
                if prereq not in mastered_topics
            ]
            
            # Add missing prerequisites first
            for prereq in missing_prereqs:
                prereq_topic = self.topic_hierarchy.get_topic(prereq)
                if not prereq_topic:
                    continue
                    
                adapted_path.append({
                    "topic": prereq,
                    "type": "prerequisite",
                    "estimated_time": prereq_topic.get("estimated_duration", "2 hours"),
                    "complexity": prereq_topic.get("complexity", "intermediate")
                })
            
            # Add the main topic
            adapted_path.append({
                **step,
                "prerequisites": missing_prereqs,
                "estimated_time": topic.get("estimated_duration", "2 hours"),
                "complexity": topic.get("complexity", "intermediate")
            })
        
        return adapted_path

    def specialized_function(self, function_type: str, **kwargs) -> Any:
        """Execute specialized navigator functions."""
        function_map = {
            "analyze_topic": self.analyze_topic,
            "create_learning_path": self.create_learning_path,
            "suggest_next_topics": self.suggest_next_topics,
            "find_related_topics": lambda topic_id: self._find_related_topics(topic_id),
            "estimate_completion_time": lambda topic_id, pace: self._estimate_completion_time(
                self.topic_hierarchy.get_topic(topic_id),
                pace
            ),
            "analyze_learning_path": self.analyze_learning_path,
            "adapt_learning_path": self.adapt_learning_path
        }
        
        if function_type not in function_map:
            raise ValueError(f"Unknown function type: {function_type}")
            
        function = function_map[function_type]
        self._validate_function_params(function, kwargs)
        return function(**kwargs)

    def _analyze_prerequisites(self, topic: KnowledgeNode) -> List[str]:
        """Analyze prerequisites with confidence scores."""
        prereqs = []
        for prereq_id in topic.prerequisites:
            prereq_node = self.topic_hierarchy.get_topic(prereq_id)
            if not prereq_node:
                continue
                
            confidence = self.knowledge_mapper.calculate_prerequisite_confidence(
                topic.id,
                prereq_id,
                self.user_profile
            )
            
            if confidence > 0.7:  # Minimum confidence threshold
                prereqs.append(prereq_id)
                
        return prereqs

    def _find_related_topics(self, topic_id: str) -> List[str]:
        """Find related topics using graph analysis."""
        related = []
        topic_node = self.topic_hierarchy.get_topic(topic_id)
        
        if not topic_node:
            return related
            
        # Get direct neighbors
        neighbors = list(self.learning_graph.neighbors(topic_id))
        
        # Calculate relevance scores
        scored_topics = [
            (
                neighbor,
                self.knowledge_mapper.calculate_topic_relevance(
                    topic_id,
                    neighbor,
                    self.user_profile
                )
            )
            for neighbor in neighbors
        ]
        
        # Filter and sort by relevance
        related = [
            topic for topic, score in sorted(
                scored_topics,
                key=lambda x: x[1],
                reverse=True
            )
            if score > 0.5  # Minimum relevance threshold
        ]
        
        return related[:5]  # Return top 5 related topics

    def _analyze_complexity(self, topic: KnowledgeNode) -> str:
        """Analyze topic complexity considering user profile."""
        base_complexity = topic.complexity
        user_level = self.user_profile.get("expertise_level", "beginner")
        
        # Adjust complexity based on prerequisites mastery
        prereq_mastery = self.knowledge_mapper.calculate_prerequisites_mastery(
            topic.id,
            self.user_profile
        )
        
        if prereq_mastery > 0.8:
            return self._adjust_complexity(base_complexity, -1)
        elif prereq_mastery < 0.4:
            return self._adjust_complexity(base_complexity, 1)
            
        return base_complexity

    def _identify_learning_outcomes(self, topic: KnowledgeNode) -> List[str]:
        """Identify expected learning outcomes."""
        outcomes = []
        
        # Get base outcomes from topic
        outcomes.extend(topic.learning_outcomes)
        
        # Add derived outcomes based on topic connections
        derived_outcomes = self.knowledge_mapper.get_derived_outcomes(
            topic.id,
            self.user_profile
        )
        outcomes.extend(derived_outcomes)
        
        # Add practical application outcomes
        practical_outcomes = [
            f"Apply {topic.name} in {application}"
            for application in self._find_practical_applications(topic)
        ]
        outcomes.extend(practical_outcomes)
        
        return list(set(outcomes))  # Remove duplicates

    def _find_practical_applications(self, topic: KnowledgeNode) -> List[str]:
        """Find practical applications for a topic."""
        applications = []
        
        # Get direct applications from topic
        applications.extend(topic.practical_applications)
        
        # Get applications from related topics
        related_topics = self._find_related_topics(topic.id)
        for related_id in related_topics:
            related = self.topic_hierarchy.get_topic(related_id)
            if related:
                applications.extend(related.practical_applications)
        
        # Get industry-specific applications
        industry = self.user_profile.get("industry")
        if industry:
            industry_applications = self.knowledge_mapper.get_industry_applications(
                topic.id,
                industry
            )
            applications.extend(industry_applications)
        
        return list(set(applications))  # Remove duplicates

    def _gather_topic_resources(self, topic: KnowledgeNode) -> List[Dict[str, str]]:
        """Gather learning resources for a topic."""
        resources = []
        
        # Get base resources
        resources.extend(topic.resources)
        
        # Get user-appropriate resources
        learning_style = self.user_profile.get("learning_style", "self_paced")
        level = self.user_profile.get("expertise_level", "beginner")
        
        filtered_resources = self.knowledge_mapper.filter_resources(
            topic.id,
            learning_style,
            level
        )
        resources.extend(filtered_resources)
        
        # Add practice resources
        if self.user_profile.get("include_practice", True):
            practice_resources = self._generate_practice_resources(topic)
            resources.extend(practice_resources)
        
        return resources

    def _generate_practice_items(self, topic: KnowledgeNode) -> List[Dict[str, Any]]:
        """Generate practice items for a topic."""
        practice_items = []
        
        # Generate basic practice items
        practice_items.extend(topic.practice_items)
        
        # Generate level-appropriate exercises
        level = self.user_profile.get("expertise_level", "beginner")
        custom_exercises = self.knowledge_mapper.generate_exercises(
            topic.id,
            level
        )
        practice_items.extend(custom_exercises)
        
        # Add real-world scenarios
        scenarios = self._generate_practical_scenarios(topic)
        practice_items.extend(scenarios)
        
        return practice_items

    def _check_prerequisites(self, topic_id: str) -> bool:
        """Check if prerequisites are met."""
        topic = self.topic_hierarchy.get_topic(topic_id)
        if not topic:
            return False
            
        prereqs = topic.prerequisites
        if not prereqs:
            return True
            
        mastered_topics = set(self.user_profile.get("mastered_topics", []))
        return all(prereq in mastered_topics for prereq in prereqs)

    def analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a learning query using specialized function."""
        return self.specialized_function(
            "analyze_query",
            query=query,
            context=context,
            topic_hierarchy=self.topic_hierarchy.get_hierarchy_data(),
            user_profile=self.user_profile
        )

    def get_confidence_score(self, topic_id: str) -> float:
        """Calculate confidence score for handling a topic."""
        topic = self.topic_hierarchy.get_topic(topic_id)
        if not topic:
            return 0.0
            
        score = 0.0
        
        # Check topic presence in hierarchy
        if topic:
            score += 0.3
            
        # Check prerequisite knowledge
        if self._check_prerequisites(topic_id):
            score += 0.3
            
        # Check topic relevance to user profile
        relevance = self.knowledge_mapper.calculate_topic_relevance(
            topic_id,
            None,
            self.user_profile
        )
        score += 0.4 * relevance
        
        return min(score, 1.0)

    def get_specialization_areas(self) -> List[str]:
        """Get areas of specialization."""
        return [
            "topic navigation",
            "learning path creation",
            "prerequisite analysis",
            "complexity assessment",
            "resource curation"
        ]

    def get_topic_insights(self, topic_id: str) -> Dict[str, Any]:
        """Get comprehensive topic insights."""
        topic = self.topic_hierarchy.get_topic(topic_id)
        if not topic:
            return {}
            
        return {
            "analysis": self.analyze_topic(topic_id),
            "relationships": self._find_related_topics(topic_id),
            "learning_path": self.create_learning_path(topic_id),
            "resources": self._gather_topic_resources(topic),
            "practice": self._generate_practice_items(topic),
            "applications": self._find_practical_applications(topic),
            "confidence": self.get_confidence_score(topic_id)
        }

    def _adjust_complexity(self, base_complexity: str, adjustment: int) -> str:
        """Adjust complexity level."""
        levels = ["beginner", "intermediate", "advanced", "expert"]
        current_index = levels.index(base_complexity)
        new_index = max(0, min(len(levels) - 1, current_index + adjustment))
        return levels[new_index]

    def _generate_practical_scenarios(self, topic: KnowledgeNode) -> List[Dict[str, Any]]:
        """Generate practical scenarios for practice."""
        scenarios = []
        
        # Get industry-specific scenarios
        industry = self.user_profile.get("industry")
        if industry:
            industry_scenarios = self.knowledge_mapper.get_industry_scenarios(
                topic.id,
                industry
            )
            scenarios.extend(industry_scenarios)
        
        # Generate general practical scenarios
        general_scenarios = self.knowledge_mapper.generate_scenarios(
            topic.id,
            self.user_profile.get("expertise_level", "beginner")
        )
        scenarios.extend(general_scenarios)
        
        return scenarios

    def _generate_practice_resources(self, topic: KnowledgeNode) -> List[Dict[str, str]]:
        """Generate practice-focused resources."""
        return self.knowledge_mapper.get_practice_resources(
            topic.id,
            self.user_profile.get("expertise_level", "beginner"),
            self.user_profile.get("learning_style", "self_paced")
        )

    def _calculate_context_relevance(
        self,
        topics: List[str],
        context: Dict[str, Any]
    ) -> float:
        """Calculate relevance of topics to given context."""
        if not topics:
            return 0.0
            
        relevance_scores = []
        for topic_id in topics:
            score = self.knowledge_mapper.calculate_context_relevance(
                topic_id,
                context
            )
            relevance_scores.append(score)
            
        return sum(relevance_scores) / len(relevance_scores)

    def _suggest_learning_sequence(
        self,
        topics: List[str],
        context: Dict[str, Any]
    ) -> List[str]:
        """Suggest optimal learning sequence for topics."""
        return self.knowledge_mapper.optimize_learning_sequence(
            topics,
            self.user_profile,
            context
        )

    def get_available_functions(self) -> List[str]:
        """Get list of available specialized functions."""
        return [
            "analyze_topic",
            "create_learning_path",
            "suggest_next_topics",
            "analyze_prerequisites",
            "estimate_completion_time",
            "update_user_profile_with_learned_topic",
            "adapt_learning_path"
        ]

    def _analyze_topic(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze a topic and its relationships."""
        topic_data = self.topic_hierarchy.get_topic(topic)
        if not topic_data:
            raise ValueError(f"Topic not found: {topic}")
            
        return {
            "topic_info": self._get_topic_info(topic_data),
            "prerequisites": self._analyze_prerequisites(topic),
            "learning_path": self._create_topic_learning_path(topic),
            "estimated_time": self._estimate_completion_time(topic),
            "confidence_score": self.get_confidence_score(topic)
        }

    def _create_learning_path(
        self,
        start_topic: str,
        target_topic: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a structured learning path."""
        return {
            "path": self._generate_learning_path(start_topic, target_topic),
            "milestones": self._identify_milestones(start_topic, target_topic),
            "prerequisites": self._get_path_prerequisites(start_topic, target_topic),
            "estimated_duration": self._calculate_path_duration(start_topic, target_topic),
            "difficulty_progression": self._analyze_difficulty_progression(start_topic, target_topic)
        }

    def _suggest_next_topics(
        self,
        current_topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Suggest next topics based on current progress."""
        user_level = self._determine_user_level(context)
        current_mastery = self._assess_topic_mastery(current_topic, context)
        
        suggestions = []
        for topic in self._find_related_topics(current_topic):
            if self._is_appropriate_next_step(topic, user_level, current_mastery):
                suggestions.append({
                    "topic": topic,
                    "relevance_score": self._calculate_relevance(topic, current_topic),
                    "difficulty_increase": self._calculate_difficulty_delta(current_topic, topic),
                    "prerequisites_met": self._check_prerequisites(topic),
                    "estimated_time": self._estimate_completion_time(topic)
                })
        
        return sorted(
            suggestions,
            key=lambda x: (x["relevance_score"], -x["difficulty_increase"]),
            reverse=True
        )[:5]

    def _adapt_learning_path(
        self,
        path: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Adapt a learning path based on user profile and progress."""
        adapted_path = []
        
        # Get user's mastered topics
        mastered_topics = []
        for topic_data in user_profile.get("topics_learned", []):
            if isinstance(topic_data, dict):
                if topic_data.get("mastery_level", 0) > 0.8:
                    mastered_topics.append(topic_data["id"])
            else:
                # Handle case where topics_learned is just a list of IDs
                mastered_topics.append(topic_data)
        
        # Filter out already mastered topics
        for step in path:
            topic_id = step.get("topic")
            if not topic_id:
                # Skip invalid steps
                continue
                
            if topic_id in mastered_topics:
                # Skip mastered topics but note them
                adapted_path.append({
                    **step,
                    "status": "mastered",
                    "action": "review"
                })
            else:
                # Determine difficulty based on prerequisites
                difficulty = self._calculate_topic_difficulty(
                    topic_id,
                    mastered_topics
                )
                
                adapted_path.append({
                    **step,
                    "status": "new",
                    "difficulty": difficulty,
                    "estimated_time": self._estimate_learning_time(
                        self.topic_hierarchy.get_topic(topic_id),
                        difficulty
                    )
                })
        
        return adapted_path

    def _calculate_topic_difficulty(
        self,
        topic_id: str,
        mastered_topics: List[str]
    ) -> str:
        """Calculate difficulty of a topic based on prerequisites mastery."""
        topic = self.topic_hierarchy.get_topic(topic_id)
        if not topic:
            return "unknown"
            
        prerequisites = topic.prerequisites
        if not prerequisites:
            return "beginner"
            
        # Calculate percentage of mastered prerequisites
        mastered_count = sum(1 for p in prerequisites if p in mastered_topics)
        if not prerequisites:
            mastery_percentage = 1.0
        else:
            mastery_percentage = mastered_count / len(prerequisites)
        
        if mastery_percentage > 0.8:
            return "beginner"
        elif mastery_percentage > 0.4:
            return "intermediate"
        else:
            return "advanced"

    def _estimate_learning_time(
        self,
        topic: Optional[KnowledgeNode],
        difficulty: str
    ) -> timedelta:
        """Estimate learning time based on topic and difficulty."""
        if not topic:
            return timedelta(hours=1)  # Default estimate
            
        # Base time from topic metadata
        base_time = topic.estimated_duration or timedelta(hours=1)
        
        # Adjust based on difficulty
        if difficulty == "advanced":
            return base_time * 1.5
        elif difficulty == "intermediate":
            return base_time * 1.2
        else:
            return base_time

    def _get_prerequisites(self, topic_id: str) -> List[str]:
        """
        Get list of prerequisites for a topic.
        
        Args:
            topic_id: Topic ID to get prerequisites for
            
        Returns:
            List of prerequisite topic IDs
        """
        topic = self.topic_hierarchy.get_topic(topic_id)
        if not topic:
            return []
        
        return topic.prerequisites

    def _check_prerequisite_mastery(self, prereq_id: str, knowledge_state: Dict[str, Any]) -> bool:
        """
        Check if a prerequisite topic has been mastered.
        
        Args:
            prereq_id: Prerequisite topic ID
            knowledge_state: User's current knowledge state
            
        Returns:
            True if prerequisite is considered mastered
        """
        if prereq_id in knowledge_state:
            mastery_level = knowledge_state.get(prereq_id, 0)
            return mastery_level >= 0.7  # Threshold for mastery
        return False

    def _get_subtopics(self, topic_id: str) -> List[str]:
        """
        Get the subtopics of a given topic.
        
        Args:
            topic_id: Topic ID to get subtopics for
            
        Returns:
            List of subtopic IDs
        """
        topic = self.topic_hierarchy.get_topic(topic_id)
        if not topic:
            return []
        return [subtopic.id for subtopic in topic.get_subtopics()]

    def _estimate_topic_time(self, topic_id: str) -> timedelta:
        """
        Estimate the time required to learn a topic.
        
        Args:
            topic_id: Topic ID to estimate time for
            
        Returns:
            Estimated learning time as a timedelta
        """
        topic = self.topic_hierarchy.get_topic(topic_id)
        if not topic:
            return timedelta(hours=2)  # Default estimate of 2 hours
        return topic.estimated_duration or timedelta(hours=2)

class TopicNavigator:
    def __init__(self, config: BaseConfig):
        super().__init__(config)
        self.topic_hierarchy = TopicHierarchy()
        self.knowledge_mapper = KnowledgeMapper()

    @agent_method()
    def analyze_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """Analyzes learning query and suggests path."""
        topics = self.topic_hierarchy.extract_topics(query)
        knowledge_state = self.knowledge_mapper.get_knowledge_state()
        
        return {
            "topics": topics,
            "path": self._create_learning_path(topics, knowledge_state),
            "prerequisites": self._get_prerequisites(topics)
        }

    def _create_learning_path(
        self,
        topics: List[str],
        knowledge_state: Dict
    ) -> List[Dict]:
        """Creates optimized learning path."""
        return self.knowledge_mapper.create_path(
            topics,
            knowledge_state,
            self.config.confidence_threshold
        )

    def _get_prerequisites(self, topics: List[str]) -> List[str]:
        """Gets prerequisites for topics."""
        return self.topic_hierarchy.get_prerequisites(topics)
