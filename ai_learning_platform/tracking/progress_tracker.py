import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Tracks learning progress and interactions."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_session = {
            'interactions': [],
            'progress': {}
        }
        
    def log_interaction(
        self,
        query: str,
        response: Dict[str, Any]
    ):
        """Log a learning interaction."""
        self.current_session['interactions'].append({
            'query': query,
            'response': response
        })
        
    def save_session(self):
        """Save the current session to storage."""
        try:
            session_file = self.storage_path / 'latest_session.json'
            with open(session_file, 'w') as f:
                json.dump(self.current_session, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session: {str(e)}")