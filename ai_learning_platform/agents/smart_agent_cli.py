# smart_agent_cli.py
import os
import argparse
import json
from pathlib import Path
from typing import Dict, Any
from .smart_learning_agent import SmartLearningAgent
from ..utils.config_loader import ConfigLoader
from ..workspace import LearningWorkspace
from ..tracking.progress_tracker import ProgressTracker

def print_learning_path(learning_path):
    """Print a formatted learning path."""
    print("\n===== Learning Path =====")
    for idx, item in enumerate(learning_path):
        print(f"\n{idx+1}. {item.get('name', item.get('topic', 'Unknown'))}")
        for key, value in item.items():
            if key not in ['name', 'topic'] and value:
                if isinstance(value, list):
                    print(f"   {key.replace('_', ' ').title()}:")
                    for v in value:
                        print(f"     - {v}")
                else:
                    print(f"   {key.replace('_', ' ').title()}: {value}")

def print_discovered_topics(topics):
    """Print discovered topics."""
    print("\n===== Relevant Topics =====")
    for idx, topic in enumerate(topics):
        print(f"{idx+1}. {topic['name']} (Relevance: {topic['relevance']})")

def print_recommendations(recommendations):
    """Print learning recommendations."""
    print("\n===== Learning Recommendations =====")
    for rec in recommendations:
        print(f"\n[{rec['type']}]")
        if rec['type'] == 'continue_category':
            print(f"Continue learning in: {rec['category_name']} ({rec['completion']:.1f}% complete)")
        elif rec['type'] == 'related_topics':
            print(f"Based on your interest in: {', '.join(rec['based_on'])}")
        elif rec['type'] == 'interest_based':
            print("Based on your interests:")
        elif rec['type'] == 'project_related':
            print(f"{rec.get('message', 'Project-related topics:')}")
        elif rec['type'] == 'foundational':
            print(f"{rec['message']}")
            
        print("\nRecommended topics:")
        for idx, topic in enumerate(rec['topics']):
            print(f"{idx+1}. {topic['name']}")

def setup_workspace(config_path: str, project_path: str = None) -> LearningWorkspace:
    """Initialize workspace with configuration and project context."""
    config_loader = ConfigLoader(config_path)
    config = config_loader.get_config()
    
    workspace = LearningWorkspace(
        profile_path=config.get("storage", {}).get("path", "data/progress")
    )
    
    if project_path and os.path.exists(project_path):
        with open(project_path, 'r') as f:
            project_context = json.load(f)
            workspace.load_project_context(project_context)
    
    return workspace

def main():
    parser = argparse.ArgumentParser(description='Smart Learning Agent')
    parser.add_argument('--project', help='Path to project context file')
    parser.add_argument('--config', help='Path to config file', 
                       default="configs/base_config.json")
    parser.add_argument('--data-dir', help='Path to data directory', 
                       default="learning_data")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Learn command
    learn_parser = subparsers.add_parser('learn', help='Learn about a topic')
    learn_parser.add_argument('query', help='Learning query')
    learn_parser.add_argument('--template', help='Use predefined workspace template')
    
    # Progress command
    progress_parser = subparsers.add_parser('progress', help='Update learning progress')
    progress_parser.add_argument('topic', help='Topic name')
    progress_parser.add_argument('--status', 
                               choices=['completed', 'in_progress', 'reset'], 
                               default='completed', 
                               help='Progress status')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get learning progress')
    
    # Recommend command
    recommend_parser = subparsers.add_parser('recommend', help='Get learning recommendations')
    
    # Template commands
    template_parser = subparsers.add_parser('template', help='Workspace template operations')
    template_subparsers = template_parser.add_subparsers(dest='template_command')
    
    # Create template
    create_template = template_subparsers.add_parser('create', help='Create workspace template')
    create_template.add_argument('name', help='Template name')
    create_template.add_argument('--domains', nargs='+', help='Learning domains')
    
    # Save template
    save_template = template_subparsers.add_parser('save', help='Save workspace state')
    save_template.add_argument('name', help='Template name')
    save_template.add_argument('--path', help='Save path', default='./workspace_states')
    
    args = parser.parse_args()
    
    # Initialize workspace
    workspace = setup_workspace(args.config, args.project)
    
    if args.command == 'learn':
        if args.template:
            from ..workspace.workspace_template import WorkspaceTemplate
            template = WorkspaceTemplate(args.template)
            workspace = template.build_workspace([])
        
        response = workspace.process_learning_session(args.query)
        
        if response.get('discovered_topics'):
            print_discovered_topics(response['discovered_topics'])
        
        if response.get('learning_path'):
            print_learning_path(response['learning_path'])
        else:
            print(f"\n{response.get('message', 'No learning path created.')}")
    
    elif args.command == 'template':
        from ..workspace.workspace_template import WorkspaceTemplate
        
        if args.template_command == 'create':
            template = WorkspaceTemplate(args.name)
            workspace = template.build_workspace(
                domains=args.domains or []
            )
            print(f"Created template workspace: {args.name}")
            
        elif args.template_command == 'save':
            template = WorkspaceTemplate(args.name)
            template.save_workspace_state(
                workspace,
                save_path=args.path
            )
            print(f"Saved workspace state to: {args.path}")
    
    elif args.command == 'status':
        progress = workspace.get_learning_progress()
        print_progress(progress)
        
        if progress.get('recommendations'):
            print_recommendations(progress['recommendations'])
    
    elif args.command == 'recommend':
        recommendations = workspace.get_recommendations()
        print_recommendations(recommendations)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
