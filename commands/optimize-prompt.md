---
description: Optimize a Freeplay prompt - fetch it, suggest improvements, create a new version, and deploy
---

# Optimize Prompt

Help the user optimize a prompt in their Freeplay workspace.

## Workflow

### 1. Identify the prompt

If the user provided a prompt name, use it. Otherwise:
- Use `list_projects` to show available projects and ask which one
- Use `list_prompt_templates` to show prompts in the selected project
- Ask the user which prompt to optimize

### 2. Fetch current prompt

Use `get_prompt_template` to retrieve the current prompt content and versions.

Display the current prompt to the user clearly, showing:
- The prompt messages/template
- Current model and parameters
- Which version is deployed to each environment

### 3. Analyze and suggest improvements

Review the prompt and suggest concrete improvements. Consider:
- Clarity and specificity of instructions
- Structure and organization
- Edge case handling
- Output format specifications
- Few-shot examples if beneficial
- System prompt best practices

Present your suggested changes clearly, explaining the reasoning for each improvement.

### 4. Get user approval

Ask the user if they want to proceed with the suggested changes. They may want to:
- Accept all suggestions
- Modify some suggestions
- Add additional changes
- Cancel the optimization

### 5. Create new version

Once approved, use `create_prompt_version` to create a new version with the optimized prompt.

### 6. Deploy (optional)

Ask the user if they want to deploy the new version. If yes:
- Ask which environment (dev, staging, prod)
- Use `deploy_prompt_version` to deploy

## Arguments

The user may provide:
- `$ARGUMENTS` - prompt name or "project/prompt" format

## Example Usage

```
/freeplay:optimize-prompt my-assistant-prompt
/freeplay:optimize-prompt myproject/chat-prompt
```
