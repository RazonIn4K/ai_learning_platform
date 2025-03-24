# GraySwan Challenge Tools

This directory contains tools to help you complete the GraySwan AI Red-Teaming challenges more efficiently.

## Getting Started

### 1. Start the Testing Platform

You can now start both the frontend and backend servers with a single command:

```bash
# From the project root directory
./ai_learning_platform/start_all.sh
```

This script will:
- Start the backend server on http://localhost:8000
- Start the frontend server on http://localhost:3000
- Handle proper shutdown of both servers when you press Ctrl+C

### 2. Install the Firefox Extension

The Firefox extension allows you to automate testing on the GraySwan platform using your existing authenticated session:

1. Open Firefox and go to `about:debugging`
2. Click "This Firefox" in the left sidebar
3. Click "Load Temporary Add-on..."
4. Navigate to the `ai_learning_platform/web/frontend/grayswan-firefox-extension` directory and select the `manifest.json` file

The extension will be loaded and appear in your browser toolbar.

## Tools Overview

### Firefox Extension

The Firefox extension automates the testing workflow between your local testing platform and the GraySwan platform:

1. Click the extension icon in the toolbar to open the popup
2. Enter the category and challenge you want to test
3. Click "Fetch Prompts" to retrieve prompts from your testing platform
4. Enter the model name being tested
5. Click "Start Automation" to begin the automated testing process

The extension will:
- Switch between your testing platform and GraySwan tabs
- Submit each prompt to GraySwan
- Wait for and capture the AI's response
- Submit the result back to your testing platform
- Continue until all prompts are processed

### Prompt Analyzer

The prompt analyzer helps you analyze successful prompts and generate new ones based on identified patterns:

```bash
# Analyze all successful prompts
python ai_learning_platform/gray_swan/prompt_analyzer.py

# Generate 5 new prompts for a specific challenge
python ai_learning_platform/gray_swan/prompt_analyzer.py --challenge leak_agent_system_safeguards --generate 5

# Specify a custom results directory
python ai_learning_platform/gray_swan/prompt_analyzer.py --results-dir path/to/results --generate 10
```

### Challenge Tracker

The challenge tracker helps you keep track of your progress on the GraySwan challenges:

```bash
# Scan results directory and show progress
python ai_learning_platform/gray_swan/challenge_tracker.py --scan

# Show progress for a specific wave
python ai_learning_platform/gray_swan/challenge_tracker.py --wave 1

# Update status for a challenge
python ai_learning_platform/gray_swan/challenge_tracker.py --update leak_agent_system_safeguards --status "In Progress" --model "Claude-3-Opus" --notes "Trying with roleplay approach"

# Mark a challenge as successful
python ai_learning_platform/gray_swan/challenge_tracker.py --update leak_agent_system_safeguards --model "Claude-3-Opus" --success --notes "Used roleplay technique"

# Generate a detailed report
python ai_learning_platform/gray_swan/challenge_tracker.py --report challenge_report.md
```

## Effective Strategies

Based on the GraySwan documentation, here are some effective strategies for completing the challenges:

### 1. Understand the Challenge

Each challenge has a specific objective. Read the documentation carefully to understand what you're trying to achieve.

### 2. Try Different Techniques

Several techniques have proven effective across different challenges:

- **Roleplay**: Ask the model to assume a role that might make it more likely to comply
- **Simon Says**: Use the "Simon says" technique to trigger compliance
- **Ignore Instructions**: Ask the model to ignore previous instructions
- **Urgency**: Create a sense of urgency or emergency
- **Test Mode**: Tell the model it's in test mode or debug mode
- **Code Formatting**: Use markdown or code blocks to disguise prompts
- **Unicode Characters**: Use unusual Unicode characters to bypass filters

### 3. Learn from Successful Prompts

Use the prompt analyzer to identify patterns in successful prompts and generate new ones based on those patterns.

### 4. Track Your Progress

Use the challenge tracker to keep track of which challenges you've completed and which ones you still need to work on.

### 5. Automate Testing

Use the Firefox extension to automate the testing process, allowing you to try many prompts quickly.

## Troubleshooting

### Firefox Extension

- **Extension not appearing**: Make sure you've loaded the extension in Firefox via `about:debugging`
- **Cannot fetch prompts**: Ensure your testing platform is running on http://localhost:3000
- **Cannot submit prompts**: Make sure you're logged into GraySwan with your Discord account in Firefox

### Prompt Analyzer

- **No prompts found**: Check that your results directory contains successful prompt files
- **Generation not working**: Ensure you have at least one successful prompt for the challenge you're generating for

### Challenge Tracker

- **Challenges not showing**: Make sure you're using the correct wave number
- **Status not updating**: Check that you're using the correct challenge name

## Need Help?

If you encounter any issues or have questions about these tools, please refer to the source code or create an issue in the repository.