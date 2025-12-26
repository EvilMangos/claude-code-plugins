# Claude Code Plugins

A collection of plugins for Claude Code that extend its capabilities with specialized agents, commands, skills, and
hooks.

## Repository Structure

```
plugins/
  backend-toolbox/     # TDD and code quality framework
  telegram-notify/     # Telegram notifications hook
```

Each plugin is self-contained with its own:

- `.claude-plugin/plugin.json` - Plugin manifest and configuration
- `README.md` - Plugin-specific documentation

And optionally:

- `agents/` - Specialized autonomous agents
- `commands/` - Slash commands for workflows
- `skills/` - Domain knowledge and best practices
- `hooks/` - Event-driven automation
- `scripts/` - Supporting shell scripts

## Available Plugins

| Plugin                                        | Description                                                       |
|-----------------------------------------------|-------------------------------------------------------------------|
| [backend-toolbox](plugins/backend-toolbox/)   | TDD workflow, code quality, and backend development               |
| [telegram-notify](plugins/telegram-notify/)   | Telegram notifications on task finish or user action required     |

## Installation

Copy or symlink the desired plugin directory to your Claude Code plugins location, or reference it in your project's
`.claude/plugins.json`.

## Contributing

Each plugin should follow the standard structure and include comprehensive documentation in its own README.md file.
