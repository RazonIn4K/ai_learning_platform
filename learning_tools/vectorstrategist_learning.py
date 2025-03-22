# vectorstrategist_learning.py
"""
Specific script for VectorStrategist project learning.
This provides a simplified interface for common VectorStrategist-related learning tasks.
"""

import os
import sys
import argparse
from .smart_learning_agent import SmartLearningAgent

def vs_learn(query, project_context="learning_config/vectorstrategist_context.json"):
    """Shortcut for learning about VectorStrategist topics."""
    agent = SmartLearningAgent()
    
    # Load project context
    if os.path.exists(project_context):
        agent.load_project_context(project_context)
    else:
        print(f"Warning: Project context file not found at {project_context}")
        print("Proceeding without project context...")
    
    # Process the learning query
    response = agent.learn(query)
    
    # Print the results
    if response.get('discovered_topics'):
        print("\n===== Relevant Topics =====")
        for idx, topic in enumerate(response['discovered_topics']):
            print(f"{idx+1}. {topic['name']} (Relevance: {topic['relevance']})")
    
    if response.get('learning_path'):
        print("\n===== Learning Path for VectorStrategist =====")
        for idx, item in enumerate(response['learning_path']):
            print(f"\n{idx+1}. {item.get('name', item.get('topic', 'Unknown'))}")
            for key, value in item.items():
                if key not in ['name', 'topic'] and value:
                    if isinstance(value, list):
                        print(f"   {key.replace('_', ' ').title()}:")
                        for v in value:
                            print(f"     - {v}")
                    else:
                        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    return response

def main():
    parser = argparse.ArgumentParser(description='VectorStrategist Learning Helper')
    parser.add_argument('query', help='What you want to learn about')
    parser.add_argument('--context', default="learning_config/vectorstrategist_context.json", 
                       help='Path to project context file')
    
    args = parser.parse_args()
    vs_learn(args.query, args.context)

if __name__ == "__main__":
    main()