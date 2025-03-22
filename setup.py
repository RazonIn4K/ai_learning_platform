from setuptools import setup, find_packages

setup(
    name="vectorstrategist",
    version="0.1.0",
    description="AI Learning Platform with Topic Navigation",
    author="Your Name",
    packages=find_packages(include=['ai_learning_platform', 'ai_learning_platform.*']),
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if not line.startswith("#")
    ],
    entry_points={
        'console_scripts': [
            'vs-learn=ai_learning_platform.cli.smart_agent_cli:main',
            'vs-setup=ai_learning_platform.cli.setup_learning_system:main',
        ],
    },
    python_requires=">=3.8",
    zip_safe=False
)
