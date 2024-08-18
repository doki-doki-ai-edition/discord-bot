from discord.ext import commands
from discord import app_commands
from utils.data import Info, Configs
from utils import chat
from utils.manager import Tools
import discord

from characters.monika import THREAD_ID as monika_thread_id
from characters.sayori import THREAD_ID as sayori_thread_id
from characters.natsuki import THREAD_ID as natsuki_thread_id
from characters.yuri import THREAD_ID as yuri_thread_id


class Start(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.allModels = []
        for api in ["openai", "groq", "ollama"]:
            models = Configs().getChatModelInfo[api]
            for m in models:
                self.allModels.append(m)

    @app_commands.command(name="whitelist")
    @commands.is_owner()
    async def whitelist(self, interaction:discord.Interaction, channel:discord.TextChannel):
        """Add a channel to be whitelisted"""
        whitelist = await Info().getWhitelist
        await Tools(bot=self.bot).whitelistSetup(whitelist, channel.id)
        return await interaction.response.send_message(content="Channel added to list of available chats!")



    @app_commands.command(name="remove_whitelist")
    @commands.is_owner()
    async def remove_whitelist(self, interaction:discord.Interaction, channel_id:str):
        """Remove a whitelisted channel"""
        whitelist = await Info().getWhitelist
        state = await Tools(bot=self.bot).whitelistRemove(whitelist, channel_id)

        if state: return await interaction.response.send_message(content="Channel **removed** from whitelist.")
        return await interaction.response.send_message(content="Channel not found.")



    async def sendErrorMessage(self, interaction, message, first_message=True):
        if first_message:
            await interaction.response.send_message(content=message)
        else:
            await interaction.followup.send(content=message)
        return True


    async def errorChecks(self, interaction, channel_id, whitelist, user_id):
        if not isinstance(interaction.channel, discord.TextChannel):
            return await self.sendErrorMessage(interaction, "Start command can only be used in a Text Channel!")

        if channel_id not in whitelist["channels"]:
            return await self.sendErrorMessage(interaction, "This channel isn't **whitelisted.**")

        if user_id in self.bot.active_chat:
            return await self.sendErrorMessage(interaction, "You can't start a thread while one is currently active. Type `/stop` and try again.")

        return False

    async def model_autocomplete(self, interaction:discord.Interaction, current: str,):
        return [app_commands.Choice(name=name, value=name) for name in self.allModels]

    @app_commands.command(name="start")
    @app_commands.autocomplete(chat_model=model_autocomplete)
    async def start(self, interaction:discord.Interaction, chat_model: str, first_msg: bool):
        """Begin chatting with the club members"""

        if interaction.channel_id in self.bot.active_chat:
            return await interaction.response.send_message(content="**This chat is already active**")

        channel_id = interaction.channel.id
        user = interaction.user
        user_id = user.id
        whitelist = await Info().getWhitelist

        error = await self.errorChecks(interaction=interaction, channel_id=channel_id, whitelist=whitelist, user_id=user_id)
        if error: return

        print(f"Starting with model: {chat_model}")

        return await chat.SetupChat(bot=self.bot,
                                    interaction=interaction,
                                    chat_model=chat_model,
                                    channel_id=channel_id,
                                    first_msg=first_msg,
                                    monika_thread_id=monika_thread_id,
                                    sayori_thread_id=sayori_thread_id,
                                    natsuki_thread_id=natsuki_thread_id,
                                    yuri_thread_id=yuri_thread_id
                                    ).setup()




    @app_commands.command(name="stop")
    async def stop(self, interaction:discord.Interaction):
        """Stop any active chat"""
        self.bot.active_chat.remove(interaction.channel_id)
        await interaction.response.send_message("> Stopped any currently active chat.")




    @app_commands.command(name="resetchat")
    async def resetchat(self, interaction:discord.Interaction):
        """Resets the chat history"""
        if interaction.channel_id not in self.bot.active_chat:
            return await interaction.response.send_message("> No active chat found.")
        
        success = await Tools(bot=self.bot).resetChatHistory(interaction.channel_id)

        if not success:
            return await interaction.response.send_message("> Chat history doesn't exist.")
        await interaction.response.send_message("> Reset chat history.")



async def setup(bot):
    await bot.add_cog(Start(bot))