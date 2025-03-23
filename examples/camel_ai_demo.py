# examples/camel_ai_demo.py

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from ai_learning_platform.models.enhanced_model_manager import EnhancedModelManager
from ai_learning_platform.agents.agent_model_adapter import AgentModelAdapter
from ai_learning_platform.utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demonstrate_camel_ai():
    """Demonstrate CAMeL-AI capabilities."""
    # Initialize model manager
    config_manager = ConfigManager()
    model_manager = EnhancedModelManager(config_manager)
    
    # Initialize agent adapter
    agent_adapter = AgentModelAdapter(model_manager)
    
    # Example 1: Basic CAMeL-AI completion
    print("\n=== Example 1: Basic CAMeL-AI Completion ===")
    response = await model_manager.generate_response(
        prompt="Explain the concept of transfer learning in AI.",
        provider="camel",
        model_name="camel-base"
    )
    print(f"Response: {response.get('content', 'No content')}")
    
    # Example 2: CAMeL-AI with role playing (single role)
    print("\n=== Example 2: CAMeL-AI with Role Playing (Single Role) ===")
    response = await model_manager.generate_response(
        prompt="How should I explain neural networks to a high school student?",
        provider="camel",
        model_name="camel-base",
        role="You are an AI education specialist who excels at making complex concepts accessible to students."
    )
    print(f"Response: {response.get('content', 'No content')}")
    
    # Example 3: CAMeL-AI with role playing (dual roles)
    print("\n=== Example 3: CAMeL-AI with Role Playing (Dual Roles) ===")
    response = await model_manager.generate_response(
        prompt="I'm struggling to understand how blockchain works. Can you explain it?",
        provider="camel",
        model_name="camel-base",
        assistant_role="You are a blockchain technology expert who can explain complex concepts clearly.",
        user_role="You are a business student interested in blockchain applications in finance."
    )
    print(f"Response: {response.get('content', 'No content')}")
    
    # Example 4: Agent-based CAMeL-AI role playing
    print("\n=== Example 4: Agent-based CAMeL-AI Role Playing ===")
    response = await agent_adapter.generate_role_playing_response(
        agent_type="domain_expert",
        prompt="What are the key principles of cybersecurity I should teach my team?",
        assistant_role="You are a cybersecurity expert with experience training corporate teams.",
        user_role="You are an IT manager responsible for improving your team's security practices.",
        model_name="camel-base"
    )
    print(f"Response: {response.get('content', 'No content')}")
    
    # Example 5: Comparing responses across providers
    print("\n=== Example 5: Response Comparison Across Providers ===")
    prompt = "Explain how machine learning models can be applied to improve cybersecurity."
    
    # CAMeL-AI response
    camel_response = await model_manager.generate_response(
        prompt=prompt,
        provider="camel",
        model_name="camel-base"
    )
    
    # Try another provider (fallback to available provider)
    other_provider = "anthropic"
    other_model = "claude-3-7-sonnet-20250219"
    
    try:
        other_response = await model_manager.generate_response(
            prompt=prompt,
            provider=other_provider,
            model_name=other_model
        )
    except Exception as e:
        logger.warning(f"Could not get {other_provider} response: {str(e)}")
        other_response = {"content": f"Error: {str(e)}"}
    
    print(f"CAMeL-AI response: {camel_response.get('content', 'No content')[:200]}...")
    print(f"{other_provider.capitalize()} response: {other_response.get('content', 'No content')[:200]}...")
    
if __name__ == "__main__":
    asyncio.run(demonstrate_camel_ai())
