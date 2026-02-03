---
name: insight-optimization
description: Guide users through optimizing prompts based on insights from production data
---

# Insight-Based Prompt Optimization

This skill helps users optimize their prompts by analyzing completions associated with specific insights.

## When to Use This Skill

Activate when the user wants to:
- "Optimize a prompt based on an insight"
- "Create a dataset from insight completions"
- "Fix issues identified in [insight name]"
- "Improve prompt based on [insight name] data"

## Workflow

### Option 1: Quick Workflow (Recommended)

Use the `optimize_prompt_from_insight` tool for a one-step solution:

```
optimize_prompt_from_insight(
    project_id="...",
    insight_name="...",
    prompt_template_version_id="...",
)
```

This automatically:
1. Creates a dataset
2. Searches for insight completions
3. Adds test cases
4. Runs optimization

### Option 2: Step-by-Step (More Control)

For users who want more control or visibility:

1. **List insights** to find the relevant one:
   ```
   list_insights(project_id="...")
   ```

2. **Search completions** by insight to preview data:
   ```
   search_completions_by_insight(
       project_id="...",
       insight_name="...",
   )
   ```

3. **Create a dataset** for the test cases:
   ```
   create_prompt_dataset(
       project_id="...",
       name="Insight: [insight_name]",
       description="Dataset for optimizing based on [insight_name]",
   )
   ```

4. **Add completions to dataset**:
   ```
   add_completions_to_dataset(
       project_id="...",
       dataset_id="...",
       completions=[...],  # from step 2
   )
   ```

5. **Run optimization**:
   ```
   optimize_prompt(
       project_id="...",
       prompt_template_version_id="...",
       dataset_id="...",
   )
   ```

## Key Tools

- `list_insights` - Browse available insights
- `search_completions_by_insight` - Find completions for an insight
- `create_prompt_dataset` - Create a new dataset
- `add_completions_to_dataset` - Populate dataset from completions
- `optimize_prompt` - Run optimization on a dataset
- `optimize_prompt_from_insight` - All-in-one workflow

## Best Practices

1. **Start with list_insights** - Help users see what insights exist
2. **Preview data first** - Use `search_completions_by_insight` to show what data will be used
3. **Use descriptive names** - Name datasets clearly (e.g., "Insight: Response Quality Issues - 2024-02-03")
4. **Check record count** - Insights with more records provide better optimization data
5. **Recommend quick workflow** - Unless user needs custom dataset configuration

## Example Conversation

**User**: "I want to fix the issues in the 'Response Quality Issues' insight"

**Assistant**:
1. First, let me search for completions with that insight to see what data we have
2. I'll create a dataset from those completions
3. Then run prompt optimization using that dataset

Would you like me to use the quick workflow (`optimize_prompt_from_insight`) or go step-by-step so you can review the data first?

## Common Questions

**Q: How many completions should I use?**
A: Default is 100. More is better, but 50-100 is usually sufficient.

**Q: Can I use multiple insights?**
A: Not directly. Run separate optimizations for each insight, or manually combine datasets.

**Q: What if no completions are found?**
A: The insight might not have any associated completions, or the insight name might not match exactly. Use `list_insights` to verify the exact name.
