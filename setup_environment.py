#!/usr/bin/env python3
"""
Setup Environment Script for AI Learning Platform

This script helps set up the development environment by:
1. Creating a virtual environment
2. Installing dependencies from requirements.txt
3. Creating a template .env file if it doesn't exist
4. Providing instructions for activating the virtual environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_step(step_num, description):
    """Print a formatted step in the setup process."""
    print(f"\n\033[1;34m[Step {step_num}]\033[0m \033[1m{description}\033[0m")

def print_success(message):
    """Print a success message."""
    print(f"\033[1;32m✓ {message}\033[0m")

def print_error(message):
    """Print an error message."""
    print(f"\033[1;31m✗ {message}\033[0m")

def print_info(message):
    """Print an info message."""
    print(f"\033[1;33mℹ {message}\033[0m")

def run_command(command, error_message):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        print_error(error_message)
        return False
    except FileNotFoundError:
        print_error(f"Command not found: {command[0]}")
        return False

def create_virtual_environment(venv_name=".venv"):
    """Create a virtual environment."""
    print_step(1, "Creating virtual environment")
    
    if Path(venv_name).exists():
        print_info(f"Virtual environment '{venv_name}' already exists")
        return True
    
    return run_command(
        [sys.executable, "-m", "venv", venv_name],
        f"Failed to create virtual environment '{venv_name}'"
    )

def install_dependencies(venv_name=".venv"):
    """Install dependencies from requirements.txt."""
    print_step(2, "Installing dependencies from requirements.txt")
    
    # Determine the pip executable path based on the platform
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_name, "Scripts", "pip")
    else:
        pip_path = os.path.join(venv_name, "bin", "pip")
    
    # Upgrade pip first
    if not run_command(
        [pip_path, "install", "--upgrade", "pip"],
        "Failed to upgrade pip"
    ):
        return False
    
    # Install dependencies
    return run_command(
        [pip_path, "install", "-r", "requirements.txt"],
        "Failed to install dependencies"
    )

def create_env_template():
    """Create a template .env file if it doesn't exist."""
    print_step(3, "Setting up environment variables")
    
    env_path = Path(".env")
    if env_path.exists():
        print_info(".env file already exists")
        return True
    
    try:
        with open(".env", "w") as f:
            f.write("""# AI Learning Platform Environment Configuration

# OpenAI API key for GPT models
OPENAI_API_KEY=your-openai-key-here

# Anthropic API key for Claude models
ANTHROPIC_API_KEY=your-anthropic-key-here

# Google API key for Gemini models
GOOGLE_API_KEY=your-google-key-here

# Optional: OpenRouter API key
# OPENROUTER_API_KEY=your-openrouter-key-here

# Optional: Firebase configuration (if using Firestore)
# FIREBASE_PROJECT_ID=your-project-id
# FIREBASE_PRIVATE_KEY=your-private-key
# FIREBASE_CLIENT_EMAIL=your-client-email
""")
        print_success("Created template .env file")
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False

def print_activation_instructions(venv_name=".venv"):
    """Print instructions for activating the virtual environment."""
    print_step(4, "Next steps")
    
    print_info("To activate the virtual environment:")
    
    if platform.system() == "Windows":
        print(f"    {venv_name}\\Scripts\\activate")
    else:
        print(f"    source {venv_name}/bin/activate")
    
    print_info("After activation, you can run the project using:")
    print("    python -m ai_learning_platform.startup")
    
    print_info("Don't forget to add your API keys to the .env file")

def main():
    """Main function to set up the environment."""
    print("\033[1m=== AI Learning Platform Environment Setup ===\033[0m\n")
    
    venv_name = ".venv"
    
    if create_virtual_environment(venv_name):
        print_success("Virtual environment created successfully")
    else:
        return
    
    if install_dependencies(venv_name):
        print_success("Dependencies installed successfully")
    else:
        return
    
    if create_env_template():
        print_success("Environment setup completed")
    
    print_activation_instructions(venv_name)
    print("\n\033[1;32m=== Setup completed successfully ===\033[0m")

if __name__ == "__main__":
    main()