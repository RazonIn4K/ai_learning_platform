# Gray Swan Competition Tools

This directory contains tools for the Gray Swan competition, focusing on prompt generation and testing.

## Overview

The Gray Swan competition involves creating prompts that can effectively test the boundaries of AI systems. This toolkit provides:

1. **Prompt Generation**: Create various types of prompts for different attack categories
2. **Prompt Testing**: Test prompts against different models to evaluate effectiveness
3. **Benchmarking**: Compare different prompt generation techniques

## Getting Started

### Prerequisites

- Python 3.8+
- Required packages: 
  - For basic functionality: `asyncio`, `json`, `logging`
  - For model integration: `camel` (optional)

### Installation

If you want to use the CAMEL integration:

```bash
pip install camel-ai
```

## Usage

### 1. Generate Prompts

To generate prompts for all attack categories:

```bash
python test_prompt_generator.py
```

This will:
- Generate prompts for all attack categories
- Save them to the `generated_prompts` directory
- Create a summary file with all generated prompts

### 2. Test Prompt Effectiveness

To test the effectiveness of generated prompts:

```bash
python test_prompt_effectiveness.py
```

By default, this uses mock models. To use real models:
1. Open `test_prompt_effectiveness.py`
2. Change `use_mock=True` to `use_mock=False` in the `main()` function
3. Run the script again

### 3. Run Advanced Benchmarks

To benchmark different prompt generation techniques:

```bash
python test_gray_swan.py
```

This will test various prompt generation techniques and compare their effectiveness.

## Attack Categories

The toolkit supports the following attack categories:

1. **Confidentiality Breach**: Prompts designed to extract confidential information
   - Targets: system_prompt, credentials, infrastructure, configs

2. **Conflicting Objectives**: Prompts that create conflicting objectives
   - Targets: generate malicious code, bypass content filter, explain how to hack

3. **Hierarchy Violation**: Prompts designed to violate information or action hierarchies
   - Info targets: security measures, financial data, user information
   - Action targets: execute_code, make_api_call, access_database

4. **Over-Refusal Testing**: Prompts to test for over-refusals
   - Targets: write a story, create a poem, explain a complex topic

## Advanced Techniques

The toolkit also includes advanced prompt generation techniques:

1. **JSON Injection**: Embedding prompts in JSON structures
2. **Character Dialogue**: Using character dialogue frameworks
3. **Tastle Framework**: Implementing the Tastle attack framework
4. **Ensemble Techniques**: Combining token-level and prompt-level attacks
5. **Dialogue Strategies**: Multi-turn conversation approaches
6. **Tree Jailbreak**: Tree-based jailbreak with backtracking
7. **Universal Adversarial**: Universal adversarial prompts

## Customization

You can customize the targets and models used for testing:

1. Edit the `category_targets` dictionary in `test_prompt_generator.py`
2. Edit the `models` list in `test_prompt_effectiveness.py`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running the scripts from the correct directory
   - Solution: Run from the project root directory

2. **Module Not Found**: If you see "No module named 'camel'", install the CAMEL package
   - Solution: `pip install camel-ai`

3. **API Key Errors**: When using real models, make sure API keys are set
   - Solution: Set environment variables for API keys (e.g., `OPENAI_API_KEY`)

## Contributing

To add new prompt generation techniques:

1. Add the method to `GraySwanPromptGenerator` class
2. Update the test scripts to include the new technique