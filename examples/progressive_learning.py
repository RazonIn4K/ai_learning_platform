from ai_learning_platform.workspace import LearningWorkspace

# Initialize workspace with persistent profile
workspace = LearningWorkspace(profile_path="my_learning_profile.json")

# Day 1: Initial learning session
response = workspace.process_learning_session(
    "I want to learn about microservices. I know Python and have built monolithic apps."
)

# Day 2: Building on previous knowledge
response = workspace.process_learning_session(
    "Now that I understand microservices basics, how do I handle service discovery?"
)

# Check learning progress
context = workspace.profile_manager.get_learning_context()
print("Mastered topics:", context["mastered_topics"])
print("Current learning:", context["current_topics"])
print("Recent insights:", context["recent_sessions"][-1]["key_insights"])