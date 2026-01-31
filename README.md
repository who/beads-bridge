# Beads Bridge

A Discord bot that lets you file [Beads](https://github.com/steveyegge/beads) issues from anywhere using natural language.

## The Problem

You're away from your desk when you notice a bug or think of a task. By the time you get back to your development machine, you've forgotten the details.

## The Solution

Send a message to Discord (typed or dictated), and Beads Bridge uses Claude to interpret it and execute the corresponding `bd` command on your local machine. Fire-and-forget: you get a ✅ or ❌ reaction, nothing more.

```
!bd bug for solar project: panel efficiency is wrong in the afternoon
```

## How It Works

```
Discord Message → Claude (interprets) → bd CLI (executes) → ✅
```

- **Text-agnostic**: Type, use voice-to-text, paste—doesn't matter
- **Write-only**: Creates, updates, closes, and deletes issues (no queries—there's no feedback channel)
- **Multi-project**: Automatically detects which project you mean from `bd daemons list`

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Beads](https://github.com/steveyegge/beads) CLI installed
- Anthropic API key
- Discord bot token

### Installation

```bash
git clone https://github.com/who/beads-bridge
cd beads-bridge
uv sync
```

### Discord Bot Setup

1. Create a bot at [Discord Developer Portal](https://discord.com/developers/applications)
2. Enable **Message Content Intent** under Bot settings
3. Add bot to your server with permissions: Send Messages, Add Reactions, Read Message History
4. Get your server and channel IDs (enable Developer Mode in Discord settings)

### Configuration

```bash
export ANTHROPIC_API_KEY="your-key"
export DISCORD_BOT_TOKEN="your-bot-token"
export DISCORD_GUILD_ID="your-server-id"
export DISCORD_CHANNEL_ID="your-channel-id"
export DISCORD_COMMAND_PREFIX="!bd"  # optional, defaults to !bd
```

### Run

```bash
uv run beads-bridge
```

## Usage Examples

| Message | What happens |
|---------|--------------|
| `!bd bug for solar: panel calc is wrong` | Creates bug in solar project |
| `!bd close bd-a1b2, it's fixed` | Closes issue with reason |
| `!bd mark bd-c3d4 in progress` | Updates status |
| `!bd high priority bug: auth broken` | Creates P1 bug |
| `!bd epic for API: add OAuth` | Creates epic |

## Running as a Service (Optional)

```bash
# Create systemd user service
mkdir -p ~/.config/systemd/user
# Add beads-bridge.service (see prd/intake.md for template)
systemctl --user enable --now beads-bridge
```

## Development

```bash
uv run ruff check .   # Lint
uv run ruff format .  # Format
uv run pytest         # Test
```

## Ortus Automation

This project was scaffolded with [Ortus](https://github.com/anthropics/ortus), which provides AI-powered development workflows including PRD-to-issues decomposition and automated implementation loops. See the `ortus/` directory for scripts and prompts.

## License

MIT
