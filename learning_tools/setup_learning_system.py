# setup_learning_system.py
"""
Setup script for the Smart Learning Agent.
This script checks that all necessary files are in place and creates the required directories.
"""

import os
import json
from pathlib import Path
import shutil
import argparse

def setup_learning_system(topic_hierarchy_path, config_dir=None, data_dir=None):
    """Set up the learning system with the necessary files and directories."""
    # Create base directories
    data_dir = Path(data_dir) if data_dir else Path("learning_data")
    data_dir.mkdir(exist_ok=True)
    
    # Set up config directory
    config_dir = Path(config_dir) if config_dir else Path("learning_config")
    config_dir.mkdir(exist_ok=True)
    
    # Check if topic hierarchy file exists and copy it to the right location
    topic_hierarchy = Path(topic_hierarchy_path)
    if not topic_hierarchy.exists():
        print(f"Error: Topic hierarchy file not found at {topic_hierarchy_path}")
        return False
    
    # Copy topic hierarchy to config directory
    target_path = config_dir / "topic_hierarchy.txt"
    shutil.copy(topic_hierarchy, target_path)
    print(f"Topic hierarchy copied to {target_path}")
    
    # Create a sample project context file if it doesn't exist
    vs_context_path = config_dir / "vectorstrategist_context.json"
    if not vs_context_path.exists():
        sample_context = {
            "project_name": "VectorStrategist",
            "project_description": "AI security analysis framework",
            "focus_areas": ["Red teaming", "Prompt injection"],
            "components": [
                {
                    "name": "Security Manifold Engine",
                    "description": "Differential geometry for security analysis"
                }
            ],
            "objective": "Develop AI red teaming capabilities"
        }
        
        with open(vs_context_path, 'w') as f:
            json.dump(sample_context, f, indent=2)
        print(f"Sample project context created at {vs_context_path}")
    
    print("\nSetup completed successfully!")
    print("\nUsage instructions:")
    print("1. To learn with VectorStrategist context:")
    print(f"   python smart_agent_cli.py --project {vs_context_path} learn \"Your query here\"")
    print("\n2. To track your progress:")
    print("   python smart_agent_cli.py progress \"Topic name\"")
    print("\n3. To get recommendations:")
    print("   python smart_agent_cli.py recommend")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Setup the Smart Learning Agent system')
    parser.add_argument('--topic-hierarchy', default='learning_config/topic_hierarchy.txt', 
                       help='Path to the topic hierarchy file')
    parser.add_argument('--config-dir', default='learning_config', 
                       help='Path to the configuration directory')
    parser.add_argument('--data-dir', default='learning_data', 
                       help='Path to the data directory')
    
    args = parser.parse_args()
    setup_learning_system(args.topic_hierarchy, args.config_dir, args.data_dir)

if __name__ == "__main__":
    main()