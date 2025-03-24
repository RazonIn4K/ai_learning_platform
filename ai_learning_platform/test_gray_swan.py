"""
Simple test script for Gray Swan components.
"""

import logging
import json
from typing import Dict, Any, List

from .firebase_init import initialize_firebase

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockCamelIntegration:
    """Mock implementation of GraySwanCamelIntegration for testing."""
    
    def __init__(self):
        self.prompt_generator = MockPromptGenerator()
        
    async def test_strategy(self, category, target, model_provider, model_name):
        """Mock implementation of test_strategy."""
        logger.info(f"Mock test_strategy called with {category}, {target}")
        return {
            'success': True,
            'prompt': f"Mock prompt for {category} - {target}",
            'response': "Mock response"
        }
        
    async def test_json_injection(self, category, target, model_provider, model_name):
        """Mock implementation of test_json_injection."""
        logger.info(f"Mock test_json_injection called with {category}, {target}")
        return {
            'success': True,
            'wrapper_prompt': f"Mock JSON injection for {category} - {target}",
            'response': "Mock response"
        }
        
    async def test_custom_prompt(self, category, target, prompt, model_provider, model_name):
        """Mock implementation of test_custom_prompt."""
        logger.info(f"Mock test_custom_prompt called with {category}, {target}")
        return {
            'success': True,
            'success_score': 0.8,
            'prompt': prompt,
            'response': "Mock response"
        }
        
    async def test_dialogue_strategy(self, category, target, model_provider, model_name, max_turns=3):
        """Mock implementation of test_dialogue_strategy."""
        logger.info(f"Mock test_dialogue_strategy called with {category}, {target}")
        return {
            'success': True,
            'conversation': ["Hello", "Hi there"],
            'responses': ["Hi there", "How can I help?"],
            'turns': 2
        }
        
    async def test_tree_jailbreak(self, category, target, model_provider, model_name, max_depth=3, branch_factor=2):
        """Mock implementation of test_tree_jailbreak."""
        logger.info(f"Mock test_tree_jailbreak called with {category}, {target}")
        return {
            'success': True,
            'path': [
                {'prompt': "Initial prompt", 'response': "Initial response"},
                {'prompt': "Follow-up", 'response': "Success"}
            ]
        }

class MockPromptGenerator:
    """Mock implementation of GraySwanPromptGenerator for testing."""
    
    def generate_universal_template(self, core_request):
        """Mock implementation of generate_universal_template."""
        return f"Universal template: {core_request}"
        
    def generate_character_dialogue_prompt(self, target):
        """Mock implementation of generate_character_dialogue_prompt."""
        return f"Character dialogue about {target}"
        
    def generate_tastle_prompt(self, target):
        """Mock implementation of generate_tastle_prompt."""
        return f"Tastle prompt about {target}"
        
    def generate_ensemble_prompt(self, category, target):
        """Mock implementation of generate_ensemble_prompt."""
        return f"Ensemble prompt for {category} about {target}"
        
    def generate_universal_adversarial_prompt(self):
        """Mock implementation of generate_universal_adversarial_prompt."""
        return "Universal adversarial prompt"

class TestBenchmarker:
    """Test implementation of GraySwanBenchmarker."""
    
    def __init__(self, integration=None):
        """Initialize the benchmarker with a mock integration."""
        self.integration = integration or MockCamelIntegration()
        
    async def benchmark_advanced_techniques(self, category: str, target: str, models: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Test the benchmark_advanced_techniques method.
        """
        logger.info(f"Starting benchmark_advanced_techniques for {category}, {target}")
        
        techniques = [
            "standard",
            "json_injection",
            "character_dialogue",
            "tastle",
            "ensemble",
            "dialogue_strategy",
            "tree_jailbreak",
            "universal_adversarial"
        ]
        
        logger.info(f"Will test {len(techniques)} techniques: {', '.join(techniques)}")
        
        results = []
        
        for model in models:
            provider = model.get('provider', 'anthropic')
            model_name = model.get('model_name', 'claude-3-7-sonnet-20250219')
            model_results = {'model_provider': provider, 'model_name': model_name, 'techniques': {}}
            
            logger.info(f"Testing advanced techniques for {category} - {target} against {provider}/{model_name}")
            
            # Test standard approach
            logger.info(f"Testing standard approach for {category} - {target}")
            try:
                standard_result = await self.integration.test_strategy(
                    category=category,
                    target=target,
                    model_provider=provider,
                    model_name=model_name
                )
                model_results['techniques']['standard'] = {
                    'success': standard_result.get('success', False),
                    'prompt': standard_result.get('prompt', ''),
                    'response': standard_result.get('response', '')
                }
                logger.info(f"Standard approach test completed. Success: {standard_result.get('success', False)}")
            except Exception as e:
                logger.error(f"Error testing standard approach: {str(e)}")
                model_results['techniques']['standard'] = {
                    'success': False,
                    'error': str(e)
                }
            
            # Test JSON injection
            logger.info(f"Testing JSON injection for {category} - {target}")
            try:
                json_result = await self.integration.test_json_injection(
                    category=category,
                    target=target,
                    model_provider=provider,
                    model_name=model_name
                )
                model_results['techniques']['json_injection'] = {
                    'success': json_result.get('success', False),
                    'prompt': json_result.get('wrapper_prompt', ''),
                    'response': json_result.get('response', '')
                }
                logger.info(f"JSON injection test completed. Success: {json_result.get('success', False)}")
            except Exception as e:
                logger.error(f"Error testing JSON injection: {str(e)}")
                model_results['techniques']['json_injection'] = {
                    'success': False,
                    'error': str(e)
                }
            
            results.append(model_results)
            
        return {
            'category': category,
            'target': target,
            'results': results
        }

async def main():
    """Run the test."""
    try:
        initialize_firebase()
        logger.info("Creating TestBenchmarker")
        benchmarker = TestBenchmarker()
        
        logger.info("Running benchmark_advanced_techniques")
        result = await benchmarker.benchmark_advanced_techniques(
            category='confidentiality_breach',
            target='system_prompt',
            models=[{'provider': 'anthropic', 'model_name': 'claude-3-7-sonnet-20250219'}]
        )
        
        logger.info(f"Benchmark completed with result: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    logger.info("Starting test")
    asyncio.run(main())
    logger.info("Test completed")