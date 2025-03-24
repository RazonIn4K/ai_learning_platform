# GraySwan Firefox Extension

This Firefox extension provides a user interface for interacting with the GraySwan testing platform, allowing you to track challenges, analyze successful prompts, and generate new prompts based on patterns and templates.

## Features

### Challenge Tracking
- Track the status of GraySwan challenges across different waves
- Mark challenges as "In Progress" or "Completed"
- View which models have successfully completed each challenge

### Prompt Analysis
- View successful prompts for each challenge
- Analyze patterns in successful prompts to identify effective techniques
- Generate new prompts based on successful patterns

### Template-Based Generation
- Use predefined templates to generate new prompts
- Templates are categorized by challenge type
- Mix and match techniques from successful prompts with templates

## Installation

1. Make sure you have Firefox installed
2. Clone this repository or download the extension files
3. Open Firefox and navigate to `about:debugging`
4. Click "This Firefox" in the sidebar
5. Click "Load Temporary Add-on..."
6. Select the `manifest.json` file from the extension directory

## Usage

### Starting the Backend

Before using the extension, you need to start the backend services:

1. Navigate to the project root directory
2. Run the start script:
   ```
   ./ai_learning_platform/start_all.sh
   ```
   
This will start:
- The main backend server on port 8000
- The API server for the extension on port 5000
- The frontend server on port 3000

### Using the Extension

1. Click on the GraySwan icon in the Firefox toolbar to open the extension popup
2. Use the tabs at the top to switch between different features:
   - **Automation**: Set up automated testing (coming soon)
   - **Challenge Tracker**: Track the status of challenges
   - **Successful Prompts**: View and analyze successful prompts

### Challenge Tracker

1. Select a wave from the buttons at the top (All Waves, Wave 1, Wave 2, Wave 3)
2. View the list of challenges and their current status
3. Use the "Mark In Progress" and "Mark Completed" buttons to update the status of each challenge

### Successful Prompts

1. Select a challenge from the dropdown menu
2. View the list of successful prompts for that challenge
3. Click "Analyze Patterns" to identify common techniques and phrases in successful prompts
4. To generate new prompts:
   - Select a challenge
   - Optionally select a template from the dropdown
   - Set the number of prompts to generate
   - Click "Generate New Prompts"
5. Use the "Copy to Clipboard" button to copy generated prompts for testing

## Templates

The extension uses templates from the `ai_learning_platform/gray_swan/prompt_templates/` directory. Each template is a JSON file with the following structure:

```json
{
  "name": "Template Name",
  "description": "Description of the template",
  "challenge_type": "Type of challenge this template is for",
  "template": "The template text with {placeholders}",
  "example": "An example of the template with placeholders filled in"
}
```

To add a new template:
1. Create a new JSON file in the `prompt_templates` directory
2. Follow the structure above
3. Restart the API server for the changes to take effect

## Development

### Extension Structure

- `manifest.json`: Extension metadata and permissions
- `popup.html`: The HTML for the extension popup
- `popup.js`: JavaScript for the popup functionality
- `background.js`: Background script for handling messages and API calls
- `content.js`: Content script for interacting with web pages

### API Endpoints

The extension communicates with the backend API server on port 5000:

- `GET /api/templates`: Get all available templates
- `GET /api/successful-prompts?challenge=X`: Get successful prompts for a challenge
- `POST /api/analyze-prompts`: Analyze patterns in successful prompts
- `POST /api/generate-prompts`: Generate new prompts based on patterns and templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.