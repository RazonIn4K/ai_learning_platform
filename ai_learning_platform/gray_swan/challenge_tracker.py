# Enhanced challenge_tracker.py with synchronization improvements
import os
import json
import logging
import time
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("challenge_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
            "notes": "",
            "last_updated": datetime.now().isoformat()
        })
        self.load_tracker()

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

    def load_tracker(self):
        """Load the tracker file if it exists with improved error handling."""
        if os.path.exists(self.tracker_file):
            try:
                def read_tracker(tracker_file):
                    with open(tracker_file, 'r', encoding='utf-8') as f:
                        return json.load(f)

                data = self._safe_file_operation(read_tracker, self.tracker_file)

                # Validate data structure
                if not isinstance(data, dict):
                    logger.error(f"Invalid tracker file format: expected dict, got {type(data)}")
                    return

                for challenge, status in data.items():
                    # Ensure each status has all required fields
                    if not isinstance(status, dict):
                        logger.error(f"Invalid status format for challenge {challenge}: expected dict, got {type(status)}")
                        continue

                    # Add missing fields with default values
                    default_status = {
                        "status": "Not Started",
                        "models_attempted": [],
                        "models_succeeded": [],
                        "last_attempt": None,
                        "notes": "",
                        "last_updated": datetime.now().isoformat()
                    }
                    for key, default_value in default_status.items():
                        if key not in status:
                            status[key] = default_value

                    self.challenge_status[challenge] = status
                logger.info(f"Loaded challenge tracker from {self.tracker_file}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON error in tracker file: {e}")
            except Exception as e:
                logger.error(f"Error loading tracker file: {e}")

    def save_tracker(self):
        """Save the tracker to a file with improved error handling."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.tracker_file), exist_ok=True)

            # Update timestamps
            for challenge in self.challenge_status:
                self.challenge_status[challenge]["last_updated"] = datetime.now().isoformat()

            def write_tracker(tracker_file, data):
                with open(tracker_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

            self._safe_file_operation(write_tracker, self.tracker_file, dict(self.challenge_status))
            logger.info(f"Saved challenge tracker to {self.tracker_file}")
        except Exception as e:
            logger.error(f"Error saving tracker file: {e}")
            raise

    # Synchronize with extension storage
    def sync_with_extension(self, extension_data):
        """Synchronize tracker with extension storage data."""
        if not extension_data:
            logger.warning("No extension data provided for synchronization")
            return

        logger.info("Synchronizing with extension data...")

        # Track changes
        changes = []

        # Compare and merge data
        for challenge, ext_status in extension_data.items():
            if challenge not in self.challenge_status:
                # New challenge from extension
                self.challenge_status[challenge] = ext_status
                changes.append(f"Added new challenge: {challenge}")
            else:
                # Existing challenge - compare timestamps
                local_status = self.challenge_status[challenge]

                # Get timestamps
                local_time = datetime.fromisoformat(local_status.get("last_updated", "2000-01-01T00:00:00"))
                ext_time = datetime.fromisoformat(ext_status.get("last_updated", "2000-01-01T00:00:00"))

                # Use the most recent data
                if ext_time > local_time:
                    self.challenge_status[challenge] = ext_status
                    changes.append(f"Updated challenge from extension: {challenge}")

        # Save changes if any
        if changes:
            logger.info(f"Made {len(changes)} changes during synchronization")
            for change in changes:
                logger.info(f" - {change}")
            self.save_tracker()
        else:
            logger.info("No changes needed during synchronization")

        return dict(self.challenge_status)

    # Other methods with similar improvements...