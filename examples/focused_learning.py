from ai_learning_platform.workspace import LearningWorkspace
from ai_learning_platform.workspace.learning_workspace import WorkspaceConfig

# Initialize a learning-focused workspace
workspace = LearningWorkspace(
    WorkspaceConfig(
        primary_focus="technical_learning",
        secondary_focus="business_awareness",
        learning_style="self_taught"
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

# The session will automatically:
# 1. Break down the query into focused learning topics
# 2. Prioritize technical understanding
# 3. Note business considerations for later
# 4. Track your learning progress

# You can then explore specific aspects as needed
print("Core Learning Topics:", learning_session["core_topics"])
print("Learning Path:", learning_session["learning_path"])
print("Future Considerations:", learning_session["future_considerations"])