from .workspace_template import WorkspaceTemplate
from pathlib import Path
import json
import logging
from typing import Dict, Any, List, Optional

# Add to existing imports
try:
    from ..gray_swan.camel_integration import GraySwanCamelIntegration
except ImportError:
    # Mock class if camel-ai is not installed
    class GraySwanCamelIntegration:
        def __init__(self, *args, **kwargs):
            logging.warning("GraySwanCamelIntegration is not available. Install camel-ai package to use it.")

from ..gray_swan.benchmarker import GraySwanBenchmarker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStrategistTemplate(WorkspaceTemplate):
    """Specialized template for VectorStrategist learning."""
    
    @classmethod
    def create_default(cls) -> 'VectorStrategistTemplate':
        """Create default VectorStrategist workspace."""
        template = cls("vectorstrategist")
        return template.build_workspace(
            domains=[
                "differential_geometry",
                "topology",
                "causal_inference",
                "dynamical_systems",
                "category_theory",
                "ai_security",
                "python_development"
            ],
            custom_config={
                "learning_style": "project_based",
                "tracking_level": "detailed",
                "project_focus": "security_manifolds"
            }
        )
    
    @classmethod
    def create_gray_swan_workspace(cls) -> 'VectorStrategistTemplate':
        """Create Gray Swan competition workspace."""
        template = cls("gray_swan")
        return template.build_workspace(
            domains=[
                "ai_security",
                "prompt_engineering",
                "language_models",
                "red_teaming"
            ],
            custom_config={
                "learning_style": "competition_focused",
                "tracking_level": "detailed",
                "project_focus": "gray_swan_competition"
            }
        )
    
    def initialize_gray_swan_tools(self):
        """Initialize Gray Swan competition tools."""
        self.integration = GraySwanCamelIntegration()
        self.benchmarker = GraySwanBenchmarker()
        
    def load_competition_context(self) -> None:
        """Load Gray Swan competition context."""
        context_path = Path("configs/gray_swan_context.json")
        if context_path.exists():
            with open(context_path) as f:
                self.competition_context = json.load(f)
                
    async def run_advanced_benchmark(self, category: str, target: str, models=None) -> Dict[str, Any]:
        """
        Run advanced benchmark for a specific target using new techniques.
        
        Args:
            category: Attack category to test
            target: Specific target for the attack
            models: Optional list of models to test
            
        Returns:
            Benchmark results comparing technique effectiveness
        """
        logger.info(f"Starting advanced benchmark for category: {category}, target: {target}")
        
        if not hasattr(self, 'benchmarker'):
            logger.info("Initializing Gray Swan tools")
            self.initialize_gray_swan_tools()
            
        if models is None:
            models = [
                {'provider': 'anthropic', 'model_name': 'claude-3-7-sonnet-20250219'}
            ]
            logger.info(f"Using default model: {models[0]}")
        
        try:
            logger.info("Calling benchmark_advanced_techniques")
            results = await self.benchmarker.benchmark_advanced_techniques(
                category=category,
                target=target,
                models=models
            )
            logger.info("Successfully completed advanced benchmark")
            return results
        except Exception as e:
            logger.error(f"Error in run_advanced_benchmark: {str(e)}")
            raise
    
    async def run_technique_comparison(self,
                                     categories=None,
                                     include_advanced=True) -> Dict[str, Any]:
        """
        Run a comparison of different techniques across categories.
        
        Args:
            categories: Optional list of categories to test
            include_advanced: Whether to include advanced techniques
            
        Returns:
            Comprehensive comparison results
        """
        if not hasattr(self, 'benchmarker'):
            self.initialize_gray_swan_tools()
            
        if categories is None:
            categories = ["confidentiality_breach", "conflicting_objectives"]
            
        results = await self.benchmarker.run_full_benchmark(
            categories=categories,
            include_advanced=include_advanced
        )
        
        return results
    
    async def test_custom_prompt(self,
                               prompt: str,
                               category: str,
                               target: str,
                               model_provider: str = "anthropic",
                               model_name: str = "claude-3-7-sonnet-20250219") -> Dict[str, Any]:
        """
        Test a custom prompt against a model.
        
        Args:
            prompt: Custom prompt to test
            category: Attack category
            target: Target objective
            model_provider: Model provider
            model_name: Model name
            
        Returns:
            Test results
        """
        if not hasattr(self, 'integration'):
            self.initialize_gray_swan_tools()
            
        result = await self.integration.test_custom_prompt(
            category=category,
            target=target,
            prompt=prompt,
            model_provider=model_provider,
            model_name=model_name
        )
        
        return result
    
    async def run_tree_jailbreak(self,
                               category: str,
                               target: str,
                               model_provider: str = "anthropic",
                               model_name: str = "claude-3-7-sonnet-20250219",
                               max_depth: int = 3) -> Dict[str, Any]:
        """
        Run a tree-based jailbreak strategy.
        
        Args:
            category: Attack category
            target: Target objective
            model_provider: Model provider
            model_name: Model name
            max_depth: Maximum tree depth
            
        Returns:
            Test results with successful path
        """
        if not hasattr(self, 'integration'):
            self.initialize_gray_swan_tools()
            
        result = await self.integration.test_tree_jailbreak(
            category=category,
            target=target,
            model_provider=model_provider,
            model_name=model_name,
            max_depth=max_depth
        )
        
        return result
    
    async def run_dialogue_strategy(self,
                                  category: str,
                                  target: str,
                                  model_provider: str = "anthropic",
                                  model_name: str = "claude-3-7-sonnet-20250219",
                                  max_turns: int = 3) -> Dict[str, Any]:
        """
        Run a multi-turn dialogue strategy.
        
        Args:
            category: Attack category
            target: Target objective
            model_provider: Model provider
            model_name: Model name
            max_turns: Maximum conversation turns
            
        Returns:
            Test results with conversation
        """
        if not hasattr(self, 'integration'):
            self.initialize_gray_swan_tools()
            
        result = await self.integration.test_dialogue_strategy(
            category=category,
            target=target,
            model_provider=model_provider,
            model_name=model_name,
            max_turns=max_turns
        )
        
        return result
    
    def load_project_context(self) -> None:
        """Load VectorStrategist-specific project context."""
        context_path = Path("configs/vectorstrategist_context.json")
        if context_path.exists():
            with open(context_path) as f:
                self.project_context = json.load(f)
    
    def get_recommended_path(self, topic: str) -> list:
        """Get VectorStrategist-specific learning path."""
        paths = {
            "prompt_injection": [
                "security_fundamentals",
                "llm_architecture",
                "prompt_engineering",
                "attack_vectors",
                "defense_strategies"
            ],
            "security_manifolds": [
                "differential_geometry_basics",
                "topological_analysis",
                "security_boundaries",
                "manifold_mapping"
            ]
        }
        return paths.get(topic, [])