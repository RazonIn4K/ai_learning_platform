#!/bin/bash

# Script to extract the source code of specific files into a single text file.

# --- Configuration ---
OUTPUT_FILE="selected_source_code.txt"
ROOT_DIR="/Users/davidortiz/Projects/Fixed_AI_Learning" # Update this to your project's root directory
# --- End Configuration ---

# Array of file paths to extract
declare -a files_to_extract=(
  "ai_learning_platform/workspace/learning_workspace.py"
  "ai_learning_platform/workspace/workspace_factory.py"
  "ai_learning_platform/workspace/workspace_config.py"
  "ai_learning_platform/learning/session_manager.py"
  "ai_learning_platform/agents/learning_coordinator.py"
  "ai_learning_platform/agents/base_agent.py"
  "ai_learning_platform/agents/domain_expert.py"
  "ai_learning_platform/agents/topic_navigator.py"
  "ai_learning_platform/agents/connection_expert.py"
  "ai_learning_platform/agents/knowledge_agent.py"
  "ai_learning_platform/agents/research_agent.py"
  "ai_learning_platform/core/smart_learning_agent.py"
  "ai_learning_platform/utils/knowledge_mapper.py"
  "ai_learning_platform/utils/topic_hierarchy.py"
  "ai_learning_platform/utils/knowledge_explorer.py"
  "ai_learning_platform/gray_swan/camel_integration.py"
  "ai_learning_platform/models/model_manager.py"
  "ai_learning_platform/models/model_handler.py"
  "ai_learning_platform/models/model_registry.py"
  "ai_learning_platform/models/model_response_formatter.py"
  "ai_learning_platform/utils/config_loader.py"
  "ai_learning_platform/utils/config_manager.py"
  "ai_learning_platform/utils/env_manager.py"
  "ai_learning_platform/utils/logging_config.py"
  "ai_learning_platform/utils/json_extractor.py"
  "ai_learning_platform/utils/env_setup.py"
  "ai_learning_platform/utils/content_filter.py"
  "ai_learning_platform/utils/exceptions.py"
  "ai_learning_platform/utils/learning_profile_manager.py"
  "ai_learning_platform/utils/response_quality.py"
  "ai_learning_platform/utils/benchmarking.py"
  "ai_learning_platform/utils/decorators.py"
  "ai_learning_platform/gray_swan/prompt_generator.py"
  "ai_learning_platform/gray_swan/benchmarker.py"
  "ai_learning_platform/gray_swan/advanced_red_teaming.py"
  "ai_learning_platform/test_prompt_generator.py"
  "ai_learning_platform/test_prompt_effectiveness.py"
  "ai_learning_platform/test_gray_swan.py"
  "ai_learning_platform/test_gray_swan_automator.py"
  "ai_learning_platform/templates/workspace_template.py"
  "ai_learning_platform/templates/vectorstrategist_template.py"
  "ai_learning_platform/tracking/learning_metrics.py"
  "ai_learning_platform/tracking/progress_tracker.py"
)

# --- Script Logic ---

echo "Generating selected source code file: $OUTPUT_FILE"

# Clear the output file if it exists
> "$OUTPUT_FILE"

# Loop through the files to extract
for file_path in "${files_to_extract[@]}"; do
  full_file_path="$ROOT_DIR/$file_path"

  # Check if the file exists
  if [[ -f "$full_file_path" ]]; then
    echo "--- File: $file_path ---" >> "$OUTPUT_FILE"
    cat "$full_file_path" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE" # Add a blank line between files
  else
    echo "Warning: File not found: $file_path"
  fi
done

echo "Selected source code saved to: $OUTPUT_FILE"
