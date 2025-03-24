# GraySwan Firefox Extension

A Firefox extension that automates testing on the GraySwan platform using your existing authenticated session.

## Features

- **Automation Tab**
  - Fetch prompts from your testing platform
  - Automatically submit prompts to GraySwan
  - Capture AI responses
  - Submit results back to your testing platform

- **Challenge Tracker Tab**
  - Track progress on all GraySwan challenges
  - View which challenges are completed and which ones are still in progress
  - Mark challenges as "In Progress" or "Completed"
  - Generate progress reports
  - Filter challenges by wave

- **Successful Prompts Tab**
  - View successful prompts for each challenge
  - Copy successful prompts to reuse them
  - See which models were successful for each challenge

## Installation

1. Open Firefox and go to `about:debugging`
2. Click "This Firefox" in the left sidebar
3. Click "Load Temporary Add-on..."
4. Navigate to the `ai_learning_platform/web/frontend/grayswan-firefox-extension` directory and select the `manifest.json` file

The extension will be loaded and appear in your browser toolbar.

## Usage

### Automation Tab

1. Enter the category and challenge you want to test
2. Click "Fetch Prompts" to retrieve prompts from your testing platform
3. Enter the model name being tested
4. Click "Start Automation" to begin the automated testing process

The extension will:
- Switch between your testing platform and GraySwan tabs
- Submit each prompt to GraySwan
- Wait for and capture the AI's response
- Submit the result back to your testing platform
- Continue until all prompts are processed

### Challenge Tracker Tab

1. Select a wave (1, 2, 3, or All) to filter challenges
2. View your progress on each challenge
3. Click "Mark In Progress" to update a challenge's status
4. Click "Mark Completed" to mark a challenge as completed
5. Click "Refresh Challenges" to update the display
6. Click "Generate Report" to create a markdown report of your progress

### Successful Prompts Tab

1. Select a challenge from the dropdown
2. View all successful prompts for that challenge
3. Click "Copy Prompt" to copy a prompt to the clipboard

## Requirements

- Firefox browser
- Active Discord authentication on GraySwan (https://app.grayswan.ai/arena/chat/agent-red-teaming)
- Local testing platform running on http://localhost:3000

## Notes

This extension is designed to work with your existing authenticated session in Firefox, eliminating the need for handling authentication. It automates the testing workflow between your local testing platform and the GraySwan platform.

The extension stores your challenge progress and successful prompts in the browser's local storage, so you can track your progress over time.