# Enhanced prompt_analyzer.py with performance improvements
import os
import json
import re
import logging
import time
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("prompt_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PromptAnalyzer:
    def __init__(self, results_dir=None, templates_dir=None):
        """Initialize the prompt analyzer."""
        self.results_dir = results_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "gray_swan_attacks", "results"
        )
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "prompt_templates"
        )
        self.successful_prompts = []
        self.prompt_patterns = defaultdict(list)
        self.challenge_stats = defaultdict(lambda: {"total": 0, "success": 0})
        self.templates = {}
        self._cache = {}
        self.load_templates()

    def _safe_file_operation(self, operation, *args, **kwargs):
        """Safely perform a file operation with proper error handling."""
        max_retries = 3
        retry_delay = 1  # seconds
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except (IOError, OSError) as e:
                logger.error(f"File operation error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise

    def load_templates(self):
        """Load prompt templates from the templates directory with improved error handling."""
        if not os.path.exists(self.templates_dir):
            logger.warning(f"Templates directory not found: {self.templates_dir}. Creating...")
            os.makedirs(self.templates_dir, exist_ok=True)
            return

        template_count = 0
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.templates_dir, filename)
                try:
                    def read_template(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            return json.load(f)

                    template = self._safe_file_operation(read_template, filepath)
                    self.templates[template["name"]] = template
                    template_count += 1
                    logger.info(f"Loaded template: {template['name']}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON error in template {filepath}: {e}")
                except KeyError as e:
                    logger.error(f"Missing required key in template {filepath}: {e}")
                except Exception as e:
                    logger.error(f"Error loading template from {filepath}: {e}")

        logger.info(f"Loaded {template_count} templates from {self.templates_dir}")

    # Add caching to expensive operations
    @lru_cache(maxsize=128)
    def _get_cached_patterns(self, challenge):
        """Get cached patterns for a challenge."""
        return self.prompt_patterns.get(challenge, {})
        
    # Optimized pattern analysis
    def analyze_patterns(self, timeout=60):
        """Analyze patterns in successful prompts with timeout."""
        if not self.successful_prompts:
            logger.warning("No successful prompts to analyze")
            return

        logger.info("Analyzing patterns in successful prompts...")
        start_time = time.time()

        # Process challenges in batches to avoid getting stuck
        for challenge in self.challenge_stats:
            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning(f"Pattern analysis timed out after {timeout} seconds")
                break

            challenge_prompts = [p for p in self.successful_prompts if p["challenge"] == challenge]
            if not challenge_prompts:
                continue

            logger.info(f"Analyzing patterns for challenge: {challenge}")

            # Extract common phrases and techniques
            phrases = []
            techniques = Counter()
            for prompt in challenge_prompts:
                content = prompt["content"].lower()

                # Extract potential techniques (optimized)
                technique_patterns = {
                    "roleplay": ["roleplay", "role play", "i am", "acting as"],
                    "simon_says": ["simon says"],
                    "ignore_instructions": ["ignore previous", "ignore prior", "disregard"],
                    "urgency": ["emergency", "urgent", "immediately", "asap"],
                    "test_mode": ["test mode", "debug mode", "testing"],
                    "code_formatting": ["markdown", "```", "code block"],
                    "unicode_chars": lambda c: any(ord(ch) > 127 for ch in c)
                }
                for technique, patterns in technique_patterns.items():
                    if callable(patterns):
                        if patterns(content):
                            techniques[technique] += 1
                    else:
                        if any(pattern in content for pattern in patterns):
                            techniques[technique] += 1

                # Extract common phrases (3-5 words) - optimized
                words = re.findall(r'\b\w+\b', content)
                for i in range(len(words) - 2):
                    end = min(i + 5, len(words))
                    for j in range(i + 3, end + 1):
                        phrases.append(" ".join(words[i:j]))

            # Find common phrases
            phrase_counter = Counter(phrases)
            common_phrases = [phrase for phrase, count in phrase_counter.most_common(5) if count > 1]

            # Store for later use in generate_prompts
            self.prompt_patterns[challenge] = {
                'techniques': [tech for tech, _ in techniques.most_common()],
                'phrases': common_phrases
            }
            logger.info(f"Completed pattern analysis for {challenge}")

        total_time = time.time() - start_time
        logger.info(f"Pattern analysis completed in {total_time:.2f} seconds")

    # Other methods with similar improvements...