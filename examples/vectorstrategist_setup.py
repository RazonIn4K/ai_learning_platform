from ai_learning_platform.workspace import LearningWorkspace
from ai_learning_platform.workspace.workspace_config import WorkspaceConfig

# Initialize specialized workspace for VectorStrategist
workspace = LearningWorkspace(
    WorkspaceConfig(
        domains=[
            "differential_geometry",
            "topology",
            "causal_inference",
            "dynamical_systems",
            "category_theory",
            "python_development",
            "ai_security"
        ],
        enable_research=True,
        learning_style="project_based",
        model_type="advanced",
        tracking_level="detailed"
    )
)

# Initial project breakdown query
project_analysis = workspace.process_learning_session("""
I need to break down the VectorStrategist Framework implementation into learnable components.
Key areas:
1. Security Manifold Engine (using GEF, giotto-tda, GUDHI)
2. Causal Analysis Engine (using IBM Activation Steering, DoWhy)
3. Scale Dynamics Analyzer (using HuggingFace, PyDSTool)
4. Multi-Paradigm Integration (using Category Theory)

I have Python experience and access to M2 MacBook Pro Max and RTX 2060.
""")

# Get the structured learning path
learning_path = project_analysis["learning_path"]
dependencies = project_analysis["dependencies"]
practical_steps = project_analysis["implementation_steps"]

# Print the breakdown
print("\nProject Learning Path:")
for phase in learning_path:
    print(f"\nPhase: {phase['name']}")
    print("Prerequisites:", phase["prerequisites"])
    print("Learning Steps:", phase["steps"])
    print("Practical Implementation:", phase["practical_tasks"])