# Freeplay Plugin for Claude Code

Give Claude Code the ability to interact with [Freeplay](https://freeplay.ai)—browse projects, manage prompts, run tests, and analyze results through natural conversation.

## ⚠️ EXPERIMENTAL

**This plugin is experimental and will change.** Use at your own risk.

Current limitations:
- Does not support destructive deletion actions
- Does not support deployment operations
- Uses your regular Freeplay API key (not scoped to limit access)

**Security warning:** Because this uses your full API key, a malicious or compromised agent could extract the key and write its own code outside the plugin to perform destructive actions against your Freeplay account.

Additionally, all MCP servers share a security context within the host, enabling data exfiltration, prompt injection across tools, and cross-server data access.

Only use this with agents and MCP servers you fully trust.

---

## Installation

### From the Plugin Marketplace

```bash
claude plugin add freeplayai/freeplay-plugin
```

Set your environment variables:

```bash
export FREEPLAY_API_KEY="your-api-key"
export FREEPLAY_BASE_URL="https://app.freeplay.ai"  # optional, this is the default
```

## Running Locally

### Prerequisites

- Claude Code v1.0.33 or later (`claude --version`)
- [uv](https://docs.astral.sh/uv/) installed
- Freeplay API key

### Clone with submodules

```bash
git clone --recurse-submodules https://github.com/freeplayai/freeplay-plugin.git
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

```bash
export FREEPLAY_API_KEY="your-api-key"
export FREEPLAY_BASE_URL="https://app.freeplay.ai"  # optional, this is the default
```

### Run the plugin

```bash
claude --plugin-dir ./
```

Run with debug output:

```bash
claude --debug --plugin-dir ./
```

### Verify MCP connection

Once Claude starts, run `/mcp` to check the Freeplay server is connected.

### Updating submodules

Pull latest changes including all submodules:

```bash
git pull --recurse-submodules
```

Or set this as the default behavior:

```bash
git config submodule.recurse true
```

After updating, reinstall dependencies:

```bash
cd freeplay-mcp && uv sync && cd ..
```

## MCP Server

This plugin bundles the [Freeplay MCP server](./freeplay-mcp/README.md). See the MCP server README for standalone installation, available tools, and configuration options.

## Troubleshooting

**Plugin not loading:**
- Verify directory structure (components at root, not inside `.claude-plugin/`)
- Run with `--debug` flag to see loading errors

**MCP server not connecting:**
- Ensure submodule is initialized: `git submodule update --init`
- Run `uv sync` in the `freeplay-mcp/` directory
- Check `FREEPLAY_API_KEY` is set
- Verify the script is executable: `chmod +x scripts/run-mcp.sh`

## Support

- **Docs**: https://docs.freeplay.ai
- **Issues**: https://github.com/freeplayai/freeplay-plugin/issues
- **Security**: security@freeplay.ai
