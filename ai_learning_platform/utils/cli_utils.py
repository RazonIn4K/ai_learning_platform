# ai_learning_platform/utils/cli_utils.py
import json
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def print_results(response: Dict[str, Any]) -> None:
    """Format and print learning session results."""
    print("\nResponse:")
    print(response.get("content", "No content available"))
    
    # Print learning path if available
    if "learning_path" in response and response["learning_path"]:
        print("\nLearning Path:")
        for i, step in enumerate(response["learning_path"], 1):
            print(f"{i}. {step.get('title', 'Unknown step')}")
            print(f"   {step.get('description', 'No description')}")
            if 'estimated_duration' in step:
                print(f"   Estimated duration: {step['estimated_duration']}")
            print()

def show_progress() -> None:
    """Display learning progress from saved data."""
    try:
        # Load the latest session data
        progress_path = Path("data/progress/latest_session.json")
        if not progress_path.exists():
            print("No progress data available yet. Complete a learning session first.")
            return
            
        with open(progress_path, "r") as f:
            progress_data = json.load(f)
            
        print("\n--- Learning Progress ---")
        print(f"Last session: {progress_data.get('timestamp', 'Unknown')}")
        print(f"Topics covered: {', '.join(progress_data.get('topics_covered', ['None']))}")
        
        if 'mastery_levels' in progress_data:
            print("\nTopic Mastery:")
            for topic, level in progress_data['mastery_levels'].items():
                print(f"- {topic}: {level}")
    except Exception as e:
        print(f"Error loading progress data: {str(e)}")

def show_metrics(metrics: Dict[str, Any]) -> None:
    """Display model metrics."""
    print("\nModel Metrics:")
    for metric_name, value in metrics.items():
        print(f"{metric_name}: {value}")

def print_benchmark_results(results: Dict[str, Any]) -> None:
    """Format and print benchmark results."""
    print("\nBenchmark Results:")
    for provider, metrics in results.items():
        print(f"\n{provider}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")

def get_user_rating() -> int:
    """Get user rating input."""
    while True:
        try:
            rating = int(input("Please rate the response (1-5): "))
            if 1 <= rating <= 5:
                return rating
            print("Rating must be between 1 and 5")
        except ValueError:
            print("Please enter a valid number between 1 and 5")
