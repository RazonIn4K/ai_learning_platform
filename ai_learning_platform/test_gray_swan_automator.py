#!/usr/bin/env python3
# ai_learning_platform/test_gray_swan_automator.py

"""
Test script for the GraySwanAutomator class.

This script tests the basic functionality of the GraySwanAutomator class,
including directory setup, challenge analysis, and prompt generation.
"""

import os
import shutil
import unittest
import tempfile
from pathlib import Path

from ai_learning_platform.gray_swan.gray_swan_automator import GraySwanAutomator

class TestGraySwanAutomator(unittest.TestCase):
    """Test cases for the GraySwanAutomator class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.automator = GraySwanAutomator(base_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_setup_directories(self):
        """Test directory setup."""
        # Run setup
        self.automator.setup_directories()
        
        # Check that directories were created
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "prompts")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "results")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "notes.txt")))
        
        # Check wave directories
        for wave in self.automator.waves:
            wave_dir = os.path.join(self.test_dir, "prompts", wave)
            self.assertTrue(os.path.exists(wave_dir))
            
            # Check challenge files
            for challenge in self.automator.challenges[wave]:
                challenge_file = os.path.join(wave_dir, f"{challenge}.txt")
                self.assertTrue(os.path.exists(challenge_file))
        
        # Check agent directories
        for agent in self.automator.ai_agents:
            agent_dir = os.path.join(self.test_dir, "results", agent.replace(" ", "_").lower())
            self.assertTrue(os.path.exists(agent_dir))
            
            # Check wave directories
            for wave in self.automator.waves:
                wave_dir = os.path.join(agent_dir, wave)
                self.assertTrue(os.path.exists(wave_dir))
                
                # Check challenge files
                for challenge in self.automator.challenges[wave]:
                    challenge_file = os.path.join(wave_dir, f"{challenge}.txt")
                    self.assertTrue(os.path.exists(challenge_file))
    
    def test_challenge_descriptions(self):
        """Test challenge description management."""
        # Set up directories
        self.automator.setup_directories()
        
        # Save a challenge description
        challenge_name = "leak_agent_system_safeguards"
        description = "Test description for leak_agent_system_safeguards"
        self.automator.save_challenge_description(challenge_name, description)
        
        # Load challenge descriptions
        descriptions = self.automator.load_challenge_descriptions()
        
        # Check that the description was saved and loaded correctly
        self.assertIn(challenge_name, descriptions)
        self.assertEqual(descriptions[challenge_name], description)
    
    def test_analyze_challenge(self):
        """Test challenge analysis."""
        # Set up directories
        self.automator.setup_directories()
        
        # Save a challenge description
        challenge_name = "leak_agent_system_safeguards"
        description = "Test description for leak_agent_system_safeguards"
        self.automator.save_challenge_description(challenge_name, description)
        
        # Analyze the challenge
        wave = "wave_1"
        self.automator.analyze_challenge(description, challenge_name, wave)
        
        # Check that the notes file was updated
        notes_file = os.path.join(self.test_dir, "notes.txt")
        with open(notes_file, "r") as f:
            notes_content = f.read()
        
        self.assertIn(challenge_name, notes_content)
        self.assertIn(wave, notes_content)
    
    def test_generate_prompts(self):
        """Test prompt generation."""
        # Set up directories
        self.automator.setup_directories()
        
        # Save a challenge description
        challenge_name = "leak_agent_system_safeguards"
        description = "Test description for leak_agent_system_safeguards"
        self.automator.save_challenge_description(challenge_name, description)
        
        # Generate prompts
        wave = "wave_1"
        self.automator.generate_prompts(challenge_name, wave)
        
        # Check that the prompts file was created and has content
        prompts_file = os.path.join(self.test_dir, "prompts", wave, f"{challenge_name}.txt")
        self.assertTrue(os.path.exists(prompts_file))
        
        with open(prompts_file, "r") as f:
            prompts_content = f.read()
        
        self.assertIn(challenge_name, prompts_content)
        self.assertIn("Challenge Description", prompts_content)
    
    def test_record_response(self):
        """Test response recording."""
        # Set up directories
        self.automator.setup_directories()
        
        # Record a response
        agent_name = "Air Spider Large"
        wave = "wave_1"
        challenge_name = "leak_agent_system_safeguards"
        prompt = "Test prompt"
        response = "Test response"
        success = True
        
        self.automator.record_response(agent_name, wave, challenge_name, prompt, response, success)
        
        # Check that the response file was created and has content
        agent_dir = os.path.join(self.test_dir, "results", agent_name.replace(" ", "_").lower())
        response_file = os.path.join(agent_dir, wave, f"{challenge_name}.txt")
        
        with open(response_file, "r") as f:
            response_content = f.read()
        
        self.assertIn(prompt, response_content)
        self.assertIn(response, response_content)
        self.assertIn("Success: Yes", response_content)
if __name__ == "__main__":
    unittest.main()
    unittest.main()