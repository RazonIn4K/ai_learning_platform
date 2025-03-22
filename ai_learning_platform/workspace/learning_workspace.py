"""Core workspace implementation for AI-driven learning platform."""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
import logging
from datetime import datetime
import json
from pathlib import Path
import uuid

from ..agents import (
    TopicNavigatorAgent,
    LearningCoordinatorAgent,
    DomainExpertAgent,
    ConnectionExpert,
    ResearchAgent,
    KnowledgeAgent
)
from ..models.model_registry import ModelRegistry
from ..utils.exceptions import WorkspaceError, ConfigurationError
from ..utils.learning_profile_manager import LearningProfileManager
from ..utils.knowledge_explorer import KnowledgeExplorer
from ..utils.logging_config import setup_logging, LearningAnalytics

logger = logging.getLogger(__name__)

@dataclass
class WorkspaceConfig:
    """Configuration for learning workspace."""
    domains: List[str]
    enable_research: bool = False
    learning_style: str = "balanced"
    model_type: str = "standard"
    tracking_level: str = "basic"

class LearningWorkspace:
    """Manages the learning environment and agent interactions."""
    
    def __init__(
        self,
        config: WorkspaceConfig,
        user_profile: Optional[Dict[str, Any]] = None,
        topic_hierarchy: Optional[Any] = None,
        knowledge_mapper: Optional[Any] = None,
        profile_manager: Optional[LearningProfileManager] = None
    ):
        """Initialize the learning workspace."""
        self.config = config
        self.user_profile = user_profile or {}
        self.topic_hierarchy = topic_hierarchy
        self.knowledge_mapper = knowledge_mapper
        self.profile_manager = profile_manager or LearningProfileManager()
        self.agents = {}
        self.model_clients = {}
        self.knowledge_explorer = KnowledgeExplorer(self.topic_hierarchy)
        self.session_id = str(uuid.uuid4())
        
        # Set up logging and analytics
        self.analytics = setup_logging()
        
        self._initialize_components()
        logger.info("Learning workspace initialized successfully")

    def process_message(self, query: str) -> Dict[str, Any]:
        """
        Process a simple message without full learning session context.
        Use for quick queries that don't require tracking.
        """
        try:
            coordinator = self.agents.get("learning_coordinator")
            if not coordinator:
                raise WorkspaceError("Learning coordinator not initialized")
            
            return coordinator.process_query(
                query=query,
                context=self._prepare_basic_context()
            )
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            raise WorkspaceError(f"Message processing failed: {str(e)}")

    def process_learning_session(self, query: str) -> Dict[str, Any]:
        """Process a comprehensive learning session with full tracking and context."""
        session_id = self._start_session()
        
        try:
            start_time = datetime.now()
            
            # Log session start
            self.analytics.log_learning_event(
                "session_start",
                self.user_profile["user_id"],
                {"query": query},
                self.session_id
            )
            
            context = self._prepare_learning_context()
            response = self.agents["learning_coordinator"].process_learning_session(
                query=query,
                context=context,
                session_id=session_id
            )
            
            # If the response includes a learning path, analyze cross-domain connections
            if "learning_path" in response:
                connections = self.agents["connection_expert"].analyze_path_connections(
                    response["learning_path"]
                )
                response["connections"] = connections
                
                # Log cross-domain connections
                for conn in connections:
                    self.analytics.log_cross_domain_connection(
                        self.user_profile["user_id"],
                        conn["source_domain"],
                        conn["target_domain"],
                        conn["strength"],
                        self.session_id
                    )
            
            # Calculate session duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Log session completion
            self.analytics.log_learning_event(
                "session_complete",
                self.user_profile["user_id"],
                {
                    "duration": duration,
                    "response_type": list(response.keys())
                },
                self.session_id
            )
            
            self._update_learning_state(response)
            self._end_session(session_id, success=True)
            
            return response
        except Exception as e:
            logger.error(f"Error in learning session: {str(e)}", exc_info=True)
            self._end_session(session_id, success=False)
            self.analytics.log_error(
                self.user_profile["user_id"],
                "session_error",
                str(e),
                {"query": query},
                self.session_id
            )
            raise WorkspaceError(f"Session processing failed: {str(e)}")

    def get_learning_recommendations(self) -> Dict[str, Any]:
        """Get personalized learning recommendations based on user profile and history."""
        try:
            context = self._prepare_learning_context()
            return self.agents["knowledge"].get_recommendations(context=context)
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            raise WorkspaceError("Failed to get learning recommendations")

    def analyze_learning_progress(self) -> Dict[str, Any]:
        """Analyze user's learning progress across domains."""
        try:
            if not self.user_profile or "user_id" not in self.user_profile:
                raise WorkspaceError("User profile required for progress analysis")
            
            history = self.profile_manager.get_learning_history(
                self.user_profile["user_id"]
            )
            
            return self.agents["knowledge"].analyze_progress(
                user_profile=self.user_profile,
                learning_history=history
            )
        except Exception as e:
            logger.error(f"Error analyzing progress: {str(e)}", exc_info=True)
            raise WorkspaceError("Failed to analyze learning progress")

    def explore_topic(self, topic: str) -> Dict[str, Any]:
        """Explore a specific topic in detail."""
        try:
            context = self._prepare_learning_context()
            return self.agents["topic_navigator"].explore_topic(
                topic=topic,
                context=context
            )
        except Exception as e:
            logger.error(f"Error exploring topic: {str(e)}", exc_info=True)
            raise WorkspaceError(f"Topic exploration failed: {str(e)}")

    def get_domain_roadmap(self, domain: str) -> Dict[str, Any]:
        """Get a learning roadmap for a specific domain."""
        try:
            context = self._prepare_learning_context()
            expert = self.agents.get(f"{domain}_expert")
            if not expert:
                raise WorkspaceError(f"No expert found for domain: {domain}")
            
            return expert.get_domain_roadmap(context=context)
        except Exception as e:
            logger.error(f"Error getting domain roadmap: {str(e)}", exc_info=True)
            raise WorkspaceError(f"Failed to get roadmap for domain: {domain}")

    def _initialize_components(self) -> None:
        """Initialize workspace components."""
        try:
            self._setup_model_clients()
            self._initialize_core_agents()
            
            if self.config.enable_research:
                self._initialize_research_agents()
                
            logger.info("Workspace components initialized successfully")
        except Exception as e:
            logger.error(f"Component initialization failed: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Failed to initialize workspace: {str(e)}")

    def _setup_model_clients(self) -> None:
        """Set up model clients using ModelRegistry."""
        self.model_clients = {
            "openai/gpt-4": ModelRegistry.create_client(ModelRegistry.GPT4),
            "anthropic/claude-3-sonnet": ModelRegistry.create_client(ModelRegistry.CLAUDE_3_SONNET),
            "openchat/openchat-3.5": ModelRegistry.create_client(ModelRegistry.OPENCHAT_3_5),
            "google/gemini-pro": ModelRegistry.create_client(ModelRegistry.GEMINI_PRO)
        }
        logger.info("Model clients initialized successfully")

    def _initialize_core_agents(self) -> None:
        """Initialize core learning agents."""
        try:
            self._create_topic_navigator()
            self._create_domain_experts()
            self._create_connection_expert()
            self._create_learning_coordinator()
            
            logger.info("Core agents initialized successfully")
        except Exception as e:
            logger.error(f"Core agent initialization failed: {str(e)}", exc_info=True)
            raise ConfigurationError("Failed to initialize core agents")

    def _create_topic_navigator(self) -> None:
        """Create topic navigator agent."""
        try:
            self.agents["topic_navigator"] = TopicNavigatorAgent(
                topic_hierarchy=self.topic_hierarchy,
                knowledge_mapper=self.knowledge_mapper,
                model_name="anthropic/claude-3-sonnet",
                model_params={"temperature": 0.7},
                user_profile=self.user_profile
            )
            logger.info("Topic navigator agent created successfully")
        except Exception as e:
            logger.error(f"Failed to create topic navigator agent: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Topic navigator initialization failed: {str(e)}")

    def _create_domain_experts(self) -> None:
        """Create domain expert agents."""
        try:
            for domain in self.config.domains:
                self.agents[f"{domain}_expert"] = DomainExpertAgent(
                    domain=domain,
                    knowledge_explorer=self.knowledge_explorer,
                    model_name="openai/gpt-4",
                    model_params={"temperature": 0.5}
                )
            logger.info(f"Created {len(self.config.domains)} domain expert agents")
        except Exception as e:
            logger.error(f"Failed to create domain expert agents: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Domain expert initialization failed: {str(e)}")

    def _create_connection_expert(self) -> None:
        """Create connection expert agent."""
        try:
            self.agents["connection_expert"] = ConnectionExpert(
                knowledge_mapper=self.knowledge_mapper,
                topic_hierarchy=self.topic_hierarchy,
                knowledge_explorer=self.knowledge_explorer,
                model_name="anthropic/claude-3-sonnet",
                model_params={"temperature": 0.6}
            )
            logger.info("Connection expert agent created successfully")
        except Exception as e:
            logger.error(f"Failed to create connection expert agent: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Connection expert initialization failed: {str(e)}")

    def _create_learning_coordinator(self) -> None:
        """Create learning coordinator agent."""
        try:
            self.agents["learning_coordinator"] = LearningCoordinatorAgent(
                specialized_agents=self.agents,
                model_name="anthropic/claude-3-sonnet",
                model_params={"temperature": 0.7},
                user_profile=self.user_profile,
                profile_manager=self.profile_manager
            )
            logger.info("Learning coordinator agent created successfully")
        except Exception as e:
            logger.error(f"Failed to create learning coordinator agent: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Learning coordinator initialization failed: {str(e)}")

    def _initialize_research_agents(self) -> None:
        """Initialize research-focused agents."""
        try:
            self.agents["research"] = ResearchAgent(
                topic_hierarchy=self.topic_hierarchy,
                knowledge_mapper=self.knowledge_mapper,
                knowledge_explorer=self.knowledge_explorer,
                model_name="anthropic/claude-3-sonnet",
                model_params={"temperature": 0.8},
                user_profile=self.user_profile
            )
            
            self.agents["knowledge"] = KnowledgeAgent(
                topic_hierarchy=self.topic_hierarchy,
                profile_manager=self.profile_manager,
                knowledge_explorer=self.knowledge_explorer,
                model_name="openai/gpt-4",
                model_params={"temperature": 0.6},
                user_profile=self.user_profile
            )
            logger.info("Research agents initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize research agents: {str(e)}", exc_info=True)
            raise ConfigurationError(f"Research agent initialization failed: {str(e)}")

    def _prepare_basic_context(self) -> Dict[str, Any]:
        """Prepare minimal context for simple queries."""
        return {
            "workspace_config": self.config.__dict__,
            "session_info": {
                "timestamp": datetime.now().isoformat(),
                "session_id": self._generate_session_id()
            }
        }

    def _prepare_learning_context(self) -> Dict[str, Any]:
        """Prepare comprehensive context for learning sessions."""
        try:
            context = self._prepare_basic_context()
            
            if self.user_profile and "user_id" in self.user_profile:
                learning_history = self.profile_manager.get_learning_history(
                    self.user_profile["user_id"]
                ) or {}
                
                context.update({
                    "user_profile": self.user_profile,
                    "learning_history": learning_history,
                    "recent_topics": learning_history.get("recent_topics", []),
                    "learning_preferences": self.user_profile.get("learning_preferences", {})
                })
            
            # Add domain-specific contexts
            context["domain_contexts"] = {
                domain: self.knowledge_explorer.get_domain_context(domain)
                for domain in self.config.domains
            }
            
            return context
        except Exception as e:
            logger.error(f"Error preparing learning context: {str(e)}", exc_info=True)
            return self._prepare_basic_context()

    def save_state(self, path: str) -> None:
        """Save workspace state to disk."""
        try:
            state_dir = Path(path)
            state_dir.mkdir(parents=True, exist_ok=True)
            
            # Save core components
            with open(state_dir / "workspace_state.json", "w") as f:
                json.dump({
                    "config": self.config.__dict__,
                    "user_profile": self.user_profile,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
            
            # Save learning history if available
            if self.user_profile and "user_id" in self.user_profile:
                history = self.profile_manager.get_learning_history(
                    self.user_profile["user_id"]
                )
                if history:
                    with open(state_dir / "learning_history.json", "w") as f:
                        json.dump(history, f, indent=2)
            
            logger.info(f"Workspace state saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save workspace state: {str(e)}", exc_info=True)
            raise WorkspaceError(f"State saving failed: {str(e)}")

    def load_state(self, path: str) -> None:
        """Load workspace state from disk."""
        try:
            state_dir = Path(path)
            
            # Load core state
            with open(state_dir / "workspace_state.json", "r") as f:
                state_data = json.load(f)
                self.config = WorkspaceConfig(**state_data["config"])
                self.user_profile = state_data["user_profile"]
            
            # Load learning history if available
            history_path = state_dir / "learning_history.json"
            if history_path.exists() and self.user_profile.get("user_id"):
                with open(history_path, "r") as f:
                    history_data = json.load(f)
                    self.profile_manager.load_history(
                        self.user_profile["user_id"],
                        history_data
                    )
            
            # Reinitialize components with loaded state
            self._initialize_components()
            logger.info(f"Workspace state loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load workspace state: {str(e)}", exc_info=True)
            raise WorkspaceError(f"State loading failed: {str(e)}")

    def _update_learning_state(self, response: Dict[str, Any]) -> None:
        """Update learning state based on session response."""
        try:
            # Extract topics from response
            topics = response.get("topics", [])
            if not topics and "learning_path" in response:
                # Extract topics from learning path if direct topics not available
                topics = [item.get("topic") for item in response.get("learning_path", [])
                         if isinstance(item, dict) and "topic" in item]
            
            # Get learning metrics
            learning_metrics = response.get("learning_metrics", {})
            if not learning_metrics and "metadata" in response:
                # Try to extract metrics from metadata
                learning_metrics = response.get("metadata", {})
            
            # Extract mastered topics with confidence thresholds
            mastered_topics = self.profile_manager.extract_mastered_topics(
                topics,
                learning_metrics
            )
            
            # Update user progress if user_id exists
            if self.user_profile and "user_id" in self.user_profile:
                self.profile_manager.update_progress(
                    self.user_profile,
                    mastered_topics,
                    learning_metrics
                )
                
                # Record interaction in learning history
                self.profile_manager.record_learning_interaction(
                    self.user_profile["user_id"],
                    {
                        "timestamp": datetime.now().isoformat(),
                        "topics": topics,
                        "mastered_topics": mastered_topics,
                        "session_metrics": learning_metrics
                    }
                )
            
            # Update knowledge graph
            connections = response.get("connections", [])
            if not connections and "learning_path" in response:
                # Try to extract connections from learning path
                path = response.get("learning_path", [])
                if len(path) > 1:
                    # Create implicit connections between sequential items
                    connections = []
                    for i in range(len(path) - 1):
                        if isinstance(path[i], dict) and isinstance(path[i+1], dict):
                            if "topic" in path[i] and "topic" in path[i+1]:
                                connections.append({
                                    "source": path[i]["topic"],
                                    "target": path[i+1]["topic"],
                                    "type": "sequence",
                                    "weight": 0.8
                                })
            
            self.knowledge_mapper.update_knowledge_graph(
                self.user_profile,
                mastered_topics,
                connections
            )
            
            logger.info(f"Learning state updated successfully with {len(mastered_topics)} mastered topics")
        except Exception as e:
            logger.error(f"Failed to update learning state: {str(e)}", exc_info=True)
            raise WorkspaceError(f"Failed to update learning state: {str(e)}")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_id = self.user_profile.get("user_id", "anonymous")
        return f"session_{user_id}_{timestamp}"

    def _start_session(self) -> str:
        """Start a new learning session."""
        try:
            session_id = str(uuid.uuid4())
            logger.info(f"Starting learning session {session_id}")
            
            # Record session start if user has profile
            if self.user_profile and "user_id" in self.user_profile:
                self.profile_manager.record_session_event(
                    self.user_profile["user_id"],
                    "start",
                    {
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "config": self.config.__dict__
                    }
                )
            return session_id
        except Exception as e:
            logger.error(f"Failed to start learning session: {str(e)}", exc_info=True)
            # Return a fallback session ID if there's an error
            return f"error_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _end_session(self, session_id: str, success: bool) -> None:
        """End a learning session."""
        try:
            status = "completed" if success else "failed"
            logger.info(f"Ending learning session {session_id}: {status}")
            
            # Record session end if user has profile
            if self.user_profile and "user_id" in self.user_profile:
                self.profile_manager.record_session_event(
                    self.user_profile["user_id"],
                    "end",
                    {
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "status": status,
                        "duration": self._calculate_session_duration(session_id)
                    }
                )
        except Exception as e:
            logger.error(f"Failed to end learning session: {str(e)}", exc_info=True)
    
    def _calculate_session_duration(self, session_id: str) -> float:
        """Calculate session duration in seconds if possible."""
        try:
            if self.user_profile and "user_id" in self.user_profile:
                session_events = self.profile_manager.get_session_events(
                    self.user_profile["user_id"],
                    session_id
                )
                
                if session_events and len(session_events) > 0:
                    start_event = next((e for e in session_events if e.get("type") == "start"), None)
                    if start_event and "timestamp" in start_event:
                        start_time = datetime.fromisoformat(start_event["timestamp"])
                        end_time = datetime.now()
                        return (end_time - start_time).total_seconds()
            
            # Default to 0 if can't calculate
            return 0.0
        except Exception:
            return 0.0

    def _track_learning_progress(
        self,
        topics: List[str],
        session_metrics: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track learning progress and update user profile."""
        if not self.agents.get("topic_navigator"):
            logger.warning("Topic navigator agent not available for tracking progress")
            return {"error": "Topic navigator agent not available"}
        
        topic_navigator = self.agents["topic_navigator"]
        
        # Calculate topic mastery
        topic_mastery = {}
        for topic in topics:
            # Get metrics for this topic
            metrics = session_metrics.get(topic, {})
            
            # Calculate mastery score
            comprehension = metrics.get("comprehension", 0)
            application = metrics.get("application", 0)
            retention = metrics.get("retention", 0)
            
            # Default values if not present
            if comprehension == 0 and application == 0 and retention == 0:
                comprehension = 0.6  # Default moderately good comprehension
                application = 0.4  # Default some application
                retention = 0.5  # Default moderate retention
            
            mastery_score = (
                comprehension * 0.4 +
                application * 0.4 +
                retention * 0.2
            )
            
            # Update user profile for this topic
            update_result = topic_navigator.specialized_function(
                "update_user_profile_with_learned_topic",
                topic_id=topic,
                mastery_level=mastery_score,
                context={"session_metrics": metrics}
            )
            
            topic_mastery[topic] = {
                "score": mastery_score,
                "status": "mastered" if mastery_score > 0.8 else "in_progress",
                "strengths": self._identify_strengths(metrics),
                "gaps": self._identify_gaps(metrics),
                "update_result": update_result
            }
        
        # Calculate overall learning trajectory
        trajectory = self._calculate_learning_trajectory(
            user_profile,
            topic_mastery
        )
        
        return {
            "topic_mastery": topic_mastery,
            "updated_profile": user_profile,  # Profile already updated by specialized function
            "learning_trajectory": trajectory
        }

    def _identify_strengths(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify strengths based on metrics."""
        strengths = []
        
        if metrics.get("comprehension", 0) > 0.7:
            strengths.append("strong_comprehension")
        if metrics.get("application", 0) > 0.7:
            strengths.append("practical_application")
        if metrics.get("retention", 0) > 0.7:
            strengths.append("good_retention")
        if metrics.get("speed", 0) > 0.7:
            strengths.append("quick_learning")
        
        return strengths

    def _identify_gaps(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify learning gaps based on metrics."""
        gaps = []
        
        if metrics.get("comprehension", 0) < 0.5:
            gaps.append("needs_conceptual_reinforcement")
        if metrics.get("application", 0) < 0.5:
            gaps.append("needs_practical_exercises")
        if metrics.get("retention", 0) < 0.5:
            gaps.append("needs_spaced_repetition")
        
        return gaps

    def _calculate_learning_trajectory(
        self,
        user_profile: Dict[str, Any],
        topic_mastery: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate learning trajectory based on progress."""
        # Get historical mastery progression
        history = user_profile.get("learning_history", [])
        
        # Calculate trending topics
        trending_topics = []
        for session in history[-5:]:  # Last 5 sessions
            for topic in session.get("topics_covered", []):
                trending_topics.append(topic)
        
        # Count occurrences
        from collections import Counter
        topic_counts = Counter(trending_topics)
        
        # Identify trends
        return {
            "focus_areas": [topic for topic, count in topic_counts.most_common(3)],
            "mastery_trend": self._calculate_mastery_trend(history),
            "recommended_focus": self._recommend_next_focus(
                user_profile,
                topic_mastery
            )
        }

    def _calculate_mastery_trend(self, history: List[Dict[str, Any]]) -> str:
        """Calculate trend in mastery levels over time."""
        if len(history) < 2:
            return "insufficient_data"
        
        # Extract mastery scores from recent sessions
        recent_scores = []
        for session in history[-5:]:  # Last 5 sessions
            session_score = 0
            metrics = session.get("metrics", {})
            for topic, topic_metrics in metrics.items():
                session_score += topic_metrics.get("mastery_level", 0)
            
            if session_score > 0:  # Avoid empty sessions
                recent_scores.append(session_score)
        
        if len(recent_scores) < 2:
            return "insufficient_data"
        
        # Calculate trend
        if recent_scores[-1] > recent_scores[0] * 1.1:
            return "improving"
        elif recent_scores[-1] < recent_scores[0] * 0.9:
            return "declining"
        else:
            return "stable"

    def _recommend_next_focus(
        self,
        user_profile: Dict[str, Any],
        topic_mastery: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Recommend next learning focus based on mastery."""
        # Get topics with gaps
        topics_with_gaps = []
        for topic, data in topic_mastery.items():
            if data.get("gaps"):
                topics_with_gaps.append(topic)
        
        # If there are gaps, recommend focusing on those
        if topics_with_gaps:
            return topics_with_gaps
        
        # Otherwise, recommend next logical topics
        if not self.agents.get("topic_navigator"):
            return []
        
        # Get mastered topics
        mastered_topics = []
        for topic_data in user_profile.get("topics_learned", []):
            if isinstance(topic_data, dict):
                if topic_data.get("mastery_level", 0) > 0.8:
                    mastered_topics.append(topic_data["id"])
        
        # Get recommendations
        recommendations = self.agents["topic_navigator"].specialized_function(
            "suggest_next_topics",
            current_topics=list(topic_mastery.keys()) + mastered_topics,
            max_suggestions=3
        )
        
        return [rec.get("topic_id") for rec in recommendations]

    def analyze_learning_effectiveness(
        self,
        user_id: str,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze learning effectiveness metrics."""
        try:
            # Calculate various metrics
            metrics = {
                "completion_rate": self._calculate_completion_rate(user_id, time_period_days),
                "topic_mastery_growth": self._calculate_mastery_growth(user_id, time_period_days),
                "engagement_metrics": self._calculate_engagement_metrics(user_id, time_period_days),
                "recommended_adjustments": self._generate_learning_recommendations(user_id)
            }
            
            # Log analytics
            self.analytics.log_learning_event(
                "effectiveness_analysis",
                user_id,
                metrics,
                self.session_id
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing learning effectiveness: {str(e)}", exc_info=True)
            self.analytics.log_error(
                user_id,
                "analysis_error",
                str(e),
                {"time_period_days": time_period_days},
                self.session_id
            )
            raise
    
    def _calculate_completion_rate(self, user_id: str, days: int) -> float:
        """Calculate topic completion rate."""
        # Implementation details here
        return 0.85  # placeholder
    
    def _calculate_mastery_growth(self, user_id: str, days: int) -> Dict[str, float]:
        """Calculate mastery growth over time."""
        # Implementation details here
        return {"overall_growth": 0.15}  # placeholder
    
    def _calculate_engagement_metrics(self, user_id: str, days: int) -> Dict[str, float]:
        """Calculate user engagement metrics."""
        # Implementation details here
        return {
            "session_frequency": 0.8,
            "average_duration": 45.0,
            "completion_consistency": 0.75
        }
    
    def _generate_learning_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate personalized learning recommendations."""
        # Implementation details here
        return [
            {
                "type": "focus_area",
                "topic": "advanced_python",
                "reason": "Build on current strengths"
            }
        ]
