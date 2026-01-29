#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec uv --directory "$SCRIPT_DIR/../freeplay-mcp" run freeplay-mcp
