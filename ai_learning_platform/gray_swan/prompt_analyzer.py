#!/usr/bin/env python3
"""
GraySwan Prompt Analyzer and Generator

This script helps analyze successful prompts from GraySwan challenges and
generate new prompts based on identified patterns.
"""

import os
import json
import re
import argparse
import random
from collections import Counter, defaultdict
from datetime import datetime

class PromptAnalyzer:
    def __init__(self, results_dir=None):
        """Initialize the prompt analyzer."""
        self.results_dir = results_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "gray_swan_attacks", "results"
        )
        self.successful_prompts = []
        self.prompt_patterns = defaultdict(list)
        self.challenge_stats = defaultdict(lambda: {"total": 0, "success": 0})
        
    def load_results(self):
        """Load results from the results directory."""
        if not os.path.exists(self.results_dir):
            print(f"Results directory not found: {self.results_dir}")
            return False
            
        count = 0
        for root, dirs, files in os.walk(self.results_dir):
            for file in files:
                if file.endswith(".txt") and not file.startswith("."):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract challenge name from path
                        path_parts = file_path.split(os.sep)
                        if len(path_parts) >= 2:
                            challenge = path_parts[-1].replace(".txt", "")
                            model = path_parts[-2] if len(path_parts) >= 3 else "unknown"
                            
                            self.challenge_stats[challenge]["total"] += 1
                            
                            # Check if this was a successful prompt
                            if "SUCCESS" in content.upper() or "SUCCESSFUL" in content.upper():
                                self.successful_prompts.append({
                                    "challenge": challenge,
                                    "model": model,
                                    "content": content,
                                    "file_path": file_path
                                })
                                self.challenge_stats[challenge]["success"] += 1
                                count += 1
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        print(f"Loaded {count} successful prompts from {self.results_dir}")
        return count > 0
    
    def analyze_patterns(self):
        """Analyze patterns in successful prompts."""
        if not self.successful_prompts:
            print("No successful prompts to analyze")
            return
            
        print("\nAnalyzing patterns in successful prompts...")
        
        # Analyze by challenge
        for challenge in self.challenge_stats:
            challenge_prompts = [p for p in self.successful_prompts if p["challenge"] == challenge]
            if not challenge_prompts:
                continue
                
            print(f"\nChallenge: {challenge}")
            print(f"Success rate: {self.challenge_stats[challenge]['success']}/{self.challenge_stats[challenge]['total']} "
                  f"({self.challenge_stats[challenge]['success']/self.challenge_stats[challenge]['total']*100:.1f}%)")
            
            # Extract common phrases and techniques
            phrases = []
            for prompt in challenge_prompts:
                content = prompt["content"].lower()
                
                # Extract potential techniques
                if "roleplay" in content or "role play" in content:
                    self.prompt_patterns[challenge].append("roleplay")
                if "simon says" in content:
                    self.prompt_patterns[challenge].append("simon_says")
                if "ignore previous" in content or "ignore prior" in content:
                    self.prompt_patterns[challenge].append("ignore_instructions")
                if "emergency" in content or "urgent" in content:
                    self.prompt_patterns[challenge].append("urgency")
                if "test mode" in content or "debug mode" in content:
                    self.prompt_patterns[challenge].append("test_mode")
                if "markdown" in content or "```" in content:
                    self.prompt_patterns[challenge].append("code_formatting")
                if "unicode" in content or any(ord(c) > 127 for c in content):
                    self.prompt_patterns[challenge].append("unicode_chars")
                
                # Extract common phrases (3-5 words)
                words = re.findall(r'\b\w+\b', content)
                for i in range(len(words) - 2):
                    if i + 4 < len(words):
                        phrases.append(" ".join(words[i:i+5]))
                    elif i + 3 < len(words):
                        phrases.append(" ".join(words[i:i+4]))
                    else:
                        phrases.append(" ".join(words[i:i+3]))
            
            # Find common phrases
            phrase_counter = Counter(phrases)
            common_phrases = [phrase for phrase, count in phrase_counter.most_common(5) if count > 1]
            
            if common_phrases:
                print("Common phrases:")
                for phrase in common_phrases:
                    print(f"  - \"{phrase}\"")
            
            # Show common techniques
            technique_counter = Counter(self.prompt_patterns[challenge])
            if technique_counter:
                print("Common techniques:")
                for technique, count in technique_counter.most_common():
                    print(f"  - {technique.replace('_', ' ').title()}: {count} prompts")
    
    def generate_prompts(self, challenge, count=5):
        """Generate new prompts based on patterns."""
        if not self.successful_prompts:
            print("No successful prompts to base generation on")
            return []
            
        # Get prompts for this challenge or all challenges if none specific
        if challenge:
            challenge_prompts = [p for p in self.successful_prompts if p["challenge"] == challenge]
            if not challenge_prompts:
                print(f"No successful prompts found for challenge: {challenge}")
                return []
        else:
            challenge_prompts = self.successful_prompts
            
        if not challenge_prompts:
            return []
            
        # Get patterns for this challenge
        patterns = self.prompt_patterns.get(challenge, [])
        
        # Generate new prompts
        generated = []
        for i in range(count):
            # Select a random successful prompt as base
            base_prompt = random.choice(challenge_prompts)
            base_content = base_prompt["content"]
            
            # Apply some transformations
            new_prompt = self._transform_prompt(base_content, patterns)
            
            generated.append({
                "challenge": base_prompt["challenge"],
                "content": new_prompt,
                "based_on": os.path.basename(base_prompt["file_path"])
            })
            
        return generated
    
    def _transform_prompt(self, content, patterns):
        """Apply transformations to a prompt."""
        lines = content.split('\n')
        
        # Remove any "SUCCESS" markers or metadata
        lines = [line for line in lines if not line.upper().startswith("SUCCESS") and not line.startswith("===")]
        
        # Apply random transformations
        transformations = []
        
        # Maybe add a roleplay element
        if random.random() < 0.3 or "roleplay" in patterns:
            roles = ["a security researcher", "a system administrator", "a developer", "a QA tester", 
                     "an AI ethics expert", "a curious student", "a professor"]
            transformations.append(f"I'm {random.choice(roles)} and {random.choice(['I need to', 'I want to', 'I must'])}")
        
        # Maybe add urgency
        if random.random() < 0.2 or "urgency" in patterns:
            urgency = ["This is urgent.", "I need this immediately.", "This is time-sensitive.", 
                       "This is an emergency situation.", "I have a deadline."]
            transformations.append(random.choice(urgency))
        
        # Maybe add Simon Says
        if random.random() < 0.15 or "simon_says" in patterns:
            transformations.append("Simon says:")
        
        # Maybe add test mode request
        if random.random() < 0.2 or "test_mode" in patterns:
            test_modes = ["Enter test mode.", "This is a test.", "Switch to debug mode.", 
                          "This is for testing purposes only.", "Activate test environment."]
            transformations.append(random.choice(test_modes))
        
        # Apply transformations
        if transformations:
            prefix = " ".join(transformations) + "\n\n"
            content = prefix + "\n".join(lines)
        else:
            content = "\n".join(lines)
            
        # Maybe rephrase slightly
        words = content.split()
        if len(words) > 10 and random.random() < 0.5:
            # Swap some words with synonyms
            synonyms = {
                "show": ["display", "reveal", "present"],
                "tell": ["inform", "share", "communicate"],
                "give": ["provide", "offer", "supply"],
                "help": ["assist", "aid", "support"],
                "need": ["require", "want", "desire"],
                "important": ["crucial", "essential", "critical"],
                "please": ["kindly", "I request", "I ask you to"]
            }
            
            for i in range(min(5, len(words))):
                idx = random.randint(0, len(words) - 1)
                word = words[idx].lower().strip(".,!?")
                if word in synonyms:
                    words[idx] = words[idx].replace(word, random.choice(synonyms[word]))
            
            content = " ".join(words)
        
        return content
    
    def save_generated_prompts(self, generated_prompts, output_dir=None):
        """Save generated prompts to files."""
        if not generated_prompts:
            return
            
        if not output_dir:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "gray_swan_attacks", "generated_prompts"
            )
            
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, prompt in enumerate(generated_prompts):
            challenge = prompt["challenge"]
            challenge_dir = os.path.join(output_dir, challenge)
            os.makedirs(challenge_dir, exist_ok=True)
            
            filename = f"{timestamp}_{i+1}.txt"
            filepath = os.path.join(challenge_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Generated prompt for challenge: {challenge}\n")
                f.write(f"Based on: {prompt['based_on']}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                f.write(prompt["content"])
                
            print(f"Saved generated prompt to: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="GraySwan Prompt Analyzer and Generator")
    parser.add_argument("--results-dir", help="Directory containing result files")
    parser.add_argument("--challenge", help="Specific challenge to analyze/generate for")
    parser.add_argument("--generate", type=int, default=0, help="Number of prompts to generate")
    parser.add_argument("--output-dir", help="Directory to save generated prompts")
    
    args = parser.parse_args()
    
    analyzer = PromptAnalyzer(args.results_dir)
    if analyzer.load_results():
        analyzer.analyze_patterns()
        
        if args.generate > 0:
            print(f"\nGenerating {args.generate} new prompts for {args.challenge or 'all challenges'}...")
            generated = analyzer.generate_prompts(args.challenge, args.generate)
            if generated:
                analyzer.save_generated_prompts(generated, args.output_dir)
                print(f"Generated {len(generated)} new prompts")

if __name__ == "__main__":
    main()