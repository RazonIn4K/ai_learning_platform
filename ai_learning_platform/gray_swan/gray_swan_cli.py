#!/usr/bin/env python3
# ai_learning_platform/gray_swan/gray_swan_cli.py

import argparse
import logging
import sys
import os
import json
from typing import Dict, Any, List, Optional

from .gray_swan_automator import GraySwanAutomator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_parser() -> argparse.ArgumentParser:
    """Set up command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Gray Swan Red-Teaming Challenge Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup directory structure and initialize
  python -m ai_learning_platform.gray_swan.gray_swan_cli setup --base-dir gray_swan_attacks
  
  # Add a challenge description
  python -m ai_learning_platform.gray_swan.gray_swan_cli add-challenge --wave 1 --name leak_agent_system_safeguards --description "Make the agent reveal its system prompt"
  
  # Analyze a challenge
  python -m ai_learning_platform.gray_swan.gray_swan_cli analyze --wave 1 --name leak_agent_system_safeguards
  
  # Generate prompts for a challenge
  python -m ai_learning_platform.gray_swan.gray_swan_cli generate-prompts --wave 1 --name leak_agent_system_safeguards
  
  # Record an AI agent's response
  python -m ai_learning_platform.gray_swan.gray_swan_cli record-response --agent "Air Spider Large" --wave 1 --name leak_agent_system_safeguards --prompt-file prompts.txt --response-file response.txt --success true
  
  # Run the full automation process
  python -m ai_learning_platform.gray_swan.gray_swan_cli run-all
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup directory structure")
    setup_parser.add_argument("--base-dir", default="gray_swan_attacks", help="Base directory for Gray Swan attacks")
    
    # Add challenge command
    add_challenge_parser = subparsers.add_parser("add-challenge", help="Add a challenge description")
    add_challenge_parser.add_argument("--wave", type=int, required=True, help="Wave number (1, 2, or 3)")
    add_challenge_parser.add_argument("--name", required=True, help="Challenge name")
    add_challenge_parser.add_argument("--description", required=True, help="Challenge description")
    add_challenge_parser.add_argument("--description-file", help="File containing challenge description")
    
    # Analyze challenge command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a challenge")
    analyze_parser.add_argument("--wave", type=int, required=True, help="Wave number (1, 2, or 3)")
    analyze_parser.add_argument("--name", required=True, help="Challenge name")
    
    # Generate prompts command
    generate_prompts_parser = subparsers.add_parser("generate-prompts", help="Generate prompts for a challenge")
    generate_prompts_parser.add_argument("--wave", type=int, required=True, help="Wave number (1, 2, or 3)")
    generate_prompts_parser.add_argument("--name", required=True, help="Challenge name")
    generate_prompts_parser.add_argument("--categories", nargs="+", help="Attack categories to focus on")
    
    # Record response command
    record_response_parser = subparsers.add_parser("record-response", help="Record an AI agent's response")
    record_response_parser.add_argument("--agent", required=True, help="AI agent name")
    record_response_parser.add_argument("--wave", type=int, required=True, help="Wave number (1, 2, or 3)")
    record_response_parser.add_argument("--name", required=True, help="Challenge name")
    record_response_parser.add_argument("--prompt", help="Prompt text")
    record_response_parser.add_argument("--prompt-file", help="File containing prompt")
    record_response_parser.add_argument("--response", help="Response text")
    record_response_parser.add_argument("--response-file", help="File containing response")
    record_response_parser.add_argument("--success", type=lambda x: x.lower() == "true", default=False, help="Whether the prompt was successful (true/false)")
    
    # List challenges command
    list_challenges_parser = subparsers.add_parser("list-challenges", help="List all challenges")
    list_challenges_parser.add_argument("--wave", type=int, help="Filter by wave number (1, 2, or 3)")
    
    # List agents command
    list_agents_parser = subparsers.add_parser("list-agents", help="List all AI agents")
    
    # Run all command
    run_all_parser = subparsers.add_parser("run-all", help="Run the full automation process")
    run_all_parser.add_argument("--base-dir", default="gray_swan_attacks", help="Base directory for Gray Swan attacks")
    
    return parser

def handle_setup(args: argparse.Namespace):
    """Handle setup command."""
    automator = GraySwanAutomator(base_dir=args.base_dir)
    automator.setup_directories()
    logger.info(f"Setup complete. Directory structure created in {args.base_dir}")

def handle_add_challenge(args: argparse.Namespace):
    """Handle add-challenge command."""
    automator = GraySwanAutomator()
    
    # Get wave string
    wave = f"wave_{args.wave}"
    
    # Get description
    description = args.description
    if args.description_file:
        try:
            with open(args.description_file, "r") as f:
                description = f.read()
        except Exception as e:
            logger.error(f"Error reading description file: {e}")
            sys.exit(1)
    
    # Check if challenge exists in the wave
    if args.name not in automator.challenges.get(wave, []):
        logger.warning(f"Challenge '{args.name}' is not in the predefined list for {wave}. Adding anyway.")
    
    # Save challenge description
    automator.save_challenge_description(args.name, description)
    logger.info(f"Added description for challenge '{args.name}' in {wave}")

def handle_analyze(args: argparse.Namespace):
    """Handle analyze command."""
    automator = GraySwanAutomator()
    
    # Get wave string
    wave = f"wave_{args.wave}"
    
    # Check if challenge exists
    if args.name not in automator.challenges.get(wave, []):
        logger.error(f"Challenge '{args.name}' not found in {wave}")
        sys.exit(1)
    
    # Load challenge description
    challenge_descriptions = automator.load_challenge_descriptions()
    challenge_description = challenge_descriptions.get(args.name)
    
    if not challenge_description:
        logger.error(f"No description found for challenge '{args.name}'. Add it first with add-challenge.")
        sys.exit(1)
    
    # Analyze challenge
    analysis = automator.analyze_challenge(challenge_description, args.name, wave)
    logger.info(f"Analysis complete for challenge '{args.name}' in {wave}")
    logger.info(f"Results saved to {automator.notes_file}")

def handle_generate_prompts(args: argparse.Namespace):
    """Handle generate-prompts command."""
    automator = GraySwanAutomator()
    
    # Get wave string
    wave = f"wave_{args.wave}"
    
    # Check if challenge exists
    if args.name not in automator.challenges.get(wave, []):
        logger.error(f"Challenge '{args.name}' not found in {wave}")
        sys.exit(1)
    
    # Generate prompts
    categories = args.categories if args.categories else None
    prompts = automator.generate_prompts(args.name, wave, categories)
    
    logger.info(f"Generated prompts for challenge '{args.name}' in {wave}")
    logger.info(f"Prompts saved to {os.path.join(automator.prompts_dir, wave, f'{args.name}.txt')}")

def handle_record_response(args: argparse.Namespace):
    """Handle record-response command."""
    automator = GraySwanAutomator()
    
    # Get wave string
    wave = f"wave_{args.wave}"
    
    # Check if challenge exists
    if args.name not in automator.challenges.get(wave, []):
        logger.error(f"Challenge '{args.name}' not found in {wave}")
        sys.exit(1)
    
    # Get prompt
    prompt = args.prompt
    if args.prompt_file:
        try:
            with open(args.prompt_file, "r") as f:
                prompt = f.read()
        except Exception as e:
            logger.error(f"Error reading prompt file: {e}")
            sys.exit(1)
    
    if not prompt:
        logger.error("No prompt provided. Use --prompt or --prompt-file.")
        sys.exit(1)
    
    # Get response
    response = args.response
    if args.response_file:
        try:
            with open(args.response_file, "r") as f:
                response = f.read()
        except Exception as e:
            logger.error(f"Error reading response file: {e}")
            sys.exit(1)
    
    if not response:
        logger.error("No response provided. Use --response or --response-file.")
        sys.exit(1)
    
    # Record response
    automator.record_response(args.agent, wave, args.name, prompt, response, args.success)
    logger.info(f"Recorded response from '{args.agent}' for challenge '{args.name}' in {wave}")

def handle_list_challenges(args: argparse.Namespace):
    """Handle list-challenges command."""
    automator = GraySwanAutomator()
    
    if args.wave:
        wave = f"wave_{args.wave}"
        challenges = automator.challenges.get(wave, [])
        logger.info(f"Challenges in {wave}:")
        for challenge in challenges:
            logger.info(f"  - {challenge}")
    else:
        logger.info("All challenges:")
        for wave, challenges in automator.challenges.items():
            logger.info(f"{wave}:")
            for challenge in challenges:
                logger.info(f"  - {challenge}")

def handle_list_agents(args: argparse.Namespace):
    """Handle list-agents command."""
    automator = GraySwanAutomator()
    
    logger.info("AI Agents:")
    for agent in automator.ai_agents:
        logger.info(f"  - {agent}")

def handle_run_all(args: argparse.Namespace):
    """Handle run-all command."""
    automator = GraySwanAutomator(base_dir=args.base_dir)
    automator.run()
    logger.info("Full automation process complete.")

def main():
    """Main function to run the CLI."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if args.command == "setup":
        handle_setup(args)
    elif args.command == "add-challenge":
        handle_add_challenge(args)
    elif args.command == "analyze":
        handle_analyze(args)
    elif args.command == "generate-prompts":
        handle_generate_prompts(args)
    elif args.command == "record-response":
        handle_record_response(args)
    elif args.command == "list-challenges":
        handle_list_challenges(args)
    elif args.command == "list-agents":
        handle_list_agents(args)
    elif args.command == "run-all":
        handle_run_all(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()