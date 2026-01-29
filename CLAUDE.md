# Freeplay Plugin - Claude Code Guidelines

This is a Claude Code plugin that integrates with the Freeplay MCP server.

## Project Structure

```
freeplay-plugin/
├── .claude-plugin/           # Plugin metadata (only plugin.json goes here)
│   └── plugin.json          # Plugin manifest
├── commands/                 # User-invoked slash commands
│   └── *.md                 # Command files
├── skills/                   # Agent skills (auto-invoked by Claude)
│   └── <skill-name>/
│       └── SKILL.md
├── agents/                   # Subagent definitions
│   └── *.md
├── hooks/                    # Event handlers
│   └── hooks.json
├── .mcp.json                # MCP server configuration
└── scripts/                 # Utility scripts for hooks
```

## Best Practices

### Plugin Manifest
- Keep `plugin.json` minimal with required fields
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Only `plugin.json` goes in `.claude-plugin/` directory

### Skills vs Commands
- **Skills** (`skills/`): Auto-invoked by Claude based on context
- **Commands** (`commands/`): User-invoked via `/plugin-name:command`

### Skill Files
- Must be named `SKILL.md` inside a directory
- Include frontmatter with `name` and `description`
- Description helps Claude know when to use the skill

### MCP Servers
- Use `${CLAUDE_PLUGIN_ROOT}` for relative paths
- Configure in `.mcp.json` at plugin root

### Hooks
- Place hook scripts in `scripts/` directory
- Make scripts executable: `chmod +x scripts/*.sh`
- Use `${CLAUDE_PLUGIN_ROOT}` in hook commands

## Development Workflow

```bash
# Test locally
claude --plugin-dir ./

# Test with debug output
claude --debug --plugin-dir ./

# Multiple plugins
claude --plugin-dir ./plugin1 --plugin-dir ./plugin2
```

## Common Issues

- Components not loading: Ensure directories are at plugin root, NOT inside `.claude-plugin/`
- Scripts not executing: Check `chmod +x` permissions
- MCP server issues: Verify paths use `${CLAUDE_PLUGIN_ROOT}`
