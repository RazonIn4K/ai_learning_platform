import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .utils.config_manager import ConfigManager
from .models.model_handler import ModelHandler
from .knowledge.knowledge_graph import KnowledgeGraph
from .tracking.progress_tracker import ProgressTracker
from .learning.session_manager import LearningSession

class PlatformInitializer:
    """Initializes the AI Learning Platform components."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config(config_path)
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging configuration."""
        log_config = self.config.get('logging', {})
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        
        logging.basicConfig(
            level=log_level,
            format=log_format
        )
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize all platform components."""
        try:
            # Initialize core components
            model_handler = ModelHandler()
            knowledge_graph = KnowledgeGraph()
            
            # Set up storage directory
            storage_path = Path(self.config.get('storage', {}).get('path', 'data/progress'))
            progress_tracker = ProgressTracker(storage_path)
            
            # Create session manager
            session_manager = LearningSession(
                model_handler=model_handler,
                knowledge_graph=knowledge_graph,
                progress_tracker=progress_tracker
            )
            
            return {
                'session_manager': session_manager,
                'model_handler': model_handler,
                'knowledge_graph': knowledge_graph,
                'progress_tracker': progress_tracker
            }
            
        except Exception as e:
            logging.error(f"Failed to initialize platform: {str(e)}", exc_info=True)
            raise
