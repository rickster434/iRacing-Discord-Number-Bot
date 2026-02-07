"""
Sync command - sync car numbers with iRacing
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('iRacingBot.Commands.Sync')

class SyncCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sync", description="Sync car numbers with iRacing league data")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def sync(self, interaction: discord.Interaction):
        """Sync with iRacing"""
        await interaction.response.defer()

        guild_id = interaction.guild_id

        # Get guild config
        config = await self.bot.db.get_guild_config(guild_id)

        if not config or not config.get('league_id'):
            embed = discord.Embed(
                title="❌ Configuration Required",
                description="This server hasn't been configured yet.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Setup Required",
                value="An administrator needs to run `/setup` first to configure the league ID.",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return

        league_id = config['league_id']

        # Create status embed
        status_embed = discord.Embed(
            title="🔄 Syncing with iRacing",
            description="Please wait while we sync with iRacing...",
            color=discord.Color.blue()
        )
        status_message = await interaction.followup.send(embed=status_embed)

        try:
            # Perform sync
            success = await self.bot.sync_with_iracing(guild_id, league_id)

            if success:
                # Get updated roster stats
                assignments = await self.bot.db.get_all_assignments(guild_id)
                synced_count = sum(1 for a in assignments if a.get('synced_with_iracing'))

                embed = discord.Embed(
                    title="✅ Sync Complete",
                    description="Successfully synced with iRacing!",
                    color=discord.Color.green()
                )

                embed.add_field(
                    name="Statistics",
                    value=(
                        f"📊 Total Assignments: {len(assignments)}\n"
                        f"✅ Synced: {synced_count}\n"
                        f"⏳ Pending: {len(assignments) - synced_count}"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="League",
                    value=f"League ID: {league_id}",
                    inline=True
                )

                embed.set_footer(text="Use /roster to view the updated roster")

                await status_message.edit(embed=embed)

            else:
                embed = discord.Embed(
                    title="❌ Sync Failed",
                    description="Failed to sync with iRacing. Please check the configuration.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Possible Issues",
                    value=(
                        "• Invalid iRacing credentials\n"
                        "• Invalid league ID\n"
                        "• iRacing API temporarily unavailable\n"
                        "• No active season in the league"
                    ),
                    inline=False
                )
                embed.add_field(
                    name="Next Steps",
                    value="Check the bot logs or contact the bot administrator",
                    inline=False
                )
                await status_message.edit(embed=embed)

        except Exception as e:
            logger.error(f"Error during sync command: {e}")

            embed = discord.Embed(
                title="❌ Sync Error",
                description="An error occurred during sync.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Error",
                value=str(e)[:1024],
                inline=False
            )
            await status_message.edit(embed=embed)

    @app_commands.command(name="syncstatus", description="View sync status and statistics")
    async def syncstatus(self, interaction: discord.Interaction):
        """View sync status"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id

        config = await self.bot.db.get_guild_config(guild_id)

        if not config:
            await interaction.followup.send(
                "This server hasn't been configured yet. Use `/setup` to get started.",
                ephemeral=True
            )
            return

        # Get roster stats
        assignments = await self.bot.db.get_all_assignments(guild_id)
        synced_count = sum(1 for a in assignments if a.get('synced_with_iracing'))
        verified_count = sum(1 for a in assignments if a.get('iracing_verified'))

        embed = discord.Embed(
            title="📊 Sync Status",
            color=discord.Color.blue()
        )

        # Configuration info
        league_id = config.get('league_id', 'Not configured')
        number_range = f"{config.get('min_number', 0)}-{config.get('max_number', 999)}"

        embed.add_field(name="League ID", value=str(league_id), inline=True)
        embed.add_field(name="Number Range", value=number_range, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

        # Statistics
        embed.add_field(
            name="Total Assignments",
            value=str(len(assignments)),
            inline=True
        )
        embed.add_field(
            name="Synced with iRacing",
            value=f"{synced_count} ✅",
            inline=True
        )
        embed.add_field(
            name="iRacing Verified",
            value=f"{verified_count} 🔗",
            inline=True
        )

        # Pending assignments
        pending_count = len(assignments) - synced_count
        if pending_count > 0:
            embed.add_field(
                name="⏳ Pending Manual Assignment",
                value=f"{pending_count} number(s) need to be manually assigned in iRacing",
                inline=False
            )

        # Auto-sync status
        if self.bot.auto_sync.is_running():
            embed.add_field(
                name="Auto-Sync",
                value="✅ Enabled (runs every hour)",
                inline=False
            )
        else:
            embed.add_field(
                name="Auto-Sync",
                value="❌ Disabled",
                inline=False
            )

        embed.set_footer(text="Use /sync to manually trigger a sync")

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SyncCommands(bot))
