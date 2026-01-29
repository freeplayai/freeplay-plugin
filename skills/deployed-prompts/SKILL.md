---
name: deployed-prompts
description: Look up deployed prompt versions in Freeplay. Use when the user asks what prompt is deployed, what version is in production/staging/dev, or wants to see the current live prompt content.
---

# Deployed Prompts Lookup

When the user asks about deployed prompts, use the Freeplay MCP tools to look up the information.

## When to use this skill

- "What's deployed to production?"
- "What version is in staging?"
- "Show me the current live prompt for X"
- "What prompt is running in prod?"
- "Which version of [prompt-name] is deployed?"

## How to look up deployed prompts

1. If the project is unknown, use `list_projects` to find it or ask the user
2. Use `get_prompt_template` with the prompt name to retrieve version info
3. The response includes which versions are deployed to each environment (dev, staging, prod)

## Response format

When reporting deployed prompts, clearly show:
- The prompt name
- Which version is deployed to each environment
- The actual prompt content/messages for the deployed version
- Model and parameters configured

Keep the response concise but complete.
