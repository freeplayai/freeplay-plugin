#!/bin/bash
#
# Freeplay Plugin Evaluation Runner
#
# Usage:
#   ./runner.sh <scenario> [--plugin-dir <path>]
#
# Examples:
#   ./runner.sh integration-simple                    # Run baseline (no plugin)
#   ./runner.sh integration-simple --plugin-dir ./   # Run with plugin
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_DIR="$(dirname "$SCRIPT_DIR")"
PLUGIN_ROOT="$(dirname "$EVALS_DIR")"

# Warning about permissions
echo "⚠️  WARNING: This eval uses --dangerously-skip-permissions and runs without a sandbox."
echo "   Claude will have full access to modify files. Run at your own risk."
echo ""

# Source .env file if it exists
if [ -f "$EVALS_DIR/.env" ]; then
    echo "Loading environment from $EVALS_DIR/.env"
    set -a  # automatically export all variables
    source "$EVALS_DIR/.env"
    set +a
fi

# Parse arguments
SCENARIO=""
PLUGIN_DIR=""
MODE="baseline"

while [[ $# -gt 0 ]]; do
    case $1 in
        --plugin-dir)
            PLUGIN_DIR="$2"
            MODE="with-plugin"
            shift 2
            ;;
        *)
            SCENARIO="$1"
            shift
            ;;
    esac
done

if [ -z "$SCENARIO" ]; then
    echo "Usage: $0 <scenario> [--plugin-dir <path>]"
    echo ""
    echo "Options:"
    echo "  --plugin-dir <path>  Run with plugin from specified directory"
    echo ""
    echo "Available scenarios:"
    ls -1 "$EVALS_DIR/scenarios/"
    exit 1
fi

SCENARIO_DIR="$EVALS_DIR/scenarios/$SCENARIO"
SCENARIO_JSON="$SCENARIO_DIR/scenario.json"

if [ ! -f "$SCENARIO_JSON" ]; then
    echo "Error: Scenario '$SCENARIO' not found at $SCENARIO_JSON"
    exit 1
fi

# Extract timeout from scenario.json (default: 180 seconds)
TIMEOUT=$(jq -r '.timeout // 180' "$SCENARIO_JSON")
echo "Timeout: ${TIMEOUT}s"

# Cross-platform timeout wrapper function
run_with_timeout() {
    local timeout_secs=$1
    shift
    local cmd=("$@")

    # Run command in background
    "${cmd[@]}" &
    local pid=$!

    # Monitor with timeout
    local count=0
    while kill -0 $pid 2>/dev/null; do
        if [ $count -ge $timeout_secs ]; then
            kill -TERM $pid 2>/dev/null
            sleep 1
            kill -KILL $pid 2>/dev/null
            wait $pid 2>/dev/null
            return 124  # timeout exit code
        fi
        sleep 1
        ((count++))
    done

    # Get actual exit code
    wait $pid
    return $?
}

# Create results directory
mkdir -p "$EVALS_DIR/results"

# Create temp directory and copy project
TEMP_DIR=$(mktemp -d)
echo "Working directory: $TEMP_DIR"

cp -r "$SCENARIO_DIR/project/"* "$TEMP_DIR/"

# Extract user prompt from scenario
PROMPT=$(jq -r '.user_prompt' "$SCENARIO_JSON")
echo "User prompt: $PROMPT"

# Prepare output files
LOG_FILE="$EVALS_DIR/results/${SCENARIO}-${MODE}.log"
RESULT_FILE="$EVALS_DIR/results/${SCENARIO}-${MODE}.json"

echo "Running eval: $SCENARIO ($MODE)"
echo "Log file: $LOG_FILE"

# Run Claude Code (in temp directory)
# Note: Using --dangerously-skip-permissions because -p mode can't handle interactive permission prompts
pushd "$TEMP_DIR" > /dev/null

# Capture start time for completion verification (local time - Freeplay uses local)
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
START_EPOCH=$(date +%s)
export EVAL_START_TIME="$START_TIME"

echo ""
echo "=== Claude Output ==="

# Stream formatter - parses stream-json and shows progress
stream_and_log() {
    local log_file="$1"
    local current_tool=""
    local tool_input=""

    # Tee to log file while parsing JSON stream for display
    tee "$log_file" | while IFS= read -r line; do
        # Try to parse as JSON and extract useful info
        if echo "$line" | jq -e . >/dev/null 2>&1; then
            type=$(echo "$line" | jq -r '.type // empty')
            case "$type" in
                "assistant")
                    # Main assistant message chunks
                    content=$(echo "$line" | jq -r '.message.content[]? | select(.type=="text") | .text // empty' 2>/dev/null)
                    if [ -n "$content" ]; then
                        echo -e "\033[0;32m[RESPONSE]\033[0m $content"
                    fi
                    # Also check for tool_use in message content
                    tool_info=$(echo "$line" | jq -r '.message.content[]? | select(.type=="tool_use") | "\(.name): \(.input | tostring)"' 2>/dev/null)
                    if [ -n "$tool_info" ]; then
                        echo -e "\033[0;33m[TOOL IN MSG]\033[0m $tool_info"
                    fi
                    ;;
                "content_block_start")
                    block_type=$(echo "$line" | jq -r '.content_block.type // empty')
                    if [ "$block_type" = "thinking" ]; then
                        echo -e "\033[0;35m[THINKING START]\033[0m"
                    elif [ "$block_type" = "tool_use" ]; then
                        tool_name=$(echo "$line" | jq -r '.content_block.name // empty')
                        tool_id=$(echo "$line" | jq -r '.content_block.id // empty')
                        echo -e "\033[0;33m[TOOL CALL] $tool_name (id: $tool_id)\033[0m"
                    elif [ "$block_type" = "text" ]; then
                        echo -e "\033[0;32m[TEXT START]\033[0m"
                    fi
                    ;;
                "content_block_delta")
                    delta_type=$(echo "$line" | jq -r '.delta.type // empty')
                    if [ "$delta_type" = "thinking_delta" ]; then
                        thinking=$(echo "$line" | jq -r '.delta.thinking // empty')
                        if [ -n "$thinking" ]; then
                            echo -ne "\033[0;35m$thinking\033[0m"
                        fi
                    elif [ "$delta_type" = "text_delta" ]; then
                        text=$(echo "$line" | jq -r '.delta.text // empty')
                        if [ -n "$text" ]; then
                            echo -ne "\033[0;32m$text\033[0m"
                        fi
                    elif [ "$delta_type" = "input_json_delta" ]; then
                        # Tool input being streamed
                        json=$(echo "$line" | jq -r '.delta.partial_json // empty')
                        if [ -n "$json" ]; then
                            echo -ne "\033[0;36m$json\033[0m"
                        fi
                    fi
                    ;;
                "content_block_stop")
                    echo ""  # newline after streaming content
                    ;;
                "result")
                    # Final result
                    echo -e "\033[0;34m[RESULT]\033[0m"
                    echo "$line" | jq -r '.result // empty' 2>/dev/null
                    # Also show cost info if available
                    cost=$(echo "$line" | jq -r '.cost_usd // empty' 2>/dev/null)
                    if [ -n "$cost" ]; then
                        echo -e "\033[0;34m[COST] \$$cost\033[0m"
                    fi
                    ;;
                # MCP and tool-related events
                "system")
                    msg=$(echo "$line" | jq -r '.message // .subtype // empty')
                    echo -e "\033[0;94m[SYSTEM] $msg\033[0m"
                    # Show full line for debugging MCP init
                    echo "$line" | jq -c '.' 2>/dev/null | head -c 200
                    echo ""
                    ;;
                "mcp"*)
                    # Any MCP-related event
                    echo -e "\033[0;96m[MCP] $type\033[0m"
                    echo "$line" | jq -c '.' 2>/dev/null
                    ;;
                "tool_use"|"tool_result")
                    # Tool execution events
                    tool_name=$(echo "$line" | jq -r '.name // .tool_name // empty')
                    echo -e "\033[0;33m[$type] $tool_name\033[0m"
                    # Show truncated content
                    echo "$line" | jq -c '.input // .content // .result // .' 2>/dev/null | head -c 500
                    echo ""
                    ;;
                *)
                    # Show ALL event types for debugging - this helps find what we're missing
                    if [ -n "$type" ]; then
                        echo -e "\033[0;90m[EVENT: $type]\033[0m"
                        # Show first 300 chars of the event for debugging
                        echo "$line" | jq -c '.' 2>/dev/null | head -c 300
                        echo ""
                    fi
                    ;;
            esac
        else
            # Non-JSON output (errors, stderr, etc)
            echo -e "\033[0;91m[RAW] $line\033[0m"
        fi
    done
}

if [ -n "$PLUGIN_DIR" ]; then
    echo "With plugin from: $PLUGIN_DIR"
    echo ""
    # Resolve plugin dir to absolute path
    if [[ "$PLUGIN_DIR" != /* ]]; then
        PLUGIN_DIR="$PLUGIN_ROOT"
    fi
    # Stream JSON output for visibility into thinking and tool use
    run_with_timeout "$TIMEOUT" claude -p "$PROMPT" --dangerously-skip-permissions --plugin-dir "$PLUGIN_DIR" --verbose --output-format stream-json 2>&1 | stream_and_log "$LOG_FILE"
    CLAUDE_EXIT_CODE=$?
else
    echo "Baseline mode (no plugin)"
    echo ""
    run_with_timeout "$TIMEOUT" claude -p "$PROMPT" --dangerously-skip-permissions --verbose --output-format stream-json 2>&1 | stream_and_log "$LOG_FILE"
    CLAUDE_EXIT_CODE=$?
fi

# Check if Claude timed out
if [ "$CLAUDE_EXIT_CODE" -eq 124 ]; then
    echo ""
    echo "⚠️  Claude execution timed out after ${TIMEOUT}s"
    echo ""
fi

# Capture end time
END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
END_EPOCH=$(date +%s)
DURATION_SECS=$((END_EPOCH - START_EPOCH))

echo ""
echo "=== End Claude Output ==="

popd > /dev/null

echo "Claude execution complete (${DURATION_SECS}s)"
echo ""

# Run verification with timing info
echo "Running verification..."
export EVAL_END_TIME="$END_TIME"
export EVAL_DURATION_SECS="$DURATION_SECS"
python3 "$SCRIPT_DIR/verify.py" "$SCENARIO" "$TEMP_DIR" "$MODE" "$RESULT_FILE"

echo ""
echo "Results saved to: $RESULT_FILE"
echo ""

# Display results summary
if [ -f "$RESULT_FILE" ]; then
    echo "=== Results Summary ==="
    jq '.' "$RESULT_FILE"
fi

# Cleanup temp directory (optional - comment out for debugging)
# rm -rf "$TEMP_DIR"
echo ""
echo "Temp directory preserved at: $TEMP_DIR"
