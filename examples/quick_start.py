from ai_learning_platform.workspace.workspace_factory import WorkspaceFactory, WorkspaceConfig

# Quick start with defaults
workspace = WorkspaceFactory.quick_workspace()

# Or customize your workspace
custom_workspace = WorkspaceFactory.create_workspace(
    WorkspaceConfig(
        domains=["python", "machine_learning", "system_design"],
        enable_research=True,
        learning_style="self_taught",
        model_type="advanced"
    )
)

# Ask questions naturally
response = workspace.process_message(
    "I want to learn about building scalable systems. "
    "I know Python and have built some web apps. "
    "What should I learn next?"
)

# Get research-enhanced responses
response = workspace.process_message(
    "What are the current best practices for microservices architecture?"
)