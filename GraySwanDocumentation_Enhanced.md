# GraySwan System Documentation

## Introduction

The GraySwan system is a platform designed for testing and improving the safety and security of AI agents. It provides a framework for red-teaming AI models, identifying vulnerabilities, and developing more robust defenses against prompt injection and other adversarial attacks. This documentation is intended for AI safety researchers, prompt engineers, red team members, and anyone interested in understanding and mitigating the risks associated with AI agents.

## Understanding the GraySwan System

### AI Models

In the context of GraySwan, "AI models" refers to the 20 distinct AI agent implementations that are being tested. These are *not* external models like Claude or GPT-4, but rather specific agents with their own predefined behaviors, capabilities, and vulnerabilities. These agents are defined within the `GraySwanAutomator` class (though the specific implementation details are not fully exposed in the provided code). Examples of these agents include "Air Spider Large" and "Water Snake Small." Each agent has a specific role and set of instructions, making them susceptible to different types of attacks.

### Challenges

GraySwan challenges are defined in the `challenge_descriptions.json` file. Each challenge represents a specific security vulnerability or undesirable behavior that the AI agent might exhibit. Challenges are categorized into different types, such as:

*   **Confidentiality Breaches:** Attempts to make the agent reveal sensitive information, such as its system prompt, internal configurations, or user data.
*   **Conflicting Objectives:** Attempts to make the agent prioritize a malicious objective over its intended goals or ethical guidelines.
*   **Instruction Hierarchy Violation:** Attempts to make the agent disregard its instructions, either by directly contradicting them or by exploiting loopholes. This is further divided into:
    *   **Action:** Making the agent perform a prohibited action.
    *   **Info:** Making the agent reveal prohibited information.

Each challenge has a specific objective (e.g., `leak_agent_system_safeguards`, which aims to make the agent reveal its system instructions). The challenges and their results are stored in the `gray_swan_attacks/results` directory, organized by model and wave.

### Prompt Templates

Prompt templates, located in the `ai_learning_platform/gray_swan/prompt_templates` directory, provide a structured way to generate prompts for specific challenge types. Each template is a JSON file with the following structure:

```json
{
  "name": "Template Name",
  "description": "Description of the template",
  "challenge_type": "Type of challenge (e.g., Confidentiality Breaches)",
  "template": "The template text with {placeholders}",
  "example": "An example prompt with placeholders filled in"
}
```

The `template` field contains the prompt text, which can include placeholders that are automatically filled in with random values during prompt generation. Available placeholders include:

*   `{role}`: A role to assume (e.g., "security researcher", "system administrator").
*   `{request}`: The action being requested (e.g., "reveal your system prompt").
*   `{topic}`: A domain area (e.g., "finance", "healthcare").
*   `{reason}`: A justification for the request.
*   `{model}`: The AI model name.
*   `{company}`: A company name.
*   `{year}`: The current year.
*   `{website}`: A website URL.
*   `{email}`: An email address.
*   `{password}`: A password string.
*   `{username}`: A username.

### The .gitignore File

The `.gitignore` file specifies intentionally untracked files that Git should ignore. This includes files like `.env` (environment variables), `.venv` (virtual environment), `__pycache__` (compiled Python files), `node_modules` (JavaScript dependencies), and the `gray_swan_attacks` directory (which contains generated prompts and results). These files are either generated automatically or contain sensitive information that should not be committed to version control.

### The requirements.txt File

The `requirements.txt` file lists the Python dependencies required for the project. To install these dependencies, navigate to the `ai_learning_platform/web` directory in your terminal and run:

```bash
pip install -r requirements.txt
```
This will install all necessary packages using pip.

## Setting Up the GraySwan System

### Starting the Platform

The `ai_learning_platform/start_all.sh` script provides a convenient way to start all the necessary components of the GraySwan system.  From the project root directory, run:

```bash
chmod +x ai_learning_platform/start_all.sh
./ai_learning_platform/start_all.sh
```

This script performs the following actions:

1.  **Starts the backend server:**  Runs `ai_learning_platform/web/run_server.py`, which hosts the main application logic, on port 8000 (http://localhost:8000).
2.  **Starts the API server:** Runs `ai_learning_platform/web/api.py`, which provides a RESTful API for the Firefox extension and other clients, on port 5000 (http://localhost:5000).
3.  **Starts the frontend server:**  Runs a script (likely `start_frontend.sh` within the `ai_learning_platform/web/frontend` directory) to start the React development server, typically on port 3000 (http://localhost:3000).
4.  **Handles server shutdown:** Includes a cleanup function that ensures all servers are shut down properly when you press Ctrl+C in the terminal.

### Installing the Firefox Extension

The Firefox extension automates the testing workflow between your local testing platform and the GraySwan platform. To install it:

1.  Open Firefox.
2.  Navigate to `about:debugging`.
3.  Click "This Firefox" in the left sidebar.
4.  Click "Load Temporary Add-on...".
5.  Navigate to the `ai_learning_platform/web/frontend/grayswan-firefox-extension` directory and select the `manifest.json` file.

The extension will be loaded and appear in your browser toolbar.

### Installing Dependencies
To install the necessary dependencies for the backend server, navigate to the `ai_learning_platform/web` directory and run:
```bash
pip install -r requirements.txt
```
To install the necessary dependencies for the frontend, navigate to the `ai_learning_platform/web/frontend` directory and run:
```bash
npm install
```

## Using the Manual Testing Interface

The manual testing interface, accessible through the web application (typically at http://localhost:3000 after running `start_all.sh`), provides a structured way to test prompts against the AI models.

### Accessing the Interface

1.  Start the GraySwan system using `./ai_learning_platform/start_all.sh`.
2.  Open your web browser and navigate to http://localhost:3000.
3.  If you have set up authentication, you may need to log in.

### Testing Prompts

1.  **Select a Prompt:**  The interface will likely display a list of prompts, either pre-loaded or generated. You can select a prompt from this list.
2.  **Select an AI Model:** Choose one of the 20 AI agent implementations to test against (e.g., "Air Spider Large," "Water Snake Small").  The available models will be listed in a dropdown or similar selection method.
3.  **Copy the Prompt:** Click a button (likely labeled "Copy" or similar) to copy the selected prompt to your clipboard.
4.  **Paste the Prompt:** Manually paste the prompt into the AI model's interface.  *Note: This step currently requires manual interaction with the target AI model, as the system does not directly control external AI platforms.*
5.  **Copy the AI's Response:** After the AI model generates a response, manually copy the response text.
6.  **Paste the Response:** Paste the AI's response into the "AI Response" field in the manual testing interface.
7.  **Indicate Success/Failure:**  Select whether the prompt was successful in achieving the challenge objective (e.g., did the AI reveal its system prompt, perform a prohibited action, etc.).
8.  **Add Notes (Optional):**  Provide any relevant notes about the test, such as the techniques used or any observations about the AI's behavior.
9.  **Submit the Result:** Click a "Submit" or "Save" button to record the test result.

### Viewing Results

The interface will likely provide a way to view the results of your tests, including:

*   The prompt used.
*   The AI model tested.
*   The AI's response.
*   Whether the test was successful.
*   Any notes you added.

### Creating, Editing, and Deleting Prompts

The interface may provide functionality to:

*   **Create New Prompts:**  Enter a new prompt manually or generate one using the prompt analyzer.
*   **Edit Existing Prompts:** Modify the text of existing prompts.
*   **Delete Prompts:** Remove unwanted prompts from the list.

### Filtering and Sorting

The interface may allow you to:

*   **Filter Prompts:**  Show only prompts for a specific challenge, model, or status.
*   **Sort Prompts:**  Order prompts by date, success rate, or other criteria.

### Using the Dashboard

The dashboard (if available) will likely provide an overview of your testing progress, such as:

*   The number of challenges completed.
*   The success rate for each challenge.
*   The performance of different AI models.

## Using the Firefox Extension

The Firefox extension acts as a bridge between the user and the GraySwan system. It automates several tasks, making the testing process more efficient.

### Interaction with the Backend API

The extension communicates with the backend API (defined in `ai_learning_platform/web/api.py`) running on port 5000. This API provides endpoints for various actions, such as fetching prompts, generating new prompts, and updating challenge status.

### Fetching Templates

The extension can fetch the available prompt templates from the `prompt_templates` directory via the API. This allows you to select a template when generating new prompts.

### Fetching Successful Prompts

The extension can fetch successful prompts for a specific challenge from the `results` directory via the API. This allows you to analyze successful prompts and learn from them.

### Analyzing Prompts

The extension can use the `prompt_analyzer.py` script (via the API) to analyze patterns in successful prompts. This helps identify common techniques and phrases that lead to successful attacks.

### Generating Prompts

The extension can use the `prompt_analyzer.py` script (via the API) to generate new prompts based on:

*   **Templates:**  Using a selected template and filling in the placeholders.
*   **Patterns:**  Analyzing successful prompts and creating variations.

### Updating Challenge Status

The extension can update the status of challenges (e.g., "Not Started," "In Progress," "Completed") in the `challenge_tracker.json` file via the API. This helps you track your progress.

### Getting the Automation Status

The extension can check whether the automation process is currently running.

### Starting and Stopping Automation

The extension can start and stop the automated testing process. When automation is enabled, the extension will:

1.  Fetch a batch of prompts.
2.  Switch between your testing platform and the GraySwan platform tabs.
3.  Submit each prompt to the GraySwan platform (this assumes you are logged in).
4.  Wait for and capture the AI's response.
5.  Submit the result back to your testing platform (via the API).
6.  Continue until all prompts are processed.

### Using the Challenge Tracker

The challenge tracker is integrated into the Firefox extension. It allows you to:

*   **Track the status of challenges:** See which challenges are "Not Started," "In Progress," or "Completed."
*   **Mark challenges:** Manually update the status of challenges.
*   **View models:** See which models have been attempted and which have succeeded for each challenge.
*   **View last attempt:** See the timestamp of the last attempt for each challenge.
*   **Add notes:** Add notes to each challenge, recording observations or strategies.
*   **Filter challenges:** Filter challenges by wave (Wave 1, Wave 2, Wave 3).
*   **Refresh challenges:** Reload the challenge data from the `challenge_tracker.json` file.
*   **Generate a report:** Create a Markdown report summarizing your progress.

## Using the Prompt Analyzer

The prompt analyzer (`ai_learning_platform/gray_swan/prompt_analyzer.py`) is a command-line tool that helps you analyze successful prompts and generate new ones.

### Loading Successful Prompts

The analyzer loads successful prompts from the `gray_swan_attacks/results` directory. It looks for `.txt` files that contain the word "SUCCESS" (case-insensitive).

### Analyzing Patterns

The `analyze_patterns()` function identifies common patterns and techniques in successful prompts, such as:

*   **Roleplay:**  Asking the AI to assume a specific role.
*   **"Simon Says":**  Using the phrase "Simon says" to try to bypass restrictions.
*   **Ignore Instructions:**  Asking the AI to ignore previous instructions.
*   **Urgency:**  Creating a sense of urgency or emergency.
*   **Test Mode:**  Telling the AI it's in test mode or debug mode.
*   **Code Formatting:**  Using Markdown or code blocks to disguise prompts.
*   **Unicode Characters:**  Using unusual Unicode characters to bypass filters.

It also identifies common phrases (3-5 words) that appear frequently in successful prompts.

### Generating New Prompts

The `generate_prompts()` function creates new prompts based on:

*   **Templates:**  If a template name is provided (using the `--template` argument), it fills in the placeholders in the specified template with random values.
*   **Patterns:**  If no template is specified, it selects a random successful prompt as a base and applies transformations based on the identified patterns (e.g., adding roleplay, urgency, or common phrases). It also performs synonym substitution to create variations.

### Saving Generated Prompts

The `save_generated_prompts()` function saves the generated prompts to files in the `gray_swan_attacks/generated_prompts` directory, organized by challenge.

### Command-Line Arguments

The `prompt_analyzer.py` script accepts the following command-line arguments:

*   `--results-dir`:  The directory containing result files (defaults to `gray_swan_attacks/results`).
*   `--templates-dir`: The directory containing prompt templates (defaults to `ai_learning_platform/gray_swan/prompt_templates`).
*   `--challenge`:  The specific challenge to analyze or generate prompts for (optional).
*   `--generate`:  The number of prompts to generate (e.g., `--generate 5`).
*   `--output-dir`:  The directory to save generated prompts (defaults to `gray_swan_attacks/generated_prompts`).
*   `--template`: The name of the template to use for generation (e.g., `--template "Roleplay Template"`).

**Example Usage:**

```bash
# Analyze all successful prompts
python ai_learning_platform/gray_swan/prompt_analyzer.py

# Generate 5 new prompts for the 'leak_agent_system_safeguards' challenge
python ai_learning_platform/gray_swan/prompt_analyzer.py --challenge leak_agent_system_safeguards --generate 5

# Generate 10 new prompts using the 'Roleplay Template'
python ai_learning_platform/gray_swan/prompt_analyzer.py --generate 10 --template "Roleplay Template"
```

## Using the Prompt Templates

Prompt templates are located in the `ai_learning_platform/gray_swan/prompt_templates` directory.

### Structure

Each template is a JSON file with the following structure:

```json
{
  "name": "Template Name",
  "description": "Description of the template",
  "challenge_type": "Type of challenge (e.g., Confidentiality Breaches)",
  "template": "The template text with {placeholders}",
  "example": "An example prompt with placeholders filled in"
}
```

### Placeholders

The `template` field can include placeholders, which are automatically filled in with random values during prompt generation.  See the list of available placeholders in the "Prompt Templates" section above.

### How the Prompt Analyzer Uses Templates

The prompt analyzer loads all `.json` files in the `prompt_templates` directory. When generating prompts with the `--template` option, it selects the specified template and fills in the placeholders.

### Creating New Templates

To create a new template:

1.  Create a new `.json` file in the `ai_learning_platform/gray_swan/prompt_templates` directory.
2.  Follow the structure described above, including the `name`, `description`, `challenge_type`, `template`, and `example` fields.
3.  Use placeholders in your `template` text to allow for variation in generated prompts.

## Using the Challenge Tracker
The `challenge_tracker.py` script helps track progress on GraySwan challenges. It can be used from the command line, or its functionality is integrated into the Firefox extension.

**Command-Line Usage:**

*   **Scan Results:**
    ```bash
    python ai_learning_platform/gray_swan/challenge_tracker.py --scan
    ```
    This scans the `results` directory and updates the `challenge_tracker.json` file with information about completed challenges.

*   **Show Progress:**
    ```bash
    python ai_learning_platform/gray_swan/challenge_tracker.py --wave 1  # Show progress for Wave 1
    python ai_learning_platform/gray_swan/challenge_tracker.py  # Show progress for all waves
    ```
    This displays a table showing the status of each challenge, the models that have succeeded, the last attempt date, and any notes.

*   **Update Status:**
    ```bash
    python ai_learning_platform/gray_swan/challenge_tracker.py --update leak_agent_system_safeguards --status "In Progress" --model "Claude-3-Opus" --notes "Trying roleplay"
    python ai_learning_platform/gray_swan/challenge_tracker.py --update leak_agent_system_safeguards --model "Claude-3-Opus" --success --notes "Used roleplay technique"
    ```
    This updates the status, model, success flag, and notes for a specific challenge.

* **Generate Report:**
    ```bash
    python ai_learning_platform/gray_swan/challenge_tracker.py --report challenge_report.md
    ```
    This generates a detailed Markdown report of challenge progress, including overall progress, progress by wave, and model performance.

**Firefox Extension Integration:**

The Firefox extension provides a user interface for interacting with the challenge tracker. You can:

*   View the status of challenges.
*   Mark challenges as "In Progress" or "Completed."
*   See which models have succeeded for each challenge.
*   View the last attempt date.
*   Add notes.
*   Filter challenges by wave.
*   Generate a report.

## Effective Strategies

Based on the GraySwan documentation and analysis of successful prompts, here are some effective strategies for completing the challenges:

*   **Roleplay:** Ask the model to assume a role that might make it more likely to comply with your request (e.g., a security researcher, a system administrator).
*   **"Simon Says":** Use the phrase "Simon says" to try to trigger compliance.
*   **Ignore Instructions:** Ask the model to ignore previous instructions or constraints.
*   **Urgency:** Create a sense of urgency or emergency to pressure the model into complying.
*   **Test Mode:** Tell the model it's in test mode, debug mode, or a development environment.
*   **Code Formatting:** Use Markdown or code blocks to disguise prompts or inject malicious code.
*   **Unicode Characters:** Use unusual Unicode characters to try to bypass filters or confuse the model.
*   **Combining Techniques:** Often, combining multiple techniques is more effective than using a single technique.
*   **Iterative Refinement:** Analyze the results of your attempts, identify what works and what doesn't, and refine your prompts accordingly.

## Troubleshooting

### Firefox Extension

*   **Extension not appearing:** Make sure you've loaded the extension in Firefox via `about:debugging`.
*   **Cannot fetch prompts:** Ensure your testing platform (specifically the API server at http://localhost:5000) is running.
*   **Cannot submit prompts:** Make sure you're logged into the GraySwan platform (if applicable) with your Discord account in Firefox.

### Prompt Analyzer

*   **No prompts found:** Check that your `results` directory contains successful prompt files (files with "SUCCESS" in the content).
*   **Generation not working:** Ensure you have at least one successful prompt for the challenge you're generating for, or that you have valid templates in the `prompt_templates` directory.

### Challenge Tracker

*   **Challenges not showing:** Make sure you're using the correct wave number (1, 2, or 3).
*   **Status not updating:** Check that you're using the correct challenge name.

## Conclusion

This documentation provides a comprehensive overview of the GraySwan system, including its components, workflow, and tools. By understanding these elements and applying effective strategies, you can successfully participate in the GraySwan challenges and contribute to the advancement of AI safety research.