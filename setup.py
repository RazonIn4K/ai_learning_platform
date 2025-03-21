from setuptools import setup, find_packages

setup(
    name="ai_learning_platform",
    version="0.1.0",
    description="AI Learning Platform with Topic Navigation and Multi-Agent Workspace",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "camel-ai>=0.2.36",
        "python-dotenv>=1.0.1",
        "rich>=13.9.0",
        "pydantic<2.10.0",
        "requests>=2.31.0",
        "flask>=2.3.0",
        "markdown2>=2.4.8",
        "tqdm>=4.66.0",
        "colorama>=0.4.6",
        "networkx>=3.0",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "google-generativeai>=0.2.0",
    ],
    python_requires=">=3.10",
    entry_points={
        'console_scripts': [
            'ai-learning-platform=ai_learning_platform.cli:main',
            'ai-learning-web=ai_learning_platform.web:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
