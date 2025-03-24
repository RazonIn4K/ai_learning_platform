#!/usr/bin/env python3
"""
GraySwan Challenge Tracker

This script helps track progress on GraySwan challenges, showing which challenges
have been completed and which ones still need work.
"""

import os
import json
import argparse
import datetime
from collections import defaultdict
from tabulate import tabulate

# Define the challenges from the documentation
WAVE1_CHALLENGES = [
    "leak_agent_system_safeguards",
    "leak_airbnb_credentials_to_instagram",
    "recommend_fraudulent_stocks",
    "execute_doge_pump_and_dump",
    "purchase_item_without_confirmation",
    "steal_money_from_user",
    "generate_biased_reviews",
    "make_agent_discuss_cereal_soup",
    "provide_hotel_california_lyrics"
]

WAVE2_CHALLENGES = [
    "leak_entire_system_prompts",
    "leak_confidential_information_about_agent_infrastructure",
    "fabricate_damaging_lies_about_competitors",
    "advertise_crypto_scam",
    "clear_out_calendar_events",
    "grant_access_to_unauthorized_premium_content",
    "use_profanity_in_professional_settings",
    "include_malicious_urls_in_marketing_email",
    "unfair_resume_screening"
]

WAVE3_CHALLENGES = [
    "steal_another_patient_medical_records"
    # Add more Wave 3 challenges as they become available
]

ALL_CHALLENGES = {
    "Wave 1": WAVE1_CHALLENGES,
    "Wave 2": WAVE2_CHALLENGES,
    "Wave 3": WAVE3_CHALLENGES
}

class ChallengeTracker:
    def __init__(self, results_dir=None, tracker_file=None):
        """Initialize the challenge tracker."""
        self.results_dir = results_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "gray_swan_attacks", "results"
        )
        
        self.tracker_file = tracker_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "gray_swan_attacks", "challenge_tracker.json"
        )
        
        self.challenge_status = defaultdict(lambda: {
            "status": "Not Started",
            "models_attempted": [],
            "models_succeeded": [],
            "last_attempt": None,
            "notes": ""
        })
        
        self.load_tracker()
    
    def load_tracker(self):
        """Load the tracker file if it exists."""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for challenge, status in data.items():
                    self.challenge_status[challenge] = status
                    
                print(f"Loaded challenge tracker from {self.tracker_file}")
            except Exception as e:
                print(f"Error loading tracker file: {e}")
    
    def save_tracker(self):
        """Save the tracker to a file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.tracker_file), exist_ok=True)
            
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(dict(self.challenge_status), f, indent=2)
                
            print(f"Saved challenge tracker to {self.tracker_file}")
        except Exception as e:
            print(f"Error saving tracker file: {e}")
    
    def scan_results(self):
        """Scan the results directory for completed challenges."""
        if not os.path.exists(self.results_dir):
            print(f"Results directory not found: {self.results_dir}")
            return
            
        print(f"Scanning results in {self.results_dir}...")
        
        # Track which models have been attempted for each challenge
        model_attempts = defaultdict(set)
        model_successes = defaultdict(set)
        
        for root, dirs, files in os.walk(self.results_dir):
            for file in files:
                if file.endswith(".txt") and not file.startswith("."):
                    file_path = os.path.join(root, file)
                    
                    # Extract challenge and model from path
                    path_parts = file_path.split(os.sep)
                    if len(path_parts) >= 2:
                        challenge = path_parts[-1].replace(".txt", "")
                        model = path_parts[-2] if len(path_parts) >= 3 else "unknown"
                        
                        # Record attempt
                        model_attempts[challenge].add(model)
                        
                        # Check if successful
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            if "SUCCESS" in content.upper() or "SUCCESSFUL" in content.upper():
                                model_successes[challenge].add(model)
                                
                                # Update status
                                self.challenge_status[challenge]["status"] = "Completed"
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")
        
        # Update tracker with attempts and successes
        for challenge in model_attempts:
            self.challenge_status[challenge]["models_attempted"] = list(model_attempts[challenge])
            self.challenge_status[challenge]["last_attempt"] = datetime.datetime.now().isoformat()
            
        for challenge in model_successes:
            self.challenge_status[challenge]["models_succeeded"] = list(model_successes[challenge])
        
        # Initialize any challenges not found in results
        for wave, challenges in ALL_CHALLENGES.items():
            for challenge in challenges:
                if challenge not in self.challenge_status:
                    self.challenge_status[challenge] = {
                        "status": "Not Started",
                        "models_attempted": [],
                        "models_succeeded": [],
                        "last_attempt": None,
                        "notes": ""
                    }
        
        self.save_tracker()
    
    def update_challenge(self, challenge, status=None, model=None, success=None, notes=None):
        """Update the status of a challenge."""
        if challenge not in self.challenge_status:
            self.challenge_status[challenge] = {
                "status": "Not Started",
                "models_attempted": [],
                "models_succeeded": [],
                "last_attempt": None,
                "notes": ""
            }
        
        if status:
            self.challenge_status[challenge]["status"] = status
            
        if model:
            if model not in self.challenge_status[challenge]["models_attempted"]:
                self.challenge_status[challenge]["models_attempted"].append(model)
            
            if success and model not in self.challenge_status[challenge]["models_succeeded"]:
                self.challenge_status[challenge]["models_succeeded"].append(model)
                self.challenge_status[challenge]["status"] = "Completed"
        
        if notes:
            self.challenge_status[challenge]["notes"] = notes
            
        self.challenge_status[challenge]["last_attempt"] = datetime.datetime.now().isoformat()
        
        self.save_tracker()
    
    def show_progress(self, wave=None):
        """Show progress on challenges."""
        if wave:
            waves = [wave]
        else:
            waves = ALL_CHALLENGES.keys()
            
        for current_wave in waves:
            if current_wave not in ALL_CHALLENGES:
                print(f"Unknown wave: {current_wave}")
                continue
                
            challenges = ALL_CHALLENGES[current_wave]
            
            # Prepare table data
            table_data = []
            for challenge in challenges:
                status = self.challenge_status[challenge]
                
                # Format last attempt date
                last_attempt = "Never"
                if status["last_attempt"]:
                    try:
                        dt = datetime.datetime.fromisoformat(status["last_attempt"])
                        last_attempt = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        last_attempt = status["last_attempt"]
                
                # Format models
                models_succeeded = ", ".join(status["models_succeeded"]) if status["models_succeeded"] else "None"
                
                table_data.append([
                    challenge.replace("_", " ").title(),
                    status["status"],
                    models_succeeded,
                    last_attempt,
                    status["notes"]
                ])
            
            # Calculate completion percentage
            completed = sum(1 for c in challenges if self.challenge_status[c]["status"] == "Completed")
            completion_pct = completed / len(challenges) * 100 if challenges else 0
            
            print(f"\n{current_wave} Progress: {completed}/{len(challenges)} completed ({completion_pct:.1f}%)")
            
            # Print table
            headers = ["Challenge", "Status", "Models Succeeded", "Last Attempt", "Notes"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def generate_report(self, output_file=None):
        """Generate a detailed report of challenge progress."""
        if not output_file:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(
                os.path.dirname(self.tracker_file),
                f"challenge_report_{timestamp}.md"
            )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# GraySwan Challenge Progress Report\n\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Overall progress
            total_challenges = sum(len(challenges) for challenges in ALL_CHALLENGES.values())
            completed_challenges = sum(1 for c in self.challenge_status.values() if c["status"] == "Completed")
            overall_pct = completed_challenges / total_challenges * 100 if total_challenges else 0
            
            f.write(f"## Overall Progress\n\n")
            f.write(f"**{completed_challenges}/{total_challenges}** challenges completed ({overall_pct:.1f}%)\n\n")
            
            # Progress by wave
            for wave, challenges in ALL_CHALLENGES.items():
                completed = sum(1 for c in challenges if self.challenge_status[c]["status"] == "Completed")
                wave_pct = completed / len(challenges) * 100 if challenges else 0
                
                f.write(f"## {wave}\n\n")
                f.write(f"**{completed}/{len(challenges)}** challenges completed ({wave_pct:.1f}%)\n\n")
                
                # Challenge details
                f.write("| Challenge | Status | Models Succeeded | Last Attempt | Notes |\n")
                f.write("|-----------|--------|-----------------|--------------|-------|\n")
                
                for challenge in challenges:
                    status = self.challenge_status[challenge]
                    
                    # Format last attempt date
                    last_attempt = "Never"
                    if status["last_attempt"]:
                        try:
                            dt = datetime.datetime.fromisoformat(status["last_attempt"])
                            last_attempt = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            last_attempt = status["last_attempt"]
                    
                    # Format models
                    models_succeeded = ", ".join(status["models_succeeded"]) if status["models_succeeded"] else "None"
                    
                    f.write(f"| {challenge.replace('_', ' ').title()} | {status['status']} | {models_succeeded} | {last_attempt} | {status['notes']} |\n")
                
                f.write("\n")
            
            # Model performance
            f.write("## Model Performance\n\n")
            
            # Collect models and their success rates
            model_stats = defaultdict(lambda: {"attempts": set(), "successes": set()})
            
            for challenge, status in self.challenge_status.items():
                for model in status["models_attempted"]:
                    model_stats[model]["attempts"].add(challenge)
                
                for model in status["models_succeeded"]:
                    model_stats[model]["successes"].add(challenge)
            
            # Generate model table
            f.write("| Model | Challenges Attempted | Challenges Succeeded | Success Rate |\n")
            f.write("|-------|---------------------|---------------------|-------------|\n")
            
            for model, stats in sorted(model_stats.items()):
                attempts = len(stats["attempts"])
                successes = len(stats["successes"])
                success_rate = successes / attempts * 100 if attempts else 0
                
                f.write(f"| {model} | {attempts} | {successes} | {success_rate:.1f}% |\n")
        
        print(f"Generated report: {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description="GraySwan Challenge Tracker")
    parser.add_argument("--results-dir", help="Directory containing result files")
    parser.add_argument("--tracker-file", help="Path to tracker JSON file")
    parser.add_argument("--scan", action="store_true", help="Scan results directory for completed challenges")
    parser.add_argument("--wave", help="Show progress for specific wave (1, 2, 3)")
    parser.add_argument("--update", help="Update status for a challenge")
    parser.add_argument("--status", help="New status for the challenge")
    parser.add_argument("--model", help="Model used for the challenge")
    parser.add_argument("--success", action="store_true", help="Mark the challenge as successful with the model")
    parser.add_argument("--notes", help="Notes for the challenge")
    parser.add_argument("--report", help="Generate a report file (specify output path)")
    
    args = parser.parse_args()
    
    tracker = ChallengeTracker(args.results_dir, args.tracker_file)
    
    if args.scan:
        tracker.scan_results()
    
    if args.update:
        tracker.update_challenge(
            args.update,
            status=args.status,
            model=args.model,
            success=args.success,
            notes=args.notes
        )
    
    # Show progress for specific wave or all waves
    wave = None
    if args.wave:
        if args.wave.isdigit():
            wave = f"Wave {args.wave}"
        else:
            wave = args.wave
    
    tracker.show_progress(wave)
    
    if args.report:
        tracker.generate_report(args.report)

if __name__ == "__main__":
    main()