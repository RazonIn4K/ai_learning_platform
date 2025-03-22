from ai_learning_platform.templates.workspace_template import WorkspaceTemplate
from datetime import timedelta

# Create a workspace using the template
workspace = WorkspaceTemplate.create_vectorstrategist_workspace()

# Define your learning phases
learning_phases = {
    "Phase 1: Mathematical Foundations": {
        "duration": timedelta(weeks=4),
        "topics": [
            {
                "name": "Differential Geometry Essentials",
                "key_concepts": ["Manifolds", "Tangent spaces"],
                "practical_tasks": ["Set up GEF", "Basic manifold operations"]
            }
        ]
    }
    # Add more phases as needed
}

# Process learning session
response = workspace.process_learning_session("""
I want to learn differential geometry for security manifolds.
Starting with basic manifold theory and working towards security applications.
""")

# Save progress
template = WorkspaceTemplate("vectorstrategist")
template.save_workspace_state(
    workspace,
    save_path="./vectorstrategist_progress"
)

# Later, you can restore your progress:
restored_workspace = WorkspaceTemplate.load_workspace_state(
    "vectorstrategist",
    load_path="./vectorstrategist_progress"
)