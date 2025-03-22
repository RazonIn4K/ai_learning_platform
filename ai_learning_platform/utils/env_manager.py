import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

class EnvManager:
    """Manages environment variables and configuration."""
    
    REQUIRED_VARS = {
        'ANTHROPIC_API_KEY': 'Anthropic API key for Claude models',
        'OPENAI_API_KEY': 'OpenAI API key for GPT models',
        'GOOGLE_API_KEY': 'Google API key for Gemini models'
    }
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize environment manager."""
        self.env_file = env_file or '.env'
        self._load_environment()
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        env_path = Path(self.env_file)
        if env_path.exists():
            load_dotenv(env_path)
        
        # Validate required environment variables
        missing_vars = []
        for var, description in self.REQUIRED_VARS.items():
            if not os.getenv(var):
                missing_vars.append(f"{var} ({description})")
        
        if missing_vars:
            self._create_env_template()
            raise EnvironmentError(
                f"Missing required environment variables:\n"
                f"{chr(10).join(missing_vars)}\n"
                f"Please set these in your {self.env_file} file."
            )
    
    def _create_env_template(self) -> None:
        """Create a template .env file if it doesn't exist."""
        if not Path(self.env_file).exists():
            with open(self.env_file, 'w') as f:
                f.write("# VectorStrategist Environment Configuration\n\n")
                for var, description in self.REQUIRED_VARS.items():
                    f.write(f"# {description}\n{var}=your-key-here\n\n")