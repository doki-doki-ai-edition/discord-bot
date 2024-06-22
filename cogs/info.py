from discord.ext import commands
from discord import app_commands
from utils.data import Info, Data
from utils.views import DokiOptions
import discord


class CustomHelp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="help")
    async def help(self, interaction:discord.Interaction):
        """List of all commands"""
        help_info = await Info().getHelpInfo

        embed = discord.Embed(description=help_info['desc'], color=0xF875AA)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
        embed.set_footer(text=f"version: {self.bot.ddae_version}")
        embed.set_thumbnail(url=interaction.guild.icon)

        for category, commands_list in help_info["cmds"].items():
            embed.add_field(name=f"{category} - `{commands_list.count(',') + 1}`", value=commands_list, inline=False)

        await interaction.response.send_message(embed=embed)




    @app_commands.command(name="dokis")
    async def dokis(self, interaction:discord.Interaction):
        """List of all the characters"""
        embed = discord.Embed(
        title="Need help choosing a character?",
        description="Every character has their own unique personality. Which one would you like to talk to?",
        color=0xff084a
        )

        for i in Info().getDokis:
            embed.add_field(name=i["name"], value=i["desc"], inline=False)
        embed.set_footer(text=f"version: {self.bot.ddae_version}")
        await interaction.response.send_message(embed=embed, view=DokiOptions(self.bot, interaction, interaction.user.id))




    @app_commands.command(name="chats")
    async def chats(self, interaction:discord.Interaction):
        """List all whitelisted channels"""
        embed = discord.Embed(
        title="Chats",
        description="All of the whitelisted channels on the server.",
        color=0xff084a
        )

        whitelist = await Info().getWhitelist
        if whitelist["channels"] == []:
            return await interaction.response.send_message("None.")
        
        for i, v in enumerate(whitelist, start=1):
            embed.add_field(name="\u200b", value=f"{i}. <#{v}>")

        embed.set_footer(text=f"version: {self.bot.ddae_version}")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
  await bot.add_cog(CustomHelp(bot))