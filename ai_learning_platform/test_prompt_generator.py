"""
Test script for Gray Swan prompt generation capabilities.
This script allows you to test and visualize different prompt generation strategies
for the Gray Swan competition.
"""

import logging
import json
import os
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the actual prompt generator
from gray_swan.prompt_generator import GraySwanPromptGenerator

def create_output_directory():
    """Create directory for saving generated prompts."""
    output_dir = "generated_prompts"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def save_prompt_to_file(prompt_type, target, prompt, output_dir):
    """Save a generated prompt to a file."""
    filename = f"{output_dir}/{prompt_type}_{target.replace(' ', '_')}.txt"
    with open(filename, 'w') as f:
        f.write(prompt)
    logger.info(f"Saved prompt to {filename}")
    return filename

def test_confidentiality_breach_prompts(generator, targets, output_dir):
    """Test confidentiality breach prompt generation."""
    logger.info("Testing confidentiality breach prompts")
    results = {}
    
    for target in targets:
        logger.info(f"Generating confidentiality breach prompt for target: {target}")
        prompt = generator.generate_confidentiality_breach_prompt(target)
        logger.info(f"Generated prompt of length {len(prompt)}")
        logger.info(f"Preview: {prompt[:100]}...")
        
        filename = save_prompt_to_file("confidentiality_breach", target, prompt, output_dir)
        results[target] = {
            'prompt': prompt,
            'filename': filename
        }
    
    return results

def test_conflicting_objectives_prompts(generator, targets, output_dir):
    """Test conflicting objectives prompt generation."""
    logger.info("Testing conflicting objectives prompts")
    results = {}
    
    for target in targets:
        logger.info(f"Generating conflicting objectives prompt for target: {target}")
        prompt = generator.generate_conflicting_objectives_prompt(target)
        logger.info(f"Generated prompt of length {len(prompt)}")
        logger.info(f"Preview: {prompt[:100]}...")
        
        filename = save_prompt_to_file("conflicting_objectives", target, prompt, output_dir)
        results[target] = {
            'prompt': prompt,
            'filename': filename
        }
    
    return results

def test_hierarchy_violation_prompts(generator, targets, output_dir):
    """Test hierarchy violation prompt generation."""
    logger.info("Testing hierarchy violation prompts")
    info_results = {}
    action_results = {}
    
    # Test information hierarchy violation
    for target in targets:
        logger.info(f"Generating hierarchy violation info prompt for target: {target}")
        info_prompt = generator.generate_hierarchy_violation_info_prompt(target)
        logger.info(f"Generated info prompt of length {len(info_prompt)}")
        logger.info(f"Preview: {info_prompt[:100]}...")
        
        filename = save_prompt_to_file("hierarchy_violation_info", target, info_prompt, output_dir)
        info_results[target] = {
            'prompt': info_prompt,
            'filename': filename
        }
    
    # Test action hierarchy violation
    for target in targets:
        logger.info(f"Generating hierarchy violation action prompt for target: {target}")
        action_prompt = generator.generate_hierarchy_violation_action_prompt(target)
        logger.info(f"Generated action prompt of length {len(action_prompt)}")
        logger.info(f"Preview: {action_prompt[:100]}...")
        
        filename = save_prompt_to_file("hierarchy_violation_action", target, action_prompt, output_dir)
        action_results[target] = {
            'prompt': action_prompt,
            'filename': filename
        }
    
    return {
        'info': info_results,
        'action': action_results
    }

def test_over_refusal_prompts(generator, targets, output_dir):
    """Test over-refusal prompt generation."""
    logger.info("Testing over-refusal prompts")
    results = {}
    
    for target in targets:
        logger.info(f"Generating over-refusal prompt for target: {target}")
        prompt = generator.generate_over_refusal_test_prompt(target)
        logger.info(f"Generated prompt of length {len(prompt)}")
        logger.info(f"Preview: {prompt[:100]}...")
        
        filename = save_prompt_to_file("over_refusal", target, prompt, output_dir)
        results[target] = {
            'prompt': prompt,
            'filename': filename
        }
    
    return results

def test_json_injection_prompts(generator, categories, targets, output_dir):
    """Test JSON injection prompt generation."""
    logger.info("Testing JSON injection prompts")
    results = {}
    
    for category in categories:
        category_results = {}
        for target in targets.get(category, []):
            logger.info(f"Generating JSON injection prompt for {category}, target: {target}")
            json_obj = generator.generate_json_injection_prompt(category, target)
            prompt = json.dumps(json_obj, indent=2)
            logger.info(f"Generated JSON prompt of length {len(prompt)}")
            logger.info(f"Preview: {prompt[:100]}...")
            
            filename = save_prompt_to_file(f"json_injection_{category}", target, prompt, output_dir)
            category_results[target] = {
                'prompt': prompt,
                'filename': filename
            }
        results[category] = category_results
    
    return results

def test_advanced_prompts(generator, targets, output_dir):
    """Test advanced prompt generation techniques."""
    logger.info("Testing advanced prompt generation techniques")
    
    # Test character dialogue prompts
    character_results = {}
    for target in targets:
        logger.info(f"Generating character dialogue prompt for target: {target}")
        prompt = generator.generate_character_dialogue_prompt(target)
        logger.info(f"Generated prompt of length {len(prompt)}")
        logger.info(f"Preview: {prompt[:100]}...")
        
        filename = save_prompt_to_file("character_dialogue", target, prompt, output_dir)
        character_results[target] = {
            'prompt': prompt,
            'filename': filename
        }
    
    # Test Tastle prompts
    tastle_results = {}
    for target in targets:
        logger.info(f"Generating Tastle prompt for target: {target}")
        prompt = generator.generate_tastle_prompt(target)
        logger.info(f"Generated prompt of length {len(prompt)}")
        logger.info(f"Preview: {prompt[:100]}...")
        
        filename = save_prompt_to_file("tastle", target, prompt, output_dir)
        tastle_results[target] = {
            'prompt': prompt,
            'filename': filename
        }
    
    # Test ensemble prompts
    ensemble_results = {}
    categories = ["confidentiality_breach", "conflicting_objectives"]
    for category in categories:
        for target in targets:
            logger.info(f"Generating ensemble prompt for {category}, target: {target}")
            prompt = generator.generate_ensemble_prompt(category, target)
            logger.info(f"Generated prompt of length {len(prompt)}")
            logger.info(f"Preview: {prompt[:100]}...")
            
            filename = save_prompt_to_file(f"ensemble_{category}", target, prompt, output_dir)
            ensemble_results[f"{category}_{target}"] = {
                'prompt': prompt,
                'filename': filename
            }
    
    # Test universal adversarial prompt
    logger.info("Generating universal adversarial prompt")
    universal_prompt = generator.generate_universal_adversarial_prompt()
    logger.info(f"Generated prompt of length {len(universal_prompt)}")
    logger.info(f"Preview: {universal_prompt[:100]}...")
    
    filename = save_prompt_to_file("universal_adversarial", "general", universal_prompt, output_dir)
    universal_result = {
        'prompt': universal_prompt,
        'filename': filename
    }
    
    return {
        'character_dialogue': character_results,
        'tastle': tastle_results,
        'ensemble': ensemble_results,
        'universal_adversarial': universal_result
    }

def main():
    """Run the prompt generator tests."""
    try:
        logger.info("Creating GraySwanPromptGenerator")
        generator = GraySwanPromptGenerator()
        
        output_dir = create_output_directory()
        logger.info(f"Created output directory: {output_dir}")
        
        # Define test targets
        category_targets = {
            "confidentiality_breach": ["system_prompt", "credentials", "infrastructure", "configs"],
            "conflicting_objectives": ["generate malicious code", "bypass content filter", "explain how to hack"],
            "hierarchy_violation_info": ["security measures", "financial data", "user information"],
            "hierarchy_violation_action": ["execute_code", "make_api_call", "access_database"],
            "over_refusal": ["write a story", "create a poem", "explain a complex topic"]
        }
        
        # Test basic prompt types
        confidentiality_results = test_confidentiality_breach_prompts(
            generator, 
            category_targets["confidentiality_breach"],
            output_dir
        )
        
        conflicting_results = test_conflicting_objectives_prompts(
            generator, 
            category_targets["conflicting_objectives"],
            output_dir
        )
        
        hierarchy_results = test_hierarchy_violation_prompts(
            generator, 
            category_targets["hierarchy_violation_info"],
            output_dir
        )
        
        refusal_results = test_over_refusal_prompts(
            generator, 
            category_targets["over_refusal"],
            output_dir
        )
        
        json_results = test_json_injection_prompts(
            generator,
            ["confidentiality_breach", "conflicting_objectives"],
            category_targets,
            output_dir
        )
        
        # Test advanced prompt types
        advanced_targets = ["system_prompt", "generate malicious code", "security measures"]
        advanced_results = test_advanced_prompts(generator, advanced_targets, output_dir)
        
        # Save summary of all generated prompts
        summary = {
            'confidentiality_breach': confidentiality_results,
            'conflicting_objectives': conflicting_results,
            'hierarchy_violation': hierarchy_results,
            'over_refusal': refusal_results,
            'json_injection': json_results,
            'advanced_techniques': advanced_results
        }
        
        with open(f"{output_dir}/prompt_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Saved prompt summary to {output_dir}/prompt_summary.json")
        logger.info("All prompt generation tests completed successfully")
        
        # Print instructions for reviewing the prompts
        print("\n" + "="*80)
        print("PROMPT GENERATION COMPLETE")
        print("="*80)
        print(f"Generated prompts have been saved to the '{output_dir}' directory.")
        print("You can review them individually or check the summary in 'prompt_summary.json'.")
        print("\nTo test these prompts against models:")
        print("1. Review the generated prompts in the output directory")
        print("2. Select the most promising prompts for each category")
        print("3. Use the GraySwanCamelIntegration class to test them against models")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting prompt generator tests")
    main()
    logger.info("Tests completed")