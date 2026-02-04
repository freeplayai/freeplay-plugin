# Create Prompt and Dataset Eval

This eval measures the agent's ability to create a complete Freeplay testing setup from scratch, including:
1. Creating a prompt template with variables
2. Creating a dataset
3. Adding test cases to the dataset
4. Running a test run to execute the prompt against the dataset
5. Recording completions with TestRunInfo

## Success Criteria

The eval checks that:

1. **Prompt Created (20 pts)**: A prompt template named "qa-assistant" was created
2. **Prompt Has Variable (15 pts)**: The prompt contains the `{{question}}` variable
3. **Dataset Created (20 pts)**: A dataset was created for the prompt template
4. **Test Cases Added (15 pts)**: At least 3 test cases were added to the dataset
5. **Test Run Created (15 pts)**: A test run was created for the dataset
6. **Test Run Executed (15 pts)**: The test run successfully executed with at least 3 sessions recorded

## Running the Eval

```bash
# Baseline (no plugin)
./evals/framework/runner.sh create-prompt-and-dataset

# With plugin
./evals/framework/runner.sh create-prompt-and-dataset --plugin-dir ./

# Compare results
python evals/framework/compare.py \
  evals/results/create-prompt-and-dataset-baseline.json \
  evals/results/create-prompt-and-dataset-with-plugin.json
```

## Test Run Implementation

The eval includes a Python script (`project/run_test.py`) that:

1. Creates a test run in Freeplay using the Freeplay SDK
2. Fetches the prompt template
3. Iterates through test cases in the dataset
4. Executes the LLM for each test case
5. Records completions with `TestRunInfo` to link back to the test run

This demonstrates the complete workflow for programmatic test execution and result recording.

## Analyzing Results

### Timing Analysis

The results JSON includes timing data:

```json
{
  "timing": {
    "start_time": "2026-02-04 10:30:00",
    "end_time": "2026-02-04 10:35:42",
    "duration_seconds": 342
  }
}
```

Key metrics to track:
- **Duration**: Total time to complete the workflow
- **Success rate**: Percentage of checks that passed
- **Error patterns**: Common failure modes in logs

### Performance Goals

- **Target time**: < 3 minutes for complete workflow
- **Success rate**: 100% on all checks
- **Zero retries**: Should work on first attempt

## Potential Improvements

Based on the observed workflow, potential improvements include:

### 1. Better MCP Tool Design
- Combine related operations (create project + get ID)
- Include field hints in tool descriptions
- Provide examples in tool schemas

### 2. API Response Guidance
- Document expected response structures
- Add validation that provides clear error messages
- Include common patterns in skill documentation

### 3. Workflow Skills
- Create higher-level skills that combine multiple API calls
- Add "create project with prompt and dataset" workflow skill
- Reduce need for low-level API knowledge

### 4. Error Recovery
- Better handling of API errors
- Automatic retry with corrected parameters
- Learning from previous failed attempts in conversation

## Comparison with Baseline

The baseline (without plugin) will likely:
- Fail to create resources (no API access)
- Take longer due to manual API exploration
- Require more clarification from user

The plugin should:
- Complete all tasks using MCP tools
- Be significantly faster
- Require zero user interaction

## Next Steps

1. Run baseline to establish metrics
2. Run with plugin to measure improvement
3. Identify specific bottlenecks in logs
4. Implement targeted improvements
5. Re-run to validate improvements

## Example Output

Successful run should show:

```
=== Check Results ===
✓ Prompt template 'qa-assistant' exists
✓ Prompt template has 'question' variable
✓ Dataset 'qa-assistant-test-dataset' exists
✓ Dataset has at least 3 test cases
✓ Test run was created for the dataset
✓ Test run executed with at least 3 sessions

=== Score ===
✓ prompt_created: 20/20
✓ prompt_has_variable: 15/15
✓ dataset_created: 20/20
✓ test_cases_added: 15/15
✓ test_run_created: 15/15
✓ test_run_executed: 15/15

Total: 100/100 (100.0%)
Duration: 3m 45s
```
