"""Discord bot that receives text commands and processes them via Claude."""

import os

import discord
from dotenv import load_dotenv

load_dotenv()

from beads_bridge.processor import process_command

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
DISCORD_CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID")
COMMAND_PREFIX = os.environ.get("DISCORD_COMMAND_PREFIX", "!bd")


class BeadsBridgeBot(discord.Client):
    """Discord bot that listens for commands in a specific channel."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        self.guild_id = int(DISCORD_GUILD_ID) if DISCORD_GUILD_ID else None
        self.channel_id = int(DISCORD_CHANNEL_ID) if DISCORD_CHANNEL_ID else None

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        print(f"[bot] Logged in as {self.user}")
        if self.guild_id:
            print(f"[bot] Guild: {self.guild_id}")
        if self.channel_id:
            print(f"[bot] Channel: {self.channel_id}")
        if COMMAND_PREFIX:
            print(f"[bot] Prefix: '{COMMAND_PREFIX}'")
        else:
            print("[bot] No prefix configured - processing all messages")

    async def on_message(self, message: discord.Message) -> None:
        """Called when a message is received."""
        # Ignore own messages
        if message.author == self.user:
            return

        # Check guild filter
        if self.guild_id and message.guild and message.guild.id != self.guild_id:
            return

        # Check channel filter
        if self.channel_id and message.channel.id != self.channel_id:
            return

        content = message.content.strip()

        # Check command prefix
        if COMMAND_PREFIX:
            if not content.startswith(COMMAND_PREFIX):
                return
            # Strip prefix and whitespace
            content = content[len(COMMAND_PREFIX) :].strip()

        if not content:
            return

        print(f"[bot] Received from {message.author}: {content[:60]}...")

        # Process the command
        result = process_command(content)

        # React to indicate result
        try:
            if result["success"]:
                await message.add_reaction("✅")
            else:
                await message.add_reaction("❌")
        except discord.errors.Forbidden:
            pass  # Can't add reactions, that's fine


def main() -> None:
    """Start the Discord bot."""
    if not DISCORD_BOT_TOKEN:
        print("[bot] Error: DISCORD_BOT_TOKEN not set")
        raise SystemExit(1)

    if not DISCORD_CHANNEL_ID:
        print("[bot] Warning: DISCORD_CHANNEL_ID not set - listening on all channels")

    bot = BeadsBridgeBot()
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
