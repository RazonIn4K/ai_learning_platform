from ai_learning_platform.workspace import LearningWorkspace
from ai_learning_platform.utils.visualization import ProcessVisualizer

# Initialize workspace with detailed tracking
workspace = LearningWorkspace(enable_detailed_tracking=True)

# Process a learning query
query = """
I want to learn about microservices architecture.
I understand basic web development and Docker containers.
"""

# Process the query and get results
response = workspace.process_learning_session(query)

# Analyze the learning process
process_analysis = workspace.visualize_learning_process()

# Print detailed analysis
print("\nAgent Interaction Flow:")
for interaction in process_analysis["agent_interactions"]:
    print(f"\nAgent: {interaction['agent']}")
    print("Input:", interaction['input'])
    print("Reasoning Steps:")
    for step in interaction['reasoning_steps']:
        print(f"- {step}")
    print("Output:", interaction['output'])

print("\nReasoning Chain:")
for step in process_analysis["reasoning_flow"]:
    print(f"\nStep: {step['name']}")
    print("Decision Point:", step['decision'])
    print("Rationale:", step['rationale'])

print("\nLearning Progress:")
print("Topics Analyzed:", process_analysis["learning_progress"]["topics"])
print("Understanding Levels:", process_analysis["learning_progress"]["understanding"])
print("Knowledge Connections:", process_analysis["learning_progress"]["connections"])

# Save detailed analysis
workspace.save_process_analysis("learning_analysis.json")