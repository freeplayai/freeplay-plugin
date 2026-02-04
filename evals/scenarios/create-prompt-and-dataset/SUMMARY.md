# Create Prompt and Dataset Eval - Summary

## What Was Built

Based on your experience creating a Freeplay project with prompt and dataset, I've created a comprehensive evaluation system to measure and improve this workflow.

### Components Created

1. **Eval Scenario** (`scenario.json`)
   - Task definition matching your workflow
   - 5 success criteria checking each step
   - Points-based scoring system (100 total points)

2. **Verification Methods** (added to `framework/verify.py`)
   - `verify_project_created()` - Check if project exists
   - `verify_prompt_has_variable()` - Validate variable usage
   - `verify_dataset_exists()` - Confirm dataset creation
   - `verify_dataset_has_test_cases()` - Count test cases

3. **API Client Extensions** (added to `FreeplayAPI` class)
   - `list_projects()` - Get all projects
   - `get_prompt_template_version()` - Fetch prompt details
   - `list_prompt_datasets()` - List datasets
   - `get_dataset_test_cases()` - Get test cases

4. **Documentation**
   - `README.md` - Scenario overview and usage
   - `ANALYSIS_GUIDE.md` - How to analyze results and improve
   - `SUMMARY.md` - This file

## Quick Start

```bash
# Navigate to evals directory
cd /Users/brian/workstation/freeplay-plugin/evals

# Ensure .env is configured
cat .env  # Should have FREEPLAY_API_KEY, FREEPLAY_BASE_URL, etc.

# Run the eval with plugin
./framework/runner.sh create-prompt-and-dataset --plugin-dir ../

# View results
cat results/create-prompt-and-dataset-with-plugin.json | jq '.'

# Check timing
cat results/create-prompt-and-dataset-with-plugin.json | jq '.timing'
```

## What It Measures

### Primary Metrics

1. **Completion Time**
   - Total duration from start to finish
   - Broken down by phase in logs
   - Target: < 3 minutes

2. **Success Rate**
   - Percentage of checks passed (0-100%)
   - Individual check results
   - Target: 100%

3. **Retry Patterns**
   - How many attempts for each API call
   - Which operations fail most often
   - Target: 0 retries

### Detailed Checks

| Check | Points | What It Validates |
|-------|--------|-------------------|
| Project Created | 20 | New project exists with correct name |
| Prompt Created | 25 | Prompt template exists and is valid |
| Prompt Has Variable | 15 | Template uses {{question}} variable |
| Dataset Created | 20 | Dataset linked to prompt template |
| Test Cases Added | 20 | At least 3 test cases in dataset |

## Expected Results

### Baseline (No Plugin)
- **Duration:** Likely fails or takes 10+ minutes
- **Score:** 0-20% (can't access Freeplay API easily)
- **Issues:** Manual API calls, credential management, etc.

### With Plugin (Current State)
Based on your experience:
- **Duration:** ~5-10 minutes
- **Score:** 100% (but with retries)
- **Issues:** API path discovery, field name confusion, trial and error

### With Plugin (Optimized - Goal)
- **Duration:** < 3 minutes
- **Score:** 100% with zero retries
- **Improvements:** Better tool descriptions, workflow skills, error messages

## How to Analyze Results

### 1. Check Overall Score

```bash
jq '.score' results/create-prompt-and-dataset-with-plugin.json
```

Should show:
```json
{
  "total": 100,
  "max_total": 100,
  "percentage": 100.0
}
```

### 2. Check Timing

```bash
jq '.timing' results/create-prompt-and-dataset-with-plugin.json
```

Shows duration in seconds. Compare against target (< 180s).

### 3. Review Logs for Bottlenecks

```bash
# Count API exploration attempts
grep -c "Read.*openapi" results/create-prompt-and-dataset-with-plugin.log

# Find errors
grep -i "error\|400\|404" results/create-prompt-and-dataset-with-plugin.log

# Look for retries
grep -c "Creating.*project\|Creating.*prompt\|Creating.*dataset" \
  results/create-prompt-and-dataset-with-plugin.log
```

### 4. Identify Specific Issues

Review the log file section by section:
- Tool discovery phase (should be quick if using MCP)
- API calls (should work on first try)
- Response handling (should parse correctly)

## Improvement Workflow

### Iterative Improvement Process

```bash
# 1. Baseline measurement
for i in {1..3}; do
  ./framework/runner.sh create-prompt-and-dataset --plugin-dir ../
  mv results/create-prompt-and-dataset-with-plugin.json \
     results/baseline-run-$i.json
done

# 2. Calculate average baseline
jq -s 'map(.timing.duration_seconds) | add / length' \
  results/baseline-run-*.json

# 3. Identify bottleneck in logs
# Example: Too much time searching OpenAPI spec

# 4. Make targeted fix
# Example: Improve MCP tool descriptions

# 5. Re-test
./framework/runner.sh create-prompt-and-dataset --plugin-dir ../

# 6. Compare
python framework/compare.py \
  results/baseline-run-1.json \
  results/create-prompt-and-dataset-with-plugin.json

# 7. Repeat for next bottleneck
```

## Common Improvements to Try

### High Impact (30-60% time reduction)

1. **Create Workflow Skill**
   - Combine create project + prompt + dataset into single skill
   - Auto-detect when user wants complete setup
   - File: `skills/setup-test-project/SKILL.md`

2. **Better Tool Examples**
   - Add example requests to MCP tool descriptions
   - Include common variable patterns ({{question}}, {{input}}, etc.)
   - File: Update tool schemas in `freeplay-mcp/src/freeplay_mcp/tools/`

### Medium Impact (10-30% time reduction)

3. **Standardize Responses**
   - Normalize response structure in MCP layer
   - Consistent field names across tools
   - File: `freeplay-mcp/src/freeplay_mcp/response.py`

4. **Improve Error Messages**
   - Add hints for common mistakes
   - Suggest correct field names
   - File: Update error handling in MCP tools

### Low Impact (5-10% time reduction)

5. **Response Caching**
   - Cache project ID after creation
   - Reuse template IDs
   - File: Add state management to MCP server

6. **Documentation Updates**
   - Add quick reference to skill docs
   - Include field mappings (output vs expected_output)
   - File: Update skill SKILL.md files

## Success Criteria

Consider the workflow optimized when:

✅ **Duration < 180s** (3 minutes)
✅ **Success rate = 100%** (all checks pass)
✅ **Zero retries** (works first time)
✅ **< 5 tool searches** (knows where to look)
✅ **No errors in logs** (clean execution)

## Next Steps

1. **Run baseline measurement** (3-5 times)
2. **Analyze logs** to find biggest bottleneck
3. **Implement fix** (start with workflow skill)
4. **Re-run eval** to measure improvement
5. **Document findings** in improvement log
6. **Repeat** for next bottleneck

## Files to Review

- **Eval scenario:** `scenarios/create-prompt-and-dataset/scenario.json`
- **Verification code:** `framework/verify.py` (lines 325-475)
- **Results:** `results/create-prompt-and-dataset-*.json`
- **Logs:** `results/create-prompt-and-dataset-*.log`
- **Analysis guide:** `ANALYSIS_GUIDE.md`

## Questions?

If the eval doesn't work as expected:

1. Check `.env` file has all required variables
2. Verify `FREEPLAY_BASE_URL` points to dev.freeplay.ai
3. Ensure API key has project creation permissions
4. Review runner.sh output for setup errors

If checks fail unexpectedly:

1. Check API response format hasn't changed
2. Verify project ID is being set correctly
3. Review verification method logic in verify.py
4. Test API calls manually to confirm expected behavior
