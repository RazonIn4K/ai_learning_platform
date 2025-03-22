from ai_learning_platform.workspace import LearningWorkspace
from ai_learning_platform.workspace.workspace_config import WorkspaceConfig

# Initialize a learning-focused workspace
workspace = LearningWorkspace(
    WorkspaceConfig(
        domains=["web_development", "system_design", "business"],
        enable_research=True,
        learning_style="self_taught",
        model_type="advanced",
        tracking_level="detailed"
    )
)

# Your complex learning query
complex_query = """
I want to understand modern web development, specifically:
- Different tech stacks and their trade-offs
- How to make scalable applications
- When to consider monetization without compromising learning
- Best practices for solo developers

I want to focus on learning but keep future monetization in mind.
"""

# Process the learning session
learning_session = workspace.process_learning_session(complex_query)

# Print the structured learning path
print("\nLearning Path:")
for topic in learning_session["learning_path"]:
    print(f"\nTopic: {topic['topic']}")
    if "prerequisites" in topic:
        print("Prerequisites:", topic["prerequisites"])
    if "learning_steps" in topic:
        print("Steps:", topic["learning_steps"])

# Track progress
progress = workspace.track_learning_progress(
    topics=["web_development_basics", "system_design"],
    metrics={"comprehension": {"web_development": 0.7}},
    user_profile={"experience_level": "intermediate"}
)

print("\nProgress Tracking:")
for topic, mastery in progress["topic_mastery"].items():
    print(f"\n{topic}:")
    print("Strengths:", mastery["strengths"])
    print("Gaps:", mastery["gaps"])
