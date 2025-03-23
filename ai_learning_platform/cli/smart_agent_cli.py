# ai_learning_platform/cli/smart_agent_cli.py

import argparse
import sys
import asyncio
import logging
from typing import Dict, Any

from ai_learning_platform.benchmark.benchmarker import Benchmarker
from ai_learning_platform.workspace.workspace_factory import WorkspaceFactory
from ai_learning_platform.utils.env_setup import EnvironmentSetup
from ai_learning_platform.utils.config_manager import ConfigManager
from ai_learning_platform.models.enhanced_model_manager import EnhancedModelManager
from ai_learning_platform.agents.agent_model_adapter import AgentModelAdapter
from ai_learning_platform.utils.exceptions import (
    RateLimitError,
    TokenLimitError,
    CredentialError,
    ModelError,
    ConfigurationError
)
from ai_learning_platform.utils.cli_utils import (
    print_results,
    show_progress,
    show_metrics,
    get_user_rating,
    print_benchmark_results  # Add this if not already defined in cli_utils.py
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def learn_command(query: str, args):
    """Execute the learn command."""
    try:
        # Set up environment
        env_setup = EnvironmentSetup()
        
        # Create workspace
        workspace = WorkspaceFactory.create_workspace(
            model_provider=args.provider,
            model_name=args.model,
            use_camel=args.use_camel,
            use_openrouter=args.use_openrouter
        )
        
        # Process the query
        response = await workspace.process_learning_session(query)
        return response
    
    except Exception as e:
        logger.error(f"Error during learning: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }

async def handle_command(args, config_manager, model_manager):
    """Handles the execution of a specific command."""
    if args.command == 'learn':
        if not args.query:
            print("Error: Query required for learn command", file=sys.stderr)
            sys.exit(1)
        result = await learn_command(args.query, args)

        # Handle result as needed
        if result.get('status') == 'error':
            print(f"Error: {result.get('message', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
        else:
            cli_utils.print_results(result) # Use the utility function

    elif args.command == 'progress':
        cli_utils.show_progress() # Use the utility function

    elif args.command == 'setup':
        env_setup = EnvironmentSetup()
        providers = env_setup.get_available_providers()

        print("\nAvailable Providers:")
        for provider, available in providers.items():
            status = "✅ Available" if available else "❌ Not configured"
            print(f"- {provider}: {status}")

        print(f"\nDefault provider: {env_setup.suggest_default_provider()}")
        print("\nTo configure providers, edit the config file.")

    elif args.command == 'validate_config':
        if config_manager.validate_config():
            print("Configuration is valid.")
        else:
            print("Configuration is invalid. See logs for details.", file=sys.stderr)
            sys.exit(1)

    elif args.command == 'metrics':
        cli_utils.show_metrics(model_manager.metrics) # Use the utility function
    
    elif args.command == 'rate_response':
        if not args.query:
            print("Error: query is required to rate a response", file=sys.stderr)
            sys.exit(1)
        rating = cli_utils.get_user_rating() # Use the utility function
        print(f"Thank you for your rating: {rating}")

async def main_async():
    """Async main function."""
    parser = argparse.ArgumentParser(description='AI Learning Platform CLI')
    parser.add_argument('command', choices=['learn', 'setup', 'progress', 'validate_config', 'metrics', 'rate_response', 'benchmark', 'role_play'])
    parser.add_argument('query', nargs='?', help='Learning query')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--provider', choices=['anthropic', 'openai', 'google', 'openrouter', 'camel'], help='Model provider')
    parser.add_argument('--model', help='Model name')
    parser.add_argument('--profile', help='Config profile to use')
    parser.add_argument('--no-cache', action='store_true', help='Disable response caching')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark')
    parser.add_argument('--role', help='Role for CAMeL-AI role playing')
    parser.add_argument('--assistant-role', help='Assistant role for CAMeL-AI role playing')
    parser.add_argument('--user-role', help='User role for CAMeL-AI role playing')
    
    args = parser.parse_args()
    
    try:
        # Initialize config manager
        config_manager = ConfigManager()
        
        # Set active profile if specified
        if args.profile:
            config_manager.set_profile(args.profile)
            
        # Initialize model manager
        model_manager = EnhancedModelManager(config_manager)
        
        # Get model settings
        provider = args.provider or config_manager.get_config().get('model_parameters', {}).get('provider', 'anthropic')
        model_name = args.model or config_manager.get_config().get('model_parameters', {}).get('model_name', 'claude-3-7-sonnet-20250219')
        
        if args.command == 'learn':
            if not args.query:
                print("Error: Query required for learn command")
                sys.exit(1)
                
            # Create agent adapter
            agent_adapter = AgentModelAdapter(model_manager)
            
            # Initialize workspace
            workspace = WorkspaceFactory().create_workspace()
            
            # Process query
            response = workspace.process_learning_session(
                args.query,
                provider=provider,
                model_name=model_name,
                use_cache=not args.no_cache
            )
            
            print_results(response)
            
        elif args.command == 'role_play':
            if not args.query:
                print("Error: Query required for role_play command")
                sys.exit(1)
                
            # Create agent adapter
            agent_adapter = AgentModelAdapter(model_manager)
            
            # Override provider to camel
            provider = 'camel'
            
            # Check if roles are provided
            if args.assistant_role and args.user_role:
                # Use dual role playing
                response = asyncio.run(agent_adapter.generate_role_playing_response(
                    agent_type="domain_expert",
                    prompt=args.query,
                    assistant_role=args.assistant_role,
                    user_role=args.user_role,
                    model_name=model_name
                ))
            elif args.role:
                # Use single role playing
                response = asyncio.run(model_manager.generate_response(
                    prompt=args.query,
                    provider=provider,
                    model_name=model_name,
                    role=args.role
                ))
            else:
                print("Error: Either --role or both --assistant-role and --user-role must be provided")
                sys.exit(1)
                
            print_results(response)
            
        elif args.command == 'progress':
            show_progress()
            
        elif args.command == 'metrics':
            show_metrics(model_manager.metrics)
            
        elif args.command == 'validate_config':
            valid = config_manager.validate_config()
            if valid:
                print("Configuration is valid.")
            else:
                print("Configuration is invalid. See logs for details.")
                
        elif args.command == 'rate_response':
            if not args.query:
                print("Error: Query required for rate_response command")
                sys.exit(1)
                
            # Display rating dialog
            rating = get_user_rating()
            print(f"Thank you for your rating: {rating}")
            
        elif args.command == 'benchmark':
            # Run benchmark
            benchmarker = Benchmarker(model_manager)
            
            # If provider is specified, benchmark that provider
            if args.provider:
                print(f"Benchmarking {args.provider}/{args.model}...")
                result = asyncio.run(benchmarker.benchmark_provider(
                    provider=args.provider,
                    model_name=args.model,
                    use_cache=not args.no_cache
                ))
                
                print_benchmark_results(result)
            else:
                # Benchmark all available providers
                print("Benchmarking all available providers...")
                providers = [
                    {"provider": "anthropic", "model": "claude-3-7-sonnet-20250219"},
                    {"provider": "openai", "model": "gpt-4"},
                    {"provider": "google", "model": "gemini-pro"},
                    {"provider": "openrouter", "model": "anthropic/claude-3-opus"},
                    {"provider": "camel", "model": "camel-base"}
                ]
                
                result = asyncio.run(benchmarker.compare_providers(providers))
                print_benchmark_results(result)
                
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    """CLI main entry point."""
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
