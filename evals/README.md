# Freeplay Plugin Evaluation Suite

Measures whether the Freeplay plugin improves Claude Code's ability to help users accomplish Freeplay-related tasks compared to a baseline (no plugin).

## Quick Start

```bash
# Set up environment
cp evals/.env.example evals/.env
# Edit evals/.env with your API keys

# Run baseline eval (no plugin)
./evals/framework/runner.sh integration-simple

# Run eval with plugin
./evals/framework/runner.sh integration-simple --plugin-dir ./

# Compare results
python evals/framework/compare.py \
  evals/results/integration-simple-baseline.json \
  evals/results/integration-simple-with-plugin.json
```

## Directory Structure

```
evals/
├── README.md                    # This file
├── .env                         # API credentials (not committed)
├── .env.example                 # Template for credentials
├── framework/
│   ├── runner.sh               # Main eval runner script
│   ├── verify.py               # Verification/scoring logic
│   └── compare.py              # Generate comparison reports
├── scenarios/
│   └── integration-simple/     # Eval: Basic SDK integration
│       ├── scenario.json       # Scenario definition
│       └── project/            # Test project to modify
└── results/                    # Output from eval runs
```

## Scenarios

### integration-simple

**Task**: Integrate Freeplay SDK into a simple AI project that calls OpenAI directly.

**Success Criteria**:
1. Code is modified to use Freeplay SDK (30 points)
2. Code runs without errors (30 points)
3. Completions are logged to Freeplay (40 points)

### integration-with-prompt

**Task**: Integrate Freeplay SDK with prompt management - create a prompt template and record completions with prompt info.

**Success Criteria**:
1. Code imports Freeplay and uses prompts (20 points)
2. Code runs without errors (20 points)
3. Prompt template 'summarize' exists in Freeplay (30 points)
4. Completion has prompt info attached (30 points)

## Environment Variables

Create `evals/.env` with:

```bash
# Required for test project
OPENAI_API_KEY=your-openai-api-key

# Required for API verification
FREEPLAY_API_KEY=your-freeplay-api-key
FREEPLAY_PROJECT_ID=your-project-id
FREEPLAY_BASE_URL=https://localhost:8080  # or https://app.freeplay.ai
FREEPLAY_VERIFY_SSL=false                 # Set to true for production
FREEPLAY_API_BASE=https://localhost:8080
```

## Running Evaluations

```bash
# Baseline (no plugin)
./evals/framework/runner.sh <scenario-name>

# With plugin
./evals/framework/runner.sh <scenario-name> --plugin-dir ./
```

Output streams in real-time and results are saved to `evals/results/`.

## Results Format

```json
{
  "scenario": "integration-simple",
  "mode": "with-plugin",
  "timestamp": "2026-01-30T20:31:16Z",
  "checks": [
    {"check": "file_contains", "passed": true, ...},
    {"check": "code_runs", "passed": true, ...},
    {"check": "api_verify", "passed": true, "completion_count": 1, ...}
  ],
  "score": {
    "categories": {...},
    "total": 100,
    "max_total": 100,
    "percentage": 100.0
  }
}
```

## Adding New Scenarios

1. Create directory: `evals/scenarios/<name>/`
2. Add `scenario.json` with:
   - `name`: Scenario identifier
   - `description`: What the eval tests
   - `user_prompt`: Prompt sent to Claude
   - `success_criteria`: List of checks
   - `scoring`: Point allocation
3. Add `project/` directory with test files

## Scoring Categories

| Category | Description |
|----------|-------------|
| `code_modified` | Code contains expected patterns |
| `code_runs` | Code executes without errors |
| `completion_logged` | Data appears in Freeplay (within 5 min) |
