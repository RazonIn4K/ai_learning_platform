# Initialize your learning session
workspace = LearningWorkspace()

# Start with a broad query
response = workspace.process_learning_session("""
I want to learn modern web development and eventually create a profitable service.
Help me focus on learning while keeping monetization in mind.
""")

# The response will be structured with clear priorities
print("\nCore Technical Topics to Master:")
for topic in response["core_topics"]:
    print(f"- {topic['name']}: {topic['why_important']}")

print("\nLearning Path:")
for step in response["learning_path"]:
    print(f"\nStep: {step['topic']}")
    print("Technical Focus:", step['learning_steps'])
    print("Practical Exercise:", step['practical_exercises'])
    print("Business Context:", step['business_relevance'])

# Check your progress
progress = workspace.get_learning_progress()
print("\nLearning Progress:")
print("Mastered:", progress["mastered_concepts"])
print("Currently Learning:", progress["current_focus"])
print("Next Focus:", progress["next_steps"])

# When ready to explore business aspects
business_context = workspace.get_business_context(
    technical_progress=progress["mastered_concepts"]
)
print("\nBusiness Considerations:")
print("Ready to Explore:", business_context["ready_topics"])
print("Future Topics:", business_context["future_topics"])