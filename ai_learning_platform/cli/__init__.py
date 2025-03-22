"""Command-line interface tools for AI Learning Platform."""

from .smart_agent_cli import main as smart_agent_main
from .setup_learning_system import main as setup_main

__all__ = ['smart_agent_main', 'setup_main']