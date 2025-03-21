# Fixed_AI_Learning Platform

A unified platform that combines topic navigation and multi-agent learning workspace capabilities to provide personalized learning experiences.

## Features

- **Topic Hierarchy Navigation**: Explore a comprehensive hierarchy of computer science and cybersecurity topics without memorizing IDs
- **Multi-Agent Learning Workspace**: Interact with specialized AI agents for different knowledge domains
- **Personalized Learning**: Get customized learning paths based on your knowledge profile
- **Latest AI Models**: Support for cutting-edge models including Claude 3.7 Sonnet, GPT-4o, Gemini 2.0, and o3-mini

## Components

- **Topic Navigator**: Helps discover relevant topics and create learning paths
- **Domain Expert**: Provides in-depth knowledge about specific domains
- **Learning Coordinator**: Orchestrates interactions between specialized agents
- **Learning Workspace**: Manages the learning environment and user profile

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Fixed_AI_Learning.git
   cd Fixed_AI_Learning
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Set up environment variables by copying the example file:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your API keys.

## Usage

### CLI Interface

The platform provides a command-line interface for easy interaction:

```bash
# Run the CLI
ai-learning-platform

# Automatically set up with default domains
ai-learning-platform --setup --domains python,cybersecurity,machine_learning
```

### Web Interface

The platform also includes a web interface built with Flask:

```bash
# Run the web interface
ai-learning-web
```

Then open your browser and navigate to `http://localhost:5000`.

### Python API

You can also use the platform programmatically:

```python
from ai_learning_platform.workspace.learning_workspace import LearningWorkspace
from ai_learning_platform.models.model_registry import ModelRegistry

# Create a workspace
workspace = LearningWorkspace()

# Create agents for different domains
workspace.create_default_workspace(domains=["python", "cybersecurity"])

# Ask a question
response = workspace.process_message("How do I securely store user passwords?")
print(response)
```

## API Keys

The platform requires API keys for the following services:

- OpenAI API (for GPT-4o and o3-mini)
- Anthropic API (for Claude 3.7 Sonnet)
- Google AI API (for Gemini 2.0)

Add your API keys to the `.env` file.

## Project Structure

```
Fixed_AI_Learning/
├── ai_learning_platform/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── coordinator.py
│   │   ├── domain_expert.py
│   │   └── topic_navigator.py
│   ├── models/
│   │   └── model_registry.py
│   ├── utils/
│   │   ├── config_loader.py
│   │   └── topic_hierarchy.py
│   ├── workspace/
│   │   └── learning_workspace.py
│   ├── cli.py
│   └── web.py
├── configs/
│   ├── model_presets.json
│   └── workspace_config.json
├── examples/
│   └── run_interactive.py
├── .env.example
├── README.md
├── requirements.txt
└── setup.py
```

## Agent Architecture

The platform uses a multi-agent system where each agent specializes in a specific task:

1. **Topic Navigator**: Navigates the topic hierarchy and creates learning paths
2. **Domain Expert**: Provides domain-specific knowledge and answers questions
3. **Learning Coordinator**: Orchestrates interactions between agents

Agents use the latest AI models through a unified interface provided by the `ModelRegistry`.

## Extending the Platform

### Adding New Agents

Create a new agent by inheriting from `BaseLearningAgent`:

```python
from ai_learning_platform.agents.base_agent import BaseLearningAgent

class NewAgent(BaseLearningAgent):
    def __init__(self, model_name, model_params=None, user_profile=None):
        super().__init__(
            name="New Agent",
            system_message="Your system message here",
            model_name=model_name,
            model_params=model_params,
            user_profile=user_profile
        )
    
    def specialized_function(self, *args, **kwargs):
        # Implement specialized functionality
        pass
```

### Adding New Topics

Add new topics to the `INTEGRATED_TOPIC_HIERARCHY` dictionary in `topic_hierarchy.py`.

## Future Development

- Web interface with Next.js and TypeScript
- Support for more LLM providers
- Enhanced personalization
- Collaborative learning features
- Content generation

## License

This project is licensed under the MIT License - see the LICENSE file for details.