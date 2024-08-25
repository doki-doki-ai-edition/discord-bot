from discord.ext import commands
from discord import app_commands
from utils.data import Info, Configs
from utils import chat
from utils.manager import Tools
import discord, os


class Start(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activeChatInstance = None
        self.allPrompts = []
        self.allModels = []
        self.allCharacters = {}
        for file in os.listdir(f"{self.bot.PATH}/assets/prompts/templates"):
            self.allPrompts.append(file[:-5])
        
        for modelFamily in ["openai", "groq", "ollama"]:
            models = Configs().getChatModelInfo[modelFamily]
            for m in models:
                self.allModels.append(m)
        
        # Loop through all files in characters folder ending in .py
        for file in os.listdir(f"{self.bot.PATH}/characters/"):
            if file.endswith(".py"):
                # Create the module name by stripping the .py extension
                char = file[:-3].capitalize()
                file_path = os.path.join(f"{self.bot.PATH}/characters/", file)
                
                # Execute the file and extract the THREAD_ID
                module_globals = {"__file__": file_path}
                with open(file_path) as f:
                    exec(f.read(), module_globals)
                
                # Add THREAD_ID to the dictionary if it exists
                if 'THREAD_ID' in module_globals:
                    self.allCharacters[char] = module_globals['THREAD_ID']



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

        if user_id in self.bot.active_chat_channels:
            return await self.sendErrorMessage(interaction, "You can't start a thread while one is currently active. Type `/stop` and try again.")
        return False



    async def model_autocomplete(self, interaction:discord.Interaction, current: str,):
        return [app_commands.Choice(name=name, value=name) for name in self.allModels]

    async def prompt_autocomplete(self, interaction:discord.Interaction, current: str,):
        return [app_commands.Choice(name=name, value=name) for name in self.allPrompts]



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



    @app_commands.command(name="start")
    @app_commands.autocomplete(chat_model=model_autocomplete)
    @app_commands.autocomplete(system_prompt=prompt_autocomplete)
    async def start(self, interaction:discord.Interaction, chat_model: str, first_msg: bool, system_prompt: str):
        """Begin chatting with the club members"""

        if interaction.channel_id in self.bot.active_chat_channels:
            return await interaction.response.send_message(content="**This chat is already active**")

        channel_id = interaction.channel.id
        user = interaction.user
        user_id = user.id
        whitelist = await Info().getWhitelist

        error = await self.errorChecks(interaction=interaction, channel_id=channel_id, whitelist=whitelist, user_id=user_id)
        if error: return

        print(f"Starting with model: {chat_model}")
        self.activeChatInstance = chat.ChatManager(
            bot=self.bot,
            interaction=interaction,
            chat_model=chat_model,
            channel_id=channel_id,
            first_msg=first_msg,
            characters=self.allCharacters,
            chosen_prompt=system_prompt
        )
        return await self.activeChatInstance.setup()



    @app_commands.command(name="stop")
    async def stop(self, interaction:discord.Interaction):
        """Stop any active chat"""
        self.bot.active_chat_channels.remove(interaction.channel_id)
        self.activeChatInstance.chat_still_active = False
        self.activeChatInstance = None
        await interaction.response.send_message("> Stopped any currently active chat.")



    @app_commands.command(name="settemp")
    @app_commands.autocomplete(chat_model=model_autocomplete)
    async def settemp(self, interaction:discord.Interaction, chat_model: str, temp: float):
        """Set the temperature for a specific model"""        
        success = await Tools(bot=self.bot).setModelTemperature(chat_model, temp)

        if not success:
            return await interaction.response.send_message("> Error setting model temperature.")
        await interaction.response.send_message(f"> Set the temperature for model `{chat_model}` to `{temp}`.")



    @app_commands.command(name="resetchat")
    async def resetchat(self, interaction:discord.Interaction):
        """Resets the chat history"""
        if interaction.channel_id not in self.bot.active_chat_channels:
            return await interaction.response.send_message("> No active chat found.")
        
        success = await Tools(bot=self.bot).resetChatHistory(interaction.channel_id)

        if not success:
            return await interaction.response.send_message("> Chat history doesn't exist.")
        await interaction.response.send_message("> Reset chat history.")



async def setup(bot):
    await bot.add_cog(Start(bot))