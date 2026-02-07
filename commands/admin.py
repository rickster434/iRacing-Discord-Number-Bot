"""
Admin commands - setup and management
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger('iRacingBot.Commands.Admin')

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Configure the bot for your server")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        league_id="Your iRacing league ID",
        min_number="Minimum car number (default: 0)",
        max_number="Maximum car number (default: 999)",
        admin_role="Role for bot administrators (optional)",
        announcement_channel="Channel for number claim announcements (optional)"
    )
    async def setup(
        self,
        interaction: discord.Interaction,
        league_id: int,
        min_number: int = 0,
        max_number: int = 999,
        admin_role: Optional[discord.Role] = None,
        announcement_channel: Optional[discord.TextChannel] = None
    ):
        """Setup the bot"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id

        # Validate number range
        if min_number < 0 or max_number > 9999 or min_number > max_number:
            await interaction.followup.send(
                "❌ Invalid number range! Min must be >= 0, max must be <= 9999, and min must be < max.",
                ephemeral=True
            )
            return

        # Save configuration
        config_data = {
            'league_id': league_id,
            'min_number': min_number,
            'max_number': max_number
        }

        if admin_role:
            config_data['admin_role_id'] = admin_role.id

        if announcement_channel:
            config_data['announcement_channel_id'] = announcement_channel.id

        await self.bot.db.set_guild_config(guild_id, **config_data)

        # Try to verify league ID
        league_info = None
        try:
            if await self.bot.iracing.authenticate():
                league_info = await self.bot.iracing.get_league_info(league_id)
        except Exception as e:
            logger.warning(f"Could not verify league ID: {e}")

        # Create confirmation embed
        embed = discord.Embed(
            title="✅ Bot Configuration Complete",
            description="The bot has been configured for your server!",
            color=discord.Color.green()
        )

        embed.add_field(name="League ID", value=str(league_id), inline=True)
        embed.add_field(name="Number Range", value=f"{min_number}-{max_number}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

        if league_info:
            league_name = league_info.get('league_name', 'Unknown')
            embed.add_field(
                name="✅ League Verified",
                value=f"Connected to: **{league_name}**",
                inline=False
            )

        if admin_role:
            embed.add_field(name="Admin Role", value=admin_role.mention, inline=True)

        if announcement_channel:
            embed.add_field(name="Announcements", value=announcement_channel.mention, inline=True)

        embed.add_field(
            name="Next Steps",
            value=(
                "1. Members can now use `/claim` to claim car numbers\n"
                "2. Use `/sync` to sync with iRacing\n"
                "3. Use `/roster` to view all assignments\n"
                "4. Use `/help` to see all available commands"
            ),
            inline=False
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Log the action
        await self.bot.db.log_action(
            guild_id,
            interaction.user.id,
            "setup",
            f"Configured bot with league ID {league_id}"
        )

    @app_commands.command(name="config", description="View current bot configuration")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config(self, interaction: discord.Interaction):
        """View configuration"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id
        config = await self.bot.db.get_guild_config(guild_id)

        if not config:
            await interaction.followup.send(
                "This server hasn't been configured yet. Use `/setup` to get started.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚙️ Bot Configuration",
            color=discord.Color.blue()
        )

        # Basic settings
        league_id = config.get('league_id', 'Not set')
        embed.add_field(name="League ID", value=str(league_id), inline=True)

        number_range = f"{config.get('min_number', 0)}-{config.get('max_number', 999)}"
        embed.add_field(name="Number Range", value=number_range, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

        # Admin role
        admin_role_id = config.get('admin_role_id')
        if admin_role_id:
            admin_role = interaction.guild.get_role(admin_role_id)
            embed.add_field(
                name="Admin Role",
                value=admin_role.mention if admin_role else "Role not found",
                inline=True
            )

        # Announcement channel
        announcement_channel_id = config.get('announcement_channel_id')
        if announcement_channel_id:
            channel = self.bot.get_channel(announcement_channel_id)
            embed.add_field(
                name="Announcement Channel",
                value=channel.mention if channel else "Channel not found",
                inline=True
            )

        # Configuration date
        created_at = config.get('created_at', 'Unknown')
        if created_at != 'Unknown':
            embed.add_field(name="Configured On", value=created_at[:10], inline=True)

        embed.set_footer(text="Use /setup to update configuration")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="forcerelease", description="Force release a number (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(number="The car number to release")
    async def forcerelease(self, interaction: discord.Interaction, number: int):
        """Force release a number"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id

        assignment = await self.bot.db.get_number_assignment(guild_id, number)

        if not assignment:
            await interaction.followup.send(
                f"❌ Number **{number}** is not currently claimed.",
                ephemeral=True
            )
            return

        # Release the number
        success = await self.bot.db.release_number(guild_id, number, assignment['discord_user_id'])

        if success:
            embed = discord.Embed(
                title="✅ Number Force Released",
                description=f"Number **{number}** has been released by administrator.",
                color=discord.Color.orange()
            )

            embed.add_field(
                name="Previously Claimed By",
                value=assignment.get('discord_username', 'Unknown'),
                inline=True
            )

            embed.add_field(
                name="Released By",
                value=interaction.user.mention,
                inline=True
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

            # Log the action
            await self.bot.db.log_action(
                guild_id,
                interaction.user.id,
                "force_release",
                f"Force released number {number}"
            )

        else:
            await interaction.followup.send(
                f"❌ Failed to release number {number}.",
                ephemeral=True
            )

    @app_commands.command(name="auditlog", description="View recent bot actions (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(limit="Number of recent entries to show (default: 10)")
    async def auditlog(self, interaction: discord.Interaction, limit: int = 10):
        """View audit log"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id

        if limit < 1 or limit > 50:
            await interaction.followup.send(
                "❌ Limit must be between 1 and 50.",
                ephemeral=True
            )
            return

        logs = await self.bot.db.get_audit_log(guild_id, limit)

        if not logs:
            await interaction.followup.send(
                "No audit log entries found.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📋 Audit Log",
            description=f"Showing last {len(logs)} action(s)",
            color=discord.Color.blue()
        )

        for log in logs[:10]:  # Show max 10 in embed
            user_id = log.get('user_id', 0)
            user_mention = f"<@{user_id}>" if user_id else "System"

            timestamp = log['timestamp'][:19]  # Remove milliseconds
            action = log['action']
            details = log.get('details', 'No details')

            embed.add_field(
                name=f"{action} - {timestamp}",
                value=f"{user_mention}: {details}",
                inline=False
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="help", description="View help and available commands")
    async def help(self, interaction: discord.Interaction):
        """Show help information"""
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="🏁 iRacing Number Bot - Help",
            description="Manage car number assignments for your iRacing league",
            color=discord.Color.blue()
        )

        # User commands
        embed.add_field(
            name="👤 Member Commands",
            value=(
                "`/claim <number>` - Claim a car number\n"
                "`/release <number>` - Release your claimed number\n"
                "`/mynumbers` - View your claimed numbers\n"
                "`/check <number>` - Check if a number is available\n"
                "`/roster` - View all number assignments\n"
                "`/available` - View available numbers\n"
                "`/link <iracing_id>` - Link your iRacing account"
            ),
            inline=False
        )

        # Admin commands
        embed.add_field(
            name="👑 Admin Commands",
            value=(
                "`/setup` - Configure the bot for your server\n"
                "`/sync` - Sync with iRacing league data\n"
                "`/syncstatus` - View sync status\n"
                "`/config` - View current configuration\n"
                "`/export` - Export roster to CSV\n"
                "`/forcerelease` - Force release a number\n"
                "`/auditlog` - View recent actions"
            ),
            inline=False
        )

        embed.add_field(
            name="ℹ️ How It Works",
            value=(
                "1. Members claim numbers using `/claim`\n"
                "2. Bot reserves the number in Discord\n"
                "3. League admin manually assigns in iRacing\n"
                "4. Bot syncs to verify assignment\n"
                "5. Number shows as synced ✅"
            ),
            inline=False
        )

        embed.add_field(
            name="🔗 Links & Support",
            value=(
                "Need help? Contact your server administrator\n"
                "GitHub: Check the README for detailed setup instructions"
            ),
            inline=False
        )

        embed.set_footer(text="iRacing Number Bot | Open Source")

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
