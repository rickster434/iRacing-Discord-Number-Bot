"""
Roster command - view number assignments and available numbers
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger('iRacingBot.Commands.Roster')

class RosterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roster", description="View the current car number roster")
    async def roster(self, interaction: discord.Interaction):
        """View the complete roster"""
        await interaction.response.defer()

        guild_id = interaction.guild_id

        assignments = await self.bot.db.get_all_assignments(guild_id)

        embed = discord.Embed(
            title="🏁 Car Number Roster",
            description=f"Total claimed numbers: {len(assignments)}",
            color=discord.Color.blue()
        )

        if not assignments:
            embed.description = "No numbers have been claimed yet. Use `/claim` to be the first!"
            await interaction.followup.send(embed=embed)
            return

        # Sort by car number
        assignments.sort(key=lambda x: x['car_number'])

        # Group assignments for display (max 25 fields per embed)
        roster_text = []
        for assignment in assignments[:25]:  # Discord embed field limit
            number = assignment['car_number']
            user = assignment.get('discord_username', 'Unknown')
            status = "✅" if assignment.get('synced_with_iracing') else "⏳"

            roster_text.append(f"{status} **#{number}** - {user}")

        # Split into chunks of 10 for better formatting
        chunk_size = 10
        for i in range(0, len(roster_text), chunk_size):
            chunk = roster_text[i:i+chunk_size]
            embed.add_field(
                name=f"Numbers {i+1}-{min(i+chunk_size, len(roster_text))}",
                value="\n".join(chunk),
                inline=True
            )

        if len(assignments) > 25:
            embed.set_footer(text=f"Showing first 25 of {len(assignments)} assignments")

        embed.add_field(
            name="Legend",
            value="✅ Synced with iRacing\n⏳ Pending manual assignment",
            inline=False
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="available", description="View available car numbers")
    @app_commands.describe(
        range_start="Starting number (optional)",
        range_end="Ending number (optional)"
    )
    async def available(
        self,
        interaction: discord.Interaction,
        range_start: Optional[int] = None,
        range_end: Optional[int] = None
    ):
        """View available numbers"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id

        # Get available numbers
        available = await self.bot.db.get_available_numbers(guild_id)

        # Apply range filter if specified
        if range_start is not None or range_end is not None:
            start = range_start if range_start is not None else 0
            end = range_end if range_end is not None else 999
            available = [n for n in available if start <= n <= end]

        if not available:
            await interaction.followup.send(
                "❌ No available numbers in the specified range!",
                ephemeral=True
            )
            return

        # Create embed
        embed = discord.Embed(
            title="🔢 Available Car Numbers",
            description=f"Found {len(available)} available number(s)",
            color=discord.Color.green()
        )

        # Format numbers for display
        if len(available) <= 50:
            # Show all numbers if 50 or less
            numbers_text = ", ".join(str(n) for n in available[:50])
            embed.add_field(
                name="Available Numbers",
                value=numbers_text,
                inline=False
            )

            if len(available) > 50:
                embed.set_footer(text=f"Showing first 50 of {len(available)} available numbers")
        else:
            # Show ranges for large lists
            ranges = self._format_number_ranges(available[:100])
            embed.add_field(
                name="Available Ranges",
                value=ranges,
                inline=False
            )
            embed.set_footer(text=f"Showing first 100 of {len(available)} available numbers")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="check", description="Check if a specific number is available")
    @app_commands.describe(number="The car number to check")
    async def check(self, interaction: discord.Interaction, number: int):
        """Check if a number is available"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id

        assignment = await self.bot.db.get_number_assignment(guild_id, number)

        if assignment:
            embed = discord.Embed(
                title=f"Number {number}",
                description="❌ This number is already claimed",
                color=discord.Color.red()
            )

            embed.add_field(
                name="Claimed By",
                value=assignment.get('discord_username', 'Unknown'),
                inline=True
            )

            if assignment.get('iracing_name'):
                embed.add_field(
                    name="iRacing Account",
                    value=assignment['iracing_name'],
                    inline=True
                )

            status = "✅ Synced with iRacing" if assignment.get('synced_with_iracing') else "⏳ Pending assignment"
            embed.add_field(name="Status", value=status, inline=False)

            claimed_date = assignment['claimed_at'][:10]
            embed.add_field(name="Claimed On", value=claimed_date, inline=True)

        else:
            embed = discord.Embed(
                title=f"Number {number}",
                description="✅ This number is available!",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Claim It",
                value=f"Use `/claim {number}` to claim this number",
                inline=False
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="export", description="Export roster to CSV format")
    @app_commands.checks.has_permissions(administrator=True)
    async def export(self, interaction: discord.Interaction):
        """Export roster to CSV"""
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id

        assignments = await self.bot.db.get_all_assignments(guild_id)

        if not assignments:
            await interaction.followup.send(
                "No assignments to export!",
                ephemeral=True
            )
            return

        # Create CSV content
        csv_lines = ["Car Number,Discord User,iRacing ID,iRacing Name,Status,Claimed Date"]

        for assignment in sorted(assignments, key=lambda x: x['car_number']):
            number = assignment['car_number']
            discord_user = assignment.get('discord_username', '')
            iracing_id = assignment.get('iracing_id', '')
            iracing_name = assignment.get('iracing_name', '')
            status = 'Synced' if assignment.get('synced_with_iracing') else 'Pending'
            claimed_date = assignment['claimed_at'][:10]

            csv_lines.append(f"{number},{discord_user},{iracing_id},{iracing_name},{status},{claimed_date}")

        csv_content = "\n".join(csv_lines)

        # Create file
        import io
        file = discord.File(
            io.BytesIO(csv_content.encode()),
            filename=f"roster_{interaction.guild.name}_{guild_id}.csv"
        )

        embed = discord.Embed(
            title="📊 Roster Export",
            description=f"Exported {len(assignments)} assignments",
            color=discord.Color.blue()
        )

        await interaction.followup.send(embed=embed, file=file, ephemeral=True)

    def _format_number_ranges(self, numbers: list) -> str:
        """Format a list of numbers into ranges (e.g., 1-5, 10, 15-20)"""
        if not numbers:
            return "None"

        ranges = []
        start = numbers[0]
        end = numbers[0]

        for i in range(1, len(numbers)):
            if numbers[i] == end + 1:
                end = numbers[i]
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = numbers[i]
                end = numbers[i]

        # Add final range
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")

        return ", ".join(ranges)

async def setup(bot):
    await bot.add_cog(RosterCommands(bot))
