# Freeplay Plugin for Claude Code

A Claude Code plugin that integrates with the Freeplay MCP server for prompt management and evaluation.

## Prerequisites

- Claude Code v1.0.33 or later (`claude --version`)
- [uv](https://docs.astral.sh/uv/) installed
- Freeplay API key

## Setup

### Clone with submodules

```bash
git clone --recurse-submodules <repo-url>
cd freeplay-plugin
```

Or if already cloned:

```bash
git submodule update --init --recursive
```

### Install MCP server dependencies

```bash
cd freeplay-mcp
uv sync
cd ..
```

### Configure environment

Set your Freeplay API key:

```bash
export FREEPLAY_API_KEY="your-api-key"
```

## Local Development

### Run the plugin locally

```bash
claude --plugin-dir ./
```

### Run with debug output

```bash
claude --debug --plugin-dir ./
```

### Verify MCP connection

Once Claude starts, run `/mcp` to check the Freeplay server is connected.

## Plugin Structure

```
freeplay-plugin/
├── .claude-plugin/
│   └── plugin.json      # Plugin manifest
├── commands/
│   └── optimize-prompt.md   # /freeplay:optimize-prompt command
├── skills/              # Skills (git submodule)
│   ├── deployed-prompts/
│   ├── freeplay-api/
│   └── test-run-analysis/
├── agents/              # Custom agents
├── hooks/
│   └── hooks.json       # Event hooks
├── scripts/
│   └── run-mcp.sh       # MCP server launcher
├── freeplay-mcp/        # MCP server (git submodule)
├── .mcp.json            # MCP server config
├── CLAUDE.md            # Development guidelines
└── README.md
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/freeplay:optimize-prompt [name]` | Fetch a prompt, suggest improvements, create a new version, and deploy |

## Skills (auto-invoked)

| Skill | Triggers when |
|-------|---------------|
| `deployed-prompts` | User asks what's deployed, what version is in prod/staging/dev |
| `freeplay-api` | Writing code that interacts with the Freeplay API |
| `test-run-analysis` | User wants to review test run results or metrics |

## MCP Server Configuration

The plugin uses a shell script to launch the MCP server from the submodule:

```json
{
  "mcpServers": {
    "freeplay": {
      "command": "${CLAUDE_PLUGIN_ROOT}/scripts/run-mcp.sh",
      "args": [],
      "env": {}
    }
  }
}
```

The `run-mcp.sh` script self-locates and runs `uv` from the correct directory:

```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec uv --directory "$SCRIPT_DIR/../freeplay-mcp" run freeplay-mcp
```

**Note:** `${CLAUDE_PLUGIN_ROOT}` only works in the `command` field, not in `cwd` or `args`.

## Adding New Features

### Add a command

Create a markdown file in `commands/`:

```markdown
---
description: Brief description of the command
---

Instructions for Claude when this command is invoked.
```

### Add a skill

Create a directory in `skills/` with a `SKILL.md` file:

```markdown
---
name: skill-name
description: When Claude should auto-invoke this skill
---

Instructions for the skill.
```

### Add a hook

Edit `hooks/hooks.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/my-script.sh"
          }
        ]
      }
    ]
  }
}
```

## Troubleshooting

**Plugin not loading:**
- Verify directory structure (components at root, not inside `.claude-plugin/`)
- Run with `--debug` flag to see loading errors

**MCP server not connecting:**
- Ensure submodule is initialized: `git submodule update --init`
- Run `uv sync` in the `freeplay-mcp/` directory
- Check `FREEPLAY_API_KEY` is set
- Verify the script is executable: `chmod +x scripts/run-mcp.sh`

**Commands not appearing:**
- Restart Claude Code after changes
- Run `/help` to see available commands under the `freeplay` namespace

## Updating Submodules

Pull latest changes including all submodules:

```bash
git pull --recurse-submodules
```

Or set this as the default behavior:

```bash
git config submodule.recurse true
```

### After updating freeplay-mcp

```bash
cd freeplay-mcp
uv sync
cd ..
```
