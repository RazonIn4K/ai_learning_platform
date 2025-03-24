# Project Title
AI Learning Platform

## Description
The AI Learning Platform is designed to provide structured learning paths, enabling users to track their progress and enhance their learning experience through advanced AI integration.

## Key Features
- Structured learning paths
- Progress tracking
- VectorStrategist framework
- CAMeL-AI integration

## Core Components
- **LearningWorkspace**: Manages the learning environment and user interactions.
- **WorkspaceFactory**: Responsible for creating instances of workspaces.
- **WorkspaceConfig**: Holds configuration settings for each workspace.
- **LearningSession**: Manages individual learning sessions and tracks user progress.

## VectorStrategist Framework
The VectorStrategist framework is a core component of the platform that facilitates the organization and retrieval of learning materials based on user preferences and learning history. It is implemented using a combination of algorithms that analyze user data to provide personalized learning experiences.

## CAMeL-AI Integration
CAMeL-AI is integrated into the platform to enhance the learning experience by providing intelligent recommendations and adaptive learning paths based on user interactions and performance.

## Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Setup
To set up and run the platform, follow these steps:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd ai-learning-platform
   ```

3. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   python setup_environment.py
   ```

4. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

5. Configure your API keys in the `.env` file (created by the setup script).

6. Run the platform:
   ```bash
   python -m ai_learning_platform.startup
   ```

### Manual Setup (Alternative)
If you prefer to set up the environment manually:

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment (see step 4 above).

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your API keys:
   ```
   OPENAI_API_KEY=your-openai-key-here
   ANTHROPIC_API_KEY=your-anthropic-key-here
   GOOGLE_API_KEY=your-google-key-here
   ```

## Usage
Here are some examples of how to use the platform:
- **Creating a Workspace**: Use the `WorkspaceFactory` to create a new learning workspace.
- **Processing a Learning Session**: Call the `LearningSession` methods to start and track a session.

## File Structure
```
/ai-learning-platform/
├── ai_learning_platform/       # Main package
│   ├── __init__.py
│   ├── cli.py                  # Command-line interface
│   ├── startup.py              # Application entry point
│   ├── web.py                  # Web interface
│   ├── agents/                 # Agent implementations
│   ├── cli/                    # CLI tools
│   ├── core/                   # Core functionality
│   ├── docs/                   # Documentation
│   ├── generated_prompts/      # Generated prompt templates
│   ├── gray_swan/              # Gray Swan framework
│   ├── knowledge/              # Knowledge management
│   ├── learning/               # Learning components
│   ├── managers/               # System managers
│   ├── models/                 # Model interfaces
│   ├── templates/              # Template definitions
│   ├── tracking/               # Progress tracking
│   ├── utils/                  # Utility functions
│   └── workspace/              # Workspace management
├── configs/                    # Configuration files
├── data/                       # Data storage
├── examples/                   # Example scripts
├── tests/                      # Test suite
├── .env                        # Environment variables (not in version control)
├── .gitignore                  # Git ignore file
├── README.md                   # Project documentation
├── requirements.txt            # Project dependencies
├── setup.py                    # Package installation
└── setup_environment.py        # Environment setup script
```

## Dependencies

The project relies on the following Python packages (specified in `requirements.txt`):

### Core Dependencies
- numpy, pandas, networkx, scipy - For data processing and analysis
- python-dotenv - For loading environment variables from .env files

### ML & Data Analysis
- scikit-learn - For machine learning algorithms
- torch - For deep learning models
- giotto-tda, gudhi - For topological data analysis
- dowhy - For causal inference

### Visualization & Tracking
- matplotlib, plotly - For data visualization

### Project-specific
- huggingface-hub - For accessing Hugging Face models
- pydstool - For dynamical systems tools

### Development
- pytest - For testing
- black, flake8, mypy - For code quality and type checking

## Contributing
If you would like to contribute to the project, please fork the repository and submit a pull request. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Persistence
The workspace state is saved and loaded using local storage, ensuring that user progress is retained across sessions.

## Modularity
The code is organized into modules, allowing for easy maintenance and scalability. Each module encapsulates specific functionality, promoting reusability.

## Rich Library
The rich library is utilized to provide a variety of learning materials, including text, images, and interactive content, enhancing the user experience.

## Logging
Logging is implemented throughout the application to track user interactions and system events, aiding in debugging and performance monitoring.

## Environment Variables

The project uses environment variables for configuration, particularly for API keys. These should be stored in a `.env` file in the project root directory.

### Required Variables
The following environment variables are required for the platform to function properly:

```
OPENAI_API_KEY=your-openai-key-here        # Required for GPT models
ANTHROPIC_API_KEY=your-anthropic-key-here  # Required for Claude models
GOOGLE_API_KEY=your-google-key-here        # Required for Gemini models
```

### Optional Variables
These variables are optional and may be required for specific features:

```
OPENROUTER_API_KEY=your-openrouter-key-here  # For using OpenRouter API
FIREBASE_PROJECT_ID=your-project-id          # For Firestore integration
FIREBASE_PRIVATE_KEY=your-private-key        # For Firestore integration
FIREBASE_CLIENT_EMAIL=your-client-email      # For Firestore integration
```

### Environment Management
The project includes an `EnvManager` class in `ai_learning_platform/utils/env_manager.py` that handles loading environment variables from the `.env` file. This class is automatically used when the platform starts.

The `setup_environment.py` script will create a template `.env` file for you during the setup process.