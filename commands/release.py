"""
Release command - allows users to release their claimed numbers
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('iRacingBot.Commands.Release')

class ReleaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="release", description="Release a car number you've claimed")
    @app_commands.describe(number="The car number you want to release")
    async def release(self, interaction: discord.Interaction, number: int):
        """Release a claimed car number"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id
        user_id = interaction.user.id

        # Check if the number is claimed by this user
        assignment = await self.bot.db.get_number_assignment(guild_id, number)

        if not assignment:
            await interaction.followup.send(
                f"❌ Number **{number}** is not currently claimed.",
                ephemeral=True
            )
            return

        if assignment['discord_user_id'] != user_id:
            # Check if user is admin
            config = await self.bot.db.get_guild_config(guild_id)
            admin_role_id = config.get('admin_role_id') if config else None

            is_admin = False
            if admin_role_id:
                admin_role = interaction.guild.get_role(admin_role_id)
                if admin_role in interaction.user.roles:
                    is_admin = True

            if not is_admin and not interaction.user.guild_permissions.administrator:
                claimed_by = assignment.get('discord_username', 'another user')
                await interaction.followup.send(
                    f"❌ Number **{number}** is claimed by **{claimed_by}**. You can only release your own numbers.",
                    ephemeral=True
                )
                return

        # Release the number
        success = await self.bot.db.release_number(guild_id, number, assignment['discord_user_id'])

        if success:
            embed = discord.Embed(
                title="✅ Number Released",
                description=f"Number **{number}** has been released and is now available.",
                color=discord.Color.green()
            )

            if assignment['discord_user_id'] != user_id:
                embed.add_field(
                    name="Released by Admin",
                    value=f"Admin {interaction.user.mention} released this number",
                    inline=False
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

            # Send announcement if configured
            config = await self.bot.db.get_guild_config(guild_id)
            if config and config.get('announcement_channel_id'):
                channel = self.bot.get_channel(config['announcement_channel_id'])
                if channel:
                    announce_embed = discord.Embed(
                        title="🏁 Number Released",
                        description=f"Number **{number}** is now available",
                        color=discord.Color.orange()
                    )
                    try:
                        await channel.send(embed=announce_embed)
                    except:
                        pass

        else:
            await interaction.followup.send(
                f"❌ Failed to release number {number}. Please try again.",
                ephemeral=True
            )

    @app_commands.command(name="mynumbers", description="View your claimed car numbers")
    async def mynumbers(self, interaction: discord.Interaction):
        """View user's claimed numbers"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id
        user_id = interaction.user.id

        assignments = await self.bot.db.get_user_numbers(guild_id, user_id)

        if not assignments:
            await interaction.followup.send(
                "You haven't claimed any numbers yet. Use `/claim` to claim a number!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🏁 Your Claimed Numbers",
            description=f"You have claimed {len(assignments)} number(s)",
            color=discord.Color.blue()
        )

        for assignment in assignments:
            number = assignment['car_number']
            status = "✅ Synced" if assignment.get('synced_with_iracing') else "⏳ Pending"

            field_value = f"Status: {status}\n"

            if assignment.get('iracing_name'):
                field_value += f"iRacing: {assignment['iracing_name']}\n"

            field_value += f"Claimed: {assignment['claimed_at'][:10]}"

            embed.add_field(
                name=f"Number {number}",
                value=field_value,
                inline=True
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ReleaseCommands(bot))
