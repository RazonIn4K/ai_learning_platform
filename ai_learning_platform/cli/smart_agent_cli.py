import argparse
import sys
from pathlib import Path

from ai_learning_platform.core.smart_learning_agent import SmartLearningAgent
from ..utils.config_loader import ConfigLoader

def main():
    parser = argparse.ArgumentParser(description='VectorStrategist Learning CLI')
    parser.add_argument('command', choices=['learn', 'setup', 'progress'])
    parser.add_argument('query', nargs='?', help='Learning query')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        agent = SmartLearningAgent()
        if args.command == 'learn':
            if not args.query:
                print("Error: Query required for learn command")
                sys.exit(1)
            result = agent.learn(args.query)
            print_results(result)
        elif args.command == 'progress':
            show_progress(agent)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
