# setup_learning_system.py
"""
Setup script for the Smart Learning Agent.
This script checks that all necessary files are in place and creates the required directories.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from ai_learning_platform.utils.env_manager import EnvManager

def setup_directories() -> Dict[str, Path]:
    """Create necessary directories."""
    dirs = {
        'config': Path('configs'),
        'learning_config': Path('learning_config'),
        'data': Path('learning_data'),
        'workspace': Path('workspace_data'),
        'logs': Path('logs')
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
        
    return dirs

def create_config_files(dirs: Dict[str, Path]) -> None:
    """Create necessary configuration files."""
    # Create vectorstrategist context
    vs_context = {
        "project_name": "VectorStrategist",
        "project_description": "A framework combining differential geometry, topology, causal inference, and category theory to analyze AI security vulnerabilities",
        "focus_areas": [
            "Red teaming competitions",
            "Prompt injection attacks",
            "Adversarial machine learning",
            "Security manifold analysis",
            "Large language model vulnerability assessment"
        ],
        "components": [
            {
                "name": "Security Manifold Engine",
                "description": "Uses differential geometry and topological data analysis to map security boundaries in AI systems",
                "technologies": ["GEF", "giotto-tda", "GUDHI"]
            },
            # ... other components ...
        ]
    }
    
    for config_dir in [dirs['config'], dirs['learning_config']]:
        with open(config_dir / 'vectorstrategist_context.json', 'w') as f:
            json.dump(vs_context, f, indent=2)

def main():
    """Main setup function."""
    try:
        # Initialize environment
        env_manager = EnvManager()
        
        # Create directories
        dirs = setup_directories()
        print("✓ Created necessary directories")
        
        # Create configuration files
        create_config_files(dirs)
        print("✓ Created configuration files")
        
        print("\nSetup completed successfully!")
        print("\nUsage instructions:")
        print("1. To learn with VectorStrategist context:")
        print("   vs-learn --project learning_config/vectorstrategist_context.json learn \"Your query here\"")
        print("\n2. To track your progress:")
        print("   vs-learn progress \"Topic name\"")
        print("\n3. To get recommendations:")
        print("   vs-learn recommend")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    main()
