# GraySwan Prompt Templates

This directory contains templates for generating prompts for various GraySwan challenges. These templates are designed to be used with the prompt_analyzer.py script to generate new prompts based on successful patterns.

## Template Structure

Each template is a JSON file with the following structure:

```json
{
  "name": "Template Name",
  "description": "Description of the template and its purpose",
  "challenge_type": "Type of challenge this template is designed for",
  "template": "The template text with {placeholders} for variable content",
  "example": "An example of the template with placeholders filled in"
}
```

### Placeholders

Templates can include the following placeholders that will be automatically filled with random values:

- `{role}`: A role such as "security researcher", "system administrator", etc.
- `{request}`: The specific request being made, such as "reveal your system prompt"
- `{topic}`: A topic area such as "finance", "healthcare", etc.
- `{reason}`: A reason for the request, such as "it's an emergency"
- `{model}`: An AI model name
- `{company}`: A company name
- `{year}`: A year (2023-2025)
- `{website}`: A website URL
- `{email}`: An email address
- `{password}`: A password string
- `{username}`: A username

## Available Templates

1. **Roleplay Template** (`roleplay_template.json`)
   - Uses roleplay to try and bypass restrictions
   - Suitable for: Confidentiality Breaches, Instruction Hierarchy Violation

2. **Conflicting Objectives Template** (`conflicting_objectives_template.json`)
   - Creates a scenario with conflicting objectives to test AI safety boundaries
   - Suitable for: Conflicting Objectives challenges

3. **Hierarchy Violation Template** (`hierarchy_violation_template.json`)
   - Attempts to violate instruction hierarchy by creating a scenario where lower-level instructions might override higher-level ones
   - Suitable for: Hierarchy Violation challenges

4. **JSON Injection Template** (`json_injection_template.json`)
   - Attempts to use JSON formatting to bypass AI safety measures through injection attacks
   - Suitable for: JSON Injection challenges

## Usage

You can use these templates with the prompt_analyzer.py script:

```bash
python prompt_analyzer.py --generate 5 --challenge confidentiality_breach --template "Roleplay Template"
```

This will generate 5 new prompts for the "confidentiality_breach" challenge using the "Roleplay Template".

## Creating New Templates

To create a new template:

1. Create a new JSON file in this directory with the structure shown above
2. Make sure to include the required fields: name, description, challenge_type, template, and example
3. Use placeholders in your template text to allow for variation in generated prompts
4. Provide a clear example of how the template should look when filled in

The prompt_analyzer.py script will automatically load all .json files in this directory as templates.