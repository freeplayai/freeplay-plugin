#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# For development USE_LOCAL_MCP_SOURCE allows testing from a local source copy
# this enables testing the MCP server without publishing.
if [ "$USE_LOCAL_MCP_SOURCE" = "1" ]; then
  uv --directory "$SCRIPT_DIR/../freeplay-mcp" run freeplay-mcp
else
  uvx freeplay-mcp
fi
