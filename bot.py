"""
iRacing Discord Number Bot
A Discord bot for managing car number assignments in iRacing leagues
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import logging
from datetime import datetime
from config import Config
from database import Database
from iracing_api import iRacingAPI

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('iRacingBot')

class iRacingNumberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )

        self.config = Config()
        self.db = Database()
        self.iracing = iRacingAPI(
            username=self.config.get('IRACING_USERNAME'),
            password=self.config.get('IRACING_PASSWORD')
        )

    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up bot...")

        # Initialize database
        await self.db.initialize()

        # Load commands
        await self.load_commands()

        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

        # Start background sync task
        if not self.auto_sync.is_running():
            self.auto_sync.start()

    async def load_commands(self):
        """Load all command modules"""
        commands_list = [
            'commands.claim',
            'commands.release',
            'commands.roster',
            'commands.sync',
            'commands.admin'
        ]

        for cmd in commands_list:
            try:
                await self.load_extension(cmd)
                logger.info(f"Loaded {cmd}")
            except Exception as e:
                logger.error(f"Failed to load {cmd}: {e}")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} server(s)')

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="car numbers | /help"
            )
        )

    async def on_guild_join(self, guild):
        """Called when the bot joins a new server"""
        logger.info(f"Joined new server: {guild.name} (ID: {guild.id})")

        # Send welcome message to the first available text channel
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="👋 Thanks for adding iRacing Number Bot!",
                    description=(
                        "I help manage car number assignments for your iRacing league.\n\n"
                        "**Getting Started:**\n"
                        "1. An admin should use `/setup` to configure the bot\n"
                        "2. Members can use `/claim` to reserve car numbers\n"
                        "3. Use `/sync` to sync with iRacing\n"
                        "4. Use `/help` to see all commands\n\n"
                        "**Need help?** Check the README or contact your server admin."
                    ),
                    color=discord.Color.blue()
                )
                await channel.send(embed=embed)
                break

    @tasks.loop(hours=1)
    async def auto_sync(self):
        """Automatically sync with iRacing every hour"""
        try:
            logger.info("Starting automatic sync with iRacing...")

            # Get all configured guilds
            guilds = await self.db.get_all_guild_configs()

            for guild_config in guilds:
                guild_id = guild_config['guild_id']
                league_id = guild_config.get('league_id')

                if not league_id:
                    continue

                try:
                    # Sync numbers from iRacing
                    await self.sync_with_iracing(guild_id, league_id)
                    logger.info(f"Auto-synced guild {guild_id}")
                except Exception as e:
                    logger.error(f"Failed to auto-sync guild {guild_id}: {e}")

        except Exception as e:
            logger.error(f"Auto-sync task error: {e}")

    @auto_sync.before_loop
    async def before_auto_sync(self):
        """Wait for the bot to be ready before starting the sync loop"""
        await self.wait_until_ready()

    async def sync_with_iracing(self, guild_id: int, league_id: int):
        """Sync car numbers from iRacing"""
        try:
            # Authenticate with iRacing
            if not await self.iracing.authenticate():
                logger.error("Failed to authenticate with iRacing")
                return False

            # Get league roster from iRacing
            roster = await self.iracing.get_league_roster(league_id)

            if not roster:
                logger.warning(f"No roster data found for league {league_id}")
                return False

            # Update database with iRacing assignments
            sync_count = 0
            for member in roster:
                customer_id = member.get('cust_id')
                car_number = member.get('car_number')

                if customer_id and car_number:
                    # Check if number is already in our database
                    existing = await self.db.get_number_assignment(guild_id, car_number)

                    if not existing:
                        # Add new assignment from iRacing
                        await self.db.sync_iracing_assignment(
                            guild_id=guild_id,
                            car_number=car_number,
                            iracing_id=customer_id,
                            iracing_data=member
                        )
                        sync_count += 1

            logger.info(f"Synced {sync_count} assignments from iRacing for guild {guild_id}")
            return True

        except Exception as e:
            logger.error(f"Error syncing with iRacing: {e}")
            return False

def main():
    """Main entry point"""
    bot = iRacingNumberBot()

    # Get bot token from config
    token = bot.config.get('DISCORD_BOT_TOKEN')

    if not token:
        logger.error("DISCORD_BOT_TOKEN not found in configuration!")
        logger.error("Please create a .env file with your bot token.")
        return

    try:
        bot.run(token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
