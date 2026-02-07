"""
Claim command - allows users to claim car numbers
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('iRacingBot.Commands.Claim')

class ClaimCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="claim", description="Claim a car number for yourself")
    @app_commands.describe(
        number="The car number you want to claim",
        iracing_id="Your iRacing customer ID (optional)"
    )
    async def claim(
        self,
        interaction: discord.Interaction,
        number: int,
        iracing_id: int = None
    ):
        """Claim a car number"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id
        user_id = interaction.user.id
        username = str(interaction.user)

        # Get guild config
        config = await self.bot.db.get_guild_config(guild_id)

        if config:
            min_num = config.get('min_number', 0)
            max_num = config.get('max_number', 999)

            # Check if number is in valid range
            if number < min_num or number > max_num:
                await interaction.followup.send(
                    f"❌ Invalid number! Numbers must be between {min_num} and {max_num}.",
                    ephemeral=True
                )
                return

        # Check if number is already claimed
        existing = await self.bot.db.get_number_assignment(guild_id, number)

        if existing:
            claimed_by = existing.get('discord_username', 'Unknown')
            await interaction.followup.send(
                f"❌ Number **{number}** is already claimed by **{claimed_by}**.",
                ephemeral=True
            )
            return

        # Verify iRacing ID if provided
        iracing_name = None
        if iracing_id:
            try:
                member_info = await self.bot.iracing.get_member_info(iracing_id)
                if member_info:
                    iracing_name = member_info.get('display_name')
                    logger.info(f"Verified iRacing ID {iracing_id} for user {username}")
                else:
                    await interaction.followup.send(
                        f"⚠️ Could not verify iRacing ID {iracing_id}. Claiming without verification.",
                        ephemeral=True
                    )
            except Exception as e:
                logger.error(f"Error verifying iRacing ID: {e}")

        # Claim the number
        success = await self.bot.db.claim_number(
            guild_id=guild_id,
            car_number=number,
            discord_user_id=user_id,
            discord_username=username,
            iracing_id=iracing_id,
            iracing_name=iracing_name
        )

        if success:
            # Create success embed
            embed = discord.Embed(
                title="✅ Number Claimed!",
                description=f"You have successfully claimed number **{number}**.",
                color=discord.Color.green()
            )

            embed.add_field(name="Discord User", value=username, inline=True)

            if iracing_id and iracing_name:
                embed.add_field(name="iRacing Account", value=f"{iracing_name} (ID: {iracing_id})", inline=True)
                embed.add_field(
                    name="Next Steps",
                    value="✓ Your number is reserved!\n✓ Ask a league admin to assign it in iRacing.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Next Steps",
                    value=(
                        "✓ Your number is reserved!\n"
                        "✓ Ask a league admin to assign it in iRacing.\n"
                        "💡 Tip: Use `/link` to link your iRacing account for verification."
                    ),
                    inline=False
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

            # Send announcement if configured
            if config and config.get('announcement_channel_id'):
                channel = self.bot.get_channel(config['announcement_channel_id'])
                if channel:
                    announce_embed = discord.Embed(
                        title="🏁 New Number Claimed",
                        description=f"{interaction.user.mention} claimed number **{number}**",
                        color=discord.Color.blue()
                    )
                    try:
                        await channel.send(embed=announce_embed)
                    except:
                        pass

        else:
            await interaction.followup.send(
                f"❌ Failed to claim number {number}. Please try again.",
                ephemeral=True
            )

    @app_commands.command(name="link", description="Link your iRacing account to your Discord")
    @app_commands.describe(iracing_id="Your iRacing customer ID")
    async def link(self, interaction: discord.Interaction, iracing_id: int):
        """Link iRacing account to Discord"""
        await interaction.response.defer(ephemeral=True)

        try:
            # Verify iRacing ID
            member_info = await self.bot.iracing.get_member_info(iracing_id)

            if not member_info:
                await interaction.followup.send(
                    f"❌ Could not find iRacing member with ID {iracing_id}.",
                    ephemeral=True
                )
                return

            iracing_name = member_info.get('display_name', 'Unknown')

            # Update any existing number claims
            guild_id = interaction.guild_id
            user_id = interaction.user.id

            user_numbers = await self.bot.db.get_user_numbers(guild_id, user_id)

            if user_numbers:
                # Update existing claims with iRacing info
                for assignment in user_numbers:
                    await self.bot.db.db.execute("""
                        UPDATE number_assignments
                        SET iracing_id = ?, iracing_name = ?, iracing_verified = 1
                        WHERE id = ?
                    """, (iracing_id, iracing_name, assignment['id']))

                await self.bot.db.db.commit()

                embed = discord.Embed(
                    title="✅ iRacing Account Linked!",
                    description=f"Your Discord account is now linked to **{iracing_name}** (ID: {iracing_id})",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Updated Claims",
                    value=f"Linked to {len(user_numbers)} existing number claim(s)",
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="✅ iRacing Account Verified!",
                    description=f"Verified: **{iracing_name}** (ID: {iracing_id})",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Next Steps",
                    value="Use `/claim` to claim a car number with your verified iRacing account",
                    inline=False
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error linking iRacing account: {e}")
            await interaction.followup.send(
                "❌ An error occurred while linking your iRacing account.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ClaimCommands(bot))
