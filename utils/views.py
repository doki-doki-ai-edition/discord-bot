from utils.data import Info
from utils import chat
from discord import SelectOption, TextStyle
from discord.ui import Modal, TextInput
import discord
import io
import random
import json

class DokiOptions(discord.ui.View):

    def __init__(self, bot, interaction, user_id, *, timeout=60):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.interaction = interaction
        self.user_id = user_id
        self.add_item(SelectDoki(bot=self.bot, interaction=self.interaction, user_id=self.user_id))


class SelectDoki(discord.ui.Select):

    def __init__(self, bot, interaction, user_id):
        self.bot = bot
        self.interaction = interaction
        self.user_id = user_id
        self.dokis = Info().getDokis
        self.maxDokis = 1
        options = [ SelectOption(emoji=i['emoji'], label=i['name'])
                    for i in self.dokis if i['name']
                ]

        super().__init__(placeholder=f"Select a character",
                         max_values=self.maxDokis,
                         min_values=1,
                         options=options)

    async def callback(self, interaction: discord.Interaction):

        # Send embed containing info of the characters
        for i in self.dokis:
            if self.values[0] == i['name'] and self.values[0] != "All":

                embed = discord.Embed(
                    title=i['name'],
                    description=i['long_desc'],
                    color=0xff084a
                    )

                with open(self.bot.PATH + i['thumbnail'], 'rb') as f:
                    file = f.read()
                    file = discord.File(io.BytesIO(file), filename='0display.png')

                embed.set_image(url='attachment://0display.png')
                await interaction.response.send_message(embed=embed, file=file)